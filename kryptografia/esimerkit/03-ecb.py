"""ECB-tila paljastaa selvätekstin rakenteen, CBC ja CTR eivät."""

import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Jokainen rivi on yksi 16 tavun lohko: "kuva", jossa toistuu kaksi
# eri lohkoa. Samanlaisia rakenteita on oikeissa tiedostoissa: tyhjää
# tilaa, otsakkeita, nollatavuja.
KUVA = [
    b"................",
    b"......####......",
    b"....########....",
    b"......####......",
    b"................",
]


# @alku nayta
def nayta(salattu: bytes) -> str:
    """Korvaa jokaisen salatun lohkon kirjaimella ensiesiintymän mukaan."""
    merkit: dict[bytes, str] = {}
    rivi = []
    for i in range(0, len(salattu), 16):
        lohko = salattu[i:i + 16]
        merkit.setdefault(lohko, "ABCDEFGHIJKLMNOP"[len(merkit)])
        rivi.append(merkit[lohko])
    return " ".join(rivi)
# @loppu nayta


def main() -> None:
    avain = os.urandom(32)
    data = b"".join(KUVA)
    # @alku tilat
    tilat: dict[str, modes.ECB | modes.CBC | modes.CTR] = {
        "ECB": modes.ECB(),                 # älä käytä
        "CBC": modes.CBC(os.urandom(16)),
        "CTR": modes.CTR(os.urandom(16)),
    }
    for nimi, tila in tilat.items():
        salain = Cipher(algorithms.AES(avain), tila).encryptor()
        salattu = salain.update(data) + salain.finalize()
        print(f"{nimi}: {nayta(salattu)}")
    # @loppu tilat


if __name__ == "__main__":
    main()
