"""Opetustason staattinen ajoitusanalyysi (STA) Yosysin netlistalle.

Analyysi lukee solujen viiveet ja siirtymäajat Liberty-kirjaston
NLDM-taulukoista, laskee jokaisen johtimen kuorman ja käy piirin läpi
kerran jokaisesta alkupisteestä (tulo tai kiikku). Yksinkertaistukset:
nousevaa ja laskevaa reunaa ei eroteta (myöhäisessä analyysissa
käytetään hitaampaa, aikaisessa nopeampaa), johtimen kapasitanssi
arvioidaan haarautumisesta ja kello on ideaalinen viiveineen.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from liberty import Ryhma, lue, taulukko
from synteesi import Tulos, syntetisoi

HAK = Path(__file__).parent


# @alku rajoitteet
@dataclass
class Rajoitteet:
    """SDC-rajoitteita vastaavat asetukset (aikayksikkö ns, kuorma pF)."""
    jakso: float
    kello: str = "clk"
    sisaan: float = 0.0              # set_input_delay
    ulos: float = 0.0                # set_output_delay
    epavarmuus: float = 0.0          # set_clock_uncertainty
    kuorma_ulos: float = 0.005       # set_load
    tulon_slew: float = 0.10         # set_input_transition
    kellon_slew: float = 0.05
    kellon_viive: dict[str, float] = field(default_factory=dict)
    monisykli: list[tuple[str, str, int]] = field(default_factory=list)
    vaarat: list[tuple[str, str]] = field(default_factory=list)
    myohainen: float = 1.0           # OCV: myöhäisten polkujen kerroin
    aikainen: float = 1.0            # OCV: aikaisten polkujen kerroin
# @loppu rajoitteet


# Asynkronisen nollauksen vapautus tarkistetaan kuten data: recovery
# vastaa asetus- ja removal pitotarkistusta.
ASYNKRONISET = {"RN": ("recovery_rising", "removal_rising")}


def osuu(nimi: str, malli: str) -> bool:
    """Nimen vertailu malliin: * on jokerimerkki, hakasulut kirjaimellisia
    (väylän bitit, esim. q[2])."""
    return fnmatch.fnmatchcase(nimi, malli.replace("[", "[[]"))


@dataclass
class Askel:
    piste: str
    solu: str
    lisays: float
    saapuminen: float


@dataclass
class Polku:
    alku: str
    loppu: str
    lajia: str                       # "asetus" tai "pito"
    saapuminen: float
    vaadittu: float
    askeleet: list[Askel]

    @property
    def marginaali(self) -> float:
        if self.lajia == "asetus":
            return self.vaadittu - self.saapuminen
        return self.saapuminen - self.vaadittu


@dataclass
class _Tila:
    aika: float
    slew: float
    edellinen: tuple[int, str, str, float] | None


class Analyysi:
    """Netlista, kirjasto ja rajoitteet; polut laskee metodi polut()."""

    def __init__(self, tulos: Tulos, rajoitteet: Rajoitteet,
                 kirjasto: Ryhma | None = None) -> None:
        self.r = rajoitteet
        self.lib = kirjasto or lue(HAK / "opetus.lib")
        m = tulos.moduuli()
        self.solut: dict[str, dict[str, Any]] = m["cells"]
        self.portit: dict[str, dict[str, Any]] = m["ports"]
        self.nimet = self._bittien_nimet(m["netnames"])
        self.libsolut = {c.nimi: c for c in self.lib.kaikki("cell")}
        self._liitokset()
        self.kuorma = {b: self._kuorma(b) for b in self.nielut}

    # --- netlistan rakenne -------------------------------------------
    @staticmethod
    def _bittien_nimet(netnames: dict[str, Any]) -> dict[int, str]:
        nimet: dict[int, str] = {}
        for nimi, n in sorted(netnames.items(),
                              key=lambda x: (x[1]["hide_name"], x[0])):
            bitit = n["bits"]
            for i, b in enumerate(bitit):
                if not isinstance(b, int) or b in nimet:
                    continue
                if nimi.startswith("$"):            # Yosysin oma nimi
                    nimet[b] = f"n{b}"
                else:
                    nimet[b] = f"{nimi}[{i}]" if len(bitit) > 1 else nimi
        return nimet

    def suunta(self, tyyppi: str, pinni: str) -> str:
        return self.libsolut[tyyppi].yksi("pin", pinni).attr["direction"]

    def on_kiikku(self, tyyppi: str) -> bool:
        return bool(self.libsolut[tyyppi].kaikki("ff"))

    def _liitokset(self) -> None:
        self.ajurit: dict[int, tuple[str, str]] = {}
        self.nielut: dict[int, list[tuple[str, str]]] = {}
        for nimi, c in self.solut.items():
            for pinni, bitit in c["connections"].items():
                for b in bitit:
                    if not isinstance(b, int):
                        continue
                    if self.suunta(c["type"], pinni) == "output":
                        self.ajurit[b] = (nimi, pinni)
                    else:
                        self.nielut.setdefault(b, []).append((nimi, pinni))
                    self.nielut.setdefault(b, [])
        self.ulostulot = {b for p in self.portit.values()
                          if p["direction"] == "output" for b in p["bits"]
                          if isinstance(b, int)}

    # @alku kuorma
    def _kuorma(self, bitti: int) -> float:
        """Nielujen pinnikapasitanssit + johdinarvio + lähtöportti."""
        nielut = self.nielut[bitti]
        c = sum(float(self.libsolut[self.solut[s]["type"]]
                      .yksi("pin", p).attr["capacitance"])
                for s, p in nielut)
        c += 0.001 * (1 + len(nielut))        # johdinkuorman arvio
        if bitti in self.ulostulot:
            c += self.r.kuorma_ulos
        return c
    # @loppu kuorma

    def rekisteri(self, solu: str) -> str:
        q = self.solut[solu]["connections"]["Q"][0]
        return self.nimet.get(q, solu)

    def _kellon_viive(self, rekisteri: str) -> float:
        for malli, viive in self.r.kellon_viive.items():
            if osuu(rekisteri, malli):
                return viive
        return 0.0

    def _arvo(self, solu: str, pinni: str, liittyva: str, taulu: str,
              slew: float, kuorma: float, suurin: bool) -> float:
        lib = self.libsolut[self.solut[solu]["type"]]
        for t in lib.yksi("pin", pinni).kaikki("timing"):
            if t.attr["related_pin"] != liittyva:
                continue
            nimi = "nldm_3x3" if "transition" in taulu or \
                "cell" in taulu else "rajoite_3x3"
            nousu = taulukko(self.lib, t.yksi(taulu.replace("*", "rise"),
                                              nimi)).arvo(slew, kuorma)
            lasku = taulukko(self.lib, t.yksi(taulu.replace("*", "fall"),
                                              nimi)).arvo(slew, kuorma)
            return max(nousu, lasku) if suurin else min(nousu, lasku)
        raise KeyError(f"{solu}.{pinni} <- {liittyva}")

    def _rajoite(self, solu: str, pinni: str, laji: str,
                 dslew: float) -> float:
        lib = self.libsolut[self.solut[solu]["type"]]
        for t in lib.yksi("pin", pinni).kaikki("timing"):
            if t.attr.get("timing_type") == laji:
                tau = taulukko(self.lib, t.yksi("rise_constraint",
                                                "rajoite_3x3"))
                return tau.arvo(self.r.kellon_slew, dslew)
        raise KeyError(laji)

    # --- eteneminen ---------------------------------------------------
    # @alku eteneminen
    def _eteneminen(self, alku: int, aika: float, slew: float,
                    myohainen: bool) -> dict[int, _Tila]:
        """Saapumisajat yhdestä alkupisteestä logiikan läpi."""
        tilat = {alku: _Tila(aika, slew, None)}
        jono = [alku]
        while jono:
            b = jono.pop()
            for solu, pinni in self.nielut.get(b, []):
                tyyppi = self.solut[solu]["type"]
                if self.on_kiikku(tyyppi):
                    continue                        # polku päättyy
                ulos, bitit = next(
                    (p, v) for p, v in self.solut[solu]["connections"]
                    .items() if self.suunta(tyyppi, p) == "output")
                y = bitit[0]
                kerroin = self.r.myohainen if myohainen else self.r.aikainen
                d = kerroin * self._arvo(solu, ulos, pinni, "cell_*",
                                         tilat[b].slew, self.kuorma[y],
                                         myohainen)
                s = self._arvo(solu, ulos, pinni, "*_transition",
                               tilat[b].slew, self.kuorma[y], myohainen)
                uusi = tilat[b].aika + d
                vanha = tilat.get(y)
                if vanha is None or (uusi > vanha.aika if myohainen
                                     else uusi < vanha.aika):
                    tilat[y] = _Tila(uusi, s, (b, solu, tyyppi, d))
                    jono.append(y)
        return tilat
    # @loppu eteneminen

    def _alkupisteet(self) -> list[tuple[str, int, float, float, float]]:
        """(nimi, bitti, myöhäinen aika, aikainen aika, slew)."""
        alut = []
        for nimi, p in sorted(self.portit.items()):
            if p["direction"] == "input" and nimi != self.r.kello:
                for b in p["bits"]:
                    if isinstance(b, int):
                        alut.append((self.nimet[b], b, self.r.sisaan,
                                     self.r.sisaan, self.r.tulon_slew))
        for nimi, c in sorted(self.solut.items()):
            if self.on_kiikku(c["type"]):
                q = c["connections"]["Q"][0]
                rek = self.rekisteri(nimi)
                lat = self._kellon_viive(rek)
                k = self.kuorma[q]
                myo = lat + self.r.myohainen * self._arvo(
                    nimi, "Q", "CK", "cell_*", self.r.kellon_slew, k, True)
                aik = lat + self.r.aikainen * self._arvo(
                    nimi, "Q", "CK", "cell_*", self.r.kellon_slew, k, False)
                s = self._arvo(nimi, "Q", "CK", "*_transition",
                               self.r.kellon_slew, k, True)
                alut.append((rek, q, myo, aik, s))
        return alut

    def _sykleja(self, alku: str, loppu: str) -> int | None:
        for a, b in self.r.vaarat:
            if osuu(alku, a) and osuu(loppu, b):
                return None
        for a, b, n in self.r.monisykli:
            if osuu(alku, a) and osuu(loppu, b):
                return n
        return 1

    def _askeleet(self, tilat: dict[int, _Tila], b: int,
                  alku: str) -> list[Askel]:
        askeleet: list[Askel] = []
        while (t := tilat[b]).edellinen is not None:
            edellinen, solu, tyyppi, d = t.edellinen
            askeleet.append(Askel(self.nimet.get(b, solu), tyyppi, d,
                                  t.aika))
            b = edellinen
        askeleet.append(Askel(alku, "alku", tilat[b].aika, tilat[b].aika))
        return askeleet[::-1]

    # @alku tarkistukset
    def polut(self) -> list[Polku]:
        """Kaikki alku–loppu-parit asetus- ja pitotarkistuksineen."""
        tulos: list[Polku] = []
        for alku, b, myo, aik, slew in self._alkupisteet():
            myohaiset = self._eteneminen(b, myo, slew, True)
            aikaiset = self._eteneminen(b, aik, slew, False)
            for y, tila in myohaiset.items():
                for solu, pinni in self.nielut.get(y, []):
                    c = self.solut[solu]
                    if not (self.on_kiikku(c["type"]) and pinni != "CK"):
                        continue
                    loppu = self.rekisteri(solu)
                    n = self._sykleja(alku, loppu)
                    if n is None:
                        continue                    # väärä polku
                    lat = self._kellon_viive(loppu)
                    lajit = ASYNKRONISET.get(pinni, ("setup_rising",
                                                     "hold_rising"))
                    asetus = self._rajoite(solu, pinni, lajit[0],
                                           tila.slew)
                    vaadittu = (lat + n * self.r.jakso - asetus
                                - self.r.epavarmuus)
                    tulos.append(Polku(alku, loppu, "asetus", tila.aika,
                                       vaadittu, self._askeleet(
                                           myohaiset, y, alku)))
                    a = aikaiset[y]
                    pito = self._rajoite(solu, pinni, lajit[1], a.slew)
                    tulos.append(Polku(alku, loppu, "pito", a.aika,
                                       lat + pito + self.r.epavarmuus,
                                       self._askeleet(aikaiset, y, alku)))
                if y in self.ulostulot:
                    loppu = self.nimet[y]
                    n = self._sykleja(alku, loppu)
                    if n is not None:
                        tulos.append(Polku(
                            alku, loppu, "asetus", tila.aika,
                            n * self.r.jakso - self.r.ulos,
                            self._askeleet(myohaiset, y, alku)))
        return tulos
    # @loppu tarkistukset


def pahimmat(polut: list[Polku], laji: str, n: int = 1) -> list[Polku]:
    return sorted((p for p in polut if p.lajia == laji),
                  key=lambda p: (p.marginaali, p.alku, p.loppu))[:n]


# @alku raportti
def raportti(p: Polku) -> list[str]:
    rivit = [f"{p.lajia}: {p.alku} -> {p.loppu}"]
    for a in p.askeleet:
        rivit.append(f"  {a.piste:10} {a.solu:9} {a.lisays:+.3f} "
                     f"{a.saapuminen:7.3f}")
    rivit.append(f"  saapuminen {p.saapuminen:.3f}, vaadittu "
                 f"{p.vaadittu:.3f}, marginaali {p.marginaali:+.3f} ns")
    return rivit
# @loppu raportti


def main() -> None:
    # @alku kaytto
    tulos = syntetisoi([HAK / "kertoja.v"], "kertoja")
    analyysi = Analyysi(tulos, Rajoitteet(jakso=2.0, sisaan=0.3))
    polut = analyysi.polut()
    kriittinen = pahimmat(polut, "asetus")[0]
    print("\n".join(raportti(kriittinen)))
    pito = pahimmat(polut, "pito")[0]
    print(f"pahin pitomarginaali: {pito.alku} -> {pito.loppu} "
          f"{pito.marginaali:+.3f} ns")
    print(f"suurin taajuus noin "
          f"{1000 / (2.0 - kriittinen.marginaali):.0f} MHz")
    # @loppu kaytto


if __name__ == "__main__":
    main()
