package com.example.jobmatchingmobile;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class GelenBasvurularActivity extends AppCompatActivity {

    private RecyclerView recyclerViewGelenBasvurular;
    private TextView textGelenBasvurularMesaj;
    private IsverenIlaniAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_gelen_basvurular);

        recyclerViewGelenBasvurular = findViewById(R.id.recyclerViewGelenBasvurular);
        textGelenBasvurularMesaj = findViewById(R.id.textGelenBasvurularMesaj);
        recyclerViewGelenBasvurular.setLayoutManager(new LinearLayoutManager(this));
    }

    @Override
    protected void onResume() {
        super.onResume();
        basvurulariYukle();
    }

    private void basvurulariYukle() {
        SharedPreferences prefs = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
        int isverenId = prefs.getInt("aktifId", -1);

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        Call<List<IsverenIlani>> call = apiService.isverenIlanlariGetir(isverenId);

        call.enqueue(new Callback<List<IsverenIlani>>() {
            @Override
            public void onResponse(Call<List<IsverenIlani>> call, Response<List<IsverenIlani>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<IsverenIlani> ilanlar = response.body();

                    if (ilanlar.isEmpty()) {
                        textGelenBasvurularMesaj.setText("Henüz bir ilan yayınlamadınız.");
                        textGelenBasvurularMesaj.setVisibility(View.VISIBLE);
                    } else {
                        textGelenBasvurularMesaj.setVisibility(View.GONE);
                        adapter = new IsverenIlaniAdapter(GelenBasvurularActivity.this, ilanlar, isverenId);
                        recyclerViewGelenBasvurular.setAdapter(adapter);
                    }
                } else {
                    textGelenBasvurularMesaj.setText("Veriler alınırken hata oluştu.");
                    textGelenBasvurularMesaj.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(Call<List<IsverenIlani>> call, Throwable t) {
                textGelenBasvurularMesaj.setText("Bağlantı hatası: " + t.getMessage());
                textGelenBasvurularMesaj.setVisibility(View.VISIBLE);
            }
        });
    }
}