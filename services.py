import os
import requests
import re
import PyPDF2
from models import db, Kullanici, IsIlani, Basvuru
from werkzeug.security import generate_password_hash, check_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def kullanici_kayit_et(eposta, sifre, kullanici_tipi):
    try:
        mevcut_kullanici = Kullanici.query.filter_by(eposta=eposta).first()
        if mevcut_kullanici:
            return {"basari": False, "hata": "Bu e-posta zaten kayitli."}
        
        hashed_sifre = generate_password_hash(sifre)
        yeni_kullanici = Kullanici(eposta=eposta, sifre=hashed_sifre, kullanici_tipi=kullanici_tipi)
        db.session.add(yeni_kullanici)
        db.session.commit()
        return {"basari": True, "mesaj": "Kullanici basariyla olusturuldu!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def kullanici_dogrula(eposta, sifre):
    kullanici = Kullanici.query.filter_by(eposta=eposta).first()
    if kullanici and check_password_hash(kullanici.sifre, sifre):
        return {
            "basari": True, 
            "kullanici_tipi": kullanici.kullanici_tipi,
            "kullanici_id": kullanici.id
        }
    return {"basari": False, "hata": "E-posta veya sifre hatali!"}

def ilan_olustur(baslik, aciklama, kriterler, isveren_id):
    try:
        yeni_ilan = IsIlani(baslik=baslik, aciklama=aciklama, kriterler=kriterler, isveren_id=isveren_id)
        db.session.add(yeni_ilan)
        db.session.commit()
        return {"basari": True, "mesaj": "Is ilani basariyla yayinlandi!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def tum_ilanlari_getir(aday_id=None):
    ilanlar = IsIlani.query.all()
    sonuc = []
    for i in ilanlar:
        ilan_dict = {
            "id": i.id, 
            "baslik": i.baslik, 
            "aciklama": i.aciklama, 
            "kriterler": i.kriterler, 
            "isveren_id": i.isveren_id,
            "basvuruldu": False,
            "basvuru_puani": 0,
            "ai_aciklama": ""
        }
        if aday_id:
            basvuru = Basvuru.query.filter_by(ilan_id=i.id, aday_id=aday_id).first()
            if basvuru:
                ilan_dict["basvuruldu"] = True
                ilan_dict["basvuru_puani"] = basvuru.yapay_zeka_puani if basvuru.yapay_zeka_puani else 0
                ilan_dict["ai_aciklama"] = basvuru.yapay_zeka_geribildirim if basvuru.yapay_zeka_geribildirim else ""
        sonuc.append(ilan_dict)
    return sonuc

def ilan_sil(ilan_id, isveren_id):
    try:
        ilan = IsIlani.query.filter_by(id=ilan_id, isveren_id=isveren_id).first()
        if ilan:
            db.session.delete(ilan)
            db.session.commit()
            return {"basari": True, "mesaj": "İlan başarıyla silindi."}
        return {"basari": False, "hata": "İlan bulunamadı veya silme yetkiniz yok."}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def isverenin_ilanlarini_getir(isveren_id):
    ilanlar = IsIlani.query.filter_by(isveren_id=isveren_id).all()
    sonuc = []
    for ilan in ilanlar:
        basvurular = []
        for b in ilan.basvurular:
            basvurular.append({
                "id": b.id,
                "aday_id": b.aday_id,
                "cv_dosya_yolu": b.cv_dosya_yolu,
                "github_kullanici_adi": b.github_kullanici_adi,
                "puan": b.yapay_zeka_puani if b.yapay_zeka_puani else 0,
                "geribildirim": b.yapay_zeka_geribildirim,
                "tarih": b.tarih.strftime("%d-%m-%Y %H:%M")
            })
        
        basvurular.sort(key=lambda x: x["puan"], reverse=True)
        
        sonuc.append({
            "id": ilan.id,
            "baslik": ilan.baslik,
            "aciklama": ilan.aciklama,
            "kriterler": ilan.kriterler,
            "basvurular": basvurular
        })
    return sonuc

def basvuru_sil(basvuru_id, isveren_id):
    try:
        basvuru = Basvuru.query.get(basvuru_id)
        if not basvuru:
            return {"basari": False, "hata": "Başvuru bulunamadı."}
        if basvuru.ilan.isveren_id != isveren_id:
            return {"basari": False, "hata": "Yetkisiz işlem."}
        
        db.session.delete(basvuru)
        db.session.commit()
        return {"basari": True, "mesaj": "Başvuru başarıyla silindi."}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def pdf_den_bilgi_cikar(dosya_yolu):
    metin = ""
    github_kullanici_adi = None
    try:
        with open(dosya_yolu, 'rb') as dosya:
            okuyucu = PyPDF2.PdfReader(dosya)
            for sayfa in okuyucu.pages:
                sayfa_metni = sayfa.extract_text()
                if sayfa_metni:
                    metin += sayfa_metni + " "
        
        eslesme = re.search(r"github\.com/([a-zA-Z0-9._-]+)", metin)
        if eslesme:
            github_kullanici_adi = eslesme.group(1)
            
    except Exception:
        pass
        
    return metin.strip(), github_kullanici_adi

def github_bilgilerini_getir(github_kullanici_adi):
    if not github_kullanici_adi:
        return None
        
    try:
        url = f"https://api.github.com/users/{github_kullanici_adi}/repos"
        headers = {"User-Agent": "JobMatchingApp"}
        print(f"DEBUG: GitHub API isteği atılıyor: {url}", flush=True)
        cevap = requests.get(url, headers=headers, timeout=5)
        print(f"DEBUG: GitHub API status: {cevap.status_code}", flush=True)
        
        if cevap.status_code == 200:
            repolar = cevap.json()
            repo_sayisi = len(repolar)
            diller = list(set([repo.get("language") for repo in repolar if repo.get("language")]))
            return {"repo_sayisi": repo_sayisi, "diller": diller}
        return None
    except Exception as e:
        print(f"DEBUG: GitHub API hatası: {e}", flush=True)
        return None

ESANLAMLI = {
    "javasc": "javascript",
    "js": "javascript", 
    "springboot": "spring boot",
    "spring-boot": "spring boot",
    "nodejs": "node js",
    "node-js": "node js",
    "postgresql": "postgres",
    "psql": "postgres",
    "vscode": "vs code",
    "vs-code": "vs code",
    "bilgisayar muhendisi": "bilgisayar muhendisligi",
    "yazilim muhendisi": "yazilim muhendisligi",
    "ml": "machine learning",
    "ai": "yapay zeka",
    "db": "veritabani",
    "css3": "css",
    "html5": "html",
    "reactjs": "react",
    "vuejs": "vue",
    "dotnet": "net",
    ".net": "net",
    "mssql": "sql server",
    "mongo": "mongodb",
}

def ai_cv_degerlendir(cv_metni, ilan_metni, github_veri=None):
    def metni_temizle(metin):
        metin = metin.lower()
        metin = re.sub(r'[^\w\s]', ' ', metin)
        metin = re.sub(r'\s+', ' ', metin)
        for yanlis, dogru in ESANLAMLI.items():
            metin = re.sub(r'\b' + re.escape(yanlis) + r'\b', dogru, metin)
        return metin.strip()

    cv_temiz = metni_temizle(cv_metni)
    ilan_temiz = metni_temizle(ilan_metni)

    try:
        vectorizer = TfidfVectorizer(
            stop_words=None,
            ngram_range=(1, 2),
            min_df=1,
            analyzer='word'
        )
        tfidf_matris = vectorizer.fit_transform([ilan_temiz, cv_temiz])
        benzerlik_orani = cosine_similarity(tfidf_matris[0:1], tfidf_matris[1:2])[0][0]
        nlp_puani = int(benzerlik_orani * 100)
    except Exception:
        nlp_puani = 0

    ilan_kelimeler = set(ilan_temiz.split())
    cv_kelimeler = set(cv_temiz.split())
    eslesme = len(ilan_kelimeler & cv_kelimeler)
    eslesme_orani = eslesme / len(ilan_kelimeler) if ilan_kelimeler else 0
    kelime_puani = int(eslesme_orani * 100)

    ilan_kelime_sayisi = len(set(ilan_temiz.split()))
    if ilan_kelime_sayisi < 30:
        nlp_puani = int((nlp_puani * 0.1) + (kelime_puani * 0.9))
    else:
        nlp_puani = int((nlp_puani * 0.3) + (kelime_puani * 0.7))
    nlp_puani = min(nlp_puani, 100)

    api_key = os.environ.get("GROQ_API_KEY")
    ai_ozet = "GitHub profili bulunamadı veya analiz edilemedi."
    ai_katkisi = 0

    if github_veri and api_key:
        repo_sayisi = github_veri.get("repo_sayisi", 0)
        diller = ", ".join(github_veri.get("diller", []))
        
        prompt = (
            f"Sen bir İK uzmanısın. Adayın GitHub profilinde {repo_sayisi} repo var "
            f"ve şu dilleri kullanmış: {diller}. İş ilanı kriterleri: {ilan_metni}. "
            "Adayın GitHub projelerinin bu ilana uygunluğunu analiz et. "
            "Cevabını SADECE şu formatta ver:\n"
            "Skor: [0 ile 30 arası bir sayı]\n"
            "Özet: [Maksimum 2 cümlelik profesyonel bir analiz]"
        )
        print(f"DEBUG: Groq isteği atılıyor, repo_sayisi: {repo_sayisi}, diller: {diller}", flush=True)
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.1-8b-instant",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200
            }
            cevap = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=10)
            sonuc_json = cevap.json()
            
            if "choices" in sonuc_json:
                sonuc_metni = sonuc_json["choices"][0]["message"]["content"]
                puan_eslesme = re.search(r"Skor:\s*(\d+)", sonuc_metni)
                if puan_eslesme:
                    ai_katkisi = min(int(puan_eslesme.group(1)), 30)
                ozet_eslesme = re.search(r"Özet:\s*(.*)", sonuc_metni, re.DOTALL | re.IGNORECASE)
                if ozet_eslesme:
                    ai_ozet = ozet_eslesme.group(1).strip()
            else:
                ai_ozet = f"API Hatası: {sonuc_json.get('error', 'Bilinmeyen hata')}"
        except Exception as e:
            print(f"DEBUG: Groq hatası: {e}", flush=True)
            ai_katkisi = 0
            ai_ozet = "Bağlantı hatası yaşandı."
    elif not api_key and github_veri:
        ai_ozet = "Sistemde API anahtarı bulunamadı."

    final_puan = int((nlp_puani * 0.85) + ai_katkisi)
    final_puan = min(final_puan, 100)

    ozet_metni = (
        f"Kendi NLP Modelimiz ile Metin Benzerlik Skoru (TF-IDF): %{nlp_puani}\n"
        f"Yapay Zeka GitHub Analiz Skoru: +{ai_katkisi} Puan\n\n"
        f"Yapay Zeka Kanaat Özeti: {ai_ozet}\n"
    )

    return {"puan": final_puan, "ozet": ozet_metni}

