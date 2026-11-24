package fi.tutoriaalit.palveluturva.salaisuudet;

import javax.crypto.Cipher;

/** Kirjekuorisalattu tietue: salattu data ja kääritty datan avain. */
public record Kirjekuori(Avainpalvelu.Kaaritty avain, byte[] nonce,
                         byte[] salattu) {

    // @alku kirjekuori
    public static Kirjekuori salaa(Avainpalvelu kms, String paaavain,
                                   String konteksti, byte[] data) {
        var dek = kms.luoDatanAvain(paaavain, konteksti);
        byte[] nonce = Avainpalvelu.satunnainen(12);
        return new Kirjekuori(dek.kaaritty(), nonce, Avainpalvelu.aes(
                Cipher.ENCRYPT_MODE, dek.selva(), nonce, konteksti, data));
    }

    public byte[] pura(Avainpalvelu kms, String konteksti) {
        var dek = kms.avaa(avain, konteksti);
        return Avainpalvelu.aes(Cipher.DECRYPT_MODE, dek, nonce,
                konteksti, salattu);
    }
    // @loppu kirjekuori

    public Kirjekuori kaariUudelleen(Avainpalvelu kms, String konteksti) {
        return new Kirjekuori(kms.kaariUudelleen(avain, konteksti), nonce,
                salattu);
    }
}
