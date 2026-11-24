"""Työkalujen raporttien ja lokien jäsentimet.

Jokainen jäsennin palauttaa yhteisen tietomallin olion (vuo.malli).
Jäsennin hylkää raportin, jota se ei ymmärrä, eikä arvaa.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from vuo.malli import Ajoitus, Resurssit, SimTulos, Varoitus


class RaporttiVirhe(ValueError):
    """Raportti on vajaa tai ristiriitainen."""


# @alku yosys
def lue_yosys_stat(polku: Path) -> Resurssit:
    """Yosysin `stat -json` -tuloste. Ylimmän tason moduuli on ainoa."""
    data = json.loads(polku.read_text(encoding="utf-8"))
    moduulit = data["modules"]
    if len(moduulit) != 1:
        raise RaporttiVirhe(f"odotettiin yksi moduuli: {list(moduulit)}")
    (tiedot,) = moduulit.values()
    tyypit: dict[str, int] = tiedot["num_cells_by_type"]
    kiikut = sum(n for t, n in tyypit.items() if "DFF" in t)
    return Resurssit(tiedot["num_cells"], kiikut,
                     dict(sorted(tyypit.items())))


def lue_ltp(teksti: str) -> int:
    """Yosysin `ltp`: pisimmän kombinaatiopolun pituus."""
    osuma = re.search(r"\(length=(\d+)\)", teksti)
    if not osuma:
        raise RaporttiVirhe("ltp-raportista puuttuu length=")
    return int(osuma.group(1))
# @loppu yosys


# @alku sta
STA_KENTAT = {
    "jakso": r"jakso\s+([\d.]+) ns",
    "syvyys": r"Polun syvyys:\s+(\d+)",
    "saapuminen": r"saapumisaika\s+(-?[\d.]+)",
    "vaadittu": r"vaadittu aika\s+(-?[\d.]+)",
    "slack": r"slack\s+(-?[\d.]+) \((MET|VIOLATED)\)",
}


def lue_sta(teksti: str) -> Ajoitus:
    """opetus-sta:n ajoitusraportti tarkistuksineen."""
    arvot: dict[str, float] = {}
    for nimi, kuvio in STA_KENTAT.items():
        osuma = re.search(kuvio, teksti)
        if not osuma:
            raise RaporttiVirhe(f"ajoitusraportista puuttuu {nimi}")
        arvot[nimi] = float(osuma.group(1))
    tila = re.search(r"\((MET|VIOLATED)\)", teksti)
    ajoitus = Ajoitus(arvot["jakso"], arvot["saapuminen"],
                      arvot["vaadittu"], arvot["slack"],
                      int(arvot["syvyys"]))
    # Raportin sisäinen johdonmukaisuus: pyöristys on kaksi desimaalia.
    if abs(ajoitus.vaadittu - ajoitus.saapuminen - ajoitus.slack) > 0.011:
        raise RaporttiVirhe("slack ei ole vaadittu - saapumisaika")
    if tila and (tila.group(1) == "MET") != ajoitus.kunnossa:
        raise RaporttiVirhe("MET/VIOLATED ei vastaa slackin etumerkkiä")
    return ajoitus
# @loppu sta


# @alku verilator
VERILATOR = re.compile(
    r"^%(?P<laji>Warning|Error)(?:-(?P<koodi>[A-Z0-9_]+))?: "
    r"(?P<tiedosto>[^:\s]+):(?P<rivi>\d+):(?:\d+:)? (?P<viesti>.*)$")


def suhteellinen(tiedosto: str, juuri: Path | None) -> str:
    polku = Path(tiedosto)
    if juuri is not None and polku.is_absolute():
        try:
            return polku.relative_to(juuri).as_posix()
        except ValueError:
            pass
    return polku.as_posix()


def lue_verilator(teksti: str, juuri: Path | None = None) -> list[Varoitus]:
    """Verilatorin varoitukset. Jatkorivit (lähdekoodi, vihjeet)
    alkavat välilyönnillä, joten ne eivät osu kuvioon."""
    tulos = []
    for rivi in teksti.splitlines():
        if osuma := VERILATOR.match(rivi):
            koodi = osuma["koodi"] or osuma["laji"].upper()
            tulos.append(Varoitus(
                "verilator", koodi,
                suhteellinen(osuma["tiedosto"], juuri),
                int(osuma["rivi"]), osuma["viesti"]))
    return tulos
# @loppu verilator


# @alku icarus
ICARUS = re.compile(r"^(?P<tiedosto>[^:\s]+):(?P<rivi>\d+): "
                    r"(?:vvp\.tgt )?(?P<laji>sorry|warning|error): "
                    r"(?P<viesti>.*)$")


def lue_icarus(teksti: str, juuri: Path | None = None) -> list[Varoitus]:
    """Icarus Verilogin ilmoitukset; "sorry" on työkalun rajoitus."""
    return [Varoitus("icarus", o["laji"].upper(),
                     suhteellinen(o["tiedosto"], juuri), int(o["rivi"]),
                     o["viesti"])
            for r in teksti.splitlines() if (o := ICARUS.match(r))]
# @loppu icarus


# @alku sim
def lue_simulointi(teksti: str, testi: str, siemen: int) -> SimTulos:
    """Testipenkin oma tulosrivi ratkaisee, ei simulaattorin
    paluuarvo: simulaattori palauttaa nollan myös hylätystä testistä."""
    virheet = tuple(r for r in teksti.splitlines() if r.startswith("VIRHE"))
    if re.search(r"^TESTI OK", teksti, re.M):
        return SimTulos(testi, siemen, "ok")
    if osuma := re.search(r"^TESTI EPÄONNISTUI (\d+)", teksti, re.M):
        return SimTulos(testi, siemen, "virhe", int(osuma.group(1)), virheet)
    if "*** aikakatkaisu" in teksti:
        return SimTulos(testi, siemen, "aikakatkaisu")
    return SimTulos(testi, siemen, "virhe", 0, ("ei tulosriviä",))


def lue_kattavuus(teksti: str) -> dict[str, int]:
    """Testipenkin tulostamat kattavuuslokerot: nimi -> osumat."""
    kuvio = re.compile(r"^KATTAVUUS (.+) osumia=(\d+)$", re.M)
    return {o.group(1): int(o.group(2)) for o in kuvio.finditer(teksti)}
# @loppu sim
