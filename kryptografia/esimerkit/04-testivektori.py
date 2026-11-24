"""ChaCha20-Poly1305: RFC 8439:n luvun 2.8.2 testivektori."""

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

AVAIN = bytes(range(0x80, 0xA0))
NONCE = bytes.fromhex("070000004041424344454647")
LIITE = bytes.fromhex("50515253c0c1c2c3c4c5c6c7")
VIESTI = (b"Ladies and Gentlemen of the class of '99: If I could offer "
          b"you only one tip for the future, sunscreen would be it.")
ODOTETTU_ALKU = bytes.fromhex("d31a8d34648e60db7b86afbc53ef7ec2")
ODOTETTU_TUNNISTE = bytes.fromhex("1ae10b594f09e26a7e902ecbd0600691")


def main() -> None:
    salattu = ChaCha20Poly1305(AVAIN).encrypt(NONCE, VIESTI, LIITE)
    # Kirjasto palauttaa salatun tekstin ja perään 16 tavun tunnisteen.
    print("salatun alku täsmää:", salattu[:16] == ODOTETTU_ALKU)
    print("tunniste täsmää:", salattu[-16:] == ODOTETTU_TUNNISTE)


if __name__ == "__main__":
    main()
