package fi.tutoriaalit.palvelut.etakutsut.myynti;

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import java.time.Duration;

/** Katkaisijan asetukset varastokutsuille. */
public final class Katkaisijat {
    private Katkaisijat() {
    }

    // @alku katkaisija
    public static CircuitBreaker varastolle(Duration avoinna) {
        var asetukset = CircuitBreakerConfig.custom()
            .slidingWindowSize(4)          // neljä viimeisintä kutsua
            .minimumNumberOfCalls(4)
            .failureRateThreshold(50)      // puolet epäonnistui: auki
            .waitDurationInOpenState(avoinna)
            .permittedNumberOfCallsInHalfOpenState(1)
            .ignoreExceptions(TuntematonTuote.class) // ei vika
            .build();
        return CircuitBreaker.of("varasto", asetukset);
    }
    // @loppu katkaisija
}
