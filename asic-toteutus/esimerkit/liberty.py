"""Pieni Liberty-jäsennin ja NLDM-taulukoiden interpolointi.

Liberty (.lib) kuvaa solukirjaston: solujen pinta-alan, pinnien
kapasitanssit ja ajoituksen taulukkoina. Tämä jäsennin ymmärtää
ryhmät, yksinkertaiset attribuutit (a : b;) ja kompleksiset
attribuutit (a (b, c);), mikä riittää opetuskirjastolle opetus.lib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# @alku ryhma
@dataclass
class Ryhma:
    """Liberty-ryhmä: tyyppi, argumentit, attribuutit ja aliryhmät."""
    tyyppi: str
    nimi: str
    attr: dict[str, str] = field(default_factory=dict)
    kompleksi: dict[str, list[str]] = field(default_factory=dict)
    lapset: list[Ryhma] = field(default_factory=list)

    def kaikki(self, tyyppi: str) -> list[Ryhma]:
        return [r for r in self.lapset if r.tyyppi == tyyppi]

    def yksi(self, tyyppi: str, nimi: str) -> Ryhma:
        for r in self.lapset:
            if r.tyyppi == tyyppi and r.nimi == nimi:
                return r
        raise KeyError(f"{tyyppi} {nimi}")
# @loppu ryhma


_TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}();:,]|[^\s{}();:,"]+')


def _tokenit(teksti: str) -> list[str]:
    teksti = re.sub(r"/\*.*?\*/", " ", teksti, flags=re.S)
    teksti = teksti.replace("\\\n", " ")
    return _TOKEN.findall(teksti)


def _arvo(token: str) -> str:
    return token[1:-1] if token.startswith('"') else token


def jasenna(teksti: str) -> Ryhma:
    """Jäsentää Liberty-tekstin ja palauttaa ylimmän ryhmän."""
    t = _tokenit(teksti)
    i = 0

    def ryhma(tyyppi: str) -> Ryhma:
        nonlocal i
        args = argumentit()
        g = Ryhma(tyyppi, args[0] if args else "")
        assert t[i] == "{"
        i += 1
        while t[i] != "}":
            nimi = t[i]
            i += 1
            if t[i] == ":":
                g.attr[nimi] = _arvo(t[i + 1])
                i += 3 if t[i + 2] == ";" else 2
            elif t[i] == "(":
                save = i
                args = argumentit()
                if t[i] == "{":
                    i = save
                    g.lapset.append(ryhma(nimi))
                else:
                    g.kompleksi[nimi] = args
                    if t[i] == ";":
                        i += 1
            else:
                raise ValueError(f"odottamaton {t[i]!r}")
        i += 1
        return g

    def argumentit() -> list[str]:
        nonlocal i
        assert t[i] == "("
        i += 1
        args: list[str] = []
        while t[i] != ")":
            if t[i] != ",":
                args.append(_arvo(t[i]))
            i += 1
        i += 1
        return args

    nimi = t[i]
    i += 1
    return ryhma(nimi)


def lue(polku: Path) -> Ryhma:
    return jasenna(polku.read_text("utf-8"))


# @alku nldm
@dataclass
class Taulukko:
    """NLDM-taulukko: arvo indeksien 1 ja 2 funktiona."""
    indeksi1: list[float]
    indeksi2: list[float]
    arvot: list[list[float]]

    def arvo(self, x: float, y: float) -> float:
        """Bilineaarinen interpolointi (ja ekstrapolointi reunoilta)."""
        i = _vali(self.indeksi1, x)
        j = _vali(self.indeksi2, y)
        x0, x1 = self.indeksi1[i], self.indeksi1[i + 1]
        y0, y1 = self.indeksi2[j], self.indeksi2[j + 1]
        tx = (x - x0) / (x1 - x0)
        ty = (y - y0) / (y1 - y0)
        a = self.arvot
        ala = a[i][j] + ty * (a[i][j + 1] - a[i][j])
        yla = a[i + 1][j] + ty * (a[i + 1][j + 1] - a[i + 1][j])
        return ala + tx * (yla - ala)


def _vali(akseli: list[float], x: float) -> int:
    """Indeksin väli, jolle x osuu; reunoilla lähin väli."""
    for k in range(len(akseli) - 2):
        if x < akseli[k + 1]:
            return k
    return len(akseli) - 2
# @loppu nldm


def _luvut(teksti: str) -> list[float]:
    return [float(v) for v in teksti.replace('"', "").split(",")]


def taulukko(kirjasto: Ryhma, g: Ryhma) -> Taulukko:
    """Lukee taulukon; indeksit tulevat mallista, ellei niitä anneta."""
    malli = kirjasto.yksi("lu_table_template", g.nimi)
    i1 = g.kompleksi.get("index_1", malli.kompleksi["index_1"])
    i2 = g.kompleksi.get("index_2", malli.kompleksi["index_2"])
    rivit = [_luvut(r) for r in g.kompleksi["values"]]
    return Taulukko(_luvut(i1[0]), _luvut(i2[0]), rivit)


def main() -> None:
    kirjasto = lue(Path(__file__).with_name("opetus.lib"))
    # @alku kaytto
    print(f"kirjasto {kirjasto.nimi}: {len(kirjasto.kaikki('cell'))} solua")
    nand = kirjasto.yksi("cell", "NAND2_X1")
    a = nand.yksi("pin", "A")
    print(f"NAND2_X1: ala {nand.attr['area']} µm², "
          f"tulo A {a.attr['capacitance']} pF")
    y = nand.yksi("pin", "Y")
    kaari = y.kaikki("timing")[0]
    viive = taulukko(kirjasto, kaari.yksi("cell_fall", "nldm_3x3"))
    for slew, kuorma in [(0.02, 0.002), (0.10, 0.010), (0.25, 0.030)]:
        print(f"  laskeva viive, slew {slew:.2f} ns, kuorma "
              f"{kuorma * 1000:.0f} fF: {viive.arvo(slew, kuorma):.3f} ns")
    # @loppu kaytto


if __name__ == "__main__":
    main()
