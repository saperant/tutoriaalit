package fi.tutoriaalit.palveluturva.kaytannot;

import java.util.ArrayList;
import java.util.List;

/**
 * Käytäntöjen staattinen tarkastus CI:ssä (politiikat koodina).
 * Hylkää liian laajat sallivat lausekkeet ennen kuin ne päätyvät
 * tuotantoon.
 */
public final class Tarkastus {

    // @alku tarkastus
    public static List<String> loydokset(Kaytanto k) {
        List<String> tulos = new ArrayList<>();
        for (Kaytanto.Lauseke l : k.lausekkeet()) {
            if (l.vaikutus() != Kaytanto.Vaikutus.SALLI) {
                continue;
            }
            String kohde = k.nimi() + "/" + l.tunnus() + ": ";
            if (l.toiminnot().stream().anyMatch(t -> t.endsWith(":*")
                    || t.equals("*"))) {
                tulos.add(kohde + "kaikki toiminnot (*)");
            }
            if (l.resurssit().stream().anyMatch(r -> r.equals("*"))) {
                tulos.add(kohde + "kaikki resurssit (*)");
            }
            boolean kirjoittaa = l.toiminnot().stream().anyMatch(t ->
                    t.contains(":Poista") || t.contains(":Kirjoita")
                    || t.endsWith("*"));
            if (kirjoittaa && l.ehdot().isEmpty()) {
                tulos.add(kohde + "kirjoitus ilman ehtoja");
            }
        }
        return tulos;
    }
    // @loppu tarkastus

    private Tarkastus() {}
}
