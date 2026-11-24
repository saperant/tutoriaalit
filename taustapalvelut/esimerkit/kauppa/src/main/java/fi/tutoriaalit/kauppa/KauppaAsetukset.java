package fi.tutoriaalit.kauppa;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotEmpty;
import java.util.List;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.validation.annotation.Validated;

// @alku asetukset
/**
 * Sovelluksen omat asetukset tyypitettyinä. Arvot tulevat tiedostosta
 * application.yaml, ympäristömuuttujista (KAUPPA_MAKSIMIRIVIT) tai
 * komentoriviltä. Virheellinen arvo kaataa käynnistyksen heti.
 *
 * @param maksimirivit tilauksen rivien enimmäismäärä
 * @param sivunEnimmaiskoko listausten suurin sallittu sivukoko
 * @param sallitutAlkuperat selainsovellukset, joille CORS sallitaan
 */
@Validated
@ConfigurationProperties("kauppa")
public record KauppaAsetukset(
        @Min(1) @Max(100) int maksimirivit,
        @Min(1) @Max(500) int sivunEnimmaiskoko,
        @NotEmpty List<String> sallitutAlkuperat) {
}
// @loppu asetukset
