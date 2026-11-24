package fi.tutoriaalit.palvelut.viestit;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * Viisi "palvelua" (myynti, varasto, maksut, toimitus, laskutus), jotka
 * keskustelevat vain viestinvälittäjän kautta. Esimerkin vuoksi ne
 * ajetaan samassa prosessissa ja samassa tietokannassa, mutta jokaisella
 * on oma skeemansa eikä yksikään kutsu toisen koodia.
 */
@SpringBootApplication
@EnableScheduling
public class ViestiSovellus {
    public static void main(String[] args) {
        SpringApplication.run(ViestiSovellus.class, args);
    }
}
