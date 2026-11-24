package fi.tutoriaalit.palvelut.etakutsut.varasto;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.util.Map;

/** Varastopalvelu: GET /saldo/{tuote}. */
public final class VarastoPalvelin {
    private VarastoPalvelin() {
    }

    // @alku varasto
    public static Palvelin kaynnista(Map<String, Integer> saldot) {
        return Palvelin.kaynnista(vaihto -> {
            String tuote = vaihto.getRequestURI().getPath()
                .substring("/saldo/".length());
            Integer saldo = saldot.get(tuote);
            if (saldo == null) {
                Palvelin.vastaa(vaihto, 404, """
                    {"title": "Tuntematon tuote", "status": 404}""");
            } else {
                Palvelin.vastaa(vaihto, 200, """
                    {"tuote": "%s", "saldo": %d}""".formatted(tuote, saldo));
            }
        });
    }
    // @loppu varasto
}
