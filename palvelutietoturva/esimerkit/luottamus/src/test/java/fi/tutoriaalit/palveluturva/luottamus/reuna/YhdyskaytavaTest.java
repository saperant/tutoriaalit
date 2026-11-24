package fi.tutoriaalit.palveluturva.luottamus.reuna;

import static org.assertj.core.api.Assertions.assertThat;

import fi.tutoriaalit.palveluturva.luottamus.Tokenit;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.junit.jupiter.api.Test;

class YhdyskaytavaTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final Clock KELLO = Clock.fixed(
            Instant.parse("2026-11-24T10:00:00Z"), ZoneOffset.UTC);

    final Tokenit.Myontaja kirjautuminen =
            new Tokenit.Myontaja("https://kirjautuminen.example", KELLO);
    final Yhdyskaytava reuna = new Yhdyskaytava(
            new Tokenit.Tarkistaja(Map.of(kirjautuminen.nimi(),
                    kirjautuminen.julkinen()), "kauppa-api", KELLO),
            new Nopeusrajoitin(10, Duration.ofMinutes(1), KELLO));

    Yhdyskaytava.Pyynto pyynto(String runko, Map<String, String> lisat) {
        String token = kirjautuminen.myonna("asiakas-7", "kauppa-api",
                Set.of("tilaukset:kirjoitus"), Duration.ofMinutes(5),
                null);
        var otsakkeet = new java.util.HashMap<>(lisat);
        otsakkeet.put("Authorization", "Bearer " + token);
        return new Yhdyskaytava.Pyynto("POST", "/tilaukset", otsakkeet,
                runko);
    }

    @Test
    void vaarennetytSisaisetOtsakkeetPoistetaan() {
        // @alku otsakkeet
        var tulos = reuna.kasittele(pyynto(
                "{\"tuote\":\"KAHVI-1\",\"maara\":2}",
                Map.of("X-Kayttaja", "yllapitaja",
                       "X-Sisainen-Rooli", "admin")));
        var valitetty = (Yhdyskaytava.Tulos.Valitetty) tulos;
        assertThat(valitetty.pyynto().otsakkeet())
                .containsEntry("X-Kayttaja", "asiakas-7")
                .doesNotContainKey("X-Sisainen-Rooli");
        // @loppu otsakkeet
    }

    @Test
    void todennusNopeusJaSkeema() {
        // @alku hylkaykset
        var ilman = new Yhdyskaytava.Pyynto("GET", "/tilaukset",
                Map.of(), "");
        assertThat(reuna.kasittele(ilman))
                .isEqualTo(new Yhdyskaytava.Tulos.Hylatty(401,
                        "token puuttuu"));
        assertThat(reuna.kasittele(pyynto(
                "{\"tuote\":\"KAHVI-1\",\"maara\":2,\"hinta\":0}",
                Map.of()))).hasToString(
                "Hylatty[tila=400, syy=skeema: Unrecognized property"
                + " \"hinta\" (class fi.tutoriaalit.palveluturva"
                + ".luottamus.reuna.Yhdyskaytava$Tilaus), not marked"
                + " as ignorable]");
        assertThat(reuna.kasittele(pyynto(
                "{\"tuote\":\"KAHVI-1\",\"maara\":0}", Map.of())))
                .isEqualTo(new Yhdyskaytava.Tulos.Hylatty(400,
                        "skeema: maara 1–100"));
        // Kahdeksan pyyntöä lisää: raja (10/min) täyttyy.
        for (int i = 0; i < 8; i++) {
            reuna.kasittele(pyynto(
                    "{\"tuote\":\"KAHVI-1\",\"maara\":1}", Map.of()));
        }
        assertThat(reuna.kasittele(pyynto(
                "{\"tuote\":\"KAHVI-1\",\"maara\":1}", Map.of())))
                .isEqualTo(new Yhdyskaytava.Tulos.Hylatty(429,
                        "liian monta pyyntöä"));
        // @loppu hylkaykset
    }

    @Test
    void palveluaEiVoiOhittaaYhdyskaytavaa() {
        // @alku ohitusTesti
        var palvelu = new Tilauspalvelu(ALUE + "yhdyskaytava");
        // Hyökkääjä on päässyt sisäverkkoon (esim. suosituspalvelun
        // kautta) ja kutsuu tilauspalvelua suoraan.
        var suoraan = new Yhdyskaytava.Pyynto("GET", "/tilaukset",
                Map.of("X-Kayttaja", "asiakas-1"), "");
        assertThat(palvelu.kayttajaHaavoittuva(suoraan))
                .isEqualTo("asiakas-1"); // väärennys menee läpi
        assertThat(palvelu.kayttaja(Optional.of(ALUE + "suositukset"),
                suoraan)).isEmpty();
        assertThat(palvelu.kayttaja(Optional.of(ALUE + "yhdyskaytava"),
                suoraan)).contains("asiakas-1");
        // @loppu ohitusTesti
    }
}
