package fi.tutoriaalit.palveluturva.luottamus;

import fi.tutoriaalit.palveluturva.luottamus.reuna.Nopeusrajoitin;
import fi.tutoriaalit.palveluturva.luottamus.reuna.Tilauspalvelu;
import fi.tutoriaalit.palveluturva.luottamus.reuna.Yhdyskaytava;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.TreeSet;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import org.junit.jupiter.api.Test;

/**
 * Näytösajot: samat kokeet kuin muissa testeissä, mutta tulos
 * kirjoitetaan tauluksi, jossa näkyy, mitä kukin osapuoli vastasi.
 */
class NaytosTest {

    static final String ALUE = "spiffe://kauppa.example/";
    static final String LASKUTUS = ALUE + "laskutus";
    static final Clock KELLO = Clock.fixed(
            Instant.parse("2026-11-24T10:00:00Z"), ZoneOffset.UTC);

    @Test
    void otsakkeeseenLuottavaPalvelu() throws Exception {
        try (var palvelin = Palvelin.http(MtlsTest::luottaaOtsakkeeseen)) {
            var osoite = palvelin.osoite("/asiakkaat/42");
            new Naytos("02-otsake").taulu(List.of(
                    List.of("pyynnön otsake", "vastaus"),
                    List.of("(ei otsaketta)",
                            Asiakas.hae(null, osoite).toString()),
                    List.of("X-Kutsuja: " + LASKUTUS,
                            Asiakas.hae(null, osoite,
                                    Map.of("X-Kutsuja", LASKUTUS))
                                    .toString()))).vertaa();
        }
    }

    @Test
    void neljaKutsujaaMtlsPalvelulle() throws Exception {
        Varmentaja ca = Varmentaja.luo("Kaupan sisäinen CA");
        Varmentaja vieras = Varmentaja.luo("Hyökkääjän CA");
        var luotetut = List.of(ca.juuri());
        var tunti = Duration.ofHours(1);
        var tls = new VaihdettavaTls(ca.myonna(ALUE + "tilaus", tunti),
                luotetut);
        Instant ennen = Instant.now().minus(Duration.ofHours(3));

        var vainLuottamus = SSLContext.getInstance("TLSv1.3");
        var tmf = TrustManagerFactory.getInstance("PKIX");
        tmf.init(Identiteetti.luottamusvarasto(luotetut));
        vainLuottamus.init(null, tmf.getTrustManagers(), null);

        try (var palvelin = Palvelin.mtls(tls,
                MtlsTest::luottaaVarmenteeseen)) {
            var osoite = palvelin.osoite("/asiakkaat/42");
            var rivit = new ArrayList<List<String>>();
            rivit.add(List.of("kutsujan varmenne", "tulos"));
            rivit.add(List.of("laskutus", Asiakas.hae(
                    ca.myonna(LASKUTUS, tunti).tlsKonteksti(luotetut),
                    osoite).toString()));
            rivit.add(List.of("suositukset", Asiakas.hae(
                    ca.myonna(ALUE + "suositukset", tunti)
                            .tlsKonteksti(luotetut), osoite).toString()));
            rivit.add(List.of("laskutus, vieras CA", Asiakas.hae(
                    vieras.myonna(LASKUTUS, tunti).tlsKonteksti(luotetut),
                    osoite).toString()));
            rivit.add(List.of("laskutus, vanhentunut", Asiakas.hae(
                    ca.myonna(LASKUTUS, ennen, ennen.plus(tunti))
                            .tlsKonteksti(luotetut), osoite).toString()));
            rivit.add(List.of("ei varmennetta", Asiakas.hae(
                    vainLuottamus, osoite,
                    Map.of("X-Kutsuja", LASKUTUS)).toString()));
            new Naytos("04-mtls").taulu(rivit).vertaa();
        }
    }

