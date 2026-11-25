"""Nollauksen vapautus: recovery- ja removal-tarkistus.

Asynkroninen nollaus saa alkaa milloin tahansa, mutta sen on
vapauduttava kaikilta kiikuilta saman kellojakson aikana. Tahdistin
tuo vapautuksen kellon tahtiin, ja ajoitusanalyysi tarkistaa polun
tahdistimesta kiikkujen nollaustuloihin: recovery on nollauksen
asetus- ja removal sen pitotarkistus.
"""

from pathlib import Path

from sdc import lue_sdc
from sta import Analyysi, pahimmat
from synteesi import syntetisoi

HAK = Path(__file__).parent


def main() -> None:
    tulos = syntetisoi([HAK / "nollaus.v"], "nollaus")
    # @alku ajo
    r = lue_sdc(HAK / "nollaus.sdc")
    analyysi = Analyysi(tulos, r)
    t2 = next(b for b, nimi in analyysi.nimet.items() if nimi == "t2")
    print(f"t2 ajaa {len(analyysi.nielut[t2])} nollaustuloa, kuorma "
          f"{analyysi.kuorma[t2] * 1000:.0f} fF")
    print("laskurin kello myöhässä ns   recovery   removal")
    for vinous in [0.0, 0.2, 0.4]:
        r.kellon_viive = {"q[*]": vinous}
        polut = [p for p in Analyysi(tulos, r).polut() if p.alku == "t2"]
        print(f"{vinous:25.1f} "
              f"{pahimmat(polut, 'asetus')[0].marginaali:+10.3f} "
              f"{pahimmat(polut, 'pito')[0].marginaali:+9.3f}")
    # @loppu ajo


if __name__ == "__main__":
    main()
