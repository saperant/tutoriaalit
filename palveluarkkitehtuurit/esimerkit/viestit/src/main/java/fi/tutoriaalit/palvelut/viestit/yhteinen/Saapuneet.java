package fi.tutoriaalit.palvelut.viestit.yhteinen;

import java.util.Optional;
import java.util.function.Supplier;
import org.springframework.jdbc.core.simple.JdbcClient;

// @alku saapuneet
/**
 * Idempotentti vastaanottaja (inbox): käsitellyt viestit ja niiden
 * vastaukset tallennetaan samassa transaktiossa kuin käsittelyn
 * muutokset. Toistettu viesti saa saman vastauksen käsittelemättä
 * sitä uudelleen. Jokaisella palvelulla on oma taulunsa omassa
 * skeemassaan.
 */
public final class Saapuneet {
    public record Vastaus(String tyyppi, String runko) {
    }

    private final JdbcClient jdbc;
    private final String taulu;

    public Saapuneet(JdbcClient jdbc, String skeema) {
        this.jdbc = jdbc;
        this.taulu = skeema + ".saapuneet";
    }

    public Vastaus kasittele(String viestiId, Supplier<Vastaus> kasittely) {
        Optional<Vastaus> aiempi = jdbc.sql("SELECT tyyppi, runko FROM "
                + taulu + " WHERE viesti_id = ?")
            .param(viestiId).query(Vastaus.class).optional();
        if (aiempi.isPresent()) {
            return aiempi.get();
        }
        Vastaus vastaus = kasittely.get();
        jdbc.sql("INSERT INTO " + taulu
                + " (viesti_id, tyyppi, runko) VALUES (?, ?, ?)")
            .params(viestiId, vastaus.tyyppi(), vastaus.runko()).update();
        return vastaus;
    }
}
// @loppu saapuneet
