package fi.tutoriaalit.palveluturva.kaytannot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/** Näytösajot: käytäntömoottorin päätökset perusteluineen tauluna. */
class NaytosTest {

    static final String KRN = "krn:kauppa:";

    static String paatos(Moottori.Paatos p) {
        return p.peruste();
    }

    @Test
    void pyyntokohtainenPaatos() throws Exception {
        var moottori = new Moottori(List.of(KaytannotTest.lue("asiakas")));
        Map<String, String> tyokone = Map.of("asiakas", "a-7",
                "laite.hallittu", "kylla", "mfa", "kylla");
        var kotikone = new HashMap<>(tyokone);
        kotikone.put("laite.hallittu", "ei");

        var rivit = new ArrayList<List<String>>();
        rivit.add(List.of("resurssi", "laite", "päätös"));
        record Koe(String resurssi, String laite, Map<String, String> k) {}
        for (Koe k : List.of(
                new Koe("tiedostot/a-7/kuitti.pdf", "hallittu", tyokone),
                new Koe("tiedostot/a-8/kuitti.pdf", "hallittu", tyokone),
                new Koe("tiedostot/a-7/kuitti.pdf", "oma kotikone",
                        kotikone))) {
            rivit.add(List.of(k.resurssi(), k.laite(), paatos(
                    moottori.arvioi(new Moottori.Pyynto("a-7",
                            "tiedostot:Lue", KRN + k.resurssi(), k.k())))));
        }
        new Naytos("02-paatos").taulu(rivit).vertaa();
    }

    @Test
    void laajaJaRajattuKaytanto() throws Exception {
        var n = new Naytos("09-paatokset");
        record Koe(String toiminto, String resurssi) {}
        var kokeet = List.of(new Koe("tilaukset:Lue", "tilaukset/1001"),
                new Koe("tilaukset:Poista", "tilaukset/1001"),
                new Koe("salaisuudet:Lue", "salaisuudet/db"));
        for (List<String> nimet : List.of(List.of("laskutus-laaja"),
                List.of("organisaatio", "laskutus"),
                List.of("organisaatio", "laskutus-laaja"))) {
            var kaytannot = new ArrayList<Kaytanto>();
            for (String nimi : nimet) {
                kaytannot.add(KaytannotTest.lue(nimi));
            }
            var moottori = new Moottori(kaytannot);
            n.rivi("käytännöt: " + String.join(" + ", nimet));
            var rivit = new ArrayList<List<String>>();
            for (Koe k : kokeet) {
                rivit.add(List.of("  " + k.toiminto(), k.resurssi(),
                        paatos(moottori.arvioi(KaytannotTest.pyynto(
                                k.toiminto(), KRN + k.resurssi())))));
            }
            n.taulu(rivit);
        }
        n.vertaa();
    }
}
