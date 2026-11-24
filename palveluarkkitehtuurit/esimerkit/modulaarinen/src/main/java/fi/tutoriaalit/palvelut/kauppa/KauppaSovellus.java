package fi.tutoriaalit.palvelut.kauppa;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Modulaarinen monoliitti: yksi sovellus ja yksi tietokanta, mutta
 * kolme moduulia (myynti, varasto, laskutus), joiden rajat tarkistetaan
 * testeissä. Moduulin juuripaketti on sen julkinen rajapinta, ja
 * alipaketti {@code sisainen} on vain moduulin omaan käyttöön.
 */
@SpringBootApplication
public class KauppaSovellus {
    public static void main(String[] args) {
        SpringApplication.run(KauppaSovellus.class, args);
    }
}