def basvuru_kaydet(ilan_id, aday_id, cv_dosya_yolu, github_kullanici_adi, puan, geribildirim):
    try:
        mevcut_basvuru = Basvuru.query.filter_by(ilan_id=ilan_id, aday_id=aday_id).first()
        if mevcut_basvuru:
            return {"basari": False, "hata": "Bu ilana zaten başvurdunuz."}

        yeni_basvuru = Basvuru(
            ilan_id=ilan_id, 
            aday_id=aday_id, 
            cv_dosya_yolu=cv_dosya_yolu,
            github_kullanici_adi=github_kullanici_adi,
            yapay_zeka_puani=puan,
            yapay_zeka_geribildirim=geribildirim
        )
        db.session.add(yeni_basvuru)
        db.session.commit()
        return {"basari": True, "mesaj": "Başvuru başarıyla alındı ve AI tarafından değerlendirildi!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def sifre_guncelle(eposta, yeni_sifre):
    try:
        kullanici = Kullanici.query.filter_by(eposta=eposta).first()
        if not kullanici:
            return {"basari": False, "hata": "Bu e-posta adresiyle kayıtlı kullanıcı bulunamadı."}
        
        kullanici.sifre = generate_password_hash(yeni_sifre)
        db.session.commit()
        return {"basari": True, "mesaj": "Şifreniz başarıyla güncellendi!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}