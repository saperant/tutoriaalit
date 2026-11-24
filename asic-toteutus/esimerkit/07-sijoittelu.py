"""Sijoittelu: solut riveihin niin, että johdinpituus on pieni.

Laskurin netlistan solut sijoitetaan standardisolurivien paikkoihin.
Satunnaisesta alusta lähtien simuloitu jäähdytys vaihtaa kahden
paikan sisältöä ja hyväksyy huononnuksenkin todennäköisyydellä, joka
pienenee lämpötilan laskiessa. Kustannus on puolipiirin johdinpituus
(HPWL) kaikkien johdinten yli. Lopuksi arvioidaan ruuhkaisuus.
"""

import math
import random
from pathlib import Path
from typing import Any

from synteesi import syntetisoi

HAK = Path(__file__).parent
RIVEJA, PAIKKOJA = 6, 9                 # 54 paikkaa, käyttöaste ~70 %

Piste = tuple[float, float]


# @alku verkot
def verkot(m: dict[str, Any]) -> tuple[list[str], list[list[str]],
                                       dict[str, Piste]]:
    """Solut, johtimet (solujen ja porttien nimilistoina) ja porttien
    kiinteät paikat: tulot vasemmalla, lähdöt oikealla reunalla.
    Kello jätetään pois: kellopuu rakennetaan omassa vaiheessaan."""
    solut = sorted(m["cells"])
    kello = m["ports"]["clk"]["bits"][0]
    jasenet: dict[int, list[str]] = {}
    for nimi in solut:
        for v in m["cells"][nimi]["connections"].values():
            for b in v:
                if isinstance(b, int) and b != kello:
                    jasenet.setdefault(b, []).append(nimi)
    kiinteat: dict[str, Piste] = {}
    portit = m["ports"]
    tulot = [p for p in portit if portit[p]["direction"] == "input"]
    for i, (p, tieto) in enumerate(sorted(portit.items())):
        for j, b in enumerate(tieto["bits"]):
            if b == kello:
                continue
            nimi = f"{p}[{j}]"
            x = -1.0 if p in tulot else float(PAIKKOJA)
            kiinteat[nimi] = (x, (i + j * 0.7) % RIVEJA)
            jasenet.setdefault(b, []).append(nimi)
    return solut, [v for v in jasenet.values() if len(v) > 1], kiinteat
# @loppu verkot


# @alku hpwl
def hpwl(verkko: list[str], paikat: dict[str, Piste]) -> float:
    xs = [paikat[n][0] for n in verkko]
    ys = [paikat[n][1] for n in verkko]
    return (max(xs) - min(xs)) + (max(ys) - min(ys))
# @loppu hpwl


# @alku jaahdytys
def jaahdytys(solut: list[str], johtimet: list[list[str]],
              kiinteat: dict[str, Piste], siemen: int = 1
              ) -> tuple[float, float, dict[str, Piste]]:
    rng = random.Random(siemen)
    paikat_kaikki = [(float(x), float(y)) for y in range(RIVEJA)
                     for x in range(PAIKKOJA)]
    rng.shuffle(paikat_kaikki)
    sisalto: dict[Piste, str | None] = {p: None for p in paikat_kaikki}
    paikat = dict(kiinteat)
    for nimi, p in zip(solut, paikat_kaikki, strict=False):
        paikat[nimi], sisalto[p] = p, nimi
    solun_johtimet: dict[str, list[int]] = {}
    for i, j in enumerate(johtimet):
        for n in j:
            solun_johtimet.setdefault(n, []).append(i)
    alku = sum(hpwl(j, paikat) for j in johtimet)
    lampo = 4.0
    while lampo > 0.01:
        for _ in range(300):
            p1, p2 = rng.sample(paikat_kaikki, 2)
            a, b = sisalto[p1], sisalto[p2]
            mukana = {i for n in (a, b) if n for i in solun_johtimet[n]}
            ennen = sum(hpwl(johtimet[i], paikat) for i in mukana)
            for solu, p in ((a, p2), (b, p1)):
                if solu:
                    paikat[solu] = p
            muutos = sum(hpwl(johtimet[i], paikat) for i in mukana) - ennen
            if muutos <= 0 or rng.random() < math.exp(-muutos / lampo):
                sisalto[p1], sisalto[p2] = b, a
            else:                                    # peru vaihto
                for solu, p in ((a, p1), (b, p2)):
                    if solu:
                        paikat[solu] = p
        lampo *= 0.9
    loppu = sum(hpwl(j, paikat) for j in johtimet)
    return alku, loppu, paikat
# @loppu jaahdytys


# @alku ruuhka
def ruuhka(johtimet: list[list[str]], paikat: dict[str, Piste]
           ) -> list[list[float]]:
    """RUDY-arvio: jokainen johdin levittää johdinpituutensa tasaisesti
    rajaavan suorakulmionsa alueelle."""
    kartta = [[0.0] * PAIKKOJA for _ in range(RIVEJA)]
    for j in johtimet:
        xs = [min(max(paikat[n][0], 0), PAIKKOJA - 1) for n in j]
        ys = [paikat[n][1] for n in j]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        ala = (x1 - x0 + 1) * (y1 - y0 + 1)
        tiheys = hpwl(j, paikat) / ala
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                kartta[y][x] += tiheys
    return kartta
# @loppu ruuhka


def main() -> None:
    # @alku ajo
    m = syntetisoi([HAK / "laskuri.v"], "laskuri").moduuli()
    solut, johtimet, kiinteat = verkot(m)
    alku, loppu, paikat = jaahdytys(solut, johtimet, kiinteat)
    print(f"{len(solut)} solua, {len(johtimet)} johdinta, "
          f"{RIVEJA}×{PAIKKOJA} paikkaa")
    print(f"HPWL satunnainen {alku:.0f}, jäähdytyksen jälkeen {loppu:.0f}")
    kartta = ruuhka(johtimet, paikat)
    huippu = max(max(r) for r in kartta)
    print("ruuhkakartta (RUDY, 0–9 suhteessa huippuun):")
    for rivi in reversed(kartta):
        print("  " + "".join(str(min(9, int(10 * v / huippu)))
                             for v in rivi))
    # @loppu ajo


if __name__ == "__main__":
    main()
