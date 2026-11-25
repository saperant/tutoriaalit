"""Käynnistystesti: ajaa järjestelmän ja seuraa sarjakonsolia.

Testi kuvataan vaihetiedostossa, jonka rivit ovat

    odota  SEKUNNIT  SÄÄNNÖLLINEN-LAUSEKE
    laheta TEKSTI            (rivinvaihto lisätään loppuun)
    loppu  PALUUARVO         (järjestelmän on sammuttava itse)

Jokainen odotus etsii lauseketta konsolin tulosteesta edellisen osuman
jälkeen. Ytimen paniikki tai aikarajan ylitys päättää testin heti.
Testin oma tuloste ei sisällä konsolin raakatekstiä, joten se on
toistettava, vaikka ajoitukset ja osoitteet vaihtelevat.

Käyttö: python3 kaynnistystesti.py VAIHEET -- KOMENTO [ARGUMENTIT...]
"""

import os
import re
import selectors
import subprocess
import sys
import time
from dataclasses import dataclass

# Rivi otetaan vasta kokonaisena, muuten syy voisi katketa kesken.
PANIIKKI = re.compile(rb"Kernel panic - not syncing: ([^\r\n]*)\r?\n")


@dataclass
class Vaihe:
    tyyppi: str
    arvo: str
    aikaraja: float = 0.0


def lue_vaiheet(polku: str) -> list[Vaihe]:
    vaiheet = []
    with open(polku, encoding="utf-8") as f:
        for rivi in f:
            rivi = rivi.rstrip("\n")
            if not rivi.strip() or rivi.lstrip().startswith("#"):
                continue
            tyyppi, _, loput = rivi.partition(" ")
            loput = loput.strip()
            if tyyppi == "odota":
                sekunnit, _, lauseke = loput.partition(" ")
                vaiheet.append(
                    Vaihe(tyyppi, lauseke.strip(), float(sekunnit)))
            elif tyyppi in ("laheta", "loppu"):
                vaiheet.append(Vaihe(tyyppi, loput))
            else:
                raise ValueError(f"tuntematon vaihe: {rivi}")
    return vaiheet


# @alku konsoli
class Konsoli:
    """Lukee prosessin tulostetta ilman estoa ja kerää sen puskuriin."""

    def __init__(self, komento: list[str]) -> None:
        self.prosessi = subprocess.Popen(
            komento, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        assert self.prosessi.stdout is not None
        self.valitsin = selectors.DefaultSelector()
        self.valitsin.register(self.prosessi.stdout, selectors.EVENT_READ)
        self.puskuri = b""
        self.kohta = 0  # edellisen osuman loppu

    def lue(self, aikaraja: float) -> bool:
        """Lukee lisää tulostetta; False, kun tuloste on loppunut."""
        if not self.valitsin.select(aikaraja):
            return True
        assert self.prosessi.stdout is not None
        osa = os.read(self.prosessi.stdout.fileno(), 4096)
        self.puskuri += osa
        return bool(osa)

    def odota(self, lauseke: str, aikaraja: float) -> str:
        """Palauttaa osuman tai virheen kuvauksen alkaen 'VIRHE'."""
        kaava = re.compile(lauseke.encode())
        raja = time.monotonic() + aikaraja
        while True:
            osuma = kaava.search(self.puskuri, self.kohta)
            if osuma:
                self.kohta = osuma.end()
                return osuma.group(0).decode(errors="replace")
            paniikki = PANIIKKI.search(self.puskuri)
            if paniikki:
                syy = paniikki.group(1).decode(errors="replace")
                return f"VIRHE\n    ydinpaniikki: {syy}"
            jaljella = raja - time.monotonic()
            if jaljella <= 0:
                return f"VIRHE: aikaraja {aikaraja:g} s ylittyi"
            if not self.lue(jaljella):
                return "VIRHE: konsoli sulkeutui"
# @loppu konsoli

    def laheta(self, teksti: str) -> None:
        assert self.prosessi.stdin is not None
        self.prosessi.stdin.write(teksti.encode() + b"\n")
        self.prosessi.stdin.flush()

    def lopeta(self, aikaraja: float) -> int:
        """Odottaa prosessin päättymistä; aikarajan jälkeen se tapetaan."""
        raja = time.monotonic() + aikaraja
        while time.monotonic() < raja and self.lue(raja - time.monotonic()):
            pass
        try:
            return self.prosessi.wait(max(0.0, raja - time.monotonic()))
        except subprocess.TimeoutExpired:
            self.prosessi.kill()
            return self.prosessi.wait()

    def hanta(self, riveja: int) -> str:
        teksti = self.puskuri.decode(errors="replace").replace("\r", "")
        return "\n".join(teksti.splitlines()[-riveja:])


# @alku aja
def aja(vaiheet: list[Vaihe], komento: list[str]) -> int:
    konsoli = Konsoli(komento)
    for numero, vaihe in enumerate(vaiheet, 1):
        if vaihe.tyyppi == "odota":
            tulos = konsoli.odota(vaihe.arvo, vaihe.aikaraja)
            if tulos.startswith("VIRHE"):
                print(f"[{numero}] odota /{vaihe.arvo}/: {tulos}")
                if "paniikki" not in tulos:
                    print("--- konsolin viimeiset rivit ---")
                    print(konsoli.hanta(5))
                konsoli.prosessi.kill()
                konsoli.prosessi.wait()
                return 1
            print(f"[{numero}] odota /{vaihe.arvo}/: ok")
        elif vaihe.tyyppi == "laheta":
            konsoli.laheta(vaihe.arvo)
            print(f"[{numero}] laheta: {vaihe.arvo}")
        else:
            koodi = konsoli.lopeta(30)
            odotettu = int(vaihe.arvo)
            tila = "ok" if koodi == odotettu else f"VIRHE: saatiin {koodi}"
            print(f"[{numero}] loppu {odotettu}: {tila}")
            return 0 if koodi == odotettu else 1
    konsoli.prosessi.kill()
    konsoli.prosessi.wait()
    return 0
# @loppu aja


def main() -> int:
    if len(sys.argv) < 4 or sys.argv[2] != "--":
        print(__doc__, file=sys.stderr)
        return 2
    return aja(lue_vaiheet(sys.argv[1]), sys.argv[3:])


if __name__ == "__main__":
    sys.exit(main())
