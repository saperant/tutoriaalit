"""Kaatuminen natiivikoodissa. Ajettuna valitsimella -X faulthandler
tulkki tulostaa Python-kutsupinon ennen kuin prosessi päättyy."""

import ctypes


# @alku kaatuu
def nollaa_puskuri(osoite: int, pituus: int) -> None:
    ctypes.memset(osoite, 0, pituus)   # natiivikoodi kirjoittaa muistiin


def kasittele_tiedosto() -> None:
    nollaa_puskuri(0, 1)               # virhe: osoite on nolla
# @loppu kaatuu


if __name__ == "__main__":
    kasittele_tiedosto()
