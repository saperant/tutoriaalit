"""RSA oikein: OAEP-salaus ja PSS-allekirjoitus kirjastolla."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def main() -> None:
    # @alku avain
    salainen = rsa.generate_private_key(public_exponent=65537,
                                        key_size=3072)
    julkinen = salainen.public_key()
    # @loppu avain

    # @alku oaep
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),
                        algorithm=hashes.SHA256(), label=None)
    c1 = julkinen.encrypt(b"istuntoavain", oaep)
    c2 = julkinen.encrypt(b"istuntoavain", oaep)
    print("salattu", len(c1), "tavua; satunnaistettu:", c1 != c2)
    print("purettu:", salainen.decrypt(c1, oaep).decode())
    # @loppu oaep

    # @alku pss
    pss = padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                      salt_length=padding.PSS.MAX_LENGTH)
    viesti = b"julkaisu 2.1.0, sha256=..."
    allekirjoitus = salainen.sign(viesti, pss, hashes.SHA256())
    julkinen.verify(allekirjoitus, viesti, pss, hashes.SHA256())
    print("allekirjoitus kelpaa")
    try:
        julkinen.verify(allekirjoitus, viesti + b"!", pss, hashes.SHA256())
    except InvalidSignature:
        print("muutettu viesti: InvalidSignature")
    # @loppu pss


if __name__ == "__main__":
    main()
