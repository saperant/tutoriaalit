"""Vertaa luvun 5 mallien tuloksia syklimalliin ja MVA:han (luku 4).

Käyttö: python3 05-vertailu.py MALLIEN_TULOSTE
"""

import sys
from pathlib import Path

from arkki.jonot import mva

LASKENTA, VIIVE, PALVELU = 100.0, 44.0, 10.0  # kuten 04-mva.py


def main() -> None:
    # @alku luku
    tulokset: dict[tuple[str, int], tuple[float, float, int]] = {}
    for rivi in Path(sys.argv[1]).read_text("utf-8").splitlines()[1:]:
        malli, ytimia, kvantti, _aika, kaista, viive, akt = rivi.split()
        if kvantti == "0":
            tulokset[malli, int(ytimia)] = (float(kaista), float(viive),
                                            int(akt))
    # @loppu luku
    print("viiveen virhe syklimalliin verrattuna (%)")
    print(f"{'K':>3} {'sykli ns':>9} {'lt':>7} {'varaus':>7} {'MVA':>7}"
          f" {'akt. sykli/varaus':>18}")
    for k in sorted({k for _, k in tulokset}):
        # @alku virheet
        _, viite, akt_sykli = tulokset["sykli", k]
        _, r = mva(k, LASKENTA + VIIVE, [PALVELU])
        ennusteet = [tulokset["lt", k][1], tulokset["varaus", k][1],
                     VIIVE + r]
        virheet = [100 * (e / viite - 1) for e in ennusteet]
        # @loppu virheet
        suhde = akt_sykli / tulokset["varaus", k][2]
        print(f"{k:>3} {viite:9.1f}" + "".join(f"{v:+7.1f}" for v in virheet)
              + f" {suhde:18.0f}")


if __name__ == "__main__":
    main()
