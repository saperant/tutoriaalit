package fi.tutoriaalit.kauppa;

import java.time.Clock;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.*;
import org.springframework.context.annotation.Bean;

// @alku sovellus
/**
 * Verkkokaupan taustapalvelu. {@code @SpringBootApplication} käynnistää
 * komponenttihaun tästä paketista alaspäin ja automaattisen
 * konfiguroinnin luokkapolun kirjastojen perusteella.
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class KauppaSovellus {

    public static void main(String[] args) {
        SpringApplication.run(KauppaSovellus.class, args);
    }

    /** Kello on riippuvuus: testi voi antaa kiinteän ajan. */
    @Bean
    Clock kello() {
        return Clock.systemUTC();
    }
}
// @loppu sovellus
