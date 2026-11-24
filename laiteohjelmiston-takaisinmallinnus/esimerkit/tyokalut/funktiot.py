"""Funktioluettelo raa'asta kuvasta.

Käyttö: python3 funktiot.py KUVA KANTA TAULU LOPPU [--vain-kutsut]

Funktiot etsitään vektoritaulusta lähtien bl-kutsuja seuraamalla ja
(ilman valitsinta --vain-kutsut) lisäksi datan funktio-osoittimista.
Koko on etäisyys seuraavan funktion alkuun, joten se sisältää myös
funktion literaalivarannon ja täytteen.
"""
import sys

import thumb
from kuva import Kuva


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    taulu, loppu = int(sys.argv[3], 0), int(sys.argv[4], 0)
    alue = (taulu, loppu)
    if "--vain-kutsut" in sys.argv:
        juuret = thumb.vektorijuuret(kuva, taulu, 32)
        funktiot = thumb.etsi_funktiot(kuva, juuret, alue)
    else:
        funktiot = thumb.kaikki_funktiot(kuva, taulu, 32, alue)
    kutsujat = {o: 0 for o in funktiot}
    for f in funktiot.values():
        for kohde in f.kutsuu:
            if kohde in kutsujat:
                kutsujat[kohde] += 1
    alut = sorted(funktiot)
    print(f"funktioita {len(alut)}")
    print("osoite   koko käskyjä kutsuu kutsujia")
    for i, osoite in enumerate(alut):
        seuraava = alut[i + 1] if i + 1 < len(alut) else funktiot[
            osoite].loppu
        f = funktiot[osoite]
        print(f"{osoite:#07x} {seuraava - osoite:5} {f.kaskyja:7} "
              f"{len(f.kutsuu):6} {kutsujat[osoite]:8}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
