"""Tuottaa esimerkkien glTF-resurssit: hahmo.gltf ja taso.gltf.

Käyttö: python3 tee_resurssit.py [kohdehakemisto]

Koordinaatit lasketaan vain peruslaskutoimituksilla ja neliöjuurella,
joten tiedostot ovat tavulleen samat jokaisella koneella. Testi vertaa
tulosta versionhallinnassa oleviin tiedostoihin.
"""

from __future__ import annotations

import json
import math
import re
import struct
import sys
from pathlib import Path
from typing import Any

Vec = tuple[float, float, float]


# @alku puskuri
class Puskuri:
    """Kokoaa binääridatan ja sitä kuvaavat bufferView- ja accessor-oliot."""

    def __init__(self) -> None:
        self.data = bytearray()
        self.nakymat: list[dict[str, Any]] = []
        self.lukijat: list[dict[str, Any]] = []

    def lisaa(self, arvot: list[tuple[float, ...]], komponentti: str,
              tyyppi: str, rajat: bool = False) -> int:
        """Lisää taulukon ja palauttaa sen accessor-indeksin."""
        koodi, tunnus = {"f": (5126, "<f"), "H": (5123, "<H"),
                         "B": (5121, "<B")}[komponentti]
        while len(self.data) % 4:  # näkymä alkaa neljän tavun rajalta
            self.data.append(0)
        alku = len(self.data)
        for rivi in arvot:
            for arvo in rivi:
                self.data += struct.pack(tunnus, arvo)
        self.nakymat.append({"buffer": 0, "byteOffset": alku,
                             "byteLength": len(self.data) - alku})
        lukija: dict[str, Any] = {"bufferView": len(self.nakymat) - 1,
                                  "componentType": koodi,
                                  "count": len(arvot), "type": tyyppi}
        if rajat:  # pakollinen sijainneille ja animaation ajoille
            lukija["min"] = [pyorista(min(r[i] for r in arvot))
                             for i in range(len(arvot[0]))]
            lukija["max"] = [pyorista(max(r[i] for r in arvot))
                             for i in range(len(arvot[0]))]
        self.lukijat.append(lukija)
        return len(self.lukijat) - 1
# @loppu puskuri


def pyorista(x: float) -> float:
    """Arvo sellaisena kuin se on tiedostossa 32-bittisenä liukulukuna."""
    return float(struct.unpack("<f", struct.pack("<f", x))[0])


def laatikko(lo: Vec, hi: Vec) -> tuple[list[Vec], list[int]]:
    """Laatikon kulmat ja kolmioiden indeksit (vastapäivään ulkoa)."""
    p = [(hi[0] if i & 1 else lo[0], hi[1] if i & 2 else lo[1],
          hi[2] if i & 4 else lo[2]) for i in range(8)]
    sivut = [(4, 5, 7, 6), (1, 0, 2, 3), (5, 1, 3, 7), (0, 4, 6, 2),
             (6, 7, 3, 2), (0, 1, 5, 4)]
    indeksit: list[int] = []
    for a, b, c, d in sivut:
        indeksit += [a, b, c, a, c, d]
    return p, indeksit


def kierto_x(t: float) -> tuple[float, float, float, float]:
    """Kierto x-akselin ympäri kvaterniona (x, y, z, w), kun t on
    neljänneskulman tangentti. Rationaalinen esitys välttää sinin ja
    kosinin: kulma on 4 atan(t)."""
    n = 1 + t * t
    return (2 * t / n, 0.0, 0.0, (1 - t * t) / n)


def muotoile(puu: dict[str, Any]) -> str:
    """JSON, jossa lyhyet lukutaulukot ovat yhdellä rivillä."""
    teksti = json.dumps(puu, indent=1, ensure_ascii=False)

    def tiivista(m: re.Match[str]) -> str:
        yksi = re.sub(r"\s+", " ", m.group(2))
        yksi = yksi.replace("[ ", "[").replace(" ]", "]")
        return m.group(1) + yksi if len(m.group(1)) + len(yksi) <= 76 \
            else m.group(0)

    return re.sub(r"(?m)^( *(?:\"[^\"]+\": )?)(\[[^\[\]{}]*\])", tiivista,
                  teksti) + "\n"


