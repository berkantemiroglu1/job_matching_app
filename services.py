import requests
from models import db, Kullanici, IsIlani, Basvuru

def kullanici_kayit_et(eposta, sifre, kullanici_tipi):
    try:
        yeni_kullanici = Kullanici(eposta=eposta, sifre=sifre, kullanici_tipi=kullanici_tipi)
        db.session.add(yeni_kullanici)
        db.session.commit()
        return {"basari": True, "mesaj": "Kullanici basariyla olusturuldu!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

def kullanici_dogrula(eposta, sifre):
    kullanici = Kullanici.query.filter_by(eposta=eposta, sifre=sifre).first()
    if kullanici:
        return {"basari": True, "kullanici_tipi": kullanici.kullanici_tipi}
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

def tum_ilanlari_getir():
    ilanlar = IsIlani.query.all()
    return [{"id": i.id, "baslik": i.baslik, "aciklama": i.aciklama, "kriterler": i.kriterler, "isveren_id": i.isveren_id} for i in ilanlar]

def basvuru_olustur(ilan_id, aday_id, cv_metni, yapay_zeka_puani=None):
    try:
        yeni_basvuru = Basvuru(ilan_id=ilan_id, aday_id=aday_id, cv_metni=cv_metni, yapay_zeka_puani=yapay_zeka_puani)
        db.session.add(yeni_basvuru)
        db.session.commit()
        return {"basari": True, "mesaj": "Basvuru basariyla alindi!"}
    except Exception as e:
        db.session.rollback()
        return {"basari": False, "hata": str(e)}

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
        "Sen bir İK uzmanısın. Yukarıdaki bilgilere göre adayın ilana uygunluğunu 0 ile 100 arasında puanla değerlendir.\n"
        "Lütfen cevabını sadece şu formatta ver:\n"
        "Puan: [0-100 arası sayı]\n"
        "Özet: [Neden bu puanı verdiğine dair kısa ve net bir değerlendirme]"
    )
    
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        cevap = requests.post(url, json=data)
        return cevap.json()["response"]
    except Exception:
        return "Puan: 0\nÖzet: Yapay zeka değerlendirmesi sırasında hata oluştu."