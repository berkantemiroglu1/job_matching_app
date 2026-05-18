import requests # http istek
from models import db, Kullanici, IsIlani, Basvuru

def kullanici_kayit_et(eposta, sifre, kullanici_tipi):
    try:
        # yeni kayit
        yeni_kullanici = Kullanici(eposta=eposta, sifre=sifre, kullanici_tipi=kullanici_tipi)
        db.session.add(yeni_kullanici)
        db.session.commit() # onaylama
        return {"basari": True, "mesaj": "Kullanici basariyla olusturuldu!"}
    except Exception as e:
        db.session.rollback() # geri al
        return {"basari": False, "hata": str(e)}

def kullanici_dogrula(eposta, sifre):
    # giris kontrol
    kullanici = Kullanici.query.filter_by(eposta=eposta, sifre=sifre).first()
    if kullanici:
        return {"basari": True, "kullanici_tipi": kullanici.kullanici_tipi}
    return {"basari": False, "hata": "E-posta veya sifre hatali!"}

def ilan_olustur(baslik, aciklama, kriterler, isveren_id):
    try:
        # yeni ilan
        yeni_ilan = IsIlani(baslik=baslik, aciklama=aciklama, kriterler=kriterler, isveren_id=isveren_id)
        db.session.add(yeni_ilan)
        db.session.commit() # onaylama
        return {"basari": True, "mesaj": "Is ilani basariyla yayinlandi!"}
    except Exception as e:
        db.session.rollback() # geri al
        return {"basari": False, "hata": str(e)}

def tum_ilanlari_getir():
    # ilan listesi
    ilanlar = IsIlani.query.all()
    return [{"id": i.id, "baslik": i.baslik, "aciklama": i.aciklama, "kriterler": i.kriterler, "isveren_id": i.isveren_id} for i in ilanlar]

def basvuru_olustur(ilan_id, aday_id, cv_metni, yapay_zeka_puani=None):
    try:
        # yeni basvuru
        yeni_basvuru = Basvuru(ilan_id=ilan_id, aday_id=aday_id, cv_metni=cv_metni, yapay_zeka_puani=yapay_zeka_puani)
        db.session.add(yeni_basvuru)
        db.session.commit() # onaylama
        return {"basari": True, "mesaj": "Basvuru basariyla alindi!"}
    except Exception as e:
        db.session.rollback() # geri al
        return {"basari": False, "hata": str(e)}

def ai_cv_degerlendir(cv_metni, ilan_metni):
    # yerel ai
    url = "http://localhost:11434/api/generate"
    
    # prompt hazirla
    prompt = f"CV: {cv_metni}\nİlan: {ilan_metni}\nAday beklentileri karşılıyor mu? Eksikler neler? Kısa özetle."
    
    # istek paketi
    data = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }
    
    # istek at
    cevap = requests.post(url, json=data)
    
    # cevabi don
    return cevap.json()["response"]