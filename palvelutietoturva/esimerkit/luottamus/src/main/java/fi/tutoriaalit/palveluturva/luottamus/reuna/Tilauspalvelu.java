package fi.tutoriaalit.palveluturva.luottamus.reuna;

import java.util.Optional;

/**
 * Yhdyskäytävän takana oleva palvelu. Se luottaa X-Kayttaja-otsakkeeseen
 * vain, jos pyynnön toi yhdyskäytävä: kutsujan identiteetti tulee
 * mTLS-yhteydestä (ks. Palvelin.mtls), ei pyynnöstä.
 */
public final class Tilauspalvelu {

    private final String yhdyskaytava;

    public Tilauspalvelu(String yhdyskaytavanTunniste) {
        this.yhdyskaytava = yhdyskaytavanTunniste;
    }

    // @alku ohitus
    /** HAAVOITTUVA: olettaa, että kaikki tulevat yhdyskäytävän kautta. */
    public String kayttajaHaavoittuva(Yhdyskaytava.Pyynto p) {
        return p.otsakkeet().get("X-Kayttaja");
    }

    /** KORJATTU: otsake kelpaa vain yhdyskäytävän tuomana. */
    public Optional<String> kayttaja(Optional<String> kutsuja,
                                     Yhdyskaytava.Pyynto p) {
        if (kutsuja.filter(yhdyskaytava::equals).isEmpty()) {
            return Optional.empty();
        }
        return Optional.ofNullable(p.otsakkeet().get("X-Kayttaja"));
    }
    // @loppu ohitus
}
