package com.example.jobmatchingmobile;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class SifremiUnuttumActivity extends AppCompatActivity {

    private EditText editSifreSifirlaEposta, editSifreSifirlaYeniSifre;
    private Button btnSifremiYenile;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_sifremi_unuttum);

        editSifreSifirlaEposta = findViewById(R.id.editSifreSifirlaEposta);
        editSifreSifirlaYeniSifre = findViewById(R.id.editSifreSifirlaYeniSifre);
        btnSifremiYenile = findViewById(R.id.btnSifremiYenile);

        btnSifremiYenile.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String eposta = editSifreSifirlaEposta.getText().toString().trim();
                String yeniSifre = editSifreSifirlaYeniSifre.getText().toString().trim();

                if (eposta.isEmpty() || yeniSifre.isEmpty()) {
                    Toast.makeText(SifremiUnuttumActivity.this, "Lütfen tüm alanları doldurun!", Toast.LENGTH_SHORT).show();
                    return;
                }

                ApiService apiService = ApiClient.getClient().create(ApiService.class);
                SifreYenileIstek istek = new SifreYenileIstek(eposta, yeniSifre);

                Call<BasitCevap> call = apiService.sifreYenile(istek);
                call.enqueue(new Callback<BasitCevap>() {
                    @Override
                    public void onResponse(Call<BasitCevap> call, Response<BasitCevap> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            Toast.makeText(SifremiUnuttumActivity.this, response.body().mesaj, Toast.LENGTH_LONG).show();
                            finish();
                        } else {
                            Toast.makeText(SifremiUnuttumActivity.this, "Kullanıcı bulunamadı veya hata oluştu.", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<BasitCevap> call, Throwable t) {
                        Toast.makeText(SifremiUnuttumActivity.this, "Bağlantı hatası: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
            }
        });
    }
}