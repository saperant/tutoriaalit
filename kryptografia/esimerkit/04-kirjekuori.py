"""Kirjekuorisalaus: datan avain (DEK) salataan avainten avaimella (KEK)."""

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# @alku kirjekuori
@dataclass(frozen=True)
class Kirjekuori:
    kek_id: str            # millä avainten avaimella DEK on salattu
    salattu_dek: bytes     # nonce + salattu datan avain
    salattu_data: bytes    # nonce + salattu data


def salaa(keks: dict[str, bytes], kek_id: str, data: bytes) -> Kirjekuori:
    dek = AESGCM.generate_key(bit_length=256)   # uusi avain joka kerta
    n1, n2 = os.urandom(12), os.urandom(12)
    salattu_dek = AESGCM(keks[kek_id]).encrypt(n1, dek, kek_id.encode())
    salattu_data = AESGCM(dek).encrypt(n2, data, None)
    return Kirjekuori(kek_id, n1 + salattu_dek, n2 + salattu_data)


def pura_dek(keks: dict[str, bytes], k: Kirjekuori) -> bytes:
    n, s = k.salattu_dek[:12], k.salattu_dek[12:]
    return AESGCM(keks[k.kek_id]).decrypt(n, s, k.kek_id.encode())


def pura(keks: dict[str, bytes], k: Kirjekuori) -> bytes:
    n, s = k.salattu_data[:12], k.salattu_data[12:]
    return AESGCM(pura_dek(keks, k)).decrypt(n, s, None)


def kierra(keks: dict[str, bytes], k: Kirjekuori, uusi: str) -> Kirjekuori:
    """Avainten avaimen kierto: vain DEK salataan uudelleen."""
    dek = pura_dek(keks, k)
    n = os.urandom(12)
    salattu_dek = AESGCM(keks[uusi]).encrypt(n, dek, uusi.encode())
    return Kirjekuori(uusi, n + salattu_dek, k.salattu_data)
# @loppu kirjekuori


def main() -> None:
    # Oikeassa järjestelmässä KEKit ovat avaintenhallintapalvelussa (KMS).
    keks = {"kek-2025": AESGCM.generate_key(bit_length=256),
            "kek-2026": AESGCM.generate_key(bit_length=256)}
    vanha = salaa(keks, "kek-2025", b"varmuuskopio, 4 Gt" * 3)
    uusi = kierra(keks, vanha, "kek-2026")
    print("salattu data ennallaan:", uusi.salattu_data == vanha.salattu_data)
    del keks["kek-2025"]               # vanha avain voidaan poistaa
    print("purku uudella avaimella:", pura(keks, uusi)[:18].decode())


if __name__ == "__main__":
    main()
