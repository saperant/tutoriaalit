package fi.tutoriaalit.palveluturva.palvelu;

import java.util.Map;
import java.util.Set;
import org.springframework.boot.context.properties.ConfigurationProperties;

/** Mitä oikeuksia kullakin palvelulla on (application.yaml). */
@ConfigurationProperties("palvelu")
public record Luvat(Map<String, Set<String>> luvat) {
    public Set<String> oikeudet(String spiffeId) {
        return luvat.getOrDefault(spiffeId, Set.of());
    }
}
