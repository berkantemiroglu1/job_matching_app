import os
import cloudinary
import cloudinary.uploader
from flask import Blueprint, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import services

api_bp = Blueprint('api', __name__)

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_bp.route('/', methods=['GET'])
def ana_sayfa():
    return "Sistem Ayakta! Arayüzleri görmek için tarayıcıda /kayit-ekrani veya /giris-ekrani adreslerine gidin."

@api_bp.route('/kayit-ekrani', methods=['GET'])
def kayit_ekrani():
    return render_template('kayit.html')

@api_bp.route('/giris-ekrani', methods=['GET'])
def giris_ekrani():
    return render_template('giris.html')

@api_bp.route('/sifremi-unuttum-ekrani', methods=['GET'])
def sifremi_unuttum_ekrani():
    return render_template('sifremi_unuttum.html')

@api_bp.route('/ilan-ver-ekrani', methods=['GET'])
def ilan_ver_ekrani():
    return render_template('ilan_ver.html')

@api_bp.route('/ilanlar-ekrani', methods=['GET'])
def ilanlar_ekrani():
    return render_template('ilanlar.html')

@api_bp.route('/basvurular-ekrani', methods=['GET'])
def basvurular_ekrani():
    return render_template('basvurular.html')

@api_bp.route('/kayit', methods=['POST'])
def kayit_ol():
    veri = request.get_json()
    sonuc = services.kullanici_kayit_et(veri['eposta'], veri['sifre'], veri['kullanici_tipi'])
    if sonuc['basari']:
        return jsonify({"basari": True, "mesaj": sonuc['mesaj']}), 201
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/giris', methods=['POST'])
def giris_yap():
    veri = request.get_json()
    sonuc = services.kullanici_dogrula(veri['eposta'], veri['sifre'])
    if sonuc['basari']:
        return jsonify({
            "basari": True,
            "mesaj": "Giris basarili!",
            "kullanici_tipi": sonuc['kullanici_tipi'],
            "kullanici_id": sonuc['kullanici_id']
        }), 200
    return jsonify({
        "basari": False,
        "hata": sonuc['hata']
    }), 401

@api_bp.route('/sifre-yenile', methods=['POST'])
def sifre_yenile():
    veri = request.get_json()
    sonuc = services.sifre_guncelle(veri['eposta'], veri['yeni_sifre'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 200
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/ilan-ver', methods=['POST'])
def ilan_ver():
    veri = request.get_json()
    sonuc = services.ilan_olustur(veri['baslik'], veri['aciklama'], veri['kriterler'], veri['isveren_id'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 201
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/ilanlar', methods=['GET'])
def ilanlari_getir():
    kullanici_id = request.args.get('kullanici_id', type=int)
    ilanlar = services.tum_ilanlari_getir(kullanici_id)
    return jsonify(ilanlar), 200

@api_bp.route('/basvuru-yap', methods=['POST'])
def basvuru_yap():
    if 'cv_dosyasi' not in request.files:
        return jsonify({"hata": "CV dosyasi bulunamadi"}), 400

    dosya = request.files['cv_dosyasi']
    ilan_id = request.form.get('ilan_id')
    aday_id = request.form.get('aday_id')
    ilan_metni = request.form.get('ilan_metni')

    if dosya.filename == '':
        return jsonify({"hata": "Dosya secilmedi"}), 400

    filename = secure_filename(dosya.filename)
    benzersiz_ad = f"aday_{aday_id}_ilan_{ilan_id}_{filename}"
    dosya_yolu = os.path.join(UPLOAD_FOLDER, benzersiz_ad)
    dosya.save(dosya_yolu)
    print(f"DEBUG: Dosya kaydedildi mi: {os.path.exists(dosya_yolu)}")
    print(f"DEBUG: Dosya yolu: {dosya_yolu}")

    try:
        cloudinary_sonuc = cloudinary.uploader.upload(
            dosya_yolu,
            resource_type="raw",
            public_id=benzersiz_ad,
            folder="cv_uploads"
        )
        cv_url = cloudinary_sonuc['secure_url']
    except Exception:
        cv_url = benzersiz_ad

    cv_metni, github_adi = services.pdf_den_bilgi_cikar(dosya_yolu)
    print(f"DEBUG: GitHub adi: {github_adi}")
    print(f"DEBUG: CV metni ilk 200: {cv_metni[:200]}")
    github_veri = services.github_bilgilerini_getir(github_adi)
    print(f"DEBUG: github_veri: {github_veri}")
    ai_sonuc = services.ai_cv_degerlendir(cv_metni, ilan_metni, github_veri)

    kayit_sonuc = services.basvuru_kaydet(
        ilan_id,
        aday_id,
        cv_url,
        github_adi,
        ai_sonuc['puan'],
        ai_sonuc['ozet']
    )

    if kayit_sonuc['basari']:
        return jsonify({
            "mesaj": kayit_sonuc['mesaj'],
            "puan": ai_sonuc['puan'],
            "geribildirim": ai_sonuc['ozet']
        }), 201

    return jsonify({"hata": kayit_sonuc['hata']}), 400

@api_bp.route('/isveren-ilanlari/<int:isveren_id>', methods=['GET'])
def isveren_ilanlari(isveren_id):
    sonuc = services.isverenin_ilanlarini_getir(isveren_id)
    return jsonify(sonuc), 200

@api_bp.route('/ilan-sil', methods=['POST'])
def ilan_sil_route():
    veri = request.get_json()
    sonuc = services.ilan_sil(veri['ilan_id'], veri['isveren_id'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 200
    return jsonify({"hata": sonuc['hata']}), 400

@api_bp.route('/uploads/<filename>')
def cv_indir(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@api_bp.route('/basvuru-sil', methods=['POST'])
def basvuru_sil_route():
    veri = request.get_json()
    sonuc = services.basvuru_sil(veri['basvuru_id'], veri['isveren_id'])
    if sonuc['basari']:
        return jsonify({"mesaj": sonuc['mesaj']}), 200
    return jsonify({"hata": sonuc['hata']}), 400