"""Heksavedos: python3 heksa.py TIEDOSTO [ALKU] [PITUUS]

ALKU ja PITUUS voi antaa heksana (0x...). Tulosteen osoite on siirtymä
tiedoston alusta.
"""
import sys

from kuva import heksa


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    alku = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0
    pituus = int(sys.argv[3], 0) if len(sys.argv) > 3 else 64
    osa = data[alku:alku + pituus]
    for rivi in heksa(osa, alku, (len(osa) + 15) // 16):
        print(rivi)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
