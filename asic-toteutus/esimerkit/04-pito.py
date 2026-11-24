"""Kellon vinous ja pitoaika: rike, sen syy ja korjaus puskureilla.

Kun vastaanottavan kiikun kello saapuu myöhemmin kuin lähettävän,
data ehtii vaihtua ennen kuin pitoaika on kulunut. Asetusmarginaali
paranee samalla – vinous siirtää aikaa polulta toiselle. Pitorike
korjataan lisäämällä datapolulle viivettä.
"""

from pathlib import Path
from typing import Any

from sta import Analyysi, Rajoitteet, pahimmat, raportti
from synteesi import Tulos, syntetisoi

HAK = Path(__file__).parent


# @alku puskurit
def lisaa_puskurit(tulos: Tulos, bitti: int, n: int) -> None:
    """Lisää n puskuria kiikun q[bitti] D-tuloon (netlistan muokkaus)."""
    m: dict[str, Any] = tulos.moduuli()
    nimet = {name: v["bits"] for name, v in m["netnames"].items()}
    kohde = nimet["q"][bitti]
    kiikku = next(c for c in m["cells"].values()
                  if c["connections"].get("Q") == [kohde])
    seuraava = max(b for v in nimet.values() for b in v
                   if isinstance(b, int)) + 1
    edellinen = kiikku["connections"]["D"][0]
    for i in range(n):
        uusi = seuraava + i
        m["cells"][f"viive{i}"] = {
            "type": "BUF_X1",
            "connections": {"A": [edellinen], "Y": [uusi]}}
        m["netnames"][f"viive{i}"] = {"hide_name": 0, "bits": [uusi]}
        edellinen = uusi
    kiikku["connections"]["D"] = [edellinen]
# @loppu puskurit


def main() -> None:
    # @alku vinous
    print("vinous ns   asetus q1->q2   pito q1->q2")
    for vinous in [0.0, 0.1, 0.2, 0.3, 0.4]:
        tulos = syntetisoi([HAK / "siirto.v"], "siirto")
        r = Rajoitteet(jakso=2.0, sisaan=0.2,
                       kellon_viive={"q[2]": vinous})
        polut = [p for p in Analyysi(tulos, r).polut()
                 if (p.alku, p.loppu) == ("q[1]", "q[2]")]
        asetus = next(p for p in polut if p.lajia == "asetus")
        pito = next(p for p in polut if p.lajia == "pito")
        print(f"{vinous:8.1f} {asetus.marginaali:+15.3f} "
              f"{pito.marginaali:+13.3f}")
    # @loppu vinous
    # @alku korjaus
    r = Rajoitteet(jakso=2.0, sisaan=0.2, kellon_viive={"q[2]": 0.4})
    for n in [0, 2, 4]:
        tulos = syntetisoi([HAK / "siirto.v"], "siirto")
        lisaa_puskurit(tulos, 2, n)
        pito = pahimmat(Analyysi(tulos, r).polut(), "pito")[0]
        print(f"{n} puskuria: pahin pito {pito.alku} -> {pito.loppu} "
              f"{pito.marginaali:+.3f} ns")
    print("\n".join(raportti(pito)))
    # @loppu korjaus


if __name__ == "__main__":
    main()