    @Test
    void varmentajanKiertoVaiheittain() throws Exception {
        Varmentaja vanha = Varmentaja.luo("CA 2026-1");
        Varmentaja uusi = Varmentaja.luo("CA 2026-2");
        var tunti = Duration.ofHours(1);
        var vainVanha = List.of(vanha.juuri());
        var molemmat = List.of(vanha.juuri(), uusi.juuri());
        var vainUusi = List.of(uusi.juuri());
        var tilaus = new VaihdettavaTls(
                vanha.myonna(ALUE + "tilaus", tunti), vainVanha);
        var laskutusVanha = vanha.myonna(LASKUTUS, tunti);
        var laskutusUusi = uusi.myonna(LASKUTUS, tunti);

        try (var palvelin = Palvelin.mtls(tilaus,
                p -> new Palvelin.Vastaus(200, "ok"))) {
            var osoite = palvelin.osoite("/");
            var rivit = new ArrayList<List<String>>();
            // Sarakkeet: luottamusnippu, palvelimen (tilaus) varmenteen
            // myöntäjä ja kutsu asiakkaalta (laskutus), jonka varmenne
            // on vanhan tai uuden varmentajan myöntämä.
            rivit.add(List.of("vaihe", "nippu", "palvelin",
                    "asiakas: vanha", "asiakas: uusi"));
            // Asiakkaat luottavat samaan nippuun kuin palvelin.
            record Vaihe(String nimi, String nippu, String oma,
                         List<java.security.cert.X509Certificate> n) {}
            var vaiheet = List.of(
                    new Vaihe("alussa", "vanha", "vanha", vainVanha),
                    new Vaihe("1. uusi juuri nippuun", "vanha + uusi",
                            "vanha", molemmat),
                    new Vaihe("2. uudet varmenteet", "vanha + uusi",
                            "uusi", molemmat),
                    new Vaihe("3. vanha juuri pois", "uusi", "uusi",
                            vainUusi));
            for (Vaihe v : vaiheet) {
                tilaus.asetaLuotetut(v.n());
                if (v.oma().equals("uusi")) {
                    tilaus.asetaIdentiteetti(
                            uusi.myonna(ALUE + "tilaus", tunti));
                }
                rivit.add(List.of(v.nimi(), v.nippu(), v.oma(),
                        tila(Asiakas.hae(
                                laskutusVanha.tlsKonteksti(v.n()), osoite)),
                        tila(Asiakas.hae(
                                laskutusUusi.tlsKonteksti(v.n()), osoite))));
            }
            // Vaihe 1 ohitettu: palvelin esittää jo uuden varmenteen,
            // mutta asiakas tuntee vain vanhan juuren.
            tilaus.asetaLuotetut(molemmat);
            rivit.add(List.of("vaihe 1 ohitettu", "vain vanha", "uusi",
                    tila(Asiakas.hae(laskutusVanha.tlsKonteksti(vainVanha),
                            osoite)), "–"));
            new Naytos("05-kierto").taulu(rivit).vertaa();
        }
    }

    static String tila(Asiakas.Tulos t) {
        return t.tila() == 0 ? "ei yhteyttä" : String.valueOf(t.tila());
    }

    @Test
    void tokenEnnenJaJalkeenVaihdon() throws Exception {
        var kirjautuminen = new Tokenit.Myontaja(
                "https://kirjautuminen.example", KELLO);
        var sts = new Tokenit.Myontaja("https://sts.kauppa.example", KELLO);
        var avaimet = Map.of(kirjautuminen.nimi(), kirjautuminen.julkinen(),
                sts.nimi(), sts.julkinen());
        String kayttajan = kirjautuminen.myonna("asiakas-7", "kauppa-api",
                Set.of("tilaukset:luku", "tilaukset:kirjoitus",
                        "laskut:luku"), Duration.ofMinutes(30), null);
        var laskutus = new Tokenit.Tarkistaja(avaimet, LASKUTUS, KELLO);
        var vaihto = new Vaihtopalvelu(
                new Tokenit.Tarkistaja(avaimet, "kauppa-api", KELLO), sts,
                Set.of(new Vaihtopalvelu.Lupa(ALUE + "tilaus", LASKUTUS,
                        Set.of("laskut:luku"))));
        String vaihdettu = vaihto.vaihda(kayttajan, ALUE + "tilaus",
                LASKUTUS, Set.of("laskut:luku", "tilaukset:kirjoitus"));

        var n = new Naytos("06-tokenit");
        n.rivi("käyttäjän token");
        vaitteet(n, laskutus.tarkistaVainAllekirjoitus(kayttajan));
        n.rivi("  laskutus, vain allekirjoitus: hyväksytty");
        n.rivi("  laskutus, koko tarkistus:     "
                + yrita(() -> laskutus.tarkista(kayttajan)));
        n.rivi("");
        n.rivi("vaihdettu token (tilaus pyysi laskutusta varten)");
        vaitteet(n, laskutus.tarkista(vaihdettu));
        n.rivi("  laskutus, koko tarkistus:     "
                + yrita(() -> laskutus.tarkista(vaihdettu)));
        n.rivi("");
        n.rivi("suositukset pyytää vaihtoa laskutukseen:");
        n.rivi("  " + yrita(() -> vaihto.vaihda(kayttajan,
                ALUE + "suositukset", LASKUTUS, Set.of("laskut:luku")))
                .replace(ALUE, ""));
        n.vertaa();
    }

