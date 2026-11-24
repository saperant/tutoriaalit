package fi.tutoriaalit.palveluturva.palvelu;

import fi.tutoriaalit.palveluturva.havainnointi.Auditointiloki;
import fi.tutoriaalit.palveluturva.luottamus.Identiteetti;
import java.security.KeyPairGenerator;
import java.security.NoSuchAlgorithmException;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.config.annotation.method.configuration.*;
import org.springframework.security.config.annotation.web.builders.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableMethodSecurity
class Turvallisuus {

    // @alku ketju
    @Bean
    SecurityFilterChain ketju(HttpSecurity http, UserDetailsService
            palvelut) throws Exception {
        return http
                .x509(x -> x
                        // Kutsuja on varmenteen SAN-kentän SPIFFE-
                        // tunniste, ei CN eikä mikään otsake.
                        .x509PrincipalExtractor(v -> Identiteetti
                                .spiffeId(v).orElseThrow(() ->
                                new BadCredentialsException("ei SPIFFE")))
                        .userDetailsService(palvelut))
                .authorizeHttpRequests(a -> a.anyRequest().authenticated())
                .csrf(c -> c.disable()) // palvelujen välinen API: ei
                .build();               // selainta eikä evästeitä
    }

    /** Tuntematonkin, mutta luotetun varmentajan myöntämä palvelu
     *  todennetaan; oikeuksia sillä ei ole. */
    @Bean
    UserDetailsService palvelut(Luvat luvat) {
        return spiffeId -> User.withUsername(spiffeId).password("")
                .authorities(luvat.oikeudet(spiffeId).stream()
                        .map(SimpleGrantedAuthority::new).toList())
                .build();
    }
    // @loppu ketju

    @Bean
    Auditointiloki auditointiloki() throws NoSuchAlgorithmException {
        // Esimerkissä allekirjoitusavain luodaan käynnistyksessä; oikeasti
        // se on KMS:ssä, johon palvelulla on vain allekirjoitusoikeus.
        return new Auditointiloki(new Auditointiloki.Allekirjoittaja(
                KeyPairGenerator.getInstance("Ed25519").generateKeyPair()),
                100);
    }
}
