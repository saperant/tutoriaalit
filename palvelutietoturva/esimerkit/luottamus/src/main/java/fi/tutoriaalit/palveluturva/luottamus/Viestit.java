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
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/**
 * Viestinvälityksen suojaus: tuottaja allekirjoittaa viestin kuoren, ja
 * kuluttaja tarkistaa tuottajan, aiheen, allekirjoituksen, iän ja
 * toiston. Välitin on välikäsi, jonka ei tarvitse olla luotettu.
 *
 * <p>Opetustoteutus: tuotannossa kuori on esimerkiksi JWS tai
 * CloudEvents-viesti allekirjoituksineen.
 */
public final class Viestit {

    private Viestit() {}

    // @alku kuori
    /** Viesti ja sen kuori. Allekirjoitus kattaa kaikki muut kentät. */
    public record Kuori(String aihe, String tuottaja, String id,
                        Instant aika, String runko, byte[] allekirjoitus) {

        byte[] allekirjoitettava() {
            // Kentät erotetaan rivinvaihdolla, jota tunnisteissa ei
            // sallita: kenttien rajaa ei voi siirtää.
            return String.join("\n", aihe, tuottaja, id, aika.toString(),
                    runko).getBytes(StandardCharsets.UTF_8);
        }
    }
    // @loppu kuori

    /** Viestin tuottaja: palvelu, jolla on oma allekirjoitusavain. */
    public static final class Tuottaja {
        private final String tunniste;
        private final KeyPair avain;
        private final Clock kello;
        private int seuraava = 1;

        public Tuottaja(String tunniste, Clock kello) {
            this.tunniste = tunniste;
            this.kello = kello;
            try {
                this.avain = KeyPairGenerator.getInstance("Ed25519")
                        .generateKeyPair();
            } catch (GeneralSecurityException e) {
                throw new IllegalStateException(e);
            }
        }

        public String tunniste() {
            return tunniste;
        }

        public PublicKey julkinen() {
            return avain.getPublic();
        }

        public Kuori laheta(String aihe, String runko) {
            var kuori = new Kuori(aihe, tunniste,
                    tunniste + "#" + seuraava++, kello.instant(), runko,
                    new byte[0]);
            try {
                Signature s = Signature.getInstance("Ed25519");
                s.initSign(avain.getPrivate());
                s.update(kuori.allekirjoitettava());
                return new Kuori(kuori.aihe(), kuori.tuottaja(), kuori.id(),
                        kuori.aika(), kuori.runko(), s.sign());
            } catch (GeneralSecurityException e) {
                throw new IllegalStateException(e);
            }
        }
    }

    /** Hylkäyksen syy. */
    public static final class Hylatty extends Exception {
        public Hylatty(String syy) {
            super(syy);
        }
    }

    // @alku kuluttaja
    /** Kuluttaja tarkistaa jokaisen viestin itse. */
    public static final class Kuluttaja {
        private final Map<String, PublicKey> avaimet;
        private final Map<String, Set<String>> tuottajatAiheittain;
        private final Clock kello;
        private final Duration enimmaisika;
        private final Set<String> nahdyt = new HashSet<>();

        public Kuluttaja(Map<String, PublicKey> avaimet,
                         Map<String, Set<String>> tuottajatAiheittain,
                         Clock kello, Duration enimmaisika) {
            this.avaimet = Map.copyOf(avaimet);
            this.tuottajatAiheittain = Map.copyOf(tuottajatAiheittain);
            this.kello = kello;
            this.enimmaisika = enimmaisika;
        }

        public synchronized String vastaanota(Kuori k) throws Hylatty {
            // 1. Saako tämä tuottaja julkaista tähän aiheeseen?
            if (!tuottajatAiheittain.getOrDefault(k.aihe(), Set.of())
                    .contains(k.tuottaja())) {
                throw new Hylatty("tuottaja ei saa julkaista aiheeseen");
            }
            // 2. Onko viesti tuottajan allekirjoittama ja muuttamaton?
            PublicKey avain = avaimet.get(k.tuottaja());
            try {
                Signature s = Signature.getInstance("Ed25519");
                s.initVerify(avain);
                s.update(k.allekirjoitettava());
                if (!s.verify(k.allekirjoitus())) {
                    throw new Hylatty("allekirjoitus ei täsmää");
                }
            } catch (GeneralSecurityException e) {
                throw new Hylatty("allekirjoitus ei täsmää");
            }
            // 3. Onko viesti tuore ja ensimmäistä kertaa nähty?
            if (k.aika().plus(enimmaisika).isBefore(kello.instant())) {
                throw new Hylatty("liian vanha");
            }
            if (!nahdyt.add(k.id())) {
                throw new Hylatty("jo käsitelty");
            }
            return k.runko();
        }
    }
    // @loppu kuluttaja
}
