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

/** Palvelutokenit, yleisö ja tokenien vaihto (sekaantunut sijainen). */
class TokenitTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final Clock KELLO = Clock.fixed(
            Instant.parse("2026-11-24T10:00:00Z"), ZoneOffset.UTC);

    final Tokenit.Myontaja kirjautuminen =
            new Tokenit.Myontaja("https://kirjautuminen.example", KELLO);
    final Tokenit.Myontaja sts =
            new Tokenit.Myontaja("https://sts.kauppa.example", KELLO);
    final Map<String, java.security.PublicKey> avaimet = Map.of(
            kirjautuminen.nimi(), kirjautuminen.julkinen(),
            sts.nimi(), sts.julkinen());

    /** Käyttäjän token selainsovellukselle (yleisö kauppa-api). */
    String kayttajanToken() {
        return kirjautuminen.myonna("asiakas-7", "kauppa-api",
                Set.of("tilaukset:luku", "tilaukset:kirjoitus",
                       "laskut:luku"),
                Duration.ofMinutes(30), null);
    }

    @Test
    void sekaantunutSijainenHaavoittuvassaPalvelussa() throws Exception {
        // @alku sijainen
        // Laskutus tarkistaa vain allekirjoituksen. Tilauspalvelu (tai
        // kuka tahansa, jolle käyttäjän token päätyy) voi käyttää sitä
        // laskutukseen, vaikkei tokenia ole myönnetty laskutukselle.
        var laskutus = new Tokenit.Tarkistaja(avaimet,
                ALUE + "laskutus", KELLO);
        var v = laskutus.tarkistaVainAllekirjoitus(kayttajanToken());
        assertThat(v.yleiso()).isEqualTo("kauppa-api"); // ei laskutus!
        // Oikea tarkistus hylkää saman tokenin.
        assertThatThrownBy(() -> laskutus.tarkista(kayttajanToken()))
                .hasMessage("väärä yleisö: kauppa-api");
        // @loppu sijainen
    }

    @Test
    void vaihdettuTokenOnRajattu() throws Exception {
        // @alku vaihtoTesti
        var vaihto = new Vaihtopalvelu(
                new Tokenit.Tarkistaja(avaimet, "kauppa-api", KELLO), sts,
                Set.of(new Vaihtopalvelu.Lupa(ALUE + "tilaus",
                        ALUE + "laskutus", Set.of("laskut:luku"))));
        String uusi = vaihto.vaihda(kayttajanToken(), ALUE + "tilaus",
                ALUE + "laskutus", Set.of("laskut:luku",
                        "tilaukset:kirjoitus"));

        var laskutus = new Tokenit.Tarkistaja(avaimet,
                ALUE + "laskutus", KELLO);
        Tokenit.Vaitteet v = laskutus.tarkista(uusi);
        assertThat(v.kohde()).isEqualTo("asiakas-7");     // kenen puolesta
        assertThat(v.toimija()).isEqualTo(ALUE + "tilaus"); // kuka välitti
        assertThat(v.oikeudet()).containsExactly("laskut:luku");
        assertThat(v.vanhenee())
                .isEqualTo(KELLO.instant().plus(Duration.ofMinutes(5)));
        // @loppu vaihtoTesti

        // Suosituspalvelulla ei ole lupaa välittää laskutukseen.
        assertThatThrownBy(() -> vaihto.vaihda(kayttajanToken(),
                ALUE + "suositukset", ALUE + "laskutus",
                Set.of("laskut:luku")))
                .hasMessageContaining("ei saa kutsua");
    }

    @Test
    void algoritmiJaVanheneminenTarkistetaan() throws Exception {
        var tarkistaja = new Tokenit.Tarkistaja(avaimet, "kauppa-api",
                KELLO);
        String token = kayttajanToken();
        // alg=none ja muokattu sisältö hylätään.
        String[] osat = token.split("\\.");
        String none = java.util.Base64.getUrlEncoder().withoutPadding()
                .encodeToString("{\"alg\":\"none\"}".getBytes());
        assertThatThrownBy(() -> tarkistaja.tarkista(
                none + "." + osat[1] + "."))
                .hasMessage("muoto");
        assertThatThrownBy(() -> tarkistaja.tarkista(
                none + "." + osat[1] + ".x"))
                .hasMessage("algoritmi: none");
        // Myöhemmin tarkistettuna sama token on vanhentunut.
        var myohemmin = new Tokenit.Tarkistaja(avaimet, "kauppa-api",
                Clock.offset(KELLO, Duration.ofMinutes(31)));
        assertThatThrownBy(() -> myohemmin.tarkista(token))
                .hasMessage("vanhentunut");
    }
}
