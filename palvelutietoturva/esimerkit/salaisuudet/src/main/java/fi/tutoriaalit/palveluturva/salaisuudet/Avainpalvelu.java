package fi.tutoriaalit.palveluturva.salaisuudet;

import java.nio.charset.StandardCharsets;
import java.security.GeneralSecurityException;
import java.security.SecureRandom;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;

/**
 * Avainpalvelu (KMS) pienoiskoossa. Pääavaimet (KEK) eivät koskaan
 * poistu palvelusta: palvelu luo datan avaimia (DEK) ja käärii ne
 * pääavaimella. Sovellus salaa datansa DEK:llä itse ja tallentaa vain
 * käärityn DEK:n datan rinnalle (kirjekuorisalaus).
 */
public final class Avainpalvelu {

    // @alku rajapinta
    /** Datan avain: selväkielinen sovellukselle, kääritty
     *  tallennukseen. */
    public record DatanAvain(SecretKey selva, Kaaritty kaaritty) {}

    /** Kääritty avain kertoo, millä pääavaimen versiolla se
     *  käärittiin. */
    public record Kaaritty(String paaavain, int versio, byte[] nonce,
                           byte[] salattu) {}
    // @loppu rajapinta

    private static final SecureRandom SATUNNAINEN = new SecureRandom();
    private final Map<String, TreeMap<Integer, SecretKey>> paaavaimet =
            new HashMap<>();

    public synchronized void luoPaaavain(String nimi) {
        paaavaimet.put(nimi, new TreeMap<>(Map.of(1, uusiAvain())));
    }

    // @alku kaari
    /** Uusi DEK, kääritty pääavaimen uusimmalla versiolla. Konteksti
     *  (esim. "asiakkaat/tilaus") sidotaan kääreeseen: väärässä
     *  kontekstissa avaus epäonnistuu. */
    public synchronized DatanAvain luoDatanAvain(String paaavain,
                                                 String konteksti) {
        SecretKey dek = uusiAvain();
        return new DatanAvain(dek, kaari(paaavain, dek, konteksti));
    }

    public synchronized SecretKey avaa(Kaaritty k, String konteksti) {
        SecretKey kek = paaavaimet.get(k.paaavain()).get(k.versio());
        if (kek == null) {
            throw new IllegalStateException("versio " + k.versio()
                    + " on poistettu");
        }
        byte[] raaka = aes(Cipher.DECRYPT_MODE, kek, k.nonce(),
                konteksti, k.salattu());
        return new SecretKeySpec(raaka, "AES");
    }
    // @loppu kaari

    // @alku kierto
    /** Pääavaimen kierto: uusi versio uusille kääreille, vanhat
     *  versiot jäävät avaamista varten. */
    public synchronized int kierra(String paaavain) {
        var versiot = paaavaimet.get(paaavain);
        int uusi = versiot.lastKey() + 1;
        versiot.put(uusi, uusiAvain());
        return uusi;
    }

    /** Käärii DEK:n uudelleen uusimmalla versiolla. Data pysyy
     *  koskematta: vain muutaman kymmenen tavun kääre vaihtuu. */
    public synchronized Kaaritty kaariUudelleen(Kaaritty k,
                                                String konteksti) {
        return kaari(k.paaavain(), avaa(k, konteksti), konteksti);
    }

    /** Version poisto tekee sillä käärityt avaimet pysyvästi
     *  käyttökelvottomiksi (crypto-shredding). */
    public synchronized void poista(String paaavain, int versio) {
        paaavaimet.get(paaavain).remove(versio);
    }
    // @loppu kierto

    private Kaaritty kaari(String paaavain, SecretKey dek,
                           String konteksti) {
        var versiot = paaavaimet.get(paaavain);
        int versio = versiot.lastKey();
        byte[] nonce = satunnainen(12);
        return new Kaaritty(paaavain, versio, nonce, aes(
                Cipher.ENCRYPT_MODE, versiot.get(versio), nonce,
                konteksti, dek.getEncoded()));
    }

    static byte[] aes(int tila, SecretKey avain, byte[] nonce,
                      String konteksti, byte[] data) {
        try {
            Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
            c.init(tila, avain, new GCMParameterSpec(128, nonce));
            c.updateAAD(konteksti.getBytes(StandardCharsets.UTF_8));
            return c.doFinal(data);
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException("purku epäonnistui", e);
        }
    }

    static byte[] satunnainen(int tavua) {
        byte[] b = new byte[tavua];
        SATUNNAINEN.nextBytes(b);
        return b;
    }

    private static SecretKey uusiAvain() {
        try {
            KeyGenerator g = KeyGenerator.getInstance("AES");
            g.init(256);
            return g.generateKey();
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException(e);
        }
    }
}
