"""Varmenneketju Pythonilla: CA, palvelinvarmenne ja ketjun tarkistus."""

import datetime as dt

from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from cryptography.x509.verification import (
    PolicyBuilder,
    Store,
    VerificationError,
)

NYT = dt.datetime.now(dt.UTC)


def nimi(cn: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, cn)])


# @alku ca
def luo_ca() -> tuple[ec.EllipticCurvePrivateKey, x509.Certificate]:
    avain = ec.generate_private_key(ec.SECP256R1())
    ski = x509.SubjectKeyIdentifier.from_public_key(avain.public_key())
    varmenne = (
        x509.CertificateBuilder()
        .subject_name(nimi("Esimerkki Root CA"))
        .issuer_name(nimi("Esimerkki Root CA"))      # itse allekirjoitettu
        .public_key(avain.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(NYT - dt.timedelta(minutes=5))
        .not_valid_after(NYT + dt.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), True)
        .add_extension(x509.KeyUsage(
            digital_signature=False, content_commitment=False,
            key_encipherment=False, data_encipherment=False,
            key_agreement=False, key_cert_sign=True, crl_sign=True,
            encipher_only=False, decipher_only=False), True)
        .add_extension(ski, False)
        .sign(avain, hashes.SHA256())
    )
    return avain, varmenne
# @loppu ca


# @alku palvelin
def luo_palvelin(ca_avain: ec.EllipticCurvePrivateKey,
                 ca: x509.Certificate, dns: str) -> x509.Certificate:
    avain = ec.generate_private_key(ec.SECP256R1())
    aki = x509.AuthorityKeyIdentifier.from_issuer_public_key(
        ca_avain.public_key())
    return (
        x509.CertificateBuilder()
        .subject_name(nimi(dns))
        .issuer_name(ca.subject)
        .public_key(avain.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(NYT - dt.timedelta(minutes=5))
        .not_valid_after(NYT + dt.timedelta(days=90))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(dns)]),
                       False)
        .add_extension(x509.ExtendedKeyUsage(
            [ExtendedKeyUsageOID.SERVER_AUTH]), False)
        .add_extension(aki, False)
        .sign(ca_avain, hashes.SHA256())
    )
# @loppu palvelin


def main() -> None:
    ca_avain, ca = luo_ca()
    palvelin = luo_palvelin(ca_avain, ca, "palvelu.example")

    # @alku tarkistus
    tarkistaja = PolicyBuilder().store(Store([ca])).time(NYT)
    for kohde in ("palvelu.example", "huijaus.example"):
        try:
            ketju = tarkistaja.build_server_verifier(
                x509.DNSName(kohde)).verify(palvelin, [])
            print(f"{kohde}: kelpaa, ketjun pituus {len(ketju)}")
        except VerificationError:
            print(f"{kohde}: ei kelpaa")
    # @loppu tarkistus


if __name__ == "__main__":
    main()
