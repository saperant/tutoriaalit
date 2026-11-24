"""Funktioiden rajat ja nimet riisutusta ohjelmasta.

Käyttö: python3 riisuttu.py RIISUTTU KIRJASTO.o [SYMBOLILLINEN]

1. Funktioiden rajat luetaan poikkeustenkäsittelyn taulusta .eh_frame,
   joka jää ohjelmaan riisumisen jälkeenkin: jokaisella funktiolla on
   oma FDE-tietue (frame description entry) osoitealueineen.
2. Tulokohta luetaan ELF-otsakkeesta. Sen koodi (glibc:n _start)
   välittää main-funktion osoitteen rekisterissä rdi funktiolle
   __libc_start_main.
3. Kirjaston funktiot tunnistetaan allekirjoituksilla: objektitiedoston
   funktioiden tavut, joista relokaatioiden täyttämät kohdat on
   peitetty, verrataan ohjelman funktioihin.

Jos symbolillinen versio annetaan, tulokset tarkistetaan sen
symbolitaulua vasten. Tuloste ei sisällä osoitteita.
"""

import re
import subprocess
import sys

from purku import lue, osio, pura

FDE = re.compile(r"FDE cie=\w+ pc=([0-9a-f]+)\.\.([0-9a-f]+)")
RELO = re.compile(r"\t([0-9a-f]+): R_X86_64_\w+")


def aja(*komento: str) -> str:
    return subprocess.run(komento, check=True, capture_output=True,
                          text=True).stdout


def fde_alueet(tiedosto: str) -> list[tuple[int, int]]:
    """Funktioiden osoitealueet .eh_frame-taulusta."""
    tuloste = aja("readelf", "--debug-dump=frames", tiedosto)
    return sorted((int(a, 16), int(b, 16)) for a, b in FDE.findall(tuloste))


# @alku allekirjoitus
def allekirjoitukset(objekti: str) -> dict[str, list[int | None]]:
    """Objektitiedoston funktioiden tavut; relokaatiot peitetty (None)."""
    koot = {}
    for rivi in aja("nm", "-S", "--defined-only", objekti).splitlines():
        kentat = rivi.split()
        if len(kentat) == 4 and kentat[2] in "Tt":
            koot[kentat[3]] = (int(kentat[0], 16), int(kentat[1], 16))
    tavut: dict[int, int | None] = {}
    for k in [k for kk in pura(objekti).values() for k in kk]:
        for i, tavu in enumerate(k.tavut):
            tavut[k.osoite + i] = tavu
    for rivi in aja("objdump", "-dr", "-w", objekti).splitlines():
        for osuma in RELO.finditer(rivi):
            alku = int(osuma.group(1), 16)
            for i in range(4):
                tavut[alku + i] = None
    return {nimi: [tavut[a] for a in range(alku, alku + koko)]
            for nimi, (alku, koko) in koot.items()}


def sopii(malli: list[int | None], data: bytes) -> bool:
    """Vastaako data allekirjoitusta peitettyjä kohtia lukuun ottamatta."""
    return len(malli) == len(data) and all(
        m is None or m == d for m, d in zip(malli, data, strict=True))
# @loppu allekirjoitus


def tulokohta(tiedosto: str) -> int:
    tuloste = aja("readelf", "-h", tiedosto)
    osuma = re.search(r"Entry point address:\s+0x([0-9a-f]+)", tuloste)
    assert osuma, "tulokohta puuttuu"
    return int(osuma.group(1), 16)


def main_osoite(tiedosto: str, alku: int, loppu: int) -> int | None:
    """main-funktion osoite _start-koodin lea rdi -käskystä."""
    kaskyt = [k for kk in pura(tiedosto).values() for k in kk
              if alku <= k.osoite < loppu]
    for k in kaskyt:
        osuma = re.match(r"^rdi,\[rip\+0x([0-9a-f]+)\]", k.operandit)
        if k.nimi == "lea" and osuma:
            siirtyma = int(osuma.group(1), 16)
            return (k.osoite + len(k.tavut) + siirtyma) % 2**64
    return None


def main() -> None:
    riisuttu, objekti = sys.argv[1], sys.argv[2]
    todelliset: dict[int, str] = {}
    if len(sys.argv) > 3:
        for rivi in aja("nm", "--defined-only", sys.argv[3]).splitlines():
            kentat = rivi.split()
            if kentat[1] in "Tt":
                todelliset[int(kentat[0], 16)] = kentat[2]
    mallit = allekirjoitukset(objekti)
    alueet = fde_alueet(riisuttu)
    alku_osoite = tulokohta(riisuttu)
    paaohjelma = None
    for alku, loppu in alueet:
        if alku == alku_osoite:
            paaohjelma = main_osoite(riisuttu, alku, loppu)
    print(f"FDE-tietueita: {len(alueet)}")
    print(f"{'nro':<4} {'osio':<9} {'koko':>5}  {'päätelmä':<26} "
          "symbolitaulussa")
    for nro, (alku, loppu) in enumerate(alueet, 1):
        nimi = osio(riisuttu, alku)
        data = lue(riisuttu, alku, loppu - alku)
        if nimi != ".text":
            paatelma = "PLT-koodia"
        elif alku == alku_osoite:
            paatelma = "tulokohta (_start)"
        elif alku == paaohjelma:
            paatelma = "main (lea rdi _startissa)"
        else:
            osumat = [n for n, m in mallit.items() if sopii(m, data)]
            paatelma = ("kirjasto: " + ", ".join(osumat) if osumat
                        else "tuntematon")
        oikea = todelliset.get(alku, "-")
        print(f"{nro:<4} {nimi:<9} {loppu - alku:>5}  {paatelma:<26} "
              f"{oikea}")


if __name__ == "__main__":
    main()
