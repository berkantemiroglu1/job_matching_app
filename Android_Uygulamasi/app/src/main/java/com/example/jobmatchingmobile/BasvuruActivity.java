package com.example.jobmatchingmobile;

import android.content.Intent;
import android.content.SharedPreferences;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.RequestBody;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class BasvuruActivity extends AppCompatActivity {

    private TextView textSecilenDosya, textBasvuruIlanBaslik;
    private Button btnPdfSec, btnBasvuruyuTamamla;
    private Uri secilenDosyaUri = null;
    private int ilanId;
    private String ilanMetni;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_basvuru);

        textSecilenDosya = findViewById(R.id.textSecilenDosya);
        textBasvuruIlanBaslik = findViewById(R.id.textBasvuruIlanBaslik);
        btnPdfSec = findViewById(R.id.btnPdfSec);
        btnBasvuruyuTamamla = findViewById(R.id.btnBasvuruyuTamamla);

        ilanId = getIntent().getIntExtra("ilan_id", -1);
        String baslik = getIntent().getStringExtra("ilan_baslik");
        ilanMetni = getIntent().getStringExtra("ilan_metni");

        textBasvuruIlanBaslik.setText(baslik + " İçin Başvuru");

        btnPdfSec.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.setType("application/pdf");
                startActivityForResult(intent, 101);
            }
        });

        btnBasvuruyuTamamla.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (secilenDosyaUri == null) {
                    Toast.makeText(BasvuruActivity.this, "Lütfen önce bir PDF dosyası seçin!", Toast.LENGTH_SHORT).show();
                    return;
                }
                basvuruyuGonder();
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == 101 && resultCode == RESULT_OK && data != null) {
            secilenDosyaUri = data.getData();
            String dosyaAdi = dosyaAdiniGetir(secilenDosyaUri);
            textSecilenDosya.setText("Seçilen Dosya: " + dosyaAdi);
        }
    }

    private void basvuruyuGonder() {
        try {
            SharedPreferences prefs = getSharedPreferences("JobMatchPref", MODE_PRIVATE);
            int adayId = prefs.getInt("aktifId", -1);

            InputStream inputStream = getContentResolver().openInputStream(secilenDosyaUri);
            File tempFile = new File(getCacheDir(), "gecici_cv.pdf");
            FileOutputStream outputStream = new FileOutputStream(tempFile);

            byte[] buffer = new byte[1024];
            int length;
            while ((length = inputStream.read(buffer)) > 0) {
                outputStream.write(buffer, 0, length);
            }
            outputStream.close();
            inputStream.close();

            RequestBody reqFile = RequestBody.create(MediaType.parse("application/pdf"), tempFile);
            MultipartBody.Part body = MultipartBody.Part.createFormData("cv_dosyasi", tempFile.getName(), reqFile);

            RequestBody ilanIdGövde = RequestBody.create(MediaType.parse("text/plain"), String.valueOf(ilanId));
            RequestBody adayIdGövde = RequestBody.create(MediaType.parse("text/plain"), String.valueOf(adayId));
            RequestBody ilanMetniGövde = RequestBody.create(MediaType.parse("text/plain"), ilanMetni);

            ApiService apiService = ApiClient.getClient().create(ApiService.class);
            Call<BasitCevap> call = apiService.basvuruYap(body, ilanIdGövde, adayIdGövde, ilanMetniGövde);

            Toast.makeText(this, "Yapay zeka CV'nizi inceliyor, lütfen bekleyin...", Toast.LENGTH_LONG).show();
            btnBasvuruyuTamamla.setEnabled(false);

            call.enqueue(new Callback<BasitCevap>() {
                @Override
                public void onResponse(Call<BasitCevap> call, Response<BasitCevap> response) {
                    if (response.isSuccessful() && response.body() != null) {
                        Toast.makeText(BasvuruActivity.this, "Başvuru başarılı!", Toast.LENGTH_SHORT).show();
                        finish();
                    } else {
                        Toast.makeText(BasvuruActivity.this, "Hata oluştu.", Toast.LENGTH_SHORT).show();
                        btnBasvuruyuTamamla.setEnabled(true);
                    }
                }

                @Override
                public void onFailure(Call<BasitCevap> call, Throwable t) {
                    Toast.makeText(BasvuruActivity.this, "Bağlantı hatası: " + t.getMessage(), Toast.LENGTH_SHORT).show();
                    btnBasvuruyuTamamla.setEnabled(true);
                }
            });

        } catch (Exception e) {
            Toast.makeText(this, "Dosya okunurken hata oluştu", Toast.LENGTH_SHORT).show();
        }
    }

    private String dosyaAdiniGetir(Uri uri) {
        String sonuc = null;
        if (uri.getScheme().equals("content")) {
            try (Cursor cursor = getContentResolver().query(uri, null, null, null, null)) {
                if (cursor != null && cursor.moveToFirst()) {
                    int index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                    if (index != -1) {
                        sonuc = cursor.getString(index);
                    }
                }
            }
        }
        if (sonuc == null) {
            sonuc = uri.getPath();
            int kesim = sonuc.lastIndexOf('/');
            if (kesim != -1) {
                sonuc = sonuc.substring(kesim + 1);
            }
        }
        return sonuc;
    }
}