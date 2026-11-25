package fi.tutoriaalit.palveluturva.havainnointi;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

/** Näytösajot: lokin tarkistus ja poikkeaman aikajana tulosteena. */
class NaytosTest {

    static final String ALUE = HavainnointiTest.ALUE;

    @Test
    void peukaloituLoki() throws Exception {
        var allekirjoittaja = HavainnointiTest.allekirjoittaja();
        var loki = new Auditointiloki(allekirjoittaja, 2);
        for (int i = 0; i < 4; i++) {
            loki.kirjaa(HavainnointiTest.t(i, "k-" + i, "laskutus",
                    ALUE + "tilaus", "laskut:Kirjoita",
                    "krn:kauppa:laskut/" + i));
        }
        var avain = allekirjoittaja.julkinen();
        var pisteet = loki.tarkistuspisteet();
        List<String> poistettu = new ArrayList<>(loki.rivit());
        poistettu.remove(1);
        new Naytos("12-loki").taulu(List.of(
                List.of("loki", "tarkistuksen tulos"),
                List.of("alkuperäinen, 4 riviä", Auditointiloki.tarkista(
                        loki.rivit(), pisteet, avain)),
                List.of("rivi 2 poistettu, ketju laskettu uudelleen",
                        Auditointiloki.tarkista(poistettu, pisteet, avain)),
                List.of("viimeinen rivi katkaistu pois",
                        Auditointiloki.tarkista(loki.rivit().subList(0, 3),
                                pisteet, avain)))).vertaa();
    }

    @Test
    void poikkeamaJaAikajana() throws Exception {
        List<Tapahtuma> perustaso = List.of(
                HavainnointiTest.t(0, "a", "tilaus", ALUE + "suositukset",
                        "tilaukset:Lue", "krn:kauppa:tilaukset/1"),
                HavainnointiTest.t(1, "b", "laskutus", ALUE + "tilaus",
                        "laskut:Kirjoita", "krn:kauppa:laskut/1"));
        List<Tapahtuma> tanaan = List.of(
                HavainnointiTest.t(100, "x-42", "tilaus",
                        ALUE + "suositukset", "tilaukset:Lue",
                        "krn:kauppa:tilaukset/7"),
                HavainnointiTest.t(101, "x-42", "salaisuudet",
                        ALUE + "suositukset", "salaisuudet:Lue",
                        "krn:kauppa:salaisuudet/db"),
                HavainnointiTest.t(102, "x-42", "asiakkaat",
                        ALUE + "suositukset", "asiakkaat:Vie",
                        "krn:kauppa:asiakkaat/*"));
        var n = new Naytos("13-poikkeama");
        n.rivi("poikkeavat toiminnot (ei perustasossa):");
        for (Tapahtuma t : Poikkeama.poikkeavat(perustaso, tanaan)) {
            n.rivi("  " + t.toimija().substring(ALUE.length()) + ": "
                    + t.toiminto());
        }
        n.rivi("");
        n.rivi("aikajana korrelaatiotunnisteella x-42:");
        // Lokit tulevat kolmesta palvelusta eri järjestyksessä.
        for (String rivi : Poikkeama.aikajana("x-42", List.of(
                tanaan.subList(1, 3), tanaan.subList(0, 1)))) {
            n.rivi("  " + rivi.replace("krn:kauppa:", ""));
        }
        n.vertaa();
    }
}
