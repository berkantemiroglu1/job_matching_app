package com.example.jobmatchingmobile;

import android.os.Bundle;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.util.Random;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class KayitActivity extends AppCompatActivity {

    private EditText editEposta, editSifre, editMatematikCevabi;
    private Spinner spinnerKullaniciTipi;
    private TextView textMatematikSorusu, textMesaj;
    private Button btnKayitOl;
    private int dogruCevap;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_kayit);

        editEposta = findViewById(R.id.editKayitEposta);
        editSifre = findViewById(R.id.editKayitSifre);
        editMatematikCevabi = findViewById(R.id.editMatematikCevabi);
        spinnerKullaniciTipi = findViewById(R.id.spinnerKullaniciTipi);
        textMatematikSorusu = findViewById(R.id.textMatematikSorusu);
        textMesaj = findViewById(R.id.textKayitMesaj);
        btnKayitOl = findViewById(R.id.btnKayitOl);

        // Spinner (Açılır menü) içeriğini ayarlama
        String[] tipler = {"aday", "isveren"};
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, tipler);
        spinnerKullaniciTipi.setAdapter(adapter);

        // Bot koruması: Rastgele matematik sorusu üretme
        matematikSorusuUret();

        btnKayitOl.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                kayitIsleminiBaslat();
            }
        });
    }

    private void matematikSorusuUret() {
        Random random = new Random();
        int sayi1 = random.nextInt(10) + 1; // 1 ile 10 arası
        int sayi2 = random.nextInt(10) + 1;
        dogruCevap = sayi1 + sayi2;
        textMatematikSorusu.setText("Bot Koruması: " + sayi1 + " + " + sayi2 + " = ?");
    }

    private void kayitIsleminiBaslat() {
        String eposta = editEposta.getText().toString().trim();
        String sifre = editSifre.getText().toString().trim();
        String tip = spinnerKullaniciTipi.getSelectedItem().toString();
        String verilenCevap = editMatematikCevabi.getText().toString().trim();

        if (eposta.isEmpty() || sifre.isEmpty() || verilenCevap.isEmpty()) {
            textMesaj.setText("Lütfen tüm alanları doldurun.");
            textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
            return;
        }

        // Matematik kontrolü
        if (Integer.parseInt(verilenCevap) != dogruCevap) {
            textMesaj.setText("Matematik işleminin sonucu yanlış!");
            textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
            matematikSorusuUret(); // Yanlışsa yeni soru sor
            editMatematikCevabi.setText("");
            return;
        }

        textMesaj.setText("Kayıt yapılıyor, lütfen bekleyin...");
        textMesaj.setTextColor(android.graphics.Color.parseColor("#111827"));

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        KayitIstek istek = new KayitIstek(eposta, sifre, tip);

        Call<GirisCevap> call = apiService.kayitOl(istek);
        call.enqueue(new Callback<GirisCevap>() {
            @Override
            public void onResponse(Call<GirisCevap> call, Response<GirisCevap> response) {
                if (response.isSuccessful() && response.body() != null) {
                    GirisCevap cevap = response.body();
                    if (cevap.basari) {
                        textMesaj.setText("Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...");
                        textMesaj.setTextColor(android.graphics.Color.parseColor("#2ecc71"));

                        // 2 saniye bekleyip giriş ekranına geri dön (görsel güzellik için)
                        btnKayitOl.postDelayed(new Runnable() {
                            @Override
                            public void run() {
                                finish();
                            }
                        }, 2000);

                    } else {
                        textMesaj.setText(cevap.hata != null ? cevap.hata : "Kayıt başarısız.");
                        textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
                    }
                } else {
                    textMesaj.setText("Sunucu hatası.");
                    textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
                }
            }

            @Override
            public void onFailure(Call<GirisCevap> call, Throwable t) {
                textMesaj.setText("Bağlantı hatası.");
                textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
            }
        });
    }
}