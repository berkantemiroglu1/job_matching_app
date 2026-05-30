import requests
import re
import PyPDF2
from models import db, Kullanici, IsIlani, Basvuru
from werkzeug.security import generate_password_hash, check_password_hash

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
        
        eslesme = re.search(r"github\.com/([a-zA-Z0-9-]+)", metin)
        if eslesme:
            github_kullanici_adi = eslesme.group(1)
            
    except Exception as e:
        print(f"PDF Okuma Hatası: {e}")
        
    return metin.strip(), github_kullanici_adi

def github_bilgilerini_getir(github_kullanici_adi):
    if not github_kullanici_adi:
        return None
        
    try:
        url = f"https://api.github.com/users/{github_kullanici_adi}/repos"
        headers = {"User-Agent": "JobMatchingApp"}
        cevap = requests.get(url, headers=headers)
        
        if cevap.status_code == 200:
            repolar = cevap.json()
            repo_sayisi = len(repolar)
            diller = list(set([repo.get("language") for repo in repolar if repo.get("language")]))
            return {"repo_sayisi": repo_sayisi, "diller": diller}
        return None
    except Exception:
        return None

def ai_cv_degerlendir(cv_metni, ilan_metni, github_veri=None):
    url = "http://localhost:11434/api/generate"
    
    if github_veri:
        repo_sayisi = github_veri.get("repo_sayisi", 0)
        diller = ", ".join(github_veri.get("diller", []))
        github_metni = f"\nAdayın GitHub Profili: {repo_sayisi} adet açık kaynak projesi var. Kullanılan diller: {diller}."
    else:
        github_metni = "\nAdayın GitHub profili bulunmuyor, sadece CV metni üzerinden değerlendir."

    prompt = (
        f"İlan Kriterleri: {ilan_metni}\n"
        f"Adayın CV'si: {cv_metni}"
        f"{github_metni}\n\n"
        "Sen ÇOK KATI, acımasız ve gerçekçi bir İK uzmanısın. Adayın ilana uygunluğunu 0 ile 100 arasında puanla.\n"
        "KESİN KURALLAR:\n"
        "1. İlanda açıkça istenen teknolojiler (örn: SQL, React, HTML) adayın CV'sinde HİÇ YOKSA, puan kesinlikle 20-40 aralığında olmalıdır.\n"
        "2. İlanda istenen üniversite bölümü (örn: Bilgisayar Mühendisliği) ile adayın bölümü uyuşmuyorsa puan kır.\n"
        "3. Adayın sadece başka dilleri bilmesi (örn: Python, C bilip SQL bilmemesi) ilana uygun olduğu anlamına GELMEZ. İstenen kriter yoksa puanı acımasızca düşür.\n\n"
        "Lütfen cevabını kesinlikle sadece şu formatta ver:\n"
        "Puan: [0-100 arası sayı]\n"
        "Özet: [Neden bu kadar düşük veya yüksek puan verdiğine dair sert, net ve gerçekçi bir değerlendirme]"
    )
    
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        cevap = requests.post(url, json=data)
        sonuc_metni = cevap.json()["response"]
        
        puan_eslesme = re.search(r"Puan:\s*(\d+)", sonuc_metni)
        puan = int(puan_eslesme.group(1)) if puan_eslesme else 0
        
        ozet_eslesme = re.search(r"Özet:\s*(.*)", sonuc_metni, re.DOTALL | re.IGNORECASE)
        ozet = ozet_eslesme.group(1).strip() if ozet_eslesme else sonuc_metni
        
        return {"puan": puan, "ozet": ozet}
        
    except Exception:
        return {"puan": 0, "ozet": "Yapay zeka değerlendirmesi sırasında hata oluştu."}

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