package fi.tutoriaalit.palveluturva.havainnointi;

import static org.assertj.core.api.Assertions.assertThat;

import java.security.KeyPairGenerator;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class HavainnointiTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final Instant T0 = Instant.parse("2026-11-24T10:00:00Z");

    static Tapahtuma t(int sekunti, String korrelaatio, String palvelu,
                       String toimija, String toiminto, String resurssi) {
        return new Tapahtuma(T0.plusSeconds(sekunti), korrelaatio,
                palvelu, toimija, toiminto, resurssi, "sallittu",
                Map.of());
    }

    static Auditointiloki.Allekirjoittaja allekirjoittaja()
            throws Exception {
        return new Auditointiloki.Allekirjoittaja(
                KeyPairGenerator.getInstance("Ed25519").generateKeyPair());
    }

    @Test
    void salaisuudetJaKortitPeitetaan() {
        // @alku peitaTesti
        var peitetty = Peittaja.peita(Map.of(
                "Authorization", "Bearer eyJhbGciOi.eyJzdWIi.c2ln",
                "viesti", "kutsu: Bearer eyJhbGciOi.abc virhe 401",
                "kortti", "4111111111111111",
                "db_salasana", "hunter2"));
        assertThat(peitetty).hasToString("{Authorization=[peitetty],"
                + " db_salasana=[peitetty], kortti=****1111,"
                + " viesti=kutsu: Bearer [peitetty] virhe 401}");
        // @loppu peitaTesti
    }

    @Test
    void allekirjoitetutTarkistuspisteetPaljastavatMuutokset()
            throws Exception {
        // @alku lokiTesti
        var allekirjoittaja = allekirjoittaja();
        var loki = new Auditointiloki(allekirjoittaja, 2);
        for (int i = 0; i < 4; i++) {
            loki.kirjaa(t(i, "k-" + i, "laskutus", ALUE + "tilaus",
                    "laskut:Kirjoita", "krn:kauppa:laskut/" + i));
        }
        var avain = allekirjoittaja.julkinen();
        var pisteet = loki.tarkistuspisteet();
        assertThat(Auditointiloki.tarkista(loki.rivit(), pisteet, avain))
                .isEqualTo("ehjä");

        // Hyökkääjä poistaa rivin ja laskee tiivisteketjun uudelleen,
        // mutta ei voi allekirjoittaa uusia tarkistuspisteitä.
        List<String> peukaloitu = new ArrayList<>(loki.rivit());
        peukaloitu.remove(1);
        assertThat(Auditointiloki.tarkista(peukaloitu, pisteet, avain))
                .isEqualTo("rivit 1–2 on muutettu");
        assertThat(Auditointiloki.tarkista(loki.rivit().subList(0, 3),
                pisteet, avain))
                .isEqualTo("rivejä puuttuu: tarkistuspiste 4");
        // @loppu lokiTesti
    }

    @Test
    void poikkeavaToimintaJaAikajana() {
        // @alku poikkeamaTesti
        List<Tapahtuma> perustaso = List.of(
                t(0, "a", "tilaus", ALUE + "suositukset", "tilaukset:Lue",
                        "krn:kauppa:tilaukset/1"),
                t(1, "b", "laskutus", ALUE + "tilaus", "laskut:Kirjoita",
                        "krn:kauppa:laskut/1"));
        List<Tapahtuma> tanaan = List.of(
                t(100, "x-42", "tilaus", ALUE + "suositukset",
                        "tilaukset:Lue", "krn:kauppa:tilaukset/7"),
                t(101, "x-42", "salaisuudet", ALUE + "suositukset",
                        "salaisuudet:Lue", "krn:kauppa:salaisuudet/db"),
                t(102, "x-42", "asiakkaat", ALUE + "suositukset",
                        "asiakkaat:Vie", "krn:kauppa:asiakkaat/*"));
        assertThat(Poikkeama.poikkeavat(perustaso, tanaan))
                .extracting(Tapahtuma::toiminto)
                .containsExactly("salaisuudet:Lue", "asiakkaat:Vie");
        assertThat(Poikkeama.aikajana("x-42", List.of(
                tanaan.subList(1, 3), tanaan.subList(0, 1))))
                .containsExactly(
                "2026-11-24T10:01:40Z tilaus: tilaukset:Lue"
                + " krn:kauppa:tilaukset/7 -> sallittu",
                "2026-11-24T10:01:41Z salaisuudet: salaisuudet:Lue"
                + " krn:kauppa:salaisuudet/db -> sallittu",
                "2026-11-24T10:01:42Z asiakkaat: asiakkaat:Vie"
                + " krn:kauppa:asiakkaat/* -> sallittu");
        // @loppu poikkeamaTesti

        // @alku eristysTesti
        var kumotut = new Poikkeama.Kumoamislista();
        kumotut.kumoa(ALUE + "suositukset", T0.plusSeconds(130));
        assertThat(kumotut.kumottu(ALUE + "suositukset")).isTrue();
        assertThat(kumotut.kumottu(ALUE + "tilaus")).isFalse();
        // @loppu eristysTesti
    }
}
