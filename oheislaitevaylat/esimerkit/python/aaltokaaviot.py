"""Kirjan ajoituskaaviot protokollamalleista.

Kaaviot tuotetaan samoista malleista, joita esimerkit ja testit
käyttävät, joten kaavio ei voi erkaantua mallista:

    python3 aaltokaaviot.py tarkista ../kaaviot   vertaa tallennettuihin
    python3 aaltokaaviot.py kirjoita ../kaaviot   kirjoittaa uudelleen

Muoto on WaveDromin JSON-osajoukko, jonka yhteiset/kaaviot.py piirtää.
"""

import json
import sys
from pathlib import Path
from typing import Any

from mallit.can import (ACK_PAIKKA, DOMINANTTI, Kehys, arbitraatio,
                        lahetettavat, tayta)
from mallit.i2c import Isanta, Rekisterilaite, simuloi
from mallit.spi import siirto
from mallit.uart import Kehysmuoto, kehyksen_bitit
from mallit.aalto import Aalto


def uart_kehys() -> dict[str, Any]:
    """0x4B muodossa 8E1: lepo, START, data LSB ensin, pariteetti, STOP."""
    muoto = Kehysmuoto(pariteetti="E")
    aalto = Aalto(["TX"])
    aalto.lisaa(1, merkinta="lepo")
    nimet = (["START"] + [f"d{i}" for i in range(muoto.databitit)]
             + ["P"] + ["STOP"] * muoto.stopbitit)
    for bitti, nimi in zip(kehyksen_bitit(0x4B, muoto), nimet, strict=True):
        aalto.lisaa(bitti, merkinta=nimi)
    aalto.lisaa(1, merkinta="lepo")
    return {"signal": aalto.wavedrom("bitti"),
            "config": {"hscale": 1.0}}


def spi_moodit() -> dict[str, Any]:
    """Sama siirto (isäntä 0xA5, laite 0x3C) moodeissa 0 ja 3."""
    ryhmat: list[Any] = []
    for moodi in (0, 3):
        s = siirto([0xA5], [0x3C], moodi)
        ryhmat.append([f"moodi {moodi}", *s.aalto.wavedrom("näyte")])
    return {"signal": ryhmat, "config": {"hscale": 0.7}}


def i2c_osoite() -> dict[str, Any]:
    """Siirron alku: START, osoitetavu 0x90 (0x48, kirjoitus) ja ACK."""
    anturi = Rekisterilaite(0x48, bytearray([0x00, 0x60]))
    isanta = Isanta([(0x48, bytes([0x01]), 1)])
    aalto = simuloi([isanta, anturi], 120).osa(0, 44)
    scl, sda = aalto.signaali("SCL"), aalto.signaali("SDA")
    # START: SDA laskee SCL:n ollessa ylhäällä. Bitit luetaan SCL:n
    # nousevilla reunoilla: 7 osoitebittiä, R/W ja kuittaus.
    merkinnat = {t: "START" for t in range(1, len(sda))
                 if scl[t] and sda[t - 1] and not sda[t]}
    nousut = [t for t in range(1, len(scl)) if scl[t] and not scl[t - 1]]
    nimet = [*(str(sda[t]) for t in nousut[:7]), "W", "ACK"]
    merkinnat.update(zip(nousut, nimet, strict=False))
    aalto.merkinnat = merkinnat
    return {"signal": aalto.wavedrom("bitti"),
            "config": {"hscale": 0.38}}


def can_arbitraatio() -> dict[str, Any]:
    """Kolme solmua aloittaa yhtä aikaa; väylä on johdotettu JA."""
    kehykset = [Kehys(0x65A, b"\x01"), Kehys(0x123, b"\x02"),
                Kehys(0x12F, b"\x03")]
    tulos = arbitraatio(kehykset)
    leveys = 14
    signaalit: list[dict[str, Any]] = []
    for n, kehys in enumerate(kehykset):
        jono = lahetettavat(kehys)[:leveys]
        loppu = tulos.havisi.get(n, leveys)
        # Hävinnyt solmu jää kuuntelemaan: sen lähtö on resessiivinen.
        tx = [b if i <= loppu else 1 for i, b in enumerate(jono)]
        signaalit.append({"name": f"{kehys.tunniste:#05x}",
                          "wave": aallot(tx)})
    signaalit.append({})
    signaalit.append({"name": "väylä", "wave": aallot(tulos.vayla[:leveys])})
    # Kentät: SOF, tunnisteen bitit 10..0, RTR ja IDE (näissä
    # tunnisteissa ei ole täytebittejä ensimmäisten 14 bitin aikana).
    kentat = ["SOF", *(str(i) for i in range(10, -1, -1)), "RTR", "IDE"]
    signaalit.append({"name": "kenttä", "wave": "=" * leveys,
                      "data": kentat[:leveys]})
    return {"signal": signaalit, "config": {"hscale": 0.8}}


def can_kehys() -> dict[str, Any]:
    """Kokonainen datakehys 0x123, data 00 ff: kentät ja täytebitit.

    Sama kehys kuin esimerkissä can_kehys.py. Yhden bitin kentillä on
    lyhyet nimet: S = SOF, R = RTR, I = IDE, r = r0, e = erotin,
    A = ACK-paikka.
    """
    kehys = Kehys(0x123, bytes([0x00, 0xFF]))
    lyhyet = {"SOF": "S", "RTR": "R", "IDE": "I", "r0": "r"}
    nimet: list[str] = []          # kentän nimi täyttämätöntä bittiä kohti
    for nimi, kentta in kehys.kentat():
        nimet += [lyhyet.get(nimi, nimi)] * len(kentta)
    _, taytteet = tayta([b for _, k in kehys.kentat() for b in k])
    linja = lahetettavat(kehys)
    linja[ACK_PAIKKA] = DOMINANTTI   # vastaanottaja kuittaa
    kentat: list[str] = []
    for i in range(len(nimet) + len(taytteet)):
        # Täytebitti kuuluu samaan kenttään kuin sitä edeltävä bitti.
        kentat.append(kentat[-1] if i in taytteet
                      else nimet[len(kentat) - sum(t < i for t in taytteet)])
    kentat += ["e", "A", "e", *["EOF"] * 7]
    aalto, data = "", []
    for i, nimi in enumerate(kentat):
        if i and nimi == kentat[i - 1] and nimi != "e":
            aalto += "."
        else:
            aalto += "="
            data.append(nimi)
    tayte = [1 if i in taytteet else 0 for i in range(len(linja))]
    return {"signal": [{"name": "väylä", "wave": aallot(linja)},
                       {"name": "kenttä", "data": data, "wave": aalto},
                       {"name": "täytebitti", "wave": aallot(tayte)}],
            "config": {"hscale": 0.24}}


def can_bitti() -> dict[str, Any]:
    """Bitin jako aikakvantteihin: ensimmäinen rivi esimerkin
    can_ajoitus.py testatusta tulosteesta (8 MHz, 1 Mbit/s)."""
    rivi = Path(__file__).with_name("can_ajoitus.odotettu").read_text(
        encoding="utf-8").splitlines()[1].split()
    # Sarakkeet: kello, "MHz", nopeus, BRP, TQ, TSEG1, TSEG2, ...
    kvantteja, tseg1, tseg2 = int(rivi[4]), int(rivi[5]), int(rivi[6])
    if 1 + tseg1 + tseg2 != kvantteja:
        raise ValueError("SYNC + TSEG1 + TSEG2 ei ole bitin pituus")
    bitteja = 2
    kvantit = [str(q + 1) for _ in range(bitteja) for q in range(kvantteja)]
    segmentti = ("=" + "=" + "." * (tseg1 - 1) + "=" + "." * (tseg2 - 1))
    # Arvo luetaan TSEG1:n lopussa: sitä ennen se on tuntematon.
    nayte = "x" + "." * tseg1 + "=" + "." * (tseg2 - 1)
    return {"signal": [
        {"name": "aikakvantti", "wave": "=" * len(kvantit), "data": kvantit},
        {"name": "segmentti", "wave": segmentti * bitteja,
         "data": ["SYNC", "TSEG1", "TSEG2"] * bitteja},
        {"name": "bitti väylällä",
         "wave": ("=" + "." * (kvantteja - 1)) * bitteja,
         "data": [f"bitti {i + 1}" for i in range(bitteja)]},
        {"name": "luettu arvo", "wave": nayte * bitteja,
         "data": [f"bitti {i + 1}" for i in range(bitteja)]},
    ], "config": {"hscale": 1.1}}


def aallot(bitit: list[int]) -> str:
    tulos = ""
    edellinen: int | None = None
    for b in bitit:
        tulos += "." if b == edellinen else ("h" if b else "l")
        edellinen = b
    return tulos


KAAVIOT = {
    "uart-kehys": uart_kehys,
    "spi-moodit": spi_moodit,
    "i2c-osoite": i2c_osoite,
    "can-arbitraatio": can_arbitraatio,
    "can-kehys": can_kehys,
    "can-bitti": can_bitti,
}


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] not in ("tarkista", "kirjoita"):
        print(__doc__, file=sys.stderr)
        return 2
    hakemisto = Path(sys.argv[2])
    virheita = 0
    for nimi, tuota in KAAVIOT.items():
        teksti = json.dumps(tuota(), indent=1, ensure_ascii=False) + "\n"
        polku = hakemisto / f"{nimi}.json"
        if sys.argv[1] == "kirjoita":
            polku.write_text(teksti, encoding="utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != teksti:
            print(f"VIRHE: kaavio {nimi} ei vastaa mallia "
                  "(aaltokaaviot.py kirjoita)")
            virheita += 1
    return 1 if virheita else 0


if __name__ == "__main__":
    sys.exit(main())
