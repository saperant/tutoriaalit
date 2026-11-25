package fi.tutoriaalit.kauppa.turva;

import java.security.interfaces.RSAPublicKey;
import java.util.List;
import org.springframework.security.oauth2.core.*;
import org.springframework.security.oauth2.jose.jws.SignatureAlgorithm;
import org.springframework.security.oauth2.jwt.JwtClaimValidator;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.*;

/** JWT-tokenin tarkistus resurssipalvelimessa. */
public final class Tokenit {

    private Tokenit() {
    }

    // @alku tarkistin
    /**
     * Hyväksyy vain tokenin, jonka myöntäjä on allekirjoittanut
     * RS256-algoritmilla, joka on voimassa ja joka on tarkoitettu
     * tälle palvelulle.
     */
    public static JwtDecoder tarkistin(RSAPublicKey myontajanAvain,
                                       String myontaja, String yleiso) {
        var tarkistin = NimbusJwtDecoder.withPublicKey(myontajanAvain)
                .signatureAlgorithm(SignatureAlgorithm.RS256)
                .build();
        tarkistin.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
                // exp ja nbf (minuutin kellopoikkeama sallitaan) sekä iss
                JwtValidators.createDefaultWithIssuer(myontaja),
                new JwtClaimValidator<List<String>>("aud", yleisot ->
                        yleisot != null && yleisot.contains(yleiso))));
        return tarkistin;
    }
    // @loppu tarkistin

    // @alku roolit
    /** Tokenin väite "roolit" Spring Securityn rooleiksi (ROLE_...). */
    public static JwtAuthenticationConverter roolit() {
        var oikeudet = new JwtGrantedAuthoritiesConverter();
        oikeudet.setAuthoritiesClaimName("roolit");
        oikeudet.setAuthorityPrefix("ROLE_");
        var muunnin = new JwtAuthenticationConverter();
        muunnin.setJwtGrantedAuthoritiesConverter(oikeudet);
        return muunnin;
    }
    // @loppu roolit
}
