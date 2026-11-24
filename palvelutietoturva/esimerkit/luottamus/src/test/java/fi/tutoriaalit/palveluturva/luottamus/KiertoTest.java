package fi.tutoriaalit.palveluturva.luottamus;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.Test;

/**
 * Varmentajan kierto ilman katkoa: luottamusnippuun lisätään uusi
 * juuri ennen kuin yksikään uusi varmenne on käytössä, ja vanha
 * poistetaan vasta kun yksikään vanha varmenne ei ole enää käytössä.
 */
class KiertoTest {

    static final String ALUE = "spiffe://kauppa.example/";

    @Test
    void varmentajanKiertoKolmessaVaiheessa() {
        // @alku kierto
        Varmentaja vanha = Varmentaja.luo("CA 2026-1");
        Varmentaja uusi = Varmentaja.luo("CA 2026-2");
        var tilaus = new VaihdettavaTls(
                vanha.myonna(ALUE + "tilaus", Duration.ofHours(1)),
                List.of(vanha.juuri()));

        try (var palvelin = Palvelin.mtls(tilaus,
                p -> new Palvelin.Vastaus(200, p.kutsuja().orElse("?")))) {
            var osoite = palvelin.osoite("/");
            var laskutusVanha = vanha.myonna(ALUE + "laskutus",
                    Duration.ofHours(1));
            var laskutusUusi = uusi.myonna(ALUE + "laskutus",
                    Duration.ofHours(1));
            var molemmat = List.of(vanha.juuri(), uusi.juuri());

            // 1. Kaikki luottavat molempiin juuriin.
            tilaus.asetaLuotetut(molemmat);
            assertThat(Asiakas.hae(laskutusVanha.tlsKonteksti(molemmat),
                    osoite).tila()).isEqualTo(200);
            assertThat(Asiakas.hae(laskutusUusi.tlsKonteksti(molemmat),
                    osoite).tila()).isEqualTo(200);

            // 2. Palvelut saavat uudet varmenteet (lennossa).
            tilaus.asetaIdentiteetti(
                    uusi.myonna(ALUE + "tilaus", Duration.ofHours(1)));
            assertThat(Asiakas.hae(laskutusUusi.tlsKonteksti(molemmat),
                    osoite).tila()).isEqualTo(200);

            // 3. Vanha juuri poistetaan nipusta.
            tilaus.asetaLuotetut(List.of(uusi.juuri()));
            assertThat(Asiakas.hae(laskutusVanha.tlsKonteksti(molemmat),
                    osoite).tila()).isZero(); // ei enää kelpaa
            assertThat(Asiakas.hae(laskutusUusi.tlsKonteksti(
                    List.of(uusi.juuri())), osoite).tila()).isEqualTo(200);
        }
        // @loppu kierto
    }

    @Test
    void liianAikainenPoistoKatkaiseeYhteydet() {
        Varmentaja vanha = Varmentaja.luo("CA 2026-1");
        Varmentaja uusi = Varmentaja.luo("CA 2026-2");
        var tilaus = new VaihdettavaTls(
                uusi.myonna(ALUE + "tilaus", Duration.ofHours(1)),
                List.of(uusi.juuri()));
        try (var palvelin = Palvelin.mtls(tilaus,
                p -> new Palvelin.Vastaus(200, "ok"))) {
            // Asiakas, joka luottaa vain vanhaan juureen, ei tunnista
            // palvelimen uutta varmennetta: vaihe 1 jäi tekemättä.
            var laskutus = vanha.myonna(ALUE + "laskutus",
                    Duration.ofHours(1));
            assertThat(Asiakas.hae(laskutus.tlsKonteksti(
                    List.of(vanha.juuri())), palvelin.osoite("/")).tila())
                    .isZero();
        }
    }
}
