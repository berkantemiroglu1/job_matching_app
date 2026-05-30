package com.example.jobmatchingmobile;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;

public class IlanAdapter extends RecyclerView.Adapter<IlanAdapter.IlanViewHolder> {

    private List<Ilan> ilanListesi;
    private String aktifRol;

    public IlanAdapter(List<Ilan> ilanListesi, String aktifRol) {
        this.ilanListesi = ilanListesi;
        this.aktifRol = aktifRol;
    }

    @NonNull
    @Override
    public IlanViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_ilan, parent, false);
        return new IlanViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull IlanViewHolder holder, int position) {
        Ilan ilan = ilanListesi.get(position);

        holder.textBaslik.setText(ilan.baslik);
        holder.textAciklama.setText(ilan.aciklama);
        holder.textKriterler.setText("Kriterler: " + ilan.kriterler);

        if (aktifRol != null && aktifRol.equals("isveren")) {
            holder.btnBasvur.setVisibility(View.GONE);
            holder.textPuan.setVisibility(View.GONE);
            holder.textAiAciklama.setVisibility(View.GONE);
        } else {
            if (ilan.basvuruldu) {
                holder.btnBasvur.setVisibility(View.GONE);

                holder.textPuan.setVisibility(View.VISIBLE);
                holder.textPuan.setText("✓ Bu ilana başvurdunuz. AI Puanınız: " + ilan.basvuru_puani);

                if (ilan.basvuru_puani >= 80) {
                    holder.textPuan.setTextColor(android.graphics.Color.parseColor("#22C55E"));
                } else if (ilan.basvuru_puani >= 50) {
                    holder.textPuan.setTextColor(android.graphics.Color.parseColor("#EAB308"));
                } else {
                    holder.textPuan.setTextColor(android.graphics.Color.parseColor("#EF4444"));
                }

                if (ilan.ai_aciklama != null && !ilan.ai_aciklama.isEmpty()) {
                    holder.textAiAciklama.setVisibility(View.VISIBLE);
                    holder.textAiAciklama.setText(ilan.ai_aciklama);
                } else {
                    holder.textAiAciklama.setVisibility(View.GONE);
                }

            } else {
                holder.btnBasvur.setVisibility(View.VISIBLE);
                holder.btnBasvur.setText("Başvuru Yap / İncele");
                holder.btnBasvur.setBackgroundColor(android.graphics.Color.parseColor("#FF4D24"));
                holder.btnBasvur.setEnabled(true);

                holder.textPuan.setVisibility(View.GONE);
                holder.textAiAciklama.setVisibility(View.GONE);
            }
        }

        holder.btnBasvur.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                android.content.Intent intent = new android.content.Intent(v.getContext(), BasvuruActivity.class);
                intent.putExtra("ilan_id", ilan.id);
                intent.putExtra("ilan_baslik", ilan.baslik);
                intent.putExtra("ilan_metni", ilan.aciklama + " " + ilan.kriterler);
                v.getContext().startActivity(intent);
            }
        });
    }

    @Override
    public int getItemCount() {
        return ilanListesi.size();
    }

    public static class IlanViewHolder extends RecyclerView.ViewHolder {
        TextView textBaslik, textAciklama, textKriterler, textPuan, textAiAciklama;
        Button btnBasvur;

        public IlanViewHolder(@NonNull View itemView) {
            super(itemView);
            textBaslik = itemView.findViewById(R.id.textIlanBaslik);
            textAciklama = itemView.findViewById(R.id.textIlanAciklama);
            textKriterler = itemView.findViewById(R.id.textIlanKriterler);
            textPuan = itemView.findViewById(R.id.textIlanPuan);
            textAiAciklama = itemView.findViewById(R.id.textAiAciklama);
            btnBasvur = itemView.findViewById(R.id.btnBasvur);
        }
    }
    public void listeyiGuncelle(List<Ilan> yeniListe) {
        this.ilanListesi = yeniListe;
        notifyDataSetChanged();
    }
}