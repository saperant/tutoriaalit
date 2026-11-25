package fi.tutoriaalit.palveluturva.luottamus;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

/** Viestin kuoren tarkistus: tuottaja, aihe, eheys, ikä ja toisto. */
class ViestitTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final Clock KELLO = Clock.fixed(
            Instant.parse("2026-11-24T10:00:00Z"), ZoneOffset.UTC);

    final Viestit.Tuottaja tilaus =
            new Viestit.Tuottaja(ALUE + "tilaus", KELLO);
    final Viestit.Tuottaja suositukset =
            new Viestit.Tuottaja(ALUE + "suositukset", KELLO);

    Viestit.Kuluttaja laskutus(Clock kello) {
        return new Viestit.Kuluttaja(
                Map.of(tilaus.tunniste(), tilaus.julkinen(),
                       suositukset.tunniste(), suositukset.julkinen()),
                Map.of("tilaus.luotu", Set.of(tilaus.tunniste())),
                kello, Duration.ofMinutes(10));
    }

    @Test
    void kuluttajaTarkistaaTuottajanEheydenJaToiston() throws Exception {
        // @alku testi
        var laskutus = laskutus(KELLO);
        var viesti = tilaus.laheta("tilaus.luotu", "{\"tilaus\":1001}");
        assertThat(laskutus.vastaanota(viesti))
                .isEqualTo("{\"tilaus\":1001}");
        // Sama viesti toimitetaan uudelleen (tai hyökkääjä toistaa sen).
        assertThatThrownBy(() -> laskutus.vastaanota(viesti))
                .hasMessage("jo käsitelty");

        // Murrettu suosituspalvelu pääsee välittimeen ja julkaisee
        // tilausaiheeseen omalla avaimellaan.
        var vaarennos = suositukset.laheta("tilaus.luotu",
                "{\"tilaus\":9999}");
        assertThatThrownBy(() -> laskutus.vastaanota(vaarennos))
                .hasMessage("tuottaja ei saa julkaista aiheeseen");

        // Välittimessä muutettu runko: allekirjoitus ei enää täsmää.
        var aito = tilaus.laheta("tilaus.luotu", "{\"tilaus\":1002}");
        var muutettu = new Viestit.Kuori(aito.aihe(), aito.tuottaja(),
                aito.id(), aito.aika(), "{\"tilaus\":1002,\"summa\":0}",
                aito.allekirjoitus());
        assertThatThrownBy(() -> laskutus.vastaanota(muutettu))
                .hasMessage("allekirjoitus ei täsmää");
        // @loppu testi

        // Vanha viesti: kuluttaja, jonka kello on 11 minuuttia edellä.
        var myohemmin = laskutus(Clock.offset(KELLO,
                Duration.ofMinutes(11)));
        assertThatThrownBy(() -> myohemmin.vastaanota(aito))
                .hasMessage("liian vanha");
    }
}
