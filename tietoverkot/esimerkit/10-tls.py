"""TLS: varmenneketju, palvelimen tunnistus ja salattu yhteys.

Luo opensslillä oman varmentajan (CA) ja palvelinvarmenteen, käynnistää
TLS-palvelimen ja kokeilee asiakkaalla, milloin yhteys hyväksytään.
"""

import socket
import ssl
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import cast


def openssl(*argumentit: str) -> None:
    subprocess.run(["openssl", *argumentit], check=True,
                   capture_output=True)


# @alku varmenteet
def luo_varmenteet(hak: Path) -> None:
    ec = ["-newkey", "ec", "-pkeyopt", "ec_paramgen_curve:P-256",
          "-noenc"]
    # Varmentaja: itse allekirjoitettu juurivarmenne.
    openssl("req", "-x509", *ec, "-keyout", str(hak / "ca.key"),
            "-out", str(hak / "ca.crt"), "-days", "1",
            "-subj", "/CN=Esimerkkivarmentaja",
            "-addext", "basicConstraints=critical,CA:TRUE",
            "-addext", "keyUsage=critical,keyCertSign,cRLSign")
    # Palvelin: avain ja varmennepyyntö, jonka varmentaja allekirjoittaa.
    # Nimi, johon asiakas vertaa, on SAN-laajennuksessa.
    openssl("req", *ec, "-keyout", str(hak / "palvelin.key"),
            "-out", str(hak / "palvelin.csr"), "-subj", "/CN=api.example")
    (hak / "san.ext").write_text(
        "subjectAltName=DNS:api.example\n"
        "keyUsage=critical,digitalSignature\n"
        "extendedKeyUsage=serverAuth\n"
        "authorityKeyIdentifier=keyid\n")
    openssl("x509", "-req", "-in", str(hak / "palvelin.csr"),
            "-CA", str(hak / "ca.crt"), "-CAkey", str(hak / "ca.key"),
            "-out", str(hak / "palvelin.crt"), "-days", "1",
            "-extfile", str(hak / "san.ext"))
# @loppu varmenteet


def palvelin(hak: Path, kuuntelija: socket.socket, kertoja: int) -> None:
    konteksti = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    konteksti.load_cert_chain(hak / "palvelin.crt", hak / "palvelin.key")
    for _ in range(kertoja):
        yhteys, _ = kuuntelija.accept()
        try:
            with konteksti.wrap_socket(yhteys, server_side=True) as tls:
                tls.sendall(b"salattu tervehdys")
        except ssl.SSLError:
            pass                    # asiakas hylkäsi varmenteen


# @alku asiakas
def kokeile(portti: int, nimi: str, ca: Path | None) -> None:
    konteksti = ssl.create_default_context(
        cafile=str(ca) if ca else None)
    # Oletuskonteksti tarkistaa ketjun ja nimen; älä koskaan poista
    # tarkistuksia (check_hostname = False, CERT_NONE) tuotannossa.
    with socket.create_connection(("127.0.0.1", portti)) as raaka:
        try:
            with konteksti.wrap_socket(raaka, server_hostname=nimi) as tls:
                varmenne = tls.getpeercert()
                assert varmenne is not None
                nimet = cast(tuple[tuple[str, str], ...],
                             varmenne["subjectAltName"])
                san = [arvo for _, arvo in nimet]
                cipher = tls.cipher()
                assert cipher is not None
                print(f"{nimi}: hyväksytty, {tls.version()}, {cipher[0]},"
                      f" SAN {san}")
                print(f"  {tls.recv(100).decode()}")
        except ssl.SSLCertVerificationError as virhe:
            print(f"{nimi}: hylätty: {virhe.verify_message}")
# @loppu asiakas


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        luo_varmenteet(hak)
        kuuntelija = socket.create_server(("127.0.0.1", 0))
        portti = kuuntelija.getsockname()[1]
        saie = threading.Thread(target=palvelin, args=(hak, kuuntelija, 3))
        saie.start()
        # @alku kokeet
        kokeile(portti, "api.example", hak / "ca.crt")
        kokeile(portti, "www.example", hak / "ca.crt")
        kokeile(portti, "api.example", None)   # järjestelmän varmentajat
        # @loppu kokeet
        saie.join()
        kuuntelija.close()


if __name__ == "__main__":
    main()
