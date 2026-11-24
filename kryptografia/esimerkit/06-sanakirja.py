"""Miksi nopea tiiviste ei sovi salasanoille: vuotaneen tietokannan murto."""

import hashlib
import os

YLEISET = ["123456", "salasana", "qwerty", "kesä2026", "Salasana1",
           "aurinko", "iloinen-kissa-hyppii-aidalla"]


def sha(salasana: str, suola: bytes = b"") -> str:
    return hashlib.sha256(suola + salasana.encode()).hexdigest()


def main() -> None:
    kayttajat = {"aino": "kesä2026", "bertta": "Salasana1",
                 "cecilia": "Hjk#82-vXq!2", "daniel": "kesä2026"}

    # @alku suolaton
    vuoto = {k: sha(s) for k, s in kayttajat.items()}
    taulu = {sha(s): s for s in YLEISET}       # lasketaan kerran
    murretut = {k: taulu[t] for k, t in vuoto.items() if t in taulu}
    print("suolaton: murrettu", len(murretut), "/", len(vuoto))
    print("samat tiivisteet paljastavat saman salasanan:",
          vuoto["aino"] == vuoto["daniel"])
    # @loppu suolaton

    # @alku suolattu
    suolat = {k: os.urandom(16) for k in kayttajat}
    suolattu = {k: sha(s, suolat[k]) for k, s in kayttajat.items()}
    print("suolattu: samat tiivisteet:",
          suolattu["aino"] == suolattu["daniel"])
    # Suola estää valmiit taulukot, mutta jokaisen käyttäjän arvaukset
    # ovat yhä halpoja: SHA-256:ta lasketaan miljardeja sekunnissa.
    murrettuja = sum(1 for k in suolattu for s in YLEISET
                    if sha(s, suolat[k]) == suolattu[k])
    print("suolattu: murrettu", murrettuja, "/", len(suolattu))
    # @loppu suolattu


if __name__ == "__main__":
    main()
