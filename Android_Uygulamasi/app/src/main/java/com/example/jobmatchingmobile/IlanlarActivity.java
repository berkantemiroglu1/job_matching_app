package com.example.jobmatchingmobile;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import java.util.ArrayList;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class IlanlarActivity extends AppCompatActivity {

    private RecyclerView recyclerViewIlanlar;
    private TextView textIlanlarMesaj;
    private Button btnCikisYap, btnMenuIlanlar, btnMenuEkstra1, btnMenuEkstra2;
    private EditText editArama;
    private CheckBox checkBasvurulanlariGizle;
    private IlanAdapter adapter;
    private List<Ilan> tumIlanlarListesi = new ArrayList<>();
    private String aktifRol;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_ilanlar);

        recyclerViewIlanlar = findViewById(R.id.recyclerViewIlanlar);
        textIlanlarMesaj = findViewById(R.id.textIlanlarMesaj);
        btnCikisYap = findViewById(R.id.btnCikisYap);
        btnMenuIlanlar = findViewById(R.id.btnMenuIlanlar);
        btnMenuEkstra1 = findViewById(R.id.btnMenuEkstra1);
        btnMenuEkstra2 = findViewById(R.id.btnMenuEkstra2);
        editArama = findViewById(R.id.editArama);
        checkBasvurulanlariGizle = findViewById(R.id.checkBasvurulanlariGizle);

        recyclerViewIlanlar.setLayoutManager(new LinearLayoutManager(this));

        SharedPreferences prefs = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
        aktifRol = prefs.getString("aktifRol", "aday");

        if (aktifRol.equals("isveren")) {
            btnMenuEkstra1.setVisibility(View.VISIBLE);
            btnMenuEkstra2.setVisibility(View.VISIBLE);
            checkBasvurulanlariGizle.setVisibility(View.GONE);
        } else {
            btnMenuEkstra1.setVisibility(View.GONE);
            btnMenuEkstra2.setVisibility(View.GONE);
            checkBasvurulanlariGizle.setVisibility(View.VISIBLE);
        }

        btnCikisYap.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                SharedPreferences.Editor editor = prefs.edit();
                editor.clear();
                editor.apply();

                Intent intent = new Intent(IlanlarActivity.this, MainActivity.class);
                startActivity(intent);
                finish();
            }
        });

        btnMenuEkstra1.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (aktifRol.equals("isveren")) {
                    Intent intent = new Intent(IlanlarActivity.this, GelenBasvurularActivity.class);
                    startActivity(intent);
                }
            }
        });

        btnMenuEkstra2.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(IlanlarActivity.this, IlanVerActivity.class);
                startActivity(intent);
            }
        });

        editArama.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                listeyiFiltrele();
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        checkBasvurulanlariGizle.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                listeyiFiltrele();
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        SharedPreferences prefs = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
        ilanlariYukle(prefs);
    }

    private void ilanlariYukle(SharedPreferences prefs) {
        int aktifKullaniciId = prefs.getInt("aktifId", -1);

        ApiService apiService = ApiClient.getClient().create(ApiService.class);
        Call<List<Ilan>> call = apiService.ilanlariGetir(aktifKullaniciId);

        call.enqueue(new Callback<List<Ilan>>() {
            @Override
            public void onResponse(Call<List<Ilan>> call, Response<List<Ilan>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    tumIlanlarListesi = response.body();

                    if (tumIlanlarListesi.isEmpty()) {
                        textIlanlarMesaj.setText("Şu an sistemde hiç ilan yok.");
                        textIlanlarMesaj.setVisibility(View.VISIBLE);
                    } else {
                        textIlanlarMesaj.setVisibility(View.GONE);
                        adapter = new IlanAdapter(tumIlanlarListesi, aktifRol);
                        recyclerViewIlanlar.setAdapter(adapter);
                        listeyiFiltrele();
                    }
                } else {
                    textIlanlarMesaj.setText("İlanlar alınırken bir hata oluştu.");
                    textIlanlarMesaj.setVisibility(View.VISIBLE);
                }
            }

            @Override
            public void onFailure(Call<List<Ilan>> call, Throwable t) {
                textIlanlarMesaj.setText("Bağlantı hatası: " + t.getMessage());
                textIlanlarMesaj.setVisibility(View.VISIBLE);
            }
        });
    }

    private void listeyiFiltrele() {
        if (adapter == null) return;

        String aramaMetni = editArama.getText().toString().toLowerCase().trim();
        boolean gizleAktif = checkBasvurulanlariGizle.isChecked();

        List<Ilan> filtrelenmisListe = new ArrayList<>();

        for (Ilan ilan : tumIlanlarListesi) {
            boolean gosterilecek = true;

            if (gizleAktif && ilan.basvuruldu) {
                gosterilecek = false;
            }

            if (gosterilecek && !aramaMetni.isEmpty()) {
                String baslik = ilan.baslik != null ? ilan.baslik.toLowerCase() : "";
                String aciklama = ilan.aciklama != null ? ilan.aciklama.toLowerCase() : "";
                String kriterler = ilan.kriterler != null ? ilan.kriterler.toLowerCase() : "";

                if (!baslik.contains(aramaMetni) && !aciklama.contains(aramaMetni) && !kriterler.contains(aramaMetni)) {
                    gosterilecek = false;
                }
            }

            if (gosterilecek) {
                filtrelenmisListe.add(ilan);
            }
        }

        adapter.listeyiGuncelle(filtrelenmisListe);
    }
}