"""Ed25519-allekirjoitukset: RFC 8032:n testivektori ja käyttö."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

SALAINEN = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
ODOTETTU = bytes.fromhex(
    "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
    "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")


def main() -> None:
    avain = Ed25519PrivateKey.from_private_bytes(SALAINEN)
    print("RFC 8032 täsmää:", avain.sign(b"") == ODOTETTU)

    # @alku kaytto
    salainen = Ed25519PrivateKey.generate()
    julkinen = salainen.public_key()
    viesti = b"paivitys-3.2.bin sha256=8f4e..."
    allekirjoitus = salainen.sign(viesti)          # 64 tavua
    julkinen.verify(allekirjoitus, viesti)         # poikkeus, jos ei kelpaa
    print("kelpaa,", len(allekirjoitus), "tavua; deterministinen:",
          salainen.sign(viesti) == allekirjoitus)
    try:
        julkinen.verify(allekirjoitus, viesti.replace(b"3.2", b"6.6"))
    except InvalidSignature:
        print("muutettu viesti hylättiin")
    # @loppu kaytto


if __name__ == "__main__":
    main()