    static void vaitteet(Naytos n, Tokenit.Vaitteet v) {
        long min = Duration.between(KELLO.instant(), v.vanhenee())
                .toMinutes();
        n.taulu(List.of(
                List.of("  iss", v.myontaja()),
                List.of("  sub", v.kohde()),
                List.of("  aud", v.yleiso()),
                List.of("  scope", String.join(" ",
                        new TreeSet<>(v.oikeudet()))),
                List.of("  act", v.toimija() == null ? "–" : v.toimija()),
                List.of("  exp", "nyt + " + min + " min")));
    }

    interface Koe {
        Object aja() throws Exception;
    }

    static String yrita(Koe koe) {
        try {
            koe.aja();
            return "hyväksytty";
        } catch (Exception e) {
            return "hylätty (" + e.getMessage() + ")";
        }
    }

    @Test
    void yhdyskaytavanPaatokset() throws Exception {
        var kirjautuminen = new Tokenit.Myontaja(
                "https://kirjautuminen.example", KELLO);
        var reuna = new Yhdyskaytava(
                new Tokenit.Tarkistaja(Map.of(kirjautuminen.nimi(),
                        kirjautuminen.julkinen()), "kauppa-api", KELLO),
                new Nopeusrajoitin(10, Duration.ofMinutes(1), KELLO));
        String token = "Bearer " + kirjautuminen.myonna("asiakas-7",
                "kauppa-api", Set.of("tilaukset:kirjoitus"),
                Duration.ofMinutes(5), null);
        String kelpo = "{\"tuote\":\"KAHVI-1\",\"maara\":1}";

        var rivit = new ArrayList<List<String>>();
        rivit.add(List.of("pyyntö", "yhdyskäytävän päätös"));
        rivit.add(List.of("ei tokenia", tulos(reuna.kasittele(
                new Yhdyskaytava.Pyynto("GET", "/tilaukset", Map.of(),
                        "")))));
        rivit.add(List.of("ylimääräinen kenttä", tulos(
                reuna.kasittele(new Yhdyskaytava.Pyynto("POST",
                        "/tilaukset", Map.of("Authorization", token),
                        "{\"tuote\":\"KAHVI-1\",\"maara\":2,"
                        + "\"hinta\":0}")))));
        rivit.add(List.of("maara: 0", tulos(reuna.kasittele(
                new Yhdyskaytava.Pyynto("POST", "/tilaukset",
                        Map.of("Authorization", token),
                        "{\"tuote\":\"KAHVI-1\",\"maara\":0}")))));
        rivit.add(List.of("X-Kayttaja: yllapitaja", tulos(
                reuna.kasittele(new Yhdyskaytava.Pyynto("POST",
                        "/tilaukset", Map.of("Authorization", token,
                                "X-Kayttaja", "yllapitaja",
                                "X-Sisainen-Rooli", "admin"), kelpo)))));
        for (int i = 0; i < 7; i++) {
            reuna.kasittele(new Yhdyskaytava.Pyynto("POST", "/tilaukset",
                    Map.of("Authorization", token), kelpo));
        }
        rivit.add(List.of("11. pyyntö minuutissa", tulos(
                reuna.kasittele(new Yhdyskaytava.Pyynto("POST",
                        "/tilaukset", Map.of("Authorization", token),
                        kelpo)))));
        var n = new Naytos("10-reuna").taulu(rivit);

        // Suora kutsu tilauspalveluun yhdyskäytävän ohi.
        var palvelu = new Tilauspalvelu(ALUE + "yhdyskaytava");
        var suoraan = new Yhdyskaytava.Pyynto("GET", "/tilaukset",
                Map.of("X-Kayttaja", "asiakas-1"), "");
        n.rivi("");
        n.taulu(List.of(
                List.of("suora kutsu, X-Kayttaja: asiakas-1",
                        "palvelun näkemä käyttäjä"),
                List.of("haavoittuva palvelu, kuka tahansa",
                        palvelu.kayttajaHaavoittuva(suoraan)),
                List.of("korjattu, kutsuja suositukset",
                        palvelu.kayttaja(Optional.of(ALUE + "suositukset"),
                                suoraan).orElse("hylätty")),
                List.of("korjattu, kutsuja yhdyskaytava",
                        palvelu.kayttaja(Optional.of(ALUE + "yhdyskaytava"),
                                suoraan).orElse("hylätty"))));
        n.vertaa();
    }

