"""Regressio: ajaa cocotb-testit kaikilla vikaversioilla ja siemenillä,
kokoaa vikamatriisin ja luokittelee epäonnistumiset (luku 10).

Jokainen ajo on oma aliprosessinsa (pythonpenkit/aja.py), joten ajot
voidaan tehdä rinnakkain. Tulos ei riipu ajojärjestyksestä, koska
jokaisella ajolla on oma rakennushakemistonsa ja siemenensä.

Käyttö: python3 tyokalut/regressio.py [--siemenet 5] [--rinnakkain 4]
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


# @alku kokoonpano
@dataclass(frozen=True)
class Kohde:
    top: str
    moduuli: str
    testit: tuple[str, ...]
    viat: tuple[str, ...]


KOHTEET = (
    Kohde(
        "fifo",
        "test_fifo",
        ("ohjattu", "satunnaistettu", "kulmat"),
        ("", "BUGI_TYHJA", "BUGI_SAMANAIKAINEN", "BUGI_TAYSI"),
    ),
    Kohde(
        "arbiteri",
        "test_arbiteri",
        ("satunnainen", "kuormitus"),
        ("", "BUGI_KIINTEA", "BUGI_KAKSI"),
    ),
)
# @loppu kokoonpano


@dataclass(frozen=True)
class Ajo:
    kohde: Kohde
    vika: str
    siemen: int


def aja(ajo: Ajo) -> dict[str, str]:
    """Ajaa yhden kokoonpanon; palauttaa kaatuneet testit viesteineen."""
    komento = [
        sys.executable,
        "pythonpenkit/aja.py",
        f"--top={ajo.kohde.top}",
        f"--moduuli={ajo.kohde.moduuli}",
        f"--lahde=rtl/{ajo.kohde.top}.sv",
        f"--siemen={ajo.siemen}",
        "--rakennus=regressio",
    ]
    if ajo.vika:
        komento.append(f"--vika={ajo.vika}")
    tulos = subprocess.run(
        komento, capture_output=True, text=True, check=False
    )
    kaatuneet = {}
    for rivi in tulos.stdout.splitlines():
        m = re.fullmatch(r"  KAATUI (\w+): (.*)", rivi)
        if m:
            kaatuneet[m[1]] = m[2]
    if tulos.returncode != 0 and not kaatuneet:
        raise RuntimeError(f"ajo epäonnistui: {' '.join(komento)}")
    return kaatuneet


# @alku luokittelu
def tunniste(viesti: str) -> str:
    """Epäonnistumisen tunniste: luokka ja viesti ilman lukuja.

    Saman vian eri siemenillä tuottamat viestit eroavat yleensä vain
    jaksonumeroiltaan ja arvoiltaan, joten luvut korvataan merkillä #.
    """
    return re.sub(r"\d+", "#", viesti)
    # @loppu luokittelu


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--siemenet", type=int, default=5)
    p.add_argument("--rinnakkain", type=int, default=4)
    a = p.parse_args()
    siemenet = range(1, a.siemenet + 1)

    ajot = [Ajo(k, v, s) for k in KOHTEET for v in k.viat for s in siemenet]
    with ThreadPoolExecutor(a.rinnakkain) as pooli:
        tulokset = dict(zip(ajot, pooli.map(aja, ajot), strict=True))

    # @alku matriisi
    print(f"vikamatriisi: kaatuneet siemenet / {a.siemenet}")
    for k in KOHTEET:
        print(f"{k.top:<20}" + "".join(f"{t:>16}" for t in k.testit))
        for v in k.viat:
            solut = []
            for t in k.testit:
                n = sum(t in tulokset[Ajo(k, v, s)] for s in siemenet)
                solut.append(f"{n}/{a.siemenet}" if n else "-")
            nimi = v or "ehjä"
            print(f"  {nimi:<18}" + "".join(f"{c:>16}" for c in solut))
    # @loppu matriisi

    # @alku ryhmat
    ryhmat: dict[str, list[tuple[Ajo, str]]] = defaultdict(list)
    for ajo, kaatuneet in tulokset.items():
        for testi, viesti in kaatuneet.items():
            ryhmat[f"{ajo.kohde.top}: {tunniste(viesti)}"].append(
                (ajo, testi)
            )
    print(f"\nepäonnistumiset ryhmiteltyinä ({len(ryhmat)} ryhmää):")
    for avain, jasenet in sorted(ryhmat.items()):
        ajo, testi = min(jasenet, key=lambda x: (x[0].siemen, x[1]))
        print(f"  {len(jasenet):>3} x {avain}")
        print(
            f"        toista: --vika {ajo.vika} --siemen {ajo.siemen} "
            f"--testit {testi}"
        )
        # Opetusta varten: mitkä istutetut viat ryhmään päätyivät.
        viat = sorted({a.vika for a, _ in jasenet})
        print(f"        viat: {', '.join(viat)}")
    # @loppu ryhmat
    ehjat_kaatuivat = any(
        tulokset[Ajo(k, "", s)] for k in KOHTEET for s in siemenet
    )
    return 1 if ehjat_kaatuivat else 0


if __name__ == "__main__":
    sys.exit(main())
