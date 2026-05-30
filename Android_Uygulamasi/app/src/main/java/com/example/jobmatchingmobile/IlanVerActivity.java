package com.example.jobmatchingmobile;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class IlanVerActivity extends AppCompatActivity {

    private EditText editIlanBaslik, editIlanAciklama, editIlanKriterler;
    private Button btnIlanYayinla;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ilan_ver);

        editIlanBaslik = findViewById(R.id.editIlanBaslik);
        editIlanAciklama = findViewById(R.id.editIlanAciklama);
        editIlanKriterler = findViewById(R.id.editIlanKriterler);
        btnIlanYayinla = findViewById(R.id.btnIlanYayinla);

        btnIlanYayinla.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                String baslik = editIlanBaslik.getText().toString().trim();
                String aciklama = editIlanAciklama.getText().toString().trim();
                String kriterler = editIlanKriterler.getText().toString().trim();

                if (baslik.isEmpty() || aciklama.isEmpty() || kriterler.isEmpty()) {
                    Toast.makeText(IlanVerActivity.this, "Lütfen tüm alanları doldurun!", Toast.LENGTH_SHORT).show();
                    return;
                }

                SharedPreferences prefs = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
                int isverenId = prefs.getInt("aktifId", -1);

                IlanVerIstek istek = new IlanVerIstek(baslik, aciklama, kriterler, isverenId);
                ApiService apiService = ApiClient.getClient().create(ApiService.class);

                Call<BasitCevap> call = apiService.ilanVer(istek);
                call.enqueue(new Callback<BasitCevap>() {
                    @Override
                    public void onResponse(Call<BasitCevap> call, Response<BasitCevap> response) {
                        if (response.isSuccessful() && response.body() != null) {
                            Toast.makeText(IlanVerActivity.this, "İlan başarıyla yayınlandı!", Toast.LENGTH_SHORT).show();
                            finish();
                        } else {
                            Toast.makeText(IlanVerActivity.this, "Bir hata oluştu.", Toast.LENGTH_SHORT).show();
                        }
                    }

                    @Override
                    public void onFailure(Call<BasitCevap> call, Throwable t) {
                        Toast.makeText(IlanVerActivity.this, "Bağlantı hatası: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    }
                });
            }
        });
    }
}