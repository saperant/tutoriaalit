package fi.tutoriaalit.palveluturva.luottamus;

import java.net.Socket;
import java.security.GeneralSecurityException;
import java.security.KeyStore;
import java.security.Principal;
import java.security.PrivateKey;
import java.security.cert.CertificateException;
import java.security.cert.X509Certificate;
import java.util.List;
import java.util.concurrent.atomic.AtomicReference;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLEngine;
import javax.net.ssl.TrustManagerFactory;
import javax.net.ssl.X509ExtendedKeyManager;
import javax.net.ssl.X509ExtendedTrustManager;

/**
 * TLS-konteksti, jonka oma varmenne ja luotetut juuret voi vaihtaa
 * lennossa. Uudet yhteydet käyttävät heti uusia arvoja, joten
 * varmenteen ja varmentajan kierto ei vaadi palvelun uudelleen-
 * käynnistystä. (Spring Bootissa sama on SSL-nipun reload-on-update.)
 */
public final class VaihdettavaTls {

    private final AtomicReference<X509ExtendedKeyManager> avaimet =
            new AtomicReference<>();
    private final AtomicReference<X509ExtendedTrustManager> luottamus =
            new AtomicReference<>();
    private final SSLContext konteksti;

    public VaihdettavaTls(Identiteetti oma,
                          List<X509Certificate> luotetut) {
        asetaIdentiteetti(oma);
        asetaLuotetut(luotetut);
        try {
            konteksti = SSLContext.getInstance("TLSv1.3");
            konteksti.init(new X509ExtendedKeyManager[] {new Avaimet()},
                    new X509ExtendedTrustManager[] {new Luottamus()},
                    null);
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException(e);
        }
    }

    public SSLContext konteksti() {
        return konteksti;
    }

    // @alku vaihto
    public void asetaIdentiteetti(Identiteetti oma) {
        try {
            KeyStore varasto = KeyStore.getInstance("PKCS12");
            varasto.load(null, null);
            varasto.setKeyEntry("oma", oma.avain(), new char[0],
                    new java.security.cert.Certificate[] {
                        oma.varmenne(), oma.myontaja()});
            var kmf = KeyManagerFactory.getInstance("PKIX");
            kmf.init(varasto, new char[0]);
            avaimet.set((X509ExtendedKeyManager) kmf.getKeyManagers()[0]);
        } catch (GeneralSecurityException | java.io.IOException e) {
            throw new IllegalStateException(e);
        }
    }

    public void asetaLuotetut(List<X509Certificate> juuret) {
        try {
            var tmf = TrustManagerFactory.getInstance("PKIX");
            tmf.init(Identiteetti.luottamusvarasto(juuret));
            luottamus.set(
                    (X509ExtendedTrustManager) tmf.getTrustManagers()[0]);
        } catch (GeneralSecurityException | java.io.IOException e) {
            throw new IllegalStateException(e);
        }
    }
    // @loppu vaihto

    /** Välittää kutsut kulloiseenkin avainhallintaan. */
    private final class Avaimet extends X509ExtendedKeyManager {
        public String[] getClientAliases(String t, Principal[] p) {
            return avaimet.get().getClientAliases(t, p);
        }
        public String chooseClientAlias(String[] t, Principal[] p,
                                        Socket s) {
            return avaimet.get().chooseClientAlias(t, p, s);
        }
        public String chooseEngineClientAlias(String[] t, Principal[] p,
                                              SSLEngine e) {
            return avaimet.get().chooseEngineClientAlias(t, p, e);
        }
        public String[] getServerAliases(String t, Principal[] p) {
            return avaimet.get().getServerAliases(t, p);
        }
        public String chooseServerAlias(String t, Principal[] p,
                                        Socket s) {
            return avaimet.get().chooseServerAlias(t, p, s);
        }
        public String chooseEngineServerAlias(String t, Principal[] p,
                                              SSLEngine e) {
            return avaimet.get().chooseEngineServerAlias(t, p, e);
        }
        public X509Certificate[] getCertificateChain(String a) {
            return avaimet.get().getCertificateChain(a);
        }
        public PrivateKey getPrivateKey(String a) {
            return avaimet.get().getPrivateKey(a);
        }
    }

    /** Välittää kutsut kulloiseenkin luottamushallintaan. */
    private final class Luottamus extends X509ExtendedTrustManager {
        public void checkClientTrusted(X509Certificate[] c, String a)
                throws CertificateException {
            luottamus.get().checkClientTrusted(c, a);
        }
        public void checkClientTrusted(X509Certificate[] c, String a,
                                       Socket s)
                throws CertificateException {
            luottamus.get().checkClientTrusted(c, a, s);
        }
        public void checkClientTrusted(X509Certificate[] c, String a,
                                       SSLEngine e)
                throws CertificateException {
            luottamus.get().checkClientTrusted(c, a, e);
        }
        public void checkServerTrusted(X509Certificate[] c, String a)
                throws CertificateException {
            luottamus.get().checkServerTrusted(c, a);
        }
        public void checkServerTrusted(X509Certificate[] c, String a,
                                       Socket s)
                throws CertificateException {
            luottamus.get().checkServerTrusted(c, a, s);
        }
        public void checkServerTrusted(X509Certificate[] c, String a,
                                       SSLEngine e)
                throws CertificateException {
            luottamus.get().checkServerTrusted(c, a, e);
        }
        public X509Certificate[] getAcceptedIssuers() {
            return luottamus.get().getAcceptedIssuers();
        }
    }
}
