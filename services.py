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