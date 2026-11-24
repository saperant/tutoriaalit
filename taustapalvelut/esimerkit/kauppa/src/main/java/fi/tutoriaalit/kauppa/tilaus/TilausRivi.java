package fi.tutoriaalit.kauppa.tilaus;

import org.springframework.data.relational.core.mapping.Table;

/** Tilauksen rivi; kuuluu Tilaus-aggregaattiin, ei omaa repositoriota. */
@Table("tilaus_rivi")
public record TilausRivi(long tuoteId, int maara, long hintaSentteina) {
}
