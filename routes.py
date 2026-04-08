from flask import Blueprint, request, jsonify
import services

# Blueprint tanımlaması
api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def ana_sayfa():
    return "Sistem Ayakta! Veritabanı Hazır."

@api_bp.route('/kayit', methods=['POST'])
def kayit_ol():
    veri = request.get_json()
    # Postman'den gelen JSON içindeki 'eposta', 'sifre' ve 'kullanici_tipi' aranır
    sonuc = services.kullanici_kayit_et(veri['eposta'], veri['sifre'], veri['kullanici_tipi'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 201
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/giris', methods=['POST'])
def giris_yap():
    veri = request.get_json()
    sonuc = services.kullanici_dogrula(veri['eposta'], veri['sifre'])
    if sonuc['basari']:
        return jsonify({"mesaj": "Giris basarili!", "kullanici_tipi": sonuc['kullanici_tipi']}), 200
    return jsonify({"hata": sonuc['hata']}), 401

@api_bp.route('/ilan-ver', methods=['POST'])
def ilan_ver():
    veri = request.get_json()
    sonuc = services.ilan_olustur(veri['baslik'], veri['aciklama'], veri['kriterler'], veri['isveren_id'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 201
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/ilanlar', methods=['GET'])
def ilanlari_getir():
    ilanlar = services.tum_ilanlari_getir()
    return jsonify(ilanlar), 200

@api_bp.route('/basvuru-yap', methods=['POST'])
def basvuru_yap():
    veri = request.get_json()
    # cv_metni olarak güncellendi
    sonuc = services.basvuru_olustur(veri['ilan_id'], veri['aday_id'], veri['cv_metni'], veri.get('yapay_zeka_puani'))
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 201
    return jsonify({"hata": sonuc['hata']}), 400