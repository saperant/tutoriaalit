package fi.tutoriaalit.palvelut.viestit.integraatio;

import java.util.HashMap;
import java.util.Map;

/** Integraatiomallien viesti: otsakkeet ja runko (EIP: Message). */
public record Sanoma(Map<String, String> otsakkeet, String runko) {
    public String otsake(String nimi) {
        return otsakkeet.get(nimi);
    }

    public Sanoma lisaa(String nimi, String arvo) {
        var uudet = new HashMap<>(otsakkeet);
        uudet.put(nimi, arvo);
        return new Sanoma(Map.copyOf(uudet), runko);
    }
}
