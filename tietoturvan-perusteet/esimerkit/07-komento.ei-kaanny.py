"""Komentoinjektio: ruff (flake8-bandit, S602) löytää shell=True-kutsun.

Rivit, joilla on merkintä @virhe, ovat haavoittuva versio. Ilman niitä
ohjelma käyttää turvallista muotoa, ja tarkistus menee läpi.
"""

import subprocess


# @alku tervehdys
def tervehdys(nimi: str) -> str:
    komento = f"echo Hei {nimi}"                             # @virhe
    tulos = subprocess.run(komento, shell=True,              # @virhe
                           capture_output=True, text=True)  # @virhe
    # Argumenttilista: nimi on yksi argumentti eikä komentotulkin syötettä.
    # S603/S607 muistuttavat aliprosesseista; tässä ne on tarkistettu.
    tulos = subprocess.run(["echo", "Hei", nimi],  # noqa: S603, S607
                           capture_output=True, text=True, check=True)
    return tulos.stdout
# @loppu tervehdys


print(tervehdys("Aino; echo HYOKKAAJAN KOMENTO AJETTIIN"), end="")
