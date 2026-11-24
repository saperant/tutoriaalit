package fi.tutoriaalit.palveluturva.luottamus;

import java.math.BigInteger;
import java.security.GeneralSecurityException;
import java.security.KeyPair;
import java.security.KeyPairGenerator;
import java.security.cert.X509Certificate;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.concurrent.atomic.AtomicLong;
import javax.security.auth.x500.X500Principal;
import org.bouncycastle.asn1.x509.BasicConstraints;
import org.bouncycastle.asn1.x509.ExtendedKeyUsage;
import org.bouncycastle.asn1.x509.Extension;
import org.bouncycastle.asn1.x509.GeneralName;
import org.bouncycastle.asn1.x509.GeneralNames;
import org.bouncycastle.asn1.x509.KeyPurposeId;
import org.bouncycastle.asn1.x509.KeyUsage;
import org.bouncycastle.cert.X509v3CertificateBuilder;
import org.bouncycastle.cert.jcajce.JcaX509CertificateConverter;
import org.bouncycastle.cert.jcajce.JcaX509v3CertificateBuilder;
import org.bouncycastle.operator.OperatorCreationException;
import org.bouncycastle.operator.jcajce.JcaContentSignerBuilder;

/**
 * Pieni varmentaja testejä varten. Myöntää palveluille lyhytikäisiä
 * varmenteita, joiden SAN-kentässä on SPIFFE-tunniste
 * (spiffe://luottamusalue/polku) ja nimi localhost.
 *
 * Tuotannossa varmentaja on erillinen palvelu (SPIRE, Vault PKI,
 * pilven varmentaja), ja sen juuriavain on laitteistossa.
 */
public final class Varmentaja {

    private final KeyPair avaimet;
    private final X509Certificate juuri;
    private final AtomicLong sarjanumero = new AtomicLong(1);

    private Varmentaja(KeyPair avaimet, X509Certificate juuri) {
        this.avaimet = avaimet;
        this.juuri = juuri;
    }

    // @alku juuri
    /** Luo uuden juurivarmentajan, jonka varmenne on voimassa vuoden. */
    public static Varmentaja luo(String nimi) {
        KeyPair avaimet = avainpari();
        Instant nyt = Instant.now();
        X500Principal dn = new X500Principal("CN=" + nimi);
        var rakentaja = new JcaX509v3CertificateBuilder(dn,
                BigInteger.ONE, Date.from(nyt.minusSeconds(60)),
                Date.from(nyt.plus(Duration.ofDays(365))), dn,
                avaimet.getPublic());
        try {
            rakentaja.addExtension(Extension.basicConstraints, true,
                    new BasicConstraints(0));
            rakentaja.addExtension(Extension.keyUsage, true,
                    new KeyUsage(KeyUsage.keyCertSign | KeyUsage.cRLSign));
        } catch (java.io.IOException e) {
            throw new IllegalStateException(e);
        }
        return new Varmentaja(avaimet,
                allekirjoita(rakentaja, avaimet));
    }
    // @loppu juuri

    public X509Certificate juuri() {
        return juuri;
    }

    // @alku myonna
    /**
     * Myöntää palvelulle varmenteen. Elinikä on tunteja, ei vuosia:
     * vuotanut avain vanhenee itsestään, eikä kumoamislistoja tarvita.
     */
    public Identiteetti myonna(String spiffeId, Duration elinika) {
        return myonna(spiffeId, Instant.now().minusSeconds(60),
                Instant.now().plus(elinika));
    }

    public Identiteetti myonna(String spiffeId, Instant alkaen,
                               Instant asti) {
        KeyPair palvelun = avainpari();
        var rakentaja = new JcaX509v3CertificateBuilder(
                juuri.getSubjectX500Principal(),
                BigInteger.valueOf(sarjanumero.incrementAndGet()),
                Date.from(alkaen), Date.from(asti),
                new X500Principal(""), palvelun.getPublic());
        var san = new GeneralNames(new GeneralName[] {
            new GeneralName(GeneralName.uniformResourceIdentifier,
                    spiffeId),
            new GeneralName(GeneralName.dNSName, "localhost")});
        try {
            rakentaja.addExtension(Extension.subjectAlternativeName,
                    true, san);
            rakentaja.addExtension(Extension.basicConstraints, true,
                    new BasicConstraints(false));
            rakentaja.addExtension(Extension.extendedKeyUsage, false,
                    new ExtendedKeyUsage(new KeyPurposeId[] {
                        KeyPurposeId.id_kp_serverAuth,
                        KeyPurposeId.id_kp_clientAuth}));
        } catch (java.io.IOException e) {
            throw new IllegalStateException(e);
        }
        X509Certificate varmenne = allekirjoita(rakentaja, avaimet);
        return new Identiteetti(spiffeId, palvelun.getPrivate(),
                varmenne, juuri);
    }
    // @loppu myonna

    private static KeyPair avainpari() {
        try {
            KeyPairGenerator g = KeyPairGenerator.getInstance("EC");
            g.initialize(256);
            return g.generateKeyPair();
        } catch (GeneralSecurityException e) {
            throw new IllegalStateException(e);
        }
    }

    private static X509Certificate allekirjoita(
            X509v3CertificateBuilder rakentaja, KeyPair allekirjoittaja) {
        try {
            var allekirjoitin = new JcaContentSignerBuilder(
                    "SHA256withECDSA").build(allekirjoittaja.getPrivate());
            return new JcaX509CertificateConverter()
                    .getCertificate(rakentaja.build(allekirjoitin));
        } catch (OperatorCreationException
                 | java.security.cert.CertificateException e) {
            throw new IllegalStateException(e);
        }
    }
}
