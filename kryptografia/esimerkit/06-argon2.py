"""Salasanan tallennus ja tarkistus Argon2id:llä."""

import os

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id

# @alku asetukset
# OWASP:n vähimmäissuositus: 19 MiB muistia, 2 kierrosta, 1 kaista.
MUISTI_KIB = 19 * 1024
KIERROKSET = 2
# @loppu asetukset


# @alku tallennus
def tiivista(salasana: str) -> str:
    """Palauttaa PHC-merkkijonon, jossa ovat algoritmi, asetukset ja suola."""
    kdf = Argon2id(salt=os.urandom(16), length=32, iterations=KIERROKSET,
                   lanes=1, memory_cost=MUISTI_KIB)
    return kdf.derive_phc_encoded(salasana.encode())


def tarkista(salasana: str, tallennettu: str) -> bool:
    try:
        Argon2id.verify_phc_encoded(salasana.encode(), tallennettu)
    except InvalidKey:
        return False
    return True


def vaatii_uudelleentiivistyksen(tallennettu: str) -> bool:
    """Asetuksia on kiristetty: päivitä tiiviste onnistuneen kirjautumisen
    yhteydessä, kun selväkielinen salasana on hetken käytettävissä."""
    asetukset = tallennettu.split("$")[3]
    return asetukset != f"m={MUISTI_KIB},t={KIERROKSET},p=1"
# @loppu tallennus


def main() -> None:
    tallennettu = tiivista("iloinen-kissa-hyppii-aidalla")
    print("muoto:", "$".join(tallennettu.split("$")[:4]) + "$...")
    print("oikea salasana:", tarkista("iloinen-kissa-hyppii-aidalla",
                                      tallennettu))
    print("väärä salasana:", tarkista("iloinen-koira", tallennettu))
    print("sama salasana, eri tiiviste:",
          tiivista("abc") != tiivista("abc"))
    vanha = "$argon2id$v=19$m=4096,t=3,p=1$c3VvbGE$aGFzaA"
    print("vanha tiiviste päivitetään:", vaatii_uudelleentiivistyksen(vanha))


if __name__ == "__main__":
    main()
