package fi.tutoriaalit.palvelut.uudistus.uusi;

import java.time.LocalDate;

/** Uuden järjestelmän malli: omat käsitteet, ei vanhan koodeja. */
public record Asiakas(String id, String etunimi, String sukunimi,
                      Tila tila, LocalDate asiakkaanaAlkaen) {
    public enum Tila { AKTIIVINEN, PASSIIVINEN, ESTETTY }

    public String json() {
        return """
            {"id": "%s", "etunimi": "%s", "sukunimi": "%s", \
            "tila": "%s", "asiakkaanaAlkaen": "%s"}"""
            .formatted(id, etunimi, sukunimi, tila, asiakkaanaAlkaen);
    }
}
