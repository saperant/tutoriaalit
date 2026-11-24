package fi.tutoriaalit.palveluturva.palvelu;

import fi.tutoriaalit.palveluturva.havainnointi.Auditointiloki;
import fi.tutoriaalit.palveluturva.havainnointi.Tapahtuma;
import java.security.Principal;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
class LaskuRajapinta {

    private final Auditointiloki loki;

    LaskuRajapinta(Auditointiloki loki) {
        this.loki = loki;
    }

    // @alku rajapinta
    @GetMapping("/laskut/{id}")
    @PreAuthorize("hasAuthority('laskut:luku')")
    String lue(@PathVariable long id, Principal kutsuja,
               @RequestHeader(name = "X-Korrelaatio", required = false)
               String korrelaatio) {
        kirjaa(korrelaatio, kutsuja, "laskut:Lue", id);
        return "lasku " + id + ": 120,00 €";
    }

    @DeleteMapping("/laskut/{id}")
    @PreAuthorize("hasAuthority('laskut:mitatointi')")
    String mitatoi(@PathVariable long id, Principal kutsuja,
                   @RequestHeader(name = "X-Korrelaatio", required = false)
                   String korrelaatio) {
        kirjaa(korrelaatio, kutsuja, "laskut:Mitatoi", id);
        return "lasku " + id + " mitätöity";
    }
    // @loppu rajapinta

    private void kirjaa(String korrelaatio, Principal kutsuja,
                        String toiminto, long id) {
        loki.kirjaa(new Tapahtuma(Instant.now(),
                korrelaatio != null ? korrelaatio
                        : UUID.randomUUID().toString(),
                "laskutus", kutsuja.getName(), toiminto,
                "krn:kauppa:laskut/" + id, "sallittu", Map.of()));
    }
}
