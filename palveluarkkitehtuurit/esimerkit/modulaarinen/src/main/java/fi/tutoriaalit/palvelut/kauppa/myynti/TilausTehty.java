package fi.tutoriaalit.palvelut.kauppa.myynti;

/** Myynnin julkaisema tapahtuma: tilaus on tehty. */
public record TilausTehty(long tilausId, String asiakas, String tuote,
                          int maara) {
}
