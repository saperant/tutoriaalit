package fi.tutoriaalit.kauppa.virheet;

import java.net.URI;
import java.util.List;
import java.util.Map;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

// @alku ongelmat
/**
 * Muuntaa sovelluksen poikkeukset RFC 9457 -muotoisiksi
 * ongelmakuvauksiksi (application/problem+json). Springin omat virheet,
 * kuten validointi ja väärä sisältötyyppi, saavat saman muodon
 * asetuksella spring.mvc.problemdetails.enabled.
 */
@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)   // ennen Springin oletuskäsittelijää
public class Ongelmat {

    private static final String TYYPIT = "https://kauppa.example/ongelmat/";

    @ExceptionHandler
    ProblemDetail eiLoydy(EiLoydy virhe) {
        return ongelma(HttpStatus.NOT_FOUND, "ei-loydy", virhe.getMessage());
    }

    @ExceptionHandler
    ProblemDetail saldo(SaldoEiRiita virhe) {
        ProblemDetail p = ongelma(HttpStatus.CONFLICT, "saldo",
                virhe.getMessage());
        p.setProperty("tuote", virhe.tuoteId());   // koneluettava lisätieto
        p.setProperty("pyydetty", virhe.pyydetty());
        return p;
    }

    @ExceptionHandler
    ProblemDetail virheellinen(VirheellinenPyynto virhe) {
        return ongelma(HttpStatus.BAD_REQUEST, "pyynto", virhe.getMessage());
    }

    @ExceptionHandler
    ProblemDetail versio(OptimisticLockingFailureException virhe) {
        return ongelma(HttpStatus.PRECONDITION_FAILED, "versio",
                "resurssia on muutettu; hae uusi versio");
    }

    // @alku kentat
    /** Validointivirhe kentittäin; asiakas näyttää viestit lomakkeella. */
    @ExceptionHandler
    ProblemDetail kentat(MethodArgumentNotValidException virhe) {
        ProblemDetail p = ongelma(HttpStatus.BAD_REQUEST, "validointi",
                "pyynnön kentät eivät kelpaa");
        List<Map<String, String>> virheet = virhe.getFieldErrors().stream()
                .map(k -> Map.of("kentta", k.getField(),
                        "syy", String.valueOf(k.getCode()),
                        "viesti", String.valueOf(k.getDefaultMessage())))
                .sorted((a, b) -> a.get("kentta").compareTo(b.get("kentta")))
                .toList();
        p.setProperty("virheet", virheet);
        return p;
    }
    // @loppu kentat

    private static ProblemDetail ongelma(HttpStatus tila, String tyyppi,
            String kuvaus) {
        ProblemDetail p = ProblemDetail.forStatusAndDetail(tila, kuvaus);
        p.setType(URI.create(TYYPIT + tyyppi));
        return p;
    }
}
// @loppu ongelmat
