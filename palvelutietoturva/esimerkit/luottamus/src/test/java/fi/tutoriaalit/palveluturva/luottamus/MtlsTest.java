package fi.tutoriaalit.palveluturva.luottamus;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** Otsakkeeseen luottava palvelu vastaan mTLS ja identiteetti. */
class MtlsTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final String LASKUTUS = ALUE + "laskutus";
    static final String SUOSITUKSET = ALUE + "suositukset";

    // @alku haavoittuva
    /** HAAVOITTUVA: kutsuja kertoo itse, kuka on. */
    static Palvelin.Vastaus luottaaOtsakkeeseen(Palvelin.Pyynto p) {
        String kutsuja = p.otsake("X-Kutsuja");
        if (LASKUTUS.equals(kutsuja)) {
            return new Palvelin.Vastaus(200, "asiakas 42: IBAN FI49...");
        }
        return new Palvelin.Vastaus(403, "ei oikeutta");
    }
    // @loppu haavoittuva

    // @alku korjattu
    /** KORJATTU: kutsuja on se, jonka varmenne TLS-kättelyssä
     *  todistettiin. Sallitut kutsujat on lueteltu nimeltä. */
    static final Set<String> SALLITUT = Set.of(LASKUTUS);

    static Palvelin.Vastaus luottaaVarmenteeseen(Palvelin.Pyynto p) {
        if (p.kutsuja().filter(SALLITUT::contains).isPresent()) {
            return new Palvelin.Vastaus(200, "asiakas 42: IBAN FI49...");
        }
        return new Palvelin.Vastaus(403, "ei oikeutta: "
                + p.kutsuja().orElse("tuntematon"));
    }
    // @loppu korjattu

    @Test
    void otsakkeeseenLuottavaPalveluPaljastaaTiedot() {
        // @alku hyokkays
        try (var palvelin = Palvelin.http(MtlsTest::luottaaOtsakkeeseen)) {
            var tulos = Asiakas.hae(null, palvelin.osoite("/asiakkaat/42"),
                    Map.of("X-Kutsuja", LASKUTUS)); // kuka tahansa
            assertThat(tulos.tila()).isEqualTo(200); // verkossa voi
        }                                            // väittää näin
        // @loppu hyokkays
    }

    @Test
    void mtlsTodentaaKutsujanJaValtuutusNimeaa() {
        // @alku mtls
        Varmentaja ca = Varmentaja.luo("Kaupan sisäinen CA");
        Varmentaja vieras = Varmentaja.luo("Hyökkääjän CA");
        var luotetut = List.of(ca.juuri());
        Identiteetti tilaus = ca.myonna(ALUE + "tilaus",
                Duration.ofHours(1));
        var tls = new VaihdettavaTls(tilaus, luotetut);

        try (var palvelin = Palvelin.mtls(tls,
                MtlsTest::luottaaVarmenteeseen)) {
            var osoite = palvelin.osoite("/asiakkaat/42");
            var laskutus = ca.myonna(LASKUTUS, Duration.ofHours(1));
            var suositukset = ca.myonna(SUOSITUKSET, Duration.ofHours(1));
            var vaarennetty = vieras.myonna(LASKUTUS, Duration.ofHours(1));

            assertThat(Asiakas.hae(laskutus.tlsKonteksti(luotetut),
                    osoite).tila()).isEqualTo(200);
            assertThat(Asiakas.hae(suositukset.tlsKonteksti(luotetut),
                    osoite).toString())
                    .isEqualTo("403 ei oikeutta: " + SUOSITUKSET);
            assertThat(Asiakas.hae(vaarennetty.tlsKonteksti(luotetut),
                    osoite).toString()).isEqualTo("ei yhteyttä");
        }
        // @loppu mtls
    }

    @Test
    void ilmanAsiakasvarmennettaEiYhteytta() throws Exception {
        Varmentaja ca = Varmentaja.luo("Kaupan sisäinen CA");
        var tls = new VaihdettavaTls(ca.myonna(ALUE + "tilaus",
                Duration.ofHours(1)), List.of(ca.juuri()));
        try (var palvelin = Palvelin.mtls(tls,
                MtlsTest::luottaaVarmenteeseen)) {
            // Asiakas luottaa palvelimeen mutta ei esitä varmennetta.
            var vainLuottamus = javax.net.ssl.SSLContext
                    .getInstance("TLSv1.3");
            var tmf = javax.net.ssl.TrustManagerFactory
                    .getInstance("PKIX");
            tmf.init(Identiteetti.luottamusvarasto(List.of(ca.juuri())));
            vainLuottamus.init(null, tmf.getTrustManagers(), null);
            var tulos = Asiakas.hae(vainLuottamus,
                    palvelin.osoite("/asiakkaat/42"),
                    Map.of("X-Kutsuja", LASKUTUS));
            assertThat(tulos.toString()).isEqualTo("ei yhteyttä");
        }
    }

    @Test
    void vanhentunutVarmenneHylataan() {
        // @alku vanhentunut
        Varmentaja ca = Varmentaja.luo("Kaupan sisäinen CA");
        var luotetut = List.of(ca.juuri());
        var tls = new VaihdettavaTls(ca.myonna(ALUE + "tilaus",
                Duration.ofHours(1)), luotetut);
        Instant tunteja = Instant.now().minus(Duration.ofHours(3));
        Identiteetti vanha = ca.myonna(LASKUTUS, tunteja,
                tunteja.plus(Duration.ofHours(1))); // vanheni 2 h sitten
        try (var palvelin = Palvelin.mtls(tls,
                MtlsTest::luottaaVarmenteeseen)) {
            assertThat(Asiakas.hae(vanha.tlsKonteksti(luotetut),
                    palvelin.osoite("/asiakkaat/42")).toString())
                    .isEqualTo("ei yhteyttä");
        }
        // @loppu vanhentunut
    }

    @Test
    void varmenteessaOnSpiffeTunniste() {
        Varmentaja ca = Varmentaja.luo("Kaupan sisäinen CA");
        var laskutus = ca.myonna(LASKUTUS, Duration.ofMinutes(30));
        assertThat(Identiteetti.spiffeId(laskutus.varmenne()))
                .contains(LASKUTUS);
        assertThat(laskutus.varmenne().getNotAfter().toInstant())
                .isBefore(Instant.now().plus(Duration.ofMinutes(31)));
    }
}
