"""Simulaation käynnistimen argumentit: yksiköt ja rajat tarkistetaan
jäsennysvaiheessa, jolloin virheilmoitus kertoo käyttäjälle tarkasti,
mikä on vialla, ennen kuin mitään on ajettu."""

import argparse
import re
import sys

# @alku tyypit
YKSIKOT = {"Hz": 1, "kHz": 10**3, "MHz": 10**6, "GHz": 10**9}


def taajuus(teksti: str) -> int:
    """'100MHz' -> 100_000_000. Virheestä ArgumentTypeError."""
    osuma = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kMG]?Hz)", teksti)
    if osuma is None:
        raise argparse.ArgumentTypeError(
            f"virheellinen taajuus {teksti!r}, esim. 100MHz")
    return round(float(osuma[1]) * YKSIKOT[osuma[2]])


def ei_negatiivinen(teksti: str) -> int:
    arvo = int(teksti)  # ValueError -> argparse: "invalid ... value"
    if arvo < 0:
        raise argparse.ArgumentTypeError("arvon on oltava >= 0")
    return arvo
# @loppu tyypit


def tee_jasennin() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aja-sim")
    p.add_argument("--kello", type=taajuus, required=True)
    p.add_argument("--siemen", type=ei_negatiivinen, default=1)
    p.add_argument("testi")
    return p


def main() -> int:
    p = tee_jasennin()
    ok = p.parse_args(["--kello", "125MHz", "--siemen", "7", "uart"])
    print(f"{ok.testi}: kello {ok.kello} Hz, siemen {ok.siemen}")
    huono = p.parse_args(sys.argv[1:])  # tästä argparse lopettaa (2)
    print(huono)
    return 0


if __name__ == "__main__":
    sys.exit(main())
