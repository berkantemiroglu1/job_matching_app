# python -m pytest --cov=. test_app.py
import pytest
from app import create_app
from models import db, Kullanici

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Testleri hafızada (RAM) çalıştır, gerçek DB'yi bozma
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_ana_sayfa(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Sistem Ayakta!" in response.data

def test_kullanici_kayit(client):
    veri = {
        "eposta": "test@test.com",
        "sifre": "123456",
        "kullanici_tipi": "aday"
    }
    response = client.post('/kayit', json=veri)
    assert response.status_code == 201
    assert b"Kullanici basariyla olusturuldu!" in response.data

    response_hata = client.post('/kayit', json=veri)
    assert response_hata.status_code == 400