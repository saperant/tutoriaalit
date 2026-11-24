"""GIL: C++-koodi vapauttaa sen, jotta muut säikeet pääsevät
ajoon, ja ottaa sen takaisin ennen kuin koskee Python-olioihin."""

import threading
import time

import numpy as np
import rinnakkain


# @alku odotus
def kokeile(vapauta: bool) -> bool:
    def asettaja() -> None:
        time.sleep(0.05)               # Python-koodia: tarvitsee GIL:n
        rinnakkain.aseta_lippu()

    saie = threading.Thread(target=asettaja)
    saie.start()
    tulos = rinnakkain.odota_lippua(500, vapauta)
    saie.join()
    return tulos


def main() -> None:
    print("GIL varattuna, lippu asettui:", kokeile(vapauta=False))
    print("GIL vapautettuna, lippu asettui:", kokeile(vapauta=True))
    # @loppu odotus

    # @alku saikeet
    data = np.random.default_rng(3).random(1_000_000)
    summa = rinnakkain.summa_saikeilla(data, 4)
    print("neljän säikeen summa täsmää:",
          bool(np.isclose(summa, data.sum())))
    # @loppu saikeet

    # @alku takaisinkutsu
    saadut: list[int] = []
    rinnakkain.raportoi_taustalla(3, saadut.append)
    print("taustasäikeen kutsut:", saadut)
    # @loppu takaisinkutsu


if __name__ == "__main__":
    main()
