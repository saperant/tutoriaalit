"""objdumpin purkutulosteen jäsentäminen analyysiskripteille.

Funktio `pura` ajaa objdumpin Intel-syntaksilla ja palauttaa kunkin
funktion käskyt. Analyysit käsittelevät käskyjä osoitteineen, mutta
tulostavat vain osoitteista riippumattomia tuloksia.
"""

import re
import subprocess
from dataclasses import dataclass

RIVI = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+?)\s*\t(\S+)\s*(.*)$")
FUNKTIO = re.compile(r"^([0-9a-f]+) <(.+)>:$")
ETULIITTEET = ("notrack", "bnd", "rep", "repz", "repnz", "lock")
KOHDE = re.compile(r"^([0-9a-f]+) <(.+)>$")


@dataclass(frozen=True)
class Kasky:
    """Yksi purettu käsky."""

    osoite: int
    tavut: bytes
    nimi: str
    operandit: str

    @property
    def kohde(self) -> int | None:
        """Suoran hypyn tai kutsun kohdeosoite, muuten None."""
        osuma = KOHDE.match(self.operandit)
        return int(osuma.group(1), 16) if osuma else None

    @property
    def kohdenimi(self) -> str:
        """Suoran hypyn tai kutsun kohde symbolina, esim. 'puts@plt'."""
        osuma = KOHDE.match(self.operandit)
        return osuma.group(2) if osuma else ""

    @property
    def on_hyppy(self) -> bool:
        """Onko käsky ehdollinen tai ehdoton hyppy."""
        return self.nimi.startswith("j")


def pura(tiedosto: str, *valitsimet: str) -> dict[str, list[Kasky]]:
    """Purkaa tiedoston .text-osion funktioittain."""
    tuloste = subprocess.run(
        ["objdump", "-d", "-w", "-M", "intel", "-j", ".text",
         *valitsimet, tiedosto],
        check=True, capture_output=True, text=True).stdout
    funktiot: dict[str, list[Kasky]] = {}
    nykyinen: list[Kasky] = []
    for rivi in tuloste.splitlines():
        if osuma := FUNKTIO.match(rivi):
            nykyinen = funktiot.setdefault(osuma.group(2), [])
        elif osuma := RIVI.match(rivi):
            tavut = bytes.fromhex(osuma.group(2).replace(" ", ""))
            nimi = osuma.group(3)
            operandit = re.sub(r"\s+", " ", osuma.group(4)).strip()
            if nimi in ETULIITTEET and " " in operandit:
                nimi, operandit = operandit.split(" ", 1)
            nykyinen.append(Kasky(int(osuma.group(1), 16), tavut,
                                  nimi, operandit))
    return funktiot


def ilman_tayttoa(kaskyt: list[Kasky]) -> list[Kasky]:
    """Poistaa kohdistuksen täytteeksi lisätyt nop-käskyt."""
    return [k for k in kaskyt
            if k.nimi not in ("nop", "data16", "cs")
            and k.operandit != "ax,ax"]


def osiot(tiedosto: str) -> list[tuple[str, int, int, int]]:
    """Muistiin ladattavat osiot: (nimi, osoite, tiedostosiirtymä, koko)."""
    tuloste = subprocess.run(["readelf", "-SW", tiedosto], check=True,
                             capture_output=True, text=True).stdout
    tulos = []
    for osuma in re.finditer(r"\]\s+(\S+)\s+\S+\s+([0-9a-f]{16})\s+"
                             r"([0-9a-f]+)\s+([0-9a-f]+)", tuloste):
        osoite = int(osuma.group(2), 16)
        if osoite != 0:
            tulos.append((osuma.group(1), osoite, int(osuma.group(3), 16),
                          int(osuma.group(4), 16)))
    return tulos


def lue(tiedosto: str, osoite: int, koko: int) -> bytes:
    """Lukee tiedostosta muistiosoitetta vastaavat tavut."""
    for _, alku, siirtyma, pituus in osiot(tiedosto):
        if alku <= osoite < alku + pituus:
            with open(tiedosto, "rb") as f:
                f.seek(siirtyma + osoite - alku)
                return f.read(koko)
    raise ValueError(f"osoite {osoite:#x} ei ole missään osiossa")


def osio(tiedosto: str, osoite: int) -> str:
    """Sen osion nimi, johon osoite kuuluu, tai '?'."""
    for nimi, alku, _, pituus in osiot(tiedosto):
        if alku <= osoite < alku + pituus:
            return nimi
    return "?"
