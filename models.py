from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eposta = db.Column(db.String(255), unique=True, nullable=False)
    ifre = db.Column(db.String(512), nullable=False)
    kullanici_tipi = db.Column(db.String(20), nullable=False) # 'aday' veya 'isveren'

class IsIlani(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(200), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    kriterler = db.Column(db.Text, nullable=False)
    isveren_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    
    # İşveren silindiğinde veya ilan silindiğinde başvurular da otomatik silinsin
    basvurular = db.relationship('Basvuru', backref='ilan', cascade="all, delete-orphan")

class Basvuru(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ilan_id = db.Column(db.Integer, db.ForeignKey('is_ilani.id'), nullable=False)
    aday_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    cv_dosya_yolu = db.Column(db.String(255), nullable=False) # PDF dosyasının adı/yolu
    github_kullanici_adi = db.Column(db.String(100), nullable=True) # PDF'ten otomatik çekilecek
    yapay_zeka_puani = db.Column(db.Integer, nullable=True)
    yapay_zeka_geribildirim = db.Column(db.Text, nullable=True) # Adaya gösterilecek eksik/iyi yönler
    tarih = db.Column(db.DateTime, default=datetime.utcnow)