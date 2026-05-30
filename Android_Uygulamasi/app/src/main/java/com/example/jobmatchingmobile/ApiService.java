package com.example.jobmatchingmobile;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.Multipart;
import retrofit2.http.POST;
import retrofit2.http.GET;
import java.util.List;

import retrofit2.http.Part;
import retrofit2.http.Query;
public interface ApiService {
    @POST("/giris")
    Call<GirisCevap> girisYap(@Body GirisIstek istek);
    @POST("/kayit")
    Call<GirisCevap> kayitOl(@Body KayitIstek istek);
    @GET("/ilanlar")
    Call<List<Ilan>> ilanlariGetir();
    @GET("/ilanlar")
    Call<List<Ilan>> ilanlariGetir(@Query("kullanici_id") int kullaniciId);
    @POST("/ilan-ver")
    Call<BasitCevap> ilanVer(@Body IlanVerIstek istek);

    @POST("/ilan-sil")
    Call<BasitCevap> ilanSil(@Body IlanSilIstek istek);

    @POST("/basvuru-sil")
    Call<BasitCevap> basvuruSil(@Body BasvuruSilIstek istek);

    @Multipart
    @POST("/basvuru-yap")
    Call<BasitCevap> basvuruYap(
            @Part okhttp3.MultipartBody.Part cvDosyasi,
            @Part("ilan_id") okhttp3.RequestBody ilanId,
            @Part("aday_id") okhttp3.RequestBody adayId,
            @Part("ilan_metni") okhttp3.RequestBody ilanMetni
    );
    @retrofit2.http.GET("/isveren-ilanlari/{isveren_id}")
    retrofit2.Call<java.util.List<IsverenIlani>> isverenIlanlariGetir(@retrofit2.http.Path("isveren_id") int isverenId);
    @retrofit2.http.POST("/sifre-yenile")
    retrofit2.Call<BasitCevap> sifreYenile(@retrofit2.http.Body SifreYenileIstek istek);
}
