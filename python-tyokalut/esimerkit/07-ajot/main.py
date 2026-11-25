"""Ulkoisen työkalun ajaminen: yksi ajo, aikaraja, virheet ja monta
ajoa rinnakkain."""

import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

SIMULAATTORI = Path(__file__).with_name("simulaattori.py")
VIRHE = re.compile(r"^UVM_(ERROR|FATAL)\b.*$", re.MULTILINE)


@dataclass(frozen=True)
class Tulos:
    testi: str
    siemen: int
    tila: str            # läpi | epäonnistui | aikaraja | työkaluvirhe
    virheet: tuple[str, ...] = ()


# @alku aja
def aja(testi: str, siemen: int, aikaraja_s: float = 6.0) -> Tulos:
    komento = [sys.executable, str(SIMULAATTORI), testi,
               "--siemen", str(siemen)]
    try:
        p = subprocess.run(komento, capture_output=True, text=True,
                           timeout=aikaraja_s, check=False)
    except subprocess.TimeoutExpired:
        return Tulos(testi, siemen, "aikaraja")   # run() tappoi lapsen
    virheet = tuple(m[0] for m in VIRHE.finditer(p.stdout))
    if p.returncode == 0 and not virheet:
        return Tulos(testi, siemen, "läpi")
    if virheet:
        return Tulos(testi, siemen, "epäonnistui", virheet)
    # Ei virheitä lokissa mutta nollasta poikkeava paluuarvo: vika on
    # työkalussa (lisenssi, kaatuminen), ei testattavassa piirissä.
    syy = p.stderr.strip().splitlines()[-1:] or [f"paluuarvo {p.returncode}"]
    return Tulos(testi, siemen, "työkaluvirhe", tuple(syy))
# @loppu aja


# @alku rinnakkain
def aja_kaikki(ajot: list[tuple[str, int]], rinnakkain: int) -> list[Tulos]:
    # Säikeet riittävät: työ tehdään lapsiprosesseissa, Python vain
    # odottaa niitä. map() palauttaa tulokset syötteen järjestyksessä.
    with ThreadPoolExecutor(max_workers=rinnakkain) as pooli:
        return list(pooli.map(lambda a: aja(a[0], a[1], 1.0), ajot))
# @loppu rinnakkain


def main() -> int:
    # @alku check
    try:
        subprocess.run([sys.executable, str(SIMULAATTORI), "kaatuu"],
                       capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"check=True: paluuarvo {e.returncode}, "
              f"stderr: {e.stderr.strip()}")
    # @loppu check
    ajot = [("uart_perus", 1), ("uart_perus", 2), ("uart_virheet", 1),
            ("uart_virheet", 2), ("fifo_jumi", 1), ("kaatuu", 1)]
    tulokset = aja_kaikki(ajot, rinnakkain=4)
    for t in tulokset:
        print(f"{t.testi:<14}{t.siemen:>3}  {t.tila}")
        for v in t.virheet:
            print(f"    {v}")
    epaonnistuneet = sum(t.tila != "läpi" for t in tulokset)
    print(f"{len(tulokset) - epaonnistuneet}/{len(tulokset)} läpi")
    return 0


if __name__ == "__main__":
    sys.exit(main())
