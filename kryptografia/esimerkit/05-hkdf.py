"""HKDF: avainten johtaminen jaetusta salaisuudesta käyttötarkoittain."""

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


def johda(salaisuus: bytes, suola: bytes, tarkoitus: bytes,
          pituus: int = 32) -> bytes:
    return HKDF(algorithm=hashes.SHA256(), length=pituus, salt=suola,
                info=tarkoitus).derive(salaisuus)


def main() -> None:
    # RFC 5869, testitapaus 1.
    okm = johda(b"\x0b" * 22, bytes(range(13)), bytes(range(0xF0, 0xFA)),
                42)
    print("RFC 5869 täsmää:", okm.hex().startswith("3cb25f25faacd57a9043"))

    # @alku tarkoitus
    paa = bytes(32)  # esim. avaintenvaihdon tulos
    salaus = johda(paa, b"istunto-17", b"sovellus v1 salaus")
    mac = johda(paa, b"istunto-17", b"sovellus v1 mac")
    print("eri tarkoitus, eri avain:", salaus != mac)
    # @loppu tarkoitus


if __name__ == "__main__":
    main()
