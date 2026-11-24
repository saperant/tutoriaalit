package fi.tutoriaalit.kauppa.tuote;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verifyNoInteractions;

import fi.tutoriaalit.kauppa.KauppaAsetukset;
import fi.tutoriaalit.kauppa.turva.TurvaAsetukset;
import fi.tutoriaalit.kauppa.virheet.EiLoydy;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.dao.OptimisticLockingFailureException;
import org.springframework.http.MediaType;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.assertj.MockMvcTester;

// @alku viipale
/**
 * Web-viipale: ohjain, JSON-muunnos, validointi, virheiden käsittely ja
 * turvaketju, mutta ei palvelua eikä tietokantaa. Palvelu korvataan
 * Mockito-valeoliolla, joten testi on nopea ja kohdistettu.
 */
@WebMvcTest(TuoteOhjain.class)
@Import({TurvaAsetukset.class, TuoteOhjainTest.Asetukset.class})
class TuoteOhjainTest {

    @TestConfiguration
    static class Asetukset {
        @Bean
        KauppaAsetukset kauppaAsetukset() {
            return new KauppaAsetukset(20, 100,
                    List.of("http://localhost:5173"));
        }
    }

    @Autowired
    MockMvcTester mvc;

    @MockitoBean
    TuotePalvelu palvelu;

    @MockitoBean
    JdbcClient jdbc;            // käyttäjähaku; @WithMockUser ohittaa sen

    private static final Tuote TEE =
            new Tuote(2L, "Vihreä tee", 590, 50, 3L);
    // @loppu viipale

    // @alku etag
    @Test
    void hakuPalauttaaEtaginJaKunnioittaaIfNoneMatchia() {
        given(palvelu.hae(2)).willReturn(TEE);

        assertThat(mvc.get().uri("/api/v1/tuotteet/2"))
                .hasStatusOk()
                .hasHeader("ETag", "\"3\"")
                .bodyJson().extractingPath("$.nimi").isEqualTo("Vihreä tee");

        assertThat(mvc.get().uri("/api/v1/tuotteet/2")
                .header("If-None-Match", "\"3\""))
                .hasStatus(304);
    }
    // @loppu etag

    // @alku validointi
    @Test
    @WithMockUser(roles = "YLLAPITAJA")
    void virheellinenRunkoHylataanEnnenPalvelua() {
        assertThat(mvc.post().uri("/api/v1/tuotteet")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                        {"nimi": " ", "hintaSentteina": -5, "saldo": 1}
                        """))
                .hasStatus(400)
                .hasContentType(MediaType.APPLICATION_PROBLEM_JSON)
                .bodyJson()
                .extractingPath("$.virheet[*].kentta")
                .asArray().containsExactly("hintaSentteina", "nimi");
        verifyNoInteractions(palvelu);
    }

    @Test
    void kyselyparametritkinValidoidaan() {
        assertThat(mvc.get().uri("/api/v1/tuotteet?sivu=-1"))
                .hasStatus(400)
                .hasContentType(MediaType.APPLICATION_PROBLEM_JSON);
        verifyNoInteractions(palvelu);
    }
    // @loppu validointi

    // @alku valtuutus
    @Test
    void lisaysVaatiiTunnistautumisenJaRoolin() {
        String runko = """
                {"nimi": "Tee", "hintaSentteina": 500, "saldo": 1}
                """;
        assertThat(mvc.post().uri("/api/v1/tuotteet")
                .contentType(MediaType.APPLICATION_JSON).content(runko))
                .hasStatus(401);                       // kuka olet?
    }

    @Test
    @WithMockUser(roles = "ASIAKAS")
    void asiakasEiSaaLisataTuotteita() {
        assertThat(mvc.post().uri("/api/v1/tuotteet")
                .contentType(MediaType.APPLICATION_JSON)
                .content("{\"nimi\": \"Tee\", \"hintaSentteina\": 1}"))
                .hasStatus(403);                       // et saa
    }
    // @loppu valtuutus

    // @alku ehdollinen
    @Test
    @WithMockUser(roles = "YLLAPITAJA")
    void hinnanMuutosVaatiiVersionJaHylkaaVanhan() {
        String runko = "{\"hintaSentteina\": 650}";
        assertThat(mvc.put().uri("/api/v1/tuotteet/2/hinta")
                .contentType(MediaType.APPLICATION_JSON).content(runko))
                .hasStatus(428);              // Precondition Required

        given(palvelu.muutaHinta(2, 2, 650)).willThrow(
                new OptimisticLockingFailureException("versio muuttui"));
        assertThat(mvc.put().uri("/api/v1/tuotteet/2/hinta")
                .header("If-Match", "\"2\"")
                .contentType(MediaType.APPLICATION_JSON).content(runko))
                .hasStatus(412)
                .bodyJson().extractingPath("$.type")
                .isEqualTo("https://kauppa.example/ongelmat/versio");
    }
    // @loppu ehdollinen

    // @alku puuttuu
    @Test
    void puuttuvaTuoteOn404() {
        given(palvelu.hae(anyLong())).willThrow(new EiLoydy("tuote", 99));
        assertThat(mvc.get().uri("/api/v1/tuotteet/99"))
                .hasStatus(404)
                .hasContentType(MediaType.APPLICATION_PROBLEM_JSON)
                .bodyJson()
                .hasPathSatisfying("$.type", t -> assertThat(t).isEqualTo(
                        "https://kauppa.example/ongelmat/ei-loydy"))
                .hasPathSatisfying("$.detail", d -> assertThat(d)
                        .isEqualTo("tuote 99 ei löydy"));
    }
    // @loppu puuttuu
}
