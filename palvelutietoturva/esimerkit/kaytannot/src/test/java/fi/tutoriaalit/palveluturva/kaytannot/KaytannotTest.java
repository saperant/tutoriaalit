package fi.tutoriaalit.palveluturva.kaytannot;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class KaytannotTest {

    static final String LASKUTUS = "spiffe://kauppa.example/laskutus";

    static Kaytanto lue(String nimi) throws IOException {
        try (var in = KaytannotTest.class.getResourceAsStream(
                "/kaytannot/" + nimi + ".json")) {
            return Kaytanto.lue(nimi, in);
        }
    }

    static Moottori.Pyynto pyynto(String toiminto, String resurssi) {
        return new Moottori.Pyynto(LASKUTUS, toiminto, resurssi,
                Map.of("lahde", LASKUTUS, "ymparisto", "tuotanto"));
    }

    @Test
    void laajaKaytantoSalliiKaiken() throws IOException {
        // @alku laaja
        var laaja = new Moottori(List.of(lue("laskutus-laaja")));
        // Laskutuksen murtanut hyökkääjä voi poistaa tilauksia ja lukea
        // salaisuuksia, vaikkei laskutus koskaan tee kumpaakaan.
        assertThat(laaja.arvioi(pyynto("tilaukset:Poista",
                "krn:kauppa:tilaukset/1001")).sallittu()).isTrue();
        assertThat(laaja.arvioi(pyynto("salaisuudet:Lue",
                "krn:kauppa:salaisuudet/maksut")).sallittu()).isTrue();
        // @loppu laaja
    }

    @Test
    void vahimmatOikeudetJaNimenomainenEsto() throws IOException {
        // @alku rajattu
        var moottori = new Moottori(List.of(lue("organisaatio"),
                lue("laskutus")));
        assertThat(moottori.arvioi(pyynto("tilaukset:Lue",
                "krn:kauppa:tilaukset/1001")))
                .isEqualTo(new Moottori.Paatos(true,
                        "sallittu: laskutus/LueTilaukset"));
        assertThat(moottori.arvioi(pyynto("salaisuudet:Lue",
                "krn:kauppa:salaisuudet/maksut")))
                .isEqualTo(new Moottori.Paatos(false,
                        "oletuksena estetty"));
        // Organisaation esto voittaa, vaikka jokin käytäntö sallisi.
        var laajaJaEsto = new Moottori(List.of(lue("organisaatio"),
                lue("laskutus-laaja")));
        assertThat(laajaJaEsto.arvioi(pyynto("tilaukset:Poista",
                "krn:kauppa:tilaukset/1001")))
                .isEqualTo(new Moottori.Paatos(false,
                        "esto: organisaatio/EiPoistojaTuotannossa"));
        // @loppu rajattu
    }

    @Test
    void ehdotJaResurssimuuttuja() throws IOException {
        // @alku nollaluottamus
        var moottori = new Moottori(List.of(lue("asiakas")));
        Map<String, String> konteksti = Map.of("asiakas", "a-7",
                "laite.hallittu", "kylla", "mfa", "kylla");
        assertThat(moottori.arvioi(new Moottori.Pyynto("a-7",
                "tiedostot:Lue", "krn:kauppa:tiedostot/a-7/kuitti.pdf",
                konteksti)).sallittu()).isTrue();
        // Toisen asiakkaan tiedosto: ${asiakas} rajaa resurssin.
        assertThat(moottori.arvioi(new Moottori.Pyynto("a-7",
                "tiedostot:Lue", "krn:kauppa:tiedostot/a-8/kuitti.pdf",
                konteksti)).sallittu()).isFalse();
        // Sama käyttäjä hallitsemattomalta laitteelta: estetty. Päätös
        // tehdään jokaiselle pyynnölle, ei kerran kirjautuessa.
        var kotikone = new java.util.HashMap<>(konteksti);
        kotikone.put("laite.hallittu", "ei");
        assertThat(moottori.arvioi(new Moottori.Pyynto("a-7",
                "tiedostot:Lue", "krn:kauppa:tiedostot/a-7/kuitti.pdf",
                kotikone)).sallittu()).isFalse();
        // @loppu nollaluottamus
    }

    @Test
    void kayttamattomatOikeudetLoytyvatLokista() throws IOException {
        // @alku analyysiTesti
        List<Analyysi.Kaytto> loki = List.of(
                new Analyysi.Kaytto(LASKUTUS, "tilaukset:Lue",
                        "krn:kauppa:tilaukset/1001"),
                new Analyysi.Kaytto(LASKUTUS, "tilaukset:Lue",
                        "krn:kauppa:tilaukset/1002"),
                new Analyysi.Kaytto(LASKUTUS, "laskut:Kirjoita",
                        "krn:kauppa:laskut/77"));
        assertThat(Analyysi.kayttamattomat(lue("laskutus"), loki))
                .containsExactly("LueAsiakkaat");
        assertThat(Analyysi.ehdotus(loki)).hasToString(
                "{krn:kauppa:laskut/*=[laskut:Kirjoita],"
                + " krn:kauppa:tilaukset/*=[tilaukset:Lue]}");
        // @loppu analyysiTesti
    }

    @Test
    void kaytannotTarkastetaanCiSsa() throws IOException {
        // @alku tarkastusTesti
        assertThat(Tarkastus.loydokset(lue("laskutus-laaja")))
                .containsExactly(
                        "laskutus-laaja/Kaikki: kaikki toiminnot (*)",
                        "laskutus-laaja/Kaikki: kaikki resurssit (*)",
                        "laskutus-laaja/Kaikki: kirjoitus ilman ehtoja");
        assertThat(Tarkastus.loydokset(lue("laskutus"))).isEmpty();
        // @loppu tarkastusTesti
    }
}
