"""Rekonstruoi C++-luokkien virtuaalitaulut ja RTTI:n ELF-tiedostosta.

Käyttö: python3 vtaulu.py OHJELMA LUOKKA...

Paikkariippumattomassa ohjelmassa virtuaalitaulujen osoitteet ovat
dynaamisia relokaatioita: R_X86_64_RELATIVE-relokaation lisäys on
kohteen osoite ohjelmassa, R_X86_64_64 viittaa kirjaston symboliin.
Skripti lukee taulun paikat relokaatioista ja nimeää ne symbolitaulun
avulla. Tuloste ei sisällä osoitteita.
"""

import re
import subprocess
import sys

from purku import lue

RELOKAATIO = re.compile(r"^([0-9a-f]+)\s+[0-9a-f]+\s+(R_X86_64_\w+)\s+"
                        r"(?:([0-9a-f]+)\s*$"
                        r"|[0-9a-f]+\s+(\S+) \+ ([0-9a-f]+))")


def aja(*komento: str) -> str:
    return subprocess.run(komento, check=True, capture_output=True,
                          text=True).stdout


def symbolit(tiedosto: str) -> dict[int, tuple[str, int]]:
    """Osoite -> (symbolin nimi, koko) määritellyille symboleille."""
    tulos = {}
    for rivi in aja("nm", "-S", "--defined-only", tiedosto).splitlines():
        kentat = rivi.split()
        if len(kentat) != 4:
            continue
        osoite = int(kentat[0], 16)
        # Samassa osoitteessa voi olla useita nimiä (esim. purkajien
        # D1- ja D2-muodot); kantaolion purkaja D2 jää toissijaiseksi.
        if osoite in tulos and kentat[3].endswith("D2Ev"):
            continue
        tulos[osoite] = (kentat[3], int(kentat[1], 16))
    return tulos


def relokaatiot(tiedosto: str) -> dict[int, tuple[str, int]]:
    """Paikan osoite -> (kohdesymboli tai '', lisäys)."""
    tulos = {}
    for rivi in aja("readelf", "-rW", tiedosto).splitlines():
        if osuma := RELOKAATIO.match(rivi):
            paikka = int(osuma.group(1), 16)
            if osuma.group(2) == "R_X86_64_RELATIVE":
                tulos[paikka] = ("", int(osuma.group(3), 16))
            elif osuma.group(4):
                nimi = osuma.group(4).split("@")[0]
                tulos[paikka] = (nimi, int(osuma.group(5), 16))
    return tulos


def puretut(nimet: list[str]) -> dict[str, str]:
    """C++-nimien purku c++filtillä."""
    tuloste = subprocess.run(["c++filt"], input="\n".join(nimet),
                             check=True, capture_output=True, text=True)
    return dict(zip(nimet, tuloste.stdout.splitlines(), strict=True))


def main() -> None:
    tiedosto = sys.argv[1]
    syms = symbolit(tiedosto)
    nimella = {nimi: (osoite, koko) for osoite, (nimi, koko) in syms.items()}
    relot = relokaatiot(tiedosto)
    nimet = [nimi for nimi, _ in syms.values()]
    nimet += [nimi for nimi, _ in relot.values() if nimi]
    selko = puretut(sorted(set(nimet)))

    def kuvaa(paikka: int) -> str:
        """Yhden 8 tavun paikan sisältö luettavana."""
        if paikka not in relot:
            arvo = int.from_bytes(lue(tiedosto, paikka, 8), "little",
                                  signed=True)
            return f"{arvo} (siirtymä olion alkuun)"
        nimi, lisays = relot[paikka]
        if nimi:
            return f"{selko[nimi]} + {lisays}"
        kohde = syms.get(lisays)
        if kohde is None:
            return "tuntematon kohde"
        if kohde[0].startswith("_ZTS"):
            teksti = lue(tiedosto, lisays, kohde[1]).rstrip(b"\0")
            return f'{selko[kohde[0]]} = "{teksti.decode()}"'
        tyyppi = {"D0Ev": " [poistava purkaja]",
                  "D1Ev": " [täydellinen purkaja]"}.get(kohde[0][-4:], "")
        return selko[kohde[0]] + tyyppi

    for luokka in sys.argv[2:]:
        mangled = f"{len(luokka)}{luokka}"
        if f"_ZTV{mangled}" in nimella:
            alku, koko = nimella[f"_ZTV{mangled}"]
            print(f"vtable for {luokka}: {koko // 8} paikkaa")
            for n in range(koko // 8):
                merkki = "  <- olion vptr" if n == 2 else ""
                print(f"  [{n}] {kuvaa(alku + 8 * n)}{merkki}")
        else:
            print(f"vtable for {luokka}: ei ohjelmassa")
        alku, koko = nimella[f"_ZTI{mangled}"]
        print(f"typeinfo for {luokka}: {koko // 8} paikkaa")
        for n in range(koko // 8):
            print(f"  [{n}] {kuvaa(alku + 8 * n)}")


if __name__ == "__main__":
    main()
