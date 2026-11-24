package fi.tutoriaalit.palveluturva.havainnointi;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.MessageDigest;
import java.security.PrivateKey;
import java.security.PublicKey;
import java.security.Signature;
import java.util.ArrayList;
import java.util.HexFormat;
import java.util.List;
import tools.jackson.databind.json.JsonMapper;

/**
 * Lisäyksiin rajoitettu auditointiloki. Rivit ketjutetaan tiivisteillä,
 * ja ketjun pää allekirjoitetaan säännöllisesti avaimella, jota lokia
 * kirjoittava palvelu ei omista. Tarkistuspisteet tallennetaan muualle
 * (toinen tili, WORM-tallennus). Pelkän tiivisteketjun voi laskea
 * uudelleen se, joka pääsee muokkaamaan lokia; allekirjoitettua
 * tarkistuspistettä ei.
 */
public final class Auditointiloki {

    // @alku tarkistuspiste
    /** Allekirjoitettu tieto: n ensimmäisen rivin ketjun pää. */
    public record Tarkistuspiste(int riveja, String paa,
                                 byte[] allekirjoitus) {}

    /** Erillinen allekirjoituspalvelu (esim. KMS:n epäsymmetrinen avain). */
    public static final class Allekirjoittaja {
        private final PrivateKey avain;
        private final PublicKey julkinen;

        public Allekirjoittaja(KeyPair avaimet) {
            this.avain = avaimet.getPrivate();
            this.julkinen = avaimet.getPublic();
        }

        public PublicKey julkinen() {
            return julkinen;
        }

        Tarkistuspiste allekirjoita(int riveja, String paa) {
            return new Tarkistuspiste(riveja, paa,
                    Auditointiloki.allekirjoita(avain, riveja, paa));
        }
    }
    // @loppu tarkistuspiste

    private static final JsonMapper JSON = JsonMapper.builder().build();

    private final List<String> rivit = new ArrayList<>();
    private final List<Tarkistuspiste> pisteet = new ArrayList<>();
    private final Allekirjoittaja allekirjoittaja;
    private final int vali;
    private String paa = "0".repeat(64);

    public Auditointiloki(Allekirjoittaja allekirjoittaja, int vali) {
        this.allekirjoittaja = allekirjoittaja;
        this.vali = vali;
    }

    // @alku kirjaa
    public synchronized void kirjaa(Tapahtuma t) {
        var peitetty = new Tapahtuma(t.aika(), t.korrelaatio(),
                t.palvelu(), t.toimija(), t.toiminto(), t.resurssi(),
                t.tulos(), Peittaja.peita(t.tiedot()));
        String rivi = JSON.writeValueAsString(peitetty);
        rivit.add(rivi);
        paa = ketjuta(paa, rivi);
        if (rivit.size() % vali == 0) {
            pisteet.add(allekirjoittaja.allekirjoita(rivit.size(), paa));
        }
    }
    // @loppu kirjaa

    public synchronized List<String> rivit() {
        return new ArrayList<>(rivit); // kopio: testit voivat peukaloida
    }

    public synchronized List<Tarkistuspiste> tarkistuspisteet() {
        return List.copyOf(pisteet);
    }

    // @alku tarkista
    /** Palauttaa ensimmäisen ongelman tai "ehjä". */
    public static String tarkista(List<String> rivit,
                                  List<Tarkistuspiste> pisteet,
                                  PublicKey avain) {
        String paa = "0".repeat(64);
        int seuraava = 0;
        for (int i = 0; i < rivit.size(); i++) {
            paa = ketjuta(paa, rivit.get(i));
            while (seuraava < pisteet.size()
                    && pisteet.get(seuraava).riveja() == i + 1) {
                var p = pisteet.get(seuraava++);
                if (!vahvista(avain, p)) {
                    return "tarkistuspiste " + p.riveja()
                            + ": allekirjoitus ei täsmää";
                }
                if (!p.paa().equals(paa)) {
                    return "rivit 1–" + p.riveja() + " on muutettu";
                }
            }
        }
        if (seuraava < pisteet.size()) {
            return "rivejä puuttuu: tarkistuspiste "
                    + pisteet.get(seuraava).riveja();
        }
        return "ehjä";
    }
    // @loppu tarkista

    static String ketjuta(String edellinen, String rivi) {
        try {
            var md = MessageDigest.getInstance("SHA-256");
            md.update(edellinen.getBytes(StandardCharsets.US_ASCII));
            md.update(rivi.getBytes(StandardCharsets.UTF_8));
            return HexFormat.of().formatHex(md.digest());
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException(e);
        }
    }

    static byte[] allekirjoita(PrivateKey avain, int riveja, String paa) {
        try {
            var s = Signature.getInstance("Ed25519");
            s.initSign(avain);
            s.update((riveja + ":" + paa).getBytes(StandardCharsets.UTF_8));
            return s.sign();
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException(e);
        }
    }

    static boolean vahvista(PublicKey avain, Tarkistuspiste p) {
        try {
            var s = Signature.getInstance("Ed25519");
            s.initVerify(avain);
            s.update((p.riveja() + ":" + p.paa())
                    .getBytes(StandardCharsets.UTF_8));
            return s.verify(p.allekirjoitus());
        } catch (GeneralSecurityException e) {
            return false;
        }
    }
}
