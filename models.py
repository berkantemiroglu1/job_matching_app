from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eposta = db.Column(db.String(120), unique=True, nullable=False)
    sifre = db.Column(db.String(80), nullable=False)
    kullanici_tipi = db.Column(db.String(20), nullable=False) # isveren/aday

class IsIlani(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    baslik = db.Column(db.String(100), nullable=False)
    aciklama = db.Column(db.Text, nullable=False)
    kriterler = db.Column(db.Text, nullable=False)
    isveren_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    olusturulma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)

class Basvuru(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ilan_id = db.Column(db.Integer, db.ForeignKey('is_ilani.id'), nullable=False)
    aday_id = db.Column(db.Integer, db.ForeignKey('kullanici.id'), nullable=False)
    cv_metni = db.Column(db.Text, nullable=False)
    yapay_zeka_puani = db.Column(db.Integer, nullable=True) # gemini den gelecek puan