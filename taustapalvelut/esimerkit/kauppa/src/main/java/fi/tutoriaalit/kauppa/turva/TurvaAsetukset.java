package fi.tutoriaalit.kauppa.turva;

import fi.tutoriaalit.kauppa.KauppaAsetukset;
import java.util.List;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.*;
import org.springframework.security.config.annotation.web.builders.*;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.*;
import org.springframework.security.crypto.factory.PasswordEncoderFactories;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/** Todennus ja valtuutus. (Pitkät tuonnit tähtimuodossa PDF:n takia.) */
@Configuration
@EnableMethodSecurity      // @PreAuthorize ja @PostAuthorize käyttöön
public class TurvaAsetukset {

    // @alku ketju
    @Bean
    SecurityFilterChain turvaketju(HttpSecurity http) throws Exception {
        http.authorizeHttpRequests(polku -> polku
                .requestMatchers("/actuator/health").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/v1/tuotteet/**")
                        .permitAll()
                .requestMatchers(HttpMethod.POST, "/api/v1/tuotteet")
                        .hasRole("YLLAPITAJA")
                .requestMatchers("/api/v1/raportit/**", "/actuator/**")
                        .hasRole("YLLAPITAJA")
                .anyRequest().authenticated())
            // Tilaton rajapinta: tunnistetiedot jokaisessa pyynnössä,
            // ei istuntoevästettä. Siksi CSRF-suojaa ei tarvita.
            .httpBasic(Customizer.withDefaults())
            .sessionManagement(istunto -> istunto
                    .sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .csrf(csrf -> csrf.disable())
            .cors(Customizer.withDefaults());
        return http.build();
    }
    // @loppu ketju

    // @alku salasanat
    /**
     * Delegoiva kooderi tallentaa algoritmin tiivisteen eteen, esim.
     * {bcrypt}$2a$10$...; algoritmin voi vaihtaa vanhoja rikkomatta.
     */
    @Bean
    PasswordEncoder salasanat() {
        return PasswordEncoderFactories.createDelegatingPasswordEncoder();
    }

    @Bean
    UserDetailsService kayttajat(JdbcClient jdbc) {
        return tunnus -> jdbc.sql("""
                SELECT tunnus, salasana, rooli FROM kayttaja
                 WHERE tunnus = :tunnus
                """)
                .param("tunnus", tunnus)
                .query((rivi, n) -> User.withUsername(rivi.getString(1))
                        .password(rivi.getString(2))
                        .roles(rivi.getString(3))
                        .build())
                .optional()
                .orElseThrow(() -> new UsernameNotFoundException(tunnus));
    }
    // @loppu salasanat

    // @alku cors
    /** Selainsovellukset, jotka saavat kutsua rajapintaa toisesta
     *  alkuperästä (origin). Lista tulee asetuksista. Ketjun cors()
     *  etsii pavun juuri nimellä corsConfigurationSource. */
    @Bean
    CorsConfigurationSource corsConfigurationSource(
            KauppaAsetukset asetukset) {
        var c = new CorsConfiguration();
        c.setAllowedOrigins(asetukset.sallitutAlkuperat());
        c.setAllowedMethods(List.of("GET", "POST", "PUT"));
        c.setAllowedHeaders(List.of("Authorization", "Content-Type",
                "If-Match", "Idempotency-Key"));
        c.setExposedHeaders(List.of("ETag", "Location"));
        var lahde = new UrlBasedCorsConfigurationSource();
        lahde.registerCorsConfiguration("/api/**", c);
        return lahde;
    }
    // @loppu cors
}