# @alku hahmo
def hahmo() -> tuple[dict[str, Any], bytes]:
    """Laatikoista koottu hahmo, jolla on luuranko ja kaksi animaatiota."""
    # Nivel: nimi, vanhempi ja paikka mallin koordinaatistossa (metreinä).
    nivelet: list[tuple[str, int, Vec]] = [
        ("lantio", -1, (0, 0.9, 0)), ("selkä", 0, (0, 1.0, 0)),
        ("pää", 1, (0, 1.5, 0)), ("olka.v", 1, (0.28, 1.4, 0)),
        ("olka.o", 1, (-0.28, 1.4, 0)), ("lonkka.v", 0, (0.12, 0.9, 0)),
        ("lonkka.o", 0, (-0.12, 0.9, 0))]
    # Osa: nivel, johon laatikko on sidottu, ja laatikon kulmat.
    osat: list[tuple[int, Vec, Vec]] = [
        (0, (-0.2, 0.8, -0.11), (0.2, 0.95, 0.11)),
        (1, (-0.22, 0.95, -0.12), (0.22, 1.45, 0.12)),
        (2, (-0.12, 1.5, -0.12), (0.12, 1.8, 0.14)),
        (3, (0.22, 0.8, -0.06), (0.34, 1.44, 0.06)),
        (4, (-0.34, 0.8, -0.06), (-0.22, 1.44, 0.06)),
        (5, (0.03, 0.0, -0.08), (0.21, 0.9, 0.1)),
        (6, (-0.21, 0.0, -0.08), (-0.03, 0.9, 0.1))]
    pisteet: list[tuple[float, ...]] = []
    indeksit: list[tuple[float, ...]] = []
    sidokset: list[tuple[float, ...]] = []
    for nivel, lo, hi in osat:
        kulmat, kolmiot = laatikko(lo, hi)
        indeksit += [(len(pisteet) + k,) for k in kolmiot]
        pisteet += kulmat
        sidokset += [(nivel, 0, 0, 0)] * 8
    b = Puskuri()
    a_ind = b.lisaa(indeksit, "H", "SCALAR")
    a_pos = b.lisaa(pisteet, "f", "VEC3", rajat=True)
    a_niv = b.lisaa(sidokset, "B", "VEC4")
    a_pai = b.lisaa([(1.0, 0.0, 0.0, 0.0)] * len(pisteet), "f", "VEC4")
    # Käänteinen sidontamatriisi sarakkeittain: pelkkä siirto -paikka.
    a_sid = b.lisaa([(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
                      -x, -y, -z, 1) for _, _, (x, y, z) in nivelet],
                    "f", "MAT4")
    solmut: list[dict[str, Any]] = [{"name": "hahmo", "mesh": 0, "skin": 0}]
    for nro, (nimi, vanhempi, paikka) in enumerate(nivelet):
        juuri = nivelet[vanhempi][2] if vanhempi >= 0 else (0.0, 0.0, 0.0)
        solmu: dict[str, Any] = {
            "name": nimi,
            "translation": [round(paikka[k] - juuri[k], 6)
                            for k in range(3)]}
        lapset = [j + 1 for j, n in enumerate(nivelet) if n[1] == nro]
        if lapset:
            solmu["children"] = lapset
        solmut.append(solmu)

    def animaatio(nimi: str, kesto: float,
                  tangentit: dict[str, list[float]]) -> dict[str, Any]:
        n = len(next(iter(tangentit.values())))
        ajat = b.lisaa([(kesto * k / (n - 1),) for k in range(n)], "f",
                       "SCALAR", rajat=True)
        kanavat: list[dict[str, Any]] = []
        naytteet: list[dict[str, Any]] = []
        for nivel, sarja in tangentit.items():
            arvot = b.lisaa([kierto_x(t) for t in sarja], "f", "VEC4")
            solmu = 1 + [x[0] for x in nivelet].index(nivel)
            kanavat.append({"sampler": len(naytteet),
                            "target": {"node": solmu, "path": "rotation"}})
            naytteet.append({"input": ajat, "output": arvot,
                             "interpolation": "LINEAR"})
        return {"name": nimi, "channels": kanavat, "samplers": naytteet}

    askel = [0.0, 0.12, 0.0, -0.12, 0.0]   # noin +-27 astetta
    vasta = [-t for t in askel]
    heilu = [0.0, 0.02, 0.0, -0.02, 0.0]   # noin +-5 astetta
    puu = {
        "asset": {"version": "2.0", "generator": "tee_resurssit.py"},
        "scene": 0,
        "scenes": [{"nodes": [0, 1]}],
        "nodes": solmut,
        "meshes": [{"name": "hahmo", "primitives": [{
            "attributes": {"POSITION": a_pos, "JOINTS_0": a_niv,
                           "WEIGHTS_0": a_pai},
            "indices": a_ind, "material": 0}]}],
        "materials": [{"name": "kangas", "pbrMetallicRoughness": {
            "baseColorFactor": [0.8, 0.7, 0.35, 1.0]}}],
        "skins": [{"joints": list(range(1, len(nivelet) + 1)),
                   "inverseBindMatrices": a_sid, "skeleton": 1}],
        "animations": [
            animaatio("lepo", 2.0, {"olka.v": heilu, "olka.o": heilu}),
            animaatio("kävely", 0.8, {"lonkka.v": askel, "lonkka.o": vasta,
                                      "olka.v": vasta, "olka.o": askel})],
    }
    puu["accessors"], puu["bufferViews"] = b.lukijat, b.nakymat
    puu["buffers"] = [{"uri": "hahmo.bin", "byteLength": len(b.data)}]
    return puu, bytes(b.data)
