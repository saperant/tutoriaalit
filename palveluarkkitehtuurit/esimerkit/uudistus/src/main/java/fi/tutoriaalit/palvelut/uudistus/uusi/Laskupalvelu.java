package fi.tutoriaalit.palvelut.uudistus.uusi;

import com.sun.net.httpserver.HttpServer;
import fi.tutoriaalit.palvelut.uudistus.Http;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * Laskujen uusi toteutus. Ensimmäisessä vaiheessa se toteuttaa vanhan
 * rajapinnan sellaisenaan (GET /laskut?nro=), jotta asiakkaiden ei
 * tarvitse muuttua: vastaus on "laskujen määrä;avoin summa".
 */
public final class Laskupalvelu {
    private Laskupalvelu() {
    }

    public static HttpServer kaynnista(Map<String, List<BigDecimal>> laskut) {
        return Http.palvelin(vaihto -> {
            String nro = vaihto.getRequestURI().getQuery()
                .replace("nro=", "");
            List<BigDecimal> omat = laskut.get(nro);
            if (omat == null) {
                Http.vastaa(vaihto,
                        new Http.Vastaus(404, "text/plain", "EI LOYDY"));
                return;
            }
            BigDecimal summa = omat.stream()
                .reduce(BigDecimal.ZERO, BigDecimal::add);
            Http.vastaa(vaihto, new Http.Vastaus(200, "text/plain",
                    omat.size() + ";" + summa.toPlainString()
                        .replace('.', ',')));
        });
    }
}
