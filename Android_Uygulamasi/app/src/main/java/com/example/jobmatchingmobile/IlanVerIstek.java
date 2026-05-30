package com.example.jobmatchingmobile;

public class IlanVerIstek {
    public String baslik;
    public String aciklama;
    public String kriterler;
    public int isveren_id;

    public IlanVerIstek(String baslik, String aciklama, String kriterler, int isveren_id) {
        this.baslik = baslik;
        this.aciklama = aciklama;
        this.kriterler = kriterler;
        this.isveren_id = isveren_id;
    }
}