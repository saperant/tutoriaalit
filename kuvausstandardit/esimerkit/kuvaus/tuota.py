"""Kaikki tuotetut tiedostot yhdestä paikasta.

``tuota()`` palauttaa hakemiston ``tuotettu/`` koko sisällön
(tiedostonimi -> teksti) kirjoittamatta mitään. Kutsuja päättää,
kirjoitetaanko tiedostot (``make paivita``) vai verrataanko niitä
tallennettuihin (``11-tahdissa.py`` ja CI).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from . import laitepuu, markdown, svd
from .ajo import aja
from .kaanna import RDL, kaanna

TUOTETTU = Path(__file__).resolve().parent.parent / "tuotettu"
LEVEYS = 78


# @alku peakrdl
def peakrdl(rdl: Path, alikomento: str, lahde: str, nimi: str,
            *liput: str) -> dict[str, str]:
    """Ajaa PeakRDL:n väliaikaiseen hakemistoon ja palauttaa tiedostot."""
    with tempfile.TemporaryDirectory() as tmp:
        kohde = Path(tmp) / nimi
        aja(["peakrdl", alikomento, str(rdl / lahde), "-I", str(rdl),
             "-o", str(kohde if "." in nimi else tmp), *liput])
        return {p.name: p.read_text("utf-8")
                for p in sorted(Path(tmp).iterdir()) if p.is_file()}
# @loppu peakrdl


def rivita(rivi: str) -> list[str]:
    """Rivittää liian pitkän rivin kirjan otteeseen välilyönnin kohdalta.
    Rivin lopun kommentti siirretään omalle rivilleen, jotta katkaisu ei
    osu kommentin sisään."""
    sisennys = len(rivi) - len(rivi.lstrip())
    if len(rivi) <= LEVEYS:
        return [rivi]
    koodi, _, kommentti = rivi.partition(" // ")
    tulos = ([" " * sisennys + "// " + kommentti.strip()]
             if kommentti else [])
    while len(koodi) > LEVEYS:
        katko = koodi.rfind(" ", sisennys + 1, LEVEYS)
        tulos.append(koodi[:katko])
        koodi = " " * (sisennys + 8) + koodi[katko + 1:]
    return tulos + [koodi]


# @alku ote
def ote(teksti: str, alku: str, loppu: str, mukaan: bool = False) -> str:
    """Rivit alkumerkkijonosta loppumerkkijonoon (``mukaan``: myös sen
    rivi), yhteinen sisennys poistettuna ja pitkät rivit rivitettyinä."""
    rivit = teksti.splitlines()
    a = next(i for i, r in enumerate(rivit) if alku in r)
    b = next(i for i, r in enumerate(rivit) if i > a and loppu in r)
    valitut = rivit[a:b + 1 if mukaan else b]
    pienin = min(len(r) - len(r.lstrip()) for r in valitut if r.strip())
    tulos = []
    for r in valitut:
        tulos += rivita(r[pienin:])
    return "\n".join(tulos).rstrip() + "\n"
# @loppu ote


# @alku tuota
def tuota(rdl: Path = RDL) -> dict[str, str]:
    tiedostot: dict[str, str] = {}
    for lahde in ("ajastin.rdl", "kayttaytyminen.rdl"):
        tiedostot |= peakrdl(rdl, "regblock", lahde, "",
                             "--cpuif", "apb4-flat", "--type-style", "hier",
                             "--err-if-bad-rw", "--hwif-report")
    tiedostot |= peakrdl(rdl, "c-header", "ajastin.rdl", "ajastin.h",
                         "--type-style", "hier")
    tiedostot |= peakrdl(rdl, "uvm", "ajastin.rdl", "ajastin_uvm.sv",
                         "--type-style", "hier")
    tiedostot |= peakrdl(rdl, "ip-xact", "ajastin.rdl", "ajastin.xml",
                         "--vendor", "esimerkki.invalid",
                         "--library", "oheislaitteet")
    ajastin = kaanna("ajastin.rdl", rdl=rdl)
    tiedostot["ajastin.md"] = markdown.dokumentti(ajastin, "rdl/ajastin.rdl")
    soc = kaanna("soc.rdl", rdl=rdl)
    tiedostot["soc.svd"] = svd.svd(soc)
    tiedostot["soc.dtsi"] = laitepuu.solmut(soc)
    tiedostot |= otteet(tiedostot)
    return tiedostot
# @loppu tuota


def otteet(t: dict[str, str]) -> dict[str, str]:
    """Kirjassa näytettävät otteet tuotetuista tiedostoista."""
    return {
        "otteet/regblock_valmis.sv": ote(
            t["ajastin.sv"], "// Field: ajastin.STATUS.VALMIS",
            "// Field: ajastin.VERTAA.ARVO"),
        "otteet/regblock_lukumux.sv": ote(
            t["ajastin.sv"], "if(rd_mux_addr == 4'h0)",
            "readback_data = readback_data_var;"),
        "otteet/uvm_status.sv": ote(
            t["ajastin_uvm.sv"], "// reg - ajastin.STATUS",
            "// reg - ajastin.LASKURI"),
        "otteet/uvm_lohko.sv": ote(
            t["ajastin_uvm.sv"], "this.default_map = create_map",
            'this.LASKURI = new("LASKURI");'),
        "otteet/ipxact_status.xml": ote(
            t["ajastin.xml"], "<ipxact:name>STATUS</ipxact:name>",
            "</ipxact:register>"),
        "otteet/svd_ajastin1.xml": ote(
            t["soc.svd"], 'derivedFrom="AJASTIN0"', "</peripheral>",
            mukaan=True),
        "otteet/svd_kanava.xml": ote(
            t["soc.svd"], "<cluster>", "</register>", mukaan=True),
    }


# @alku vertaa
def vertaa(hakemisto: Path = TUOTETTU, rdl: Path = RDL) -> list[str]:
    """Tiedostot, jotka puuttuvat tai poikkeavat tuoreesta tuotoksesta."""
    poikkeavat = []
    for nimi, sisalto in tuota(rdl).items():
        polku = hakemisto / nimi
        if not polku.exists() or polku.read_text("utf-8") != sisalto:
            poikkeavat.append(nimi)
    return poikkeavat
# @loppu vertaa


def kirjoita(hakemisto: Path = TUOTETTU) -> None:
    for nimi, sisalto in tuota().items():
        polku = hakemisto / nimi
        polku.parent.mkdir(parents=True, exist_ok=True)
        polku.write_text(sisalto, encoding="utf-8")
