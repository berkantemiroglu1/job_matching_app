from flask import Flask
from models import db

app = Flask(__name__)
# veritabanı ayarı (Aynı klasöre veritabani.db adında bir dosya açacak)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Uygulama ilk çalıştığında veritabanı tablolarını otomatik oluşturur
with app.app_context():
    db.create_all()

@app.route('/')
def ana_sayfa():
    return "Sistem Ayakta! Veritabanı Hazır."

if __name__ == '__main__':
    app.run(debug=True)