package fi.tutoriaalit.palveluturva.luottamus;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.PublicKey;
import java.security.Signature;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.util.Base64;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;
import tools.jackson.core.type.TypeReference;
import tools.jackson.databind.json.JsonMapper;

/**
 * Allekirjoitetut tokenit (JWS, ES256) palvelujen väliseen käyttöön.
 * Opetustoteutus: tuotannossa käytä kirjastoa (Nimbus JOSE, jose4j) ja
 * tarkista samat asiat.
 */
public final class Tokenit {

    private static final JsonMapper JSON = JsonMapper.builder().build();
    private static final Base64.Encoder B64 =
            Base64.getUrlEncoder().withoutPadding();

    /** Tokenin väitteet tarkistuksen jälkeen. */
    public record Vaitteet(String myontaja, String kohde, String yleiso,
                           Set<String> oikeudet, String toimija,
                           Instant vanhenee) {}

    /** Hylkäyksen syy. */
    public static final class Hylatty extends Exception {
        public Hylatty(String syy) {
            super(syy);
        }
    }

    // @alku myontaja
    /** Myöntää tokeneita omalla avaimellaan. */
    public static final class Myontaja {
        private final String nimi;
        private final KeyPair avaimet;
        private final Clock kello;

        public Myontaja(String nimi, Clock kello) {
            this.nimi = nimi;
            this.kello = kello;
            try {
                KeyPairGenerator g = KeyPairGenerator.getInstance("EC");
                g.initialize(256);
                this.avaimet = g.generateKeyPair();
            } catch (GeneralSecurityException e) {
                throw new IllegalStateException(e);
            }
        }

        public String nimi() {
            return nimi;
        }

        public PublicKey julkinen() {
            return avaimet.getPublic();
        }

        public String myonna(String kohde, String yleiso,
                             Set<String> oikeudet, Duration elinika,
                             String toimija) {
            Instant nyt = kello.instant();
            Map<String, Object> v = new LinkedHashMap<>();
            v.put("iss", nimi);
            v.put("sub", kohde);
            v.put("aud", yleiso);
            v.put("scope", String.join(" ", new TreeSet<>(oikeudet)));
            v.put("iat", nyt.getEpochSecond());
            v.put("exp", nyt.plus(elinika).getEpochSecond());
            if (toimija != null) {
                v.put("act", Map.of("sub", toimija)); // RFC 8693
            }
            String otsake = b64(Map.of("alg", "ES256", "typ", "JWT"));
            String sisalto = otsake + "." + b64(v);
            return sisalto + "." + B64.encodeToString(
                    allekirjoitus(sisalto));
        }

        private byte[] allekirjoitus(String sisalto) {
            try {
                var s = Signature.getInstance("SHA256withECDSAinP1363Format");
                s.initSign(avaimet.getPrivate());
                s.update(sisalto.getBytes(StandardCharsets.US_ASCII));
                return s.sign();
            } catch (GeneralSecurityException e) {
                throw new IllegalStateException(e);
            }
        }
    }
    // @loppu myontaja

    // @alku tarkistaja
    /**
     * Tarkistaa tokenin: algoritmi on kiinnitetty, myöntäjä ja avain
     * tunnetaan, allekirjoitus täsmää, token ei ole vanhentunut ja se
     * on myönnetty juuri tälle palvelulle (aud).
     */
    public static final class Tarkistaja {
        private final Map<String, PublicKey> myontajat;
        private final String omaYleiso;
        private final Clock kello;

        public Tarkistaja(Map<String, PublicKey> myontajat,
                          String omaYleiso, Clock kello) {
            this.myontajat = Map.copyOf(myontajat);
            this.omaYleiso = omaYleiso;
            this.kello = kello;
        }

        public Vaitteet tarkista(String token) throws Hylatty {
            Map<String, Object> v = tarkistaAllekirjoitus(token);
            if (!omaYleiso.equals(v.get("aud"))) {
                throw new Hylatty("väärä yleisö: " + v.get("aud"));
            }
            Instant exp = Instant.ofEpochSecond(
                    ((Number) v.get("exp")).longValue());
            if (!kello.instant().isBefore(exp)) {
                throw new Hylatty("vanhentunut");
            }
            return vaitteet(v, exp);
        }

        /** HAAVOITTUVA: tarkistaa vain allekirjoituksen. */
        public Vaitteet tarkistaVainAllekirjoitus(String token)
                throws Hylatty {
            Map<String, Object> v = tarkistaAllekirjoitus(token);
            return vaitteet(v, Instant.ofEpochSecond(
                    ((Number) v.get("exp")).longValue()));
        }

        private Map<String, Object> tarkistaAllekirjoitus(String token)
                throws Hylatty {
            String[] osat = token.split("\\.");
            if (osat.length != 3) {
                throw new Hylatty("muoto");
            }
            Map<String, Object> otsake = lue(osat[0]);
            if (!"ES256".equals(otsake.get("alg"))) { // ei "none"
                throw new Hylatty("algoritmi: " + otsake.get("alg"));
            }
            Map<String, Object> v = lue(osat[1]);
            PublicKey avain = myontajat.get(String.valueOf(v.get("iss")));
            if (avain == null) {
                throw new Hylatty("tuntematon myöntäjä: " + v.get("iss"));
            }
            try {
                var s = Signature.getInstance("SHA256withECDSAinP1363Format");
                s.initVerify(avain);
                s.update((osat[0] + "." + osat[1])
                        .getBytes(StandardCharsets.US_ASCII));
                if (!s.verify(Base64.getUrlDecoder().decode(osat[2]))) {
                    throw new Hylatty("allekirjoitus");
                }
            } catch (GeneralSecurityException | IllegalArgumentException e) {
                throw new Hylatty("allekirjoitus");
            }
            return v;
        }
    }
    // @loppu tarkistaja

    @SuppressWarnings("unchecked")
    private static Vaitteet vaitteet(Map<String, Object> v, Instant exp) {
        String scope = String.valueOf(v.getOrDefault("scope", ""));
        Set<String> oikeudet = scope.isBlank() ? Set.of()
                : Set.copyOf(List.of(scope.split(" ")));
        Object act = v.get("act");
        String toimija = act instanceof Map<?, ?> m
                ? String.valueOf(((Map<String, Object>) m).get("sub"))
                : null;
        return new Vaitteet(String.valueOf(v.get("iss")),
                String.valueOf(v.get("sub")), String.valueOf(v.get("aud")),
                oikeudet, toimija, exp);
    }

    private static String b64(Object arvo) {
        return B64.encodeToString(JSON.writeValueAsBytes(arvo));
    }

    private static Map<String, Object> lue(String osa) throws Hylatty {
        try {
            return JSON.readValue(Base64.getUrlDecoder().decode(osa),
                    new TypeReference<Map<String, Object>>() {});
        } catch (RuntimeException e) {
            throw new Hylatty("muoto");
        }
    }

    private Tokenit() {}
}
