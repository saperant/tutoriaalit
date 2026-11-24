package fi.tutoriaalit.palveluturva.luottamus.reuna;

import fi.tutoriaalit.palveluturva.luottamus.Tokenit;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Pattern;
import tools.jackson.core.JacksonException;
import tools.jackson.databind.DeserializationFeature;
import tools.jackson.databind.json.JsonMapper;

/**
 * API-yhdyskäytävä järjestelmän reunalla. Se ei korvaa palvelujen
 * omaa tarkistusta, mutta karsii roskan ennen kuin se kuormittaa
 * palveluja: väärennetyt sisäiset otsakkeet, todentamattomat pyynnöt,
 * liian tiheät pyynnöt ja skeemaan sopimattomat rungot.
 */
public final class Yhdyskaytava {

    public record Pyynto(String metodi, String polku,
                         Map<String, String> otsakkeet, String runko) {}

    public sealed interface Tulos {
        record Valitetty(Pyynto pyynto) implements Tulos {}
        record Hylatty(int tila, String syy) implements Tulos {}
    }

    /** Tilauksen skeema. Tuntemattomat kentät hylätään. */
    public record Tilaus(String tuote, int maara) {}

    private static final Pattern TUOTE = Pattern.compile("[A-Z0-9-]{1,20}");
    private static final JsonMapper JSON = JsonMapper.builder()
            .enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
            .enable(DeserializationFeature.FAIL_ON_NULL_FOR_PRIMITIVES)
            .build();

    private final Tokenit.Tarkistaja tokenit;
    private final Nopeusrajoitin rajoitin;

    public Yhdyskaytava(Tokenit.Tarkistaja tokenit,
                        Nopeusrajoitin rajoitin) {
        this.tokenit = tokenit;
        this.rajoitin = rajoitin;
    }

    // @alku kasittele
    public Tulos kasittele(Pyynto saapuva) {
        // 1. Sisäiset otsakkeet asettaa vain yhdyskäytävä itse.
        Map<String, String> otsakkeet =
                new TreeMap<>(String.CASE_INSENSITIVE_ORDER);
        saapuva.otsakkeet().forEach((nimi, arvo) -> {
            String n = nimi.toLowerCase(Locale.ROOT);
            if (!n.equals("x-kayttaja") && !n.startsWith("x-sisainen-")) {
                otsakkeet.put(nimi, arvo);
            }
        });
        // 2. Todennus reunalla.
        String auth = otsakkeet.getOrDefault("Authorization", "");
        if (!auth.startsWith("Bearer ")) {
            return new Tulos.Hylatty(401, "token puuttuu");
        }
        Tokenit.Vaitteet kayttaja;
        try {
            kayttaja = tokenit.tarkista(auth.substring(7));
        } catch (Tokenit.Hylatty e) {
            return new Tulos.Hylatty(401, e.getMessage());
        }
        // 3. Nopeusrajoitus identiteettiä kohti, ei IP-osoitetta.
        if (!rajoitin.salli(kayttaja.kohde())) {
            return new Tulos.Hylatty(429, "liian monta pyyntöä");
        }
        // 4. Skeemavalidointi ennen kuin runko päätyy palveluun.
        if (saapuva.metodi().equals("POST")
                && saapuva.polku().equals("/tilaukset")) {
            String virhe = tarkistaTilaus(saapuva.runko());
            if (virhe != null) {
                return new Tulos.Hylatty(400, virhe);
            }
        }
        otsakkeet.put("X-Kayttaja", kayttaja.kohde());
        return new Tulos.Valitetty(new Pyynto(saapuva.metodi(),
                saapuva.polku(), otsakkeet, saapuva.runko()));
    }
    // @loppu kasittele

    static String tarkistaTilaus(String runko) {
        Tilaus t;
        try {
            t = JSON.readValue(runko, Tilaus.class);
        } catch (JacksonException e) {
            return "skeema: " + e.getOriginalMessage().split("\n")[0];
        }
        if (t.tuote() == null || !TUOTE.matcher(t.tuote()).matches()) {
            return "skeema: tuote";
        }
        if (t.maara() < 1 || t.maara() > 100) {
            return "skeema: maara 1–100";
        }
        return null;
    }
}
