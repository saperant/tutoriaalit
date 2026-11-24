package fi.tutoriaalit.palveluturva.luottamus;

import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.PrivateKey;
import java.security.cert.Certificate;
import java.security.cert.CertificateParsingException;
import java.security.cert.X509Certificate;
import java.util.List;
import java.util.Optional;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;

/**
 * Työkuorman identiteetti: SPIFFE-tunniste, yksityinen avain ja
 * varmenne, jonka varmentaja on myöntänyt.
 */
public record Identiteetti(String spiffeId, PrivateKey avain,
                           X509Certificate varmenne,
                           X509Certificate myontaja) {

    // @alku konteksti
    /**
     * TLS-konteksti, joka esittää tämän identiteetin ja luottaa vain
     * annettuihin juuriin. Sama konteksti kelpaa palvelimelle ja
     * asiakkaalle: mTLS:ssä molemmat todistavat henkilöllisyytensä.
     */
    public SSLContext tlsKonteksti(List<X509Certificate> luotetut) {
        try {
            KeyStore omat = KeyStore.getInstance("PKCS12");
            omat.load(null, null);
            omat.setKeyEntry("oma", avain, new char[0],
                    new Certificate[] {varmenne, myontaja});
            var km = KeyManagerFactory.getInstance("PKIX");
            km.init(omat, new char[0]);
            var tm = TrustManagerFactory.getInstance("PKIX");
            tm.init(luottamusvarasto(luotetut));
            SSLContext konteksti = SSLContext.getInstance("TLSv1.3");
            konteksti.init(km.getKeyManagers(), tm.getTrustManagers(),
                    null);
            return konteksti;
        } catch (GeneralSecurityException | java.io.IOException e) {
            throw new IllegalStateException(e);
        }
    }
    // @loppu konteksti

    static KeyStore luottamusvarasto(List<X509Certificate> juuret)
            throws GeneralSecurityException, java.io.IOException {
        KeyStore varasto = KeyStore.getInstance("PKCS12");
        varasto.load(null, null);
        for (int i = 0; i < juuret.size(); i++) {
            varasto.setCertificateEntry("juuri" + i, juuret.get(i));
        }
        return varasto;
    }

    // @alku tunniste
    /** Varmenteen SAN-kentän SPIFFE-tunniste, jos sellainen on. */
    public static Optional<String> spiffeId(X509Certificate varmenne) {
        try {
            var nimet = varmenne.getSubjectAlternativeNames();
            if (nimet == null) {
                return Optional.empty();
            }
            return nimet.stream()
                    .filter(n -> (Integer) n.get(0) == 6) // URI
                    .map(n -> (String) n.get(1))
                    .filter(u -> u.startsWith("spiffe://"))
                    .findFirst();
        } catch (CertificateParsingException e) {
            return Optional.empty();
        }
    }
    // @loppu tunniste
}
