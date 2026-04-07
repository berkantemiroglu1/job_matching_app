from flask import Flask, request, jsonify
from models import db, Kullanici

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def ana_sayfa():
    return "Sistem Ayakta! Veritabanı Hazır."

@app.route('/kayit', methods=['POST'])
def kayit_ol():
    veri = request.get_json()
    yeni_kullanici = Kullanici(
        eposta=veri['eposta'],
        sifre=veri['sifre'],
        kullanici_tipi=veri['kullanici_tipi']
    )
    db.session.add(yeni_kullanici)
    db.session.commit()
    return jsonify({"mesaj": "Kullanici basariyla olusturuldu!"}), 201

@app.route('/giris', methods=['POST'])
def giris_yap():
    veri = request.get_json()
    kullanici = Kullanici.query.filter_by(eposta=veri['eposta'], sifre=veri['sifre']).first()
    
    if kullanici:
        return jsonify({"mesaj": "Giris basarili!", "kullanici_tipi": kullanici.kullanici_tipi}), 200
    else:
        return jsonify({"hata": "E-posta veya sifre hatali!"}), 401

if __name__ == '__main__':
    app.run(debug=True)