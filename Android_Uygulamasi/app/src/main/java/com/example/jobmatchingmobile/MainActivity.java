package com.example.jobmatchingmobile;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class MainActivity extends AppCompatActivity {

    private EditText editEposta;
    private EditText editSifre;
    private Button btnGirisYap;
    private TextView textMesaj;
    private TextView textKayitSayfasinaGit;
    private TextView textSifremiUnuttum;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        editEposta = findViewById(R.id.editEposta);
        editSifre = findViewById(R.id.editSifre);
        btnGirisYap = findViewById(R.id.btnGirisYap);
        textMesaj = findViewById(R.id.textMesaj);
        textKayitSayfasinaGit = findViewById(R.id.textKayitSayfasinaGit);
        textSifremiUnuttum = findViewById(R.id.textSifremiUnuttum);

        textKayitSayfasinaGit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, KayitActivity.class);
                startActivity(intent);
            }
        });

        textSifremiUnuttum.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(MainActivity.this, SifremiUnuttumActivity.class);
                startActivity(intent);
            }
        });

        btnGirisYap.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                girisYap();
            }
        });
    }

    private void girisYap() {
        String eposta = editEposta.getText().toString().trim();
        String sifre = editSifre.getText().toString().trim();

        if (eposta.isEmpty() || sifre.isEmpty()) {
            textMesaj.setText("E-posta ve şifre boş bırakılamaz.");
            textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
            return;
        }

        textMesaj.setText("Giriş yapılıyor, lütfen bekleyin...");
        textMesaj.setTextColor(android.graphics.Color.parseColor("#111827"));

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        GirisIstek istek = new GirisIstek(eposta, sifre);

        Call<GirisCevap> call = apiService.girisYap(istek);
        call.enqueue(new Callback<GirisCevap>() {
            @Override
            public void onResponse(Call<GirisCevap> call, Response<GirisCevap> response) {
                if (response.isSuccessful() && response.body() != null) {
                    GirisCevap cevap = response.body();

                    if (cevap.basari) {
                        textMesaj.setText("Giriş Başarılı! Yönlendiriliyorsunuz...");
                        textMesaj.setTextColor(android.graphics.Color.parseColor("#2ecc71"));

                        SharedPreferences sharedPreferences = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
                        SharedPreferences.Editor editor = sharedPreferences.edit();
                        editor.putString("aktifRol", cevap.kullanici_tipi);
                        editor.putInt("aktifId", cevap.kullanici_id);
                        editor.apply();
                        Intent intent = new Intent(MainActivity.this, IlanlarActivity.class);
                        startActivity(intent);
                        finish();

                    } else {
                        textMesaj.setText(cevap.hata != null ? cevap.hata : "Giriş başarısız.");
                        textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
                    }
                } else {
                    textMesaj.setText("Sunucu hatası veya e-posta/şifre yanlış.");
                    textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
                }
            }

            @Override
            public void onFailure(Call<GirisCevap> call, Throwable t) {
                textMesaj.setText("Bağlantı hatası: " + t.getMessage());
                textMesaj.setTextColor(android.graphics.Color.parseColor("#FF3B57"));
            }
        });
    }
}