package fi.tutoriaalit.kauppa.tuote;

import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.Version;
import org.springframework.data.relational.core.mapping.Table;

// @alku tuote
/**
 * Tuote on oma aggregaattinsa. Hinta on sentteinä kokonaislukuna:
 * liukuluku ei esitä rahaa tarkasti. Versio-kenttä toteuttaa
 * optimistisen lukituksen: päivitys onnistuu vain, jos rivin versio on
 * sama kuin luettaessa.
 */
@Table("tuote")
public record Tuote(
        @Id Long id,
        String nimi,
        long hintaSentteina,
        int saldo,
        @Version Long versio) {

    public static Tuote uusi(String nimi, long hintaSentteina, int saldo) {
        return new Tuote(null, nimi, hintaSentteina, saldo, null);
    }

    public Tuote hinnalla(long uusiHinta) {
        return new Tuote(id, nimi, uusiHinta, saldo, versio);
    }

    // Spring Data asettaa tunnisteen ja version näillä "wither"-metodeilla.
    Tuote withId(Long uusiId) {
        return new Tuote(uusiId, nimi, hintaSentteina, saldo, versio);
    }

    Tuote withVersio(Long uusiVersio) {
        return new Tuote(id, nimi, hintaSentteina, saldo, uusiVersio);
    }
}
// @loppu tuote
