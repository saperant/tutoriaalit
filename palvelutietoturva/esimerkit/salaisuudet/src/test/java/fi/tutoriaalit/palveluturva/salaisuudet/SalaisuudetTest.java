package fi.tutoriaalit.palveluturva.salaisuudet;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.nio.charset.StandardCharsets;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

class SalaisuudetTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final byte[] IBAN = "FI49 5000 9420 0287 30"
            .getBytes(StandardCharsets.UTF_8);

    /** Kello, jota testi voi siirtää eteenpäin. */
    static final class Siirrettava extends Clock {
        Instant nyt = Instant.parse("2026-11-24T10:00:00Z");
        void siirra(Duration d) { nyt = nyt.plus(d); }
        public Instant instant() { return nyt; }
        public ZoneId getZone() { return ZoneId.of("UTC"); }
        public Clock withZone(ZoneId z) { return this; }
    }

    @Test
    void kirjekuorisalausJaKonteksti() {
        // @alku kirjekuoriTesti
        var kms = new Avainpalvelu();
        kms.luoPaaavain("asiakastiedot");
        var kuori = Kirjekuori.salaa(kms, "asiakastiedot",
                "asiakkaat/42", IBAN);

        assertThat(kuori.pura(kms, "asiakkaat/42")).isEqualTo(IBAN);
        // Sama kirjekuori kopioituna toisen asiakkaan riville ei aukea:
        // konteksti on sidottu kääreeseen ja dataan.
        assertThatThrownBy(() -> kuori.pura(kms, "asiakkaat/43"))
                .hasMessage("purku epäonnistui");
        // @loppu kirjekuoriTesti
    }

    @Test
    void paaavaimenKiertoJaPoisto() {
        // @alku kiertoTesti
        var kms = new Avainpalvelu();
        kms.luoPaaavain("asiakastiedot");
        var vanha = Kirjekuori.salaa(kms, "asiakastiedot", "a/1", IBAN);
        int uusiVersio = kms.kierra("asiakastiedot");

        // Vanha kirjekuori aukeaa yhä; uudet käyttävät versiota 2.
        assertThat(vanha.pura(kms, "a/1")).isEqualTo(IBAN);
        var uusi = vanha.kaariUudelleen(kms, "a/1");
        assertThat(uusi.avain().versio()).isEqualTo(uusiVersio);
        assertThat(uusi.salattu()).isEqualTo(vanha.salattu());

        // Kun kaikki on kääritty uudelleen, versio 1 poistetaan.
        kms.poista("asiakastiedot", 1);
        assertThat(uusi.pura(kms, "a/1")).isEqualTo(IBAN);
        assertThatThrownBy(() -> vanha.pura(kms, "a/1"))
                .hasMessage("versio 1 on poistettu");
        // @loppu kiertoTesti
    }

    @Test
    void dynaamisetTunnuksetVanhenevatJaKumoutuvat() {
        // @alku dynaaminenTesti
        var kello = new Siirrettava();
        var varasto = new Salaisuusvarasto(Map.of(), kello);
        var t = varasto.luoTietokantatunnus(ALUE + "tilaus",
                Duration.ofHours(1));
        assertThat(varasto.kelpaa(t.kayttaja(), t.salasana())).isTrue();

        kello.siirra(Duration.ofMinutes(61)); // vuokra päättyi
        assertThat(varasto.kelpaa(t.kayttaja(), t.salasana())).isFalse();

        var a = varasto.luoTietokantatunnus(ALUE + "tilaus",
                Duration.ofHours(1));
        var b = varasto.luoTietokantatunnus(ALUE + "tilaus",
                Duration.ofHours(1));
        var muu = varasto.luoTietokantatunnus(ALUE + "laskutus",
                Duration.ofHours(1));
        // Poikkeama: tilauspalvelu on murrettu.
        assertThat(varasto.kumoaKaikki(ALUE + "tilaus")).isEqualTo(3);
        assertThat(varasto.kelpaa(a.kayttaja(), a.salasana())).isFalse();
        assertThat(varasto.kelpaa(b.kayttaja(), b.salasana())).isFalse();
        assertThat(varasto.kelpaa(muu.kayttaja(), muu.salasana()))
                .isTrue();
        // @loppu dynaaminenTesti
    }

    @Test
    void lukuoikeusPolunMukaan() {
        // @alku luvat
        var varasto = new Salaisuusvarasto(Map.of(
                ALUE + "laskutus", Set.of("kauppa/laskutus/"),
                ALUE + "tilaus", Set.of("kauppa/tilaus/")),
                Clock.systemUTC());
        varasto.kirjoita("kauppa/laskutus/maksuvalittaja", IBAN);
        assertThat(varasto.lue(ALUE + "laskutus",
                "kauppa/laskutus/maksuvalittaja")).isPresent();
        assertThat(varasto.lue(ALUE + "tilaus",
                "kauppa/laskutus/maksuvalittaja")).isEmpty();
        // @loppu luvat
    }

    @Test
    void avaimenKiertoIlmanKatkoa() {
        // @alku kaksoisavain
        var kello = new Siirrettava();
        var avain = new KierrettavaAvain("avain-A", Duration.ofHours(24),
                kello);
        avain.kierra("avain-B");
        assertThat(avain.kelpaa("avain-A")).isTrue();  // siirtymäaika
        assertThat(avain.kelpaa("avain-B")).isTrue();
        kello.siirra(Duration.ofHours(25));
        assertThat(avain.kelpaa("avain-A")).isFalse(); // vanha poistui
        assertThat(avain.kelpaa("avain-B")).isTrue();
        // @loppu kaksoisavain
    }
}
