package fi.tutoriaalit.palvelut.uudistus.uusi;

import fi.tutoriaalit.palvelut.uudistus.Http;
import java.net.URI;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.Locale;
import java.util.Optional;

// @alku acl
/**
 * Korruption estokerros (anti-corruption layer): ainoa paikka, joka
 * tuntee vanhan järjestelmän muodon. Uusi koodi näkee vain Asiakas-
 * olioita. Kun vanha järjestelmä poistuu, vain tämä luokka poistuu.
 */
public final class Korruptionestokerros {
    private static final DateTimeFormatter PVM =
        DateTimeFormatter.BASIC_ISO_DATE;
    private final URI vanha;

    public Korruptionestokerros(URI vanha) {
        this.vanha = vanha;
    }

    public Optional<Asiakas> asiakas(String id) {
        var vastaus = Http.hae(vanha.resolve("/asiakas?nro=" + id));
        if (vastaus.tila() == 404) {
            return Optional.empty();
        }
        return Optional.of(kaanna(vastaus.runko()));
    }

    static Asiakas kaanna(String rivi) {
        String[] k = rivi.split(";");
        String[] nimi = k[1].split(" ", 2);       // SUKUNIMI ETUNIMI
        return new Asiakas(k[0], isoAlkukirjain(nimi[1]),
                isoAlkukirjain(nimi[0]), tila(k[2]),
                LocalDate.parse(k[3], PVM));
    }

    static Asiakas.Tila tila(String koodi) {
        return switch (koodi) {
            case "A" -> Asiakas.Tila.AKTIIVINEN;
            case "P" -> Asiakas.Tila.PASSIIVINEN;
            case "K" -> Asiakas.Tila.ESTETTY;     // "kielletty"
            default -> throw new IllegalArgumentException(koodi);
        };
    }
    // @loppu acl

    private static String isoAlkukirjain(String sana) {
        String pienet = sana.toLowerCase(Locale.ROOT);
        return Character.toUpperCase(pienet.charAt(0)) + pienet.substring(1);
    }
}