    @Test
    void viestinKuorenTarkistus() throws Exception {
        var tilaus = new Viestit.Tuottaja(ALUE + "tilaus", KELLO);
        var suositukset = new Viestit.Tuottaja(ALUE + "suositukset", KELLO);
        var avaimet = Map.of(tilaus.tunniste(), tilaus.julkinen(),
                suositukset.tunniste(), suositukset.julkinen());
        var aiheet = Map.of("tilaus.luotu", Set.of(tilaus.tunniste()));
        var laskutus = new Viestit.Kuluttaja(avaimet, aiheet, KELLO,
                Duration.ofMinutes(10));
        var myohemmin = new Viestit.Kuluttaja(avaimet, aiheet,
                Clock.offset(KELLO, Duration.ofMinutes(11)),
                Duration.ofMinutes(10));

        var aito = tilaus.laheta("tilaus.luotu", "{\"tilaus\":1001}");
        var muutettu = new Viestit.Kuori(aito.aihe(), aito.tuottaja(),
                aito.id(), aito.aika(), "{\"tilaus\":1001,\"summa\":0}",
                aito.allekirjoitus());
        var vaarennos = suositukset.laheta("tilaus.luotu",
                "{\"tilaus\":9999}");
        new Naytos("10-viestit").taulu(List.of(
                List.of("viesti aiheessa tilaus.luotu", "laskutus"),
                List.of("tilauksen allekirjoittama",
                        yrita(() -> laskutus.vastaanota(aito))),
                List.of("sama viesti uudelleen",
                        yrita(() -> laskutus.vastaanota(aito))),
                List.of("runko muutettu välittimessä",
                        yrita(() -> laskutus.vastaanota(muutettu))),
                List.of("suositusten allekirjoittama",
                        yrita(() -> laskutus.vastaanota(vaarennos))),
                List.of("11 minuuttia vanha",
                        yrita(() -> myohemmin.vastaanota(aito)))))
                .vertaa();
    }

    static String tulos(Yhdyskaytava.Tulos t) {
        if (t instanceof Yhdyskaytava.Tulos.Hylatty h) {
            // Jäsentimen pitkästä virheilmoituksesta näytetään alku.
            String syy = h.syy();
            int i = syy.indexOf(" (class");
            return h.tila() + " " + (i < 0 ? syy : syy.substring(0, i));
        }
        var o = ((Yhdyskaytava.Tulos.Valitetty) t).pyynto().otsakkeet();
        return "välitetty: X-Kayttaja=" + o.get("X-Kayttaja")
                + (o.containsKey("X-Sisainen-Rooli") ? ""
                        : ", rooliotsake poistettu");
    }
}
