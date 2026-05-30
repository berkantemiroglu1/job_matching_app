package com.example.jobmatchingmobile;

import android.content.Context;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class IsverenIlaniAdapter extends RecyclerView.Adapter<IsverenIlaniAdapter.IsverenViewHolder> {

    private List<IsverenIlani> ilanListesi;
    private Context context;
    private int isverenId;

    public IsverenIlaniAdapter(Context context, List<IsverenIlani> ilanListesi, int isverenId) {
        this.context = context;
        this.ilanListesi = ilanListesi;
        this.isverenId = isverenId;
    }

    @NonNull
    @Override
    public IsverenViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(context).inflate(R.layout.item_isveren_ilani, parent, false);
        return new IsverenViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull IsverenViewHolder holder, int position) {
        IsverenIlani ilan = ilanListesi.get(position);
        holder.textBaslik.setText(ilan.baslik);
        holder.textAciklama.setText(ilan.aciklama);

        holder.layoutBasvurularContainer.removeAllViews();

        if (ilan.basvurular == null || ilan.basvurular.isEmpty()) {
            TextView bosMesaj = new TextView(context);
            bosMesaj.setText("Bu ilana henüz başvuru yapılmadı.");
            bosMesaj.setPadding(0, 16, 0, 0);
            holder.layoutBasvurularContainer.addView(bosMesaj);
        } else {
            for (Basvuru basvuru : ilan.basvurular) {
                View basvuruView = LayoutInflater.from(context).inflate(R.layout.item_basvuru, holder.layoutBasvurularContainer, false);

                TextView textPuan = basvuruView.findViewById(R.id.textAdayPuan);
                TextView textAiGeribildirim = basvuruView.findViewById(R.id.textAiGeribildirim);
                Button btnCvIndir = basvuruView.findViewById(R.id.btnCvIndir);
                Button btnBasvuruSil = basvuruView.findViewById(R.id.btnBasvuruSil);

                textPuan.setText("AI Puanı: " + basvuru.puan + " | Tarih: " + basvuru.tarih);
                textAiGeribildirim.setText(basvuru.geribildirim);

                if (basvuru.puan >= 80) {
                    textPuan.setTextColor(Color.parseColor("#22C55E"));
                } else if (basvuru.puan >= 50) {
                    textPuan.setTextColor(Color.parseColor("#EAB308"));
                } else {
                    textPuan.setTextColor(Color.parseColor("#EF4444"));
                }

                btnCvIndir.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        String url = "http://10.0.2.2:5000/uploads/" + basvuru.cv_dosya_yolu;
                        Intent browserIntent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        context.startActivity(browserIntent);
                    }
                });

                btnBasvuruSil.setOnClickListener(new View.OnClickListener() {
                    @Override
                    public void onClick(View v) {
                        ApiService apiService = ApiClient.getClient().create(ApiService.class);
                        BasvuruSilIstek istek = new BasvuruSilIstek(basvuru.id, isverenId);
                        apiService.basvuruSil(istek).enqueue(new Callback<BasitCevap>() {
                            @Override
                            public void onResponse(Call<BasitCevap> call, Response<BasitCevap> response) {
                                if (response.isSuccessful()) {
                                    Toast.makeText(context, "Başvuru silindi.", Toast.LENGTH_SHORT).show();
                                    ilan.basvurular.remove(basvuru);
                                    notifyDataSetChanged();
                                }
                            }

                            @Override
                            public void onFailure(Call<BasitCevap> call, Throwable t) {
                            }
                        });
                    }
                });

                holder.layoutBasvurularContainer.addView(basvuruView);
            }
        }

        holder.btnIlanSil.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ApiService apiService = ApiClient.getClient().create(ApiService.class);
                IlanSilIstek istek = new IlanSilIstek(ilan.id, isverenId);
                apiService.ilanSil(istek).enqueue(new Callback<BasitCevap>() {
                    @Override
                    public void onResponse(Call<BasitCevap> call, Response<BasitCevap> response) {
                        if (response.isSuccessful()) {
                            Toast.makeText(context, "İlan silindi.", Toast.LENGTH_SHORT).show();
                            ilanListesi.remove(position);
                            notifyItemRemoved(position);
                            notifyItemRangeChanged(position, ilanListesi.size());
                        }
                    }

                    @Override
                    public void onFailure(Call<BasitCevap> call, Throwable t) {
                    }
                });
            }
        });
    }

    @Override
    public int getItemCount() {
        return ilanListesi.size();
    }

    public static class IsverenViewHolder extends RecyclerView.ViewHolder {
        TextView textBaslik, textAciklama;
        Button btnIlanSil;
        LinearLayout layoutBasvurularContainer;

        public IsverenViewHolder(@NonNull View itemView) {
            super(itemView);
            textBaslik = itemView.findViewById(R.id.textIlanBaslik);
            textAciklama = itemView.findViewById(R.id.textIlanAciklama);
            btnIlanSil = itemView.findViewById(R.id.btnIlanSil);
            layoutBasvurularContainer = itemView.findViewById(R.id.layoutBasvurularContainer);
        }
    }
}