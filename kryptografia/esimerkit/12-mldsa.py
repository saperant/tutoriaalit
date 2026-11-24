"""ML-DSA (FIPS 204): kvanttiturvallinen allekirjoitus ja sen koko."""

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)


def main() -> None:
    viesti = b"laiteohjelmisto 5.0"
    # @alku mldsa
    salainen = mldsa.MLDSA65PrivateKey.generate()
    allekirjoitus = salainen.sign(viesti)
    salainen.public_key().verify(allekirjoitus, viesti)
    # @loppu mldsa
    try:
        salainen.public_key().verify(allekirjoitus, viesti + b"!")
    except InvalidSignature:
        print("ML-DSA hylkäsi muutetun viestin")

    ed = Ed25519PrivateKey.generate()
    print("allekirjoitus: ML-DSA-65", len(allekirjoitus), "tavua, Ed25519",
          len(ed.sign(viesti)), "tavua")
    print("julkinen avain: ML-DSA-65",
          len(salainen.public_key().public_bytes_raw()), "tavua, Ed25519",
          len(ed.public_key().public_bytes_raw()), "tavua")


if __name__ == "__main__":
    main()
