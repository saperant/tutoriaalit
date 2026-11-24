package fi.tutoriaalit.palveluturva.luottamus;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.cert.CertificateEncodingException;
import java.security.cert.X509Certificate;
import java.util.Base64;

/** PEM-tiedostot (esim. Spring Bootin SSL-nippua varten). */
public final class Pem {

    private Pem() {}

    public static String varmenne(X509Certificate v) {
        try {
            return lohko("CERTIFICATE", v.getEncoded());
        } catch (CertificateEncodingException e) {
            throw new IllegalStateException(e);
        }
    }

    /** Kirjoittaa identiteetin varmenteen ja avaimen hakemistoon. */
    public static void kirjoita(Identiteetti i, Path varmenne, Path avain)
            throws IOException {
        Files.writeString(varmenne, varmenne(i.varmenne()));
        Files.writeString(avain, lohko("PRIVATE KEY",
                i.avain().getEncoded()));
    }

    private static String lohko(String tyyppi, byte[] der) {
        return "-----BEGIN " + tyyppi + "-----\n"
                + Base64.getMimeEncoder(64, new byte[] {'\n'})
                        .encodeToString(der)
                + "\n-----END " + tyyppi + "-----\n";
    }
}