# @loppu hahmo


# @alku taso
def taso() -> tuple[dict[str, Any], bytes]:
    """Pelin taso: sama yksikkökuutio monena solmuna ja tyhjät solmut
    pelin merkkeinä (aloituspaikka ja kerättävät lyhdyt)."""
    b = Puskuri()
    kulmat, kolmiot = laatikko((-0.5, 0.0, -0.5), (0.5, 1.0, 0.5))
    a_ind = b.lisaa([(k,) for k in kolmiot], "H", "SCALAR")
    a_pos = b.lisaa(list(kulmat), "f", "VEC3", rajat=True)
    # Kiila: ramppi, joka nousee z-suunnassa nollasta yhteen.
    kiila: list[tuple[float, ...]] = [
        (-0.5, 0, -0.5), (0.5, 0, -0.5), (-0.5, 0, 0.5), (0.5, 0, 0.5),
        (-0.5, 1, 0.5), (0.5, 1, 0.5)]
    k_ind = b.lisaa([(k,) for k in [0, 4, 5, 0, 5, 1, 2, 3, 5, 2, 5, 4,
                                    0, 2, 4, 1, 5, 3, 0, 1, 3, 0, 3, 2]],
                    "H", "SCALAR")
    k_pos = b.lisaa(kiila, "f", "VEC3", rajat=True)
    varit = {"ruoho": [0.47, 0.6, 0.42, 1.0], "kivi": [0.6, 0.6, 0.64, 1.0],
             "puu": [0.66, 0.5, 0.33, 1.0], "tiili": [0.7, 0.42, 0.32, 1.0]}
    nimet = list(varit)

    def verkko(nimi: str, ind: int, pos: int, vari: str) -> dict[str, Any]:
        return {"name": nimi, "primitives": [{
            "attributes": {"POSITION": pos}, "indices": ind,
            "material": nimet.index(vari)}]}

    verkot = [verkko("kuutio.ruoho", a_ind, a_pos, "ruoho"),
              verkko("kuutio.kivi", a_ind, a_pos, "kivi"),
              verkko("kuutio.tiili", a_ind, a_pos, "tiili"),
              verkko("kiila.puu", k_ind, k_pos, "puu")]
    # 90 asteen kierto y-akselin ympäri on (0, r, 0, r), r = sqrt(1/2).
    r = round(math.sqrt(0.5), 7)
    solmut: list[dict[str, Any]] = [
        {"name": "maa", "mesh": 0, "translation": [0, -1, 0],
         "scale": [40, 1, 40]},
        {"name": "tasanne", "mesh": 1, "translation": [6, 0, -6],
         "scale": [6, 1.5, 6]},
        {"name": "ramppi", "mesh": 3, "translation": [6, 0, -0.5],
         "rotation": [0, 1, 0, 0], "scale": [3, 1.5, 5]},
        {"name": "muuri", "mesh": 2, "translation": [-6, 0, -4],
         "rotation": [0, r, 0, r],
         "scale": [8, 2.5, 0.6]},
        {"name": "torni", "mesh": 1, "translation": [-9, 0, 7],
         "scale": [2, 5, 2]},
    ]
    for k in range(4):  # portaat tasanteelle toiselta puolelta
        solmut.append({"name": f"porras.{k + 1}", "mesh": 1,
                       "translation": [1.4 + 0.4 * k, 0, -6],
                       "scale": [0.4, round(0.3 * (k + 1), 6), 3]})
    solmut.append({"name": "porras.5", "mesh": 1,
                   "translation": [3, 1.2, -6], "scale": [0.4, 0.3, 3]})
    merkit = [("alku", (0, 0, 6)), ("lyhty.1", (6, 1.5, -6)),
              ("lyhty.2", (-8, 0, -1)), ("lyhty.3", (-9, 0, 4)),
              ("lyhty.4", (12, 0, 4))]
    for nimi, paikka in merkit:
        solmut.append({"name": nimi, "translation": list(paikka)})
    puu = {
        "asset": {"version": "2.0", "generator": "tee_resurssit.py"},
        "scene": 0,
        "scenes": [{"name": "taso", "nodes": list(range(len(solmut)))}],
        "nodes": solmut,
        "meshes": verkot,
        "materials": [{"name": n, "pbrMetallicRoughness": {
            "baseColorFactor": v}} for n, v in varit.items()],
        "accessors": b.lukijat, "bufferViews": b.nakymat,
        "buffers": [{"uri": "taso.bin", "byteLength": len(b.data)}],
    }
    return puu, bytes(b.data)
# @loppu taso


def main() -> int:
    kohde = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
    for nimi, (puu, data) in {"hahmo": hahmo(), "taso": taso()}.items():
        (kohde / f"{nimi}.gltf").write_text(muotoile(puu), "utf-8")
        (kohde / f"{nimi}.bin").write_bytes(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
