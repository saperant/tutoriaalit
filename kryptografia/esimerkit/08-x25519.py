"""X25519-avaintenvaihto, HKDF ja AEAD: salatun yhteyden ydin."""

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

RAW = serialization.Encoding.Raw
PUB = serialization.PublicFormat.Raw


# @alku istunto
def istuntoavain(oma: X25519PrivateKey, vieras: bytes) -> bytes:
    jaettu = oma.exchange(X25519PublicKey.from_public_bytes(vieras))
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"esimerkki v1 istuntoavain").derive(jaettu)
# @loppu istunto


def main() -> None:
    # RFC 7748, luku 6.1.
    aino = X25519PrivateKey.from_private_bytes(bytes.fromhex(
        "77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a"))
    bertta_julkinen = bytes.fromhex(
        "de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f")
    jaettu = aino.exchange(X25519PublicKey.from_public_bytes(
        bertta_julkinen))
    print("RFC 7748 täsmää:", jaettu.hex().startswith("4a5d9d5ba4ce2de1728e"))

    # @alku vaihto
    a, b = X25519PrivateKey.generate(), X25519PrivateKey.generate()
    a_pub = a.public_key().public_bytes(RAW, PUB)    # 32 tavua verkkoon
    b_pub = b.public_key().public_bytes(RAW, PUB)
    ka, kb = istuntoavain(a, b_pub), istuntoavain(b, a_pub)
    print("sama istuntoavain:", ka == kb, "julkinen avain", len(a_pub),
          "tavua")
    nonce = bytes(12)  # sallittu vain, koska avain on kertakäyttöinen
    salattu = ChaCha20Poly1305(ka).encrypt(nonce, b"hei Bertta", None)
    print("Bertta lukee:", ChaCha20Poly1305(kb).decrypt(nonce, salattu,
                                                         None).decode())
    # @loppu vaihto


if __name__ == "__main__":
    main()
