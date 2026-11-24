"""TLS 1.3 -yhteys omalla varmentajalla Pythonin ssl-moduulilla."""

import datetime as dt
import socket
import ssl
import threading
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

NYT = dt.datetime.now(dt.UTC)
PEM = serialization.Encoding.PEM


def varmenne(cn: str, avain: ec.EllipticCurvePrivateKey,
             myontaja: x509.Name, myontajan_avain: ec.EllipticCurvePrivateKey,
             ca: bool) -> x509.Certificate:
    """Tiivis versio luvun 9 rakentajista."""
    kaytto = x509.KeyUsage(
        digital_signature=not ca, content_commitment=False,
        key_encipherment=False, data_encipherment=False, key_agreement=False,
        key_cert_sign=ca, crl_sign=ca, encipher_only=False,
        decipher_only=False)
    rakentaja = (
        x509.CertificateBuilder()
        .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,
                                                    cn)]))
        .issuer_name(myontaja)
        .public_key(avain.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(NYT - dt.timedelta(minutes=5))
        .not_valid_after(NYT + dt.timedelta(days=1))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), True)
        .add_extension(kaytto, True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(
            avain.public_key()), False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
            myontajan_avain.public_key()), False)
    )
    if not ca:
        rakentaja = rakentaja.add_extension(
            x509.SubjectAlternativeName([x509.DNSName(cn)]), False)
    return rakentaja.sign(myontajan_avain, hashes.SHA256())


def valmistele() -> None:
    ca_avain = ec.generate_private_key(ec.SECP256R1())
    ca_nimi = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Testi-CA")])
    ca = varmenne("Testi-CA", ca_avain, ca_nimi, ca_avain, ca=True)
    avain = ec.generate_private_key(ec.SECP256R1())
    palvelin = varmenne("palvelu.example", avain, ca_nimi, ca_avain, ca=False)
    Path("ca.pem").write_bytes(ca.public_bytes(PEM))
    Path("palvelu.pem").write_bytes(palvelin.public_bytes(PEM))
    Path("palvelu.key").write_bytes(avain.private_bytes(
        PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption()))


# @alku palvelin
def palvele(kuuntelija: socket.socket, yhteyksia: int) -> None:
    konteksti = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    konteksti.minimum_version = ssl.TLSVersion.TLSv1_3
    konteksti.load_cert_chain("palvelu.pem", "palvelu.key")
    for _ in range(yhteyksia):
        raaka, _ = kuuntelija.accept()
        try:
            with konteksti.wrap_socket(raaka, server_side=True) as yhteys:
                yhteys.sendall(b"hei, " + yhteys.recv(100))
        except (ssl.SSLError, OSError):
            pass   # asiakas hylkäsi varmenteen
# @loppu palvelin


# @alku asiakas
def kysy(portti: int, nimi: str, cafile: str | None) -> None:
    konteksti = ssl.create_default_context(cafile=cafile)
    try:
        with socket.create_connection(("127.0.0.1", portti)) as raaka, \
                konteksti.wrap_socket(raaka, server_hostname=nimi) as y:
            y.sendall(b"asiakas")
            salain = y.cipher()
            print(f"{nimi}: {y.version()}, {salain[0] if salain else '-'}, "
                  f"vastaus {y.recv(100).decode()!r}")
    except ssl.SSLCertVerificationError as virhe:
        syy = str(virhe.verify_message).split(",")[0]
        print(f"{nimi}: hylätty: {syy}")
# @loppu asiakas


def main() -> None:
    valmistele()
    with socket.create_server(("127.0.0.1", 0)) as kuuntelija:
        portti = kuuntelija.getsockname()[1]
        saie = threading.Thread(target=palvele, args=(kuuntelija, 3))
        saie.start()
        # @alku kokeet
        kysy(portti, "palvelu.example", "ca.pem")     # oikein
        kysy(portti, "huijaus.example", "ca.pem")     # väärä nimi
        kysy(portti, "palvelu.example", None)         # tuntematon CA
        # @loppu kokeet
        saie.join()


if __name__ == "__main__":
    main()
