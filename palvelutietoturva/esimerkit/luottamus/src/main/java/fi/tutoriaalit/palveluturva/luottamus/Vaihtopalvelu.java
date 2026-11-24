package fi.tutoriaalit.palveluturva.luottamus;

import java.time.Duration;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

/**
 * Tokenien vaihto (RFC 8693, token exchange). Palvelu, joka kutsuu
 * toista palvelua käyttäjän puolesta, ei välitä käyttäjän tokenia
 * sellaisenaan. Se pyytää vaihtopalvelulta uuden tokenin, joka on
 * myönnetty vain kohdepalvelulle, sisältää vain tarvittavat oikeudet,
 * kertoo välittäjän (act) ja vanhenee nopeasti.
 */
public final class Vaihtopalvelu {

    // @alku vaihto
    /** Mitä oikeuksia kukin välittäjä saa pyytää millekin kohteelle. */
    public record Lupa(String valittaja, String kohde,
                       Set<String> oikeudet) {}

    private final Tokenit.Tarkistaja kayttajatokenit;
    private final Tokenit.Myontaja myontaja;
    private final Map<String, Lupa> luvat;

    public Vaihtopalvelu(Tokenit.Tarkistaja kayttajatokenit,
                         Tokenit.Myontaja myontaja,
                         Set<Lupa> luvat) {
        this.kayttajatokenit = kayttajatokenit;
        this.myontaja = myontaja;
        this.luvat = new java.util.HashMap<>();
        luvat.forEach(l -> this.luvat.put(l.valittaja() + ">"
                + l.kohde(), l));
    }

    /**
     * @param kayttajanToken käyttäjän token, jonka yleisö on tämä
     *                       järjestelmä (esim. kauppa-api)
     * @param valittaja      pyytäjän identiteetti mTLS-yhteydestä
     */
    public String vaihda(String kayttajanToken, String valittaja,
                         String kohde, Set<String> pyydetyt)
            throws Tokenit.Hylatty {
        Tokenit.Vaitteet kayttaja =
                kayttajatokenit.tarkista(kayttajanToken);
        Lupa lupa = luvat.get(valittaja + ">" + kohde);
        if (lupa == null) {
            throw new Tokenit.Hylatty(valittaja + " ei saa kutsua "
                    + kohde + " käyttäjän puolesta");
        }
        // Leikkaus: käyttäjällä on, välittäjä saa pyytää ja pyydetään.
        Set<String> oikeudet = new TreeSet<>(pyydetyt);
        oikeudet.retainAll(kayttaja.oikeudet());
        oikeudet.retainAll(lupa.oikeudet());
        if (oikeudet.isEmpty()) {
            throw new Tokenit.Hylatty("ei yhteisiä oikeuksia");
        }
        return myontaja.myonna(kayttaja.kohde(), kohde, oikeudet,
                Duration.ofMinutes(5), valittaja);
    }
    // @loppu vaihto
}
