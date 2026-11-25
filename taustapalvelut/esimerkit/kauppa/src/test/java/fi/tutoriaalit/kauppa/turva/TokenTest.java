package fi.tutoriaalit.kauppa.turva;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.nimbusds.jose.JWSAlgorithm;
import com.nimbusds.jose.JWSHeader;
import com.nimbusds.jose.JWSSigner;
import com.nimbusds.jose.crypto.MACSigner;
import com.nimbusds.jose.crypto.RSASSASigner;
import com.nimbusds.jwt.JWTClaimsSet;
import com.nimbusds.jwt.PlainJWT;
import com.nimbusds.jwt.SignedJWT;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.interfaces.RSAPublicKey;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.List;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.oauth2.jwt.BadJwtException;
import org.springframework.security.oauth2.jwt.JwtDecoder;

/** Tokenin tarkistus ilman tunnistuspalvelua: testi myöntää tokenit. */
class TokenTest {

    private static final String MYONTAJA = "https://tunnistus.example";
    private static final KeyPair AVAIN = avainpari();
    private static final KeyPair VIERAS_AVAIN = avainpari();

    private final JwtDecoder tarkistin = Tokenit.tarkistin(
            (RSAPublicKey) AVAIN.getPublic(), MYONTAJA, "kauppa");

    // @alku kelvollinen
    @Test
    void kelvollinenTokenHyvaksytaanJaRoolitLuetaan() {
        var jwt = tarkistin.decode(token(AVAIN, vaitteet -> { }));
        var kayttaja = Tokenit.roolit().convert(jwt);

        assertThat(kayttaja.getName()).isEqualTo("aino");
        assertThat(kayttaja.getAuthorities())
                .extracting(GrantedAuthority::getAuthority)
                .contains("ROLE_ASIAKAS");
    }
    // @loppu kelvollinen

    // @alku hylatyt
    @Test
    void vaaraAllekirjoitusHylataan() {
        hylataan(token(VIERAS_AVAIN, vaitteet -> { }));
    }

    @Test
    void vanhentunutTokenHylataan() {
        var eilen = Instant.now().minus(Duration.ofDays(1));
        hylataan(token(AVAIN, v -> v.expirationTime(Date.from(eilen))));
    }

    @Test
    void toisellePalvelulleMyonnettyTokenHylataan() {
        hylataan(token(AVAIN, v -> v.audience("laskutus")));
    }

    @Test
    void vieraanMyontajanTokenHylataan() {
        hylataan(token(AVAIN, v -> v.issuer("https://muu.example")));
    }

    @Test
    void allekirjoittamatonTokenHylataan() {          // "alg": "none"
        hylataan(new PlainJWT(vaitteet(v -> { })).serialize());
    }

    @Test
    void julkisellaAvaimellaTehtyHmacHylataan() throws Exception {
        // Algoritmin vaihto: hyökkääjä tuntee julkisen avaimen ja
        // käyttää sitä symmetrisen HS256-allekirjoituksen salaisuutena.
        var salaisuus = new MACSigner(AVAIN.getPublic().getEncoded());
        hylataan(allekirjoita(JWSAlgorithm.HS256, salaisuus, v -> { }));
    }

    private void hylataan(String token) {
        assertThatThrownBy(() -> tarkistin.decode(token))
                .isInstanceOf(BadJwtException.class);
    }
    // @loppu hylatyt

    /** Tunnistuspalvelun osuus: token, jonka väitteitä voi muuttaa. */
    private static String token(KeyPair avain,
                                Consumer<JWTClaimsSet.Builder> muutos) {
        try {
            return allekirjoita(JWSAlgorithm.RS256,
                    new RSASSASigner(avain.getPrivate()), muutos);
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    private static String allekirjoita(JWSAlgorithm algoritmi,
            JWSSigner allekirjoittaja,
            Consumer<JWTClaimsSet.Builder> muutos) throws Exception {
        var jwt = new SignedJWT(new JWSHeader(algoritmi), vaitteet(muutos));
        jwt.sign(allekirjoittaja);
        return jwt.serialize();
    }

    private static JWTClaimsSet vaitteet(
            Consumer<JWTClaimsSet.Builder> muutos) {
        var nyt = Instant.now();
        var vaitteet = new JWTClaimsSet.Builder()
                .issuer(MYONTAJA)
                .subject("aino")
                .audience("kauppa")
                .issueTime(Date.from(nyt))
                .expirationTime(Date.from(nyt.plus(Duration.ofMinutes(5))))
                .claim("roolit", List.of("ASIAKAS"));
        muutos.accept(vaitteet);
        return vaitteet.build();
    }

    private static KeyPair avainpari() {
        try {
            var generaattori = KeyPairGenerator.getInstance("RSA");
            generaattori.initialize(2048);
            return generaattori.generateKeyPair();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }
}
