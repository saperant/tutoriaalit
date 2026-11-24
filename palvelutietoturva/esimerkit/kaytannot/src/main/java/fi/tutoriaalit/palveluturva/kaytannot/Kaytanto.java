package fi.tutoriaalit.palveluturva.kaytannot;

import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Map;
import tools.jackson.databind.json.JsonMapper;

/**
 * Pääsynhallintakäytäntö: lista lausekkeita. Muoto muistuttaa pilvien
 * IAM-käytäntöjä: vaikutus, toiminnot, resurssit ja ehdot.
 */
public record Kaytanto(String nimi, List<Lauseke> lausekkeet) {

    // @alku lauseke
    public enum Vaikutus { SALLI, ESTA }

    /**
     * @param toiminnot esim. "tilaukset:Lue" tai "tilaukset:*"
     * @param resurssit esim. "krn:kauppa:tilaukset/*"; muuttuja
     *                  ${asiakas} korvataan pyynnön kontekstista
     * @param ehdot     kontekstin avaimet ja vaaditut arvot
     */
    public record Lauseke(String tunnus, Vaikutus vaikutus,
                          List<String> toiminnot, List<String> resurssit,
                          Map<String, String> ehdot) {
        public Lauseke {
            ehdot = ehdot == null ? Map.of() : Map.copyOf(ehdot);
        }
    }
    // @loppu lauseke

    private static final JsonMapper JSON = JsonMapper.builder().build();

    public static Kaytanto lue(String nimi, InputStream json)
            throws IOException {
        Lauseke[] lausekkeet = JSON.readerFor(Lauseke[].class)
                .at("/lausekkeet").readValue(json);
        return new Kaytanto(nimi, List.of(lausekkeet));
    }
}
