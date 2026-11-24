"""Summaimen arkkitehtuuri: pinta-ala ja nopeus samassa kirjastossa.

Sama yhteenlasku kolmella rakenteella: ripple-carry, Brent–Kung
(Yosysin oletus +-operaattorille) ja Kogge–Stone. ABC:n oletusskripti
optimoi pinta-alaa ja purkaa rakenteen; skriptillä "strash; map"
rakenne säilyy. Jokainen tulos analysoidaan samalla
ajoitusanalyysillä.
"""

from pathlib import Path

from sta import Analyysi, Rajoitteet, pahimmat
from synteesi import pinta_ala, solujen_alat, syntetisoi

HAK = Path(__file__).parent


def main() -> None:
    alat = solujen_alat()
    # @alku vertailu
    print("rakenne            soluja   ala µm²   polku ns   fmax MHz")
    sailyta = "-script +strash;map"
    for top, abc in [("summain_ripple", sailyta), ("summain_bk", sailyta),
                     ("summain_ks", sailyta), ("summain_bk", "")]:
        tulos = syntetisoi([HAK / "summaimet.v"], top, abc=abc)
        polut = Analyysi(tulos, Rajoitteet(jakso=10.0)).polut()
        viive = 10.0 - pahimmat(polut, "asetus")[0].marginaali
        nimi = top.removeprefix("summain_") + (
            "" if abc else ", ABC:n oletus")
        print(f"{nimi:16} {sum(tulos.solut().values()):8} "
              f"{pinta_ala(tulos, alat):9.1f} {viive:10.3f} "
              f"{1000 / viive:10.0f}")
    # @loppu vertailu


if __name__ == "__main__":
    main()
