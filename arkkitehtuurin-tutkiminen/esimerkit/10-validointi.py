"""Intervallimallin kalibrointi ja validointi eri datalla.

Käyttö: python3 10-validointi.py YDINMALLIN_TULOSTE KÄSKYVIRTA

Haaran hinta (palautus + ratkaisuaika) sovitetaan ikkunoilla 16 ja 64,
ja mallia testataan ikkunalla 128, jota sovitus ei nähnyt.
"""

import sys
from dataclasses import replace
from pathlib import Path

from arkki.intervalli import Ydin, intervallimalli
from arkki.tilasto import virheet


def main() -> None:
    kaskyt = Path(sys.argv[2]).read_text("ascii").strip()
    # @alku data
    ytimet, tarkat = [], []
    for rivi in Path(sys.argv[1]).read_text("utf-8").splitlines()[2:5]:
        ikkuna, _jaksot, cpi, perus = rivi.split()
        ytimet.append(Ydin(int(ikkuna), float(perus)))
        tarkat.append(float(cpi))
    sovitus, testi = [0, 1], [2]
    # @loppu data

    def arviot(haara: int, joukko: list[int]) -> list[float]:
        return [intervallimalli(kaskyt, replace(ytimet[i], haara=haara))
                / len(kaskyt) for i in joukko]

    # @alku kalibrointi
    def neliovirhe(haara: int) -> float:
        return sum((a / tarkat[i] - 1) ** 2 for a, i in
                   zip(arviot(haara, sovitus), sovitus, strict=True))

    paras = min(range(0, 41), key=neliovirhe)
    # @loppu kalibrointi
    print(f"oletus haara = 18, sovitettu haara = {paras}")
    print(f"{'':<10} {'sovitus MAPE':>13} {'testi MAPE':>11}"
          f" {'testi max':>10}")
    for nimi, haara in (("oletus", 18), ("sovitettu", paras)):
        s, _ = virheet(arviot(haara, sovitus), [tarkat[i] for i in sovitus])
        t, tmax = virheet(arviot(haara, testi), [tarkat[i] for i in testi])
        print(f"{nimi:<10} {s:13.1%} {t:11.1%} {tmax:10.1%}")


if __name__ == "__main__":
    main()
