import pytest
from app import create_app
from models import db, Kullanici

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    # Testleri hafızada (RAM) çalıştır, gerçek DB'yi bozma
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' 
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_ana_sayfa(client):
    response = client.get('/')
    assert response.status_code == 200

def test_kullanici_kayit(client):
    veri = {
        "eposta": "test@test.com",
        "sifre": "123456",
        "kullanici_tipi": "aday"
    }
    response = client.post('/kayit', json=veri)
    assert response.status_code == 201
    
    response_hata = client.post('/kayit', json=veri)
    assert response_hata.status_code == 400

def test_kullanici_giris(client):
    # Test için sahte bir kullanıcı oluştur
    client.post('/kayit', json={"eposta": "giris@test.com", "sifre": "123", "kullanici_tipi": "aday"})
    
    response = client.post('/giris', json={"eposta": "giris@test.com", "sifre": "123"})
    assert response.status_code == 200
    
    response_hata = client.post('/giris', json={"eposta": "giris@test.com", "sifre": "yanlis"})
    assert response_hata.status_code == 401

def test_sifre_yenile(client):
    client.post('/kayit', json={"eposta": "sifre@test.com", "sifre": "eski_sifre", "kullanici_tipi": "aday"})
    
    response = client.post('/sifre-yenile', json={"eposta": "sifre@test.com", "yeni_sifre": "yeni_sifre"})
    assert response.status_code == 200

def test_ilan_ver_ve_listele(client):
    client.post('/kayit', json={"eposta": "isveren@test.com", "sifre": "123", "kullanici_tipi": "isveren"})
    
    veri = {
        "baslik": "Python Geliştirici",
        "aciklama": "Flask bilen adaylar aranıyor.",
        "kriterler": "Python, SQL",
        "isveren_id": 1
    }
    response_ekle = client.post('/ilan-ver', json=veri)
    assert response_ekle.status_code == 201
    
    response_liste = client.get('/ilanlar')
    assert response_liste.status_code == 200

def test_arayuz_sayfalari(client):
    # Sadece HTML arayüzü döndüren (render_template) sayfaların testi
    assert client.get('/kayit-ekrani').status_code == 200
    assert client.get('/giris-ekrani').status_code == 200
    assert client.get('/sifremi-unuttum-ekrani').status_code == 200
    assert client.get('/ilan-ver-ekrani').status_code == 200
    assert client.get('/ilanlar-ekrani').status_code == 200
    assert client.get('/basvurular-ekrani').status_code == 200

def test_isveren_ilan_yonetimi(client):
    client.post('/kayit', json={"eposta": "patron@test.com", "sifre": "123", "kullanici_tipi": "isveren"})
    client.post('/ilan-ver', json={
        "baslik": "Silinecek İlan", 
        "aciklama": "Deneme", 
        "kriterler": "Deneme", 
        "isveren_id": 1
    })
    
    response_liste = client.get('/isveren-ilanlari/1')
    assert response_liste.status_code == 200
    
    response_sil = client.post('/ilan-sil', json={"ilan_id": 1, "isveren_id": 1})
    assert response_sil.status_code == 200