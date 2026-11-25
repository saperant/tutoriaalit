"""Kokoaa esimerkkien kirjoittamat PPM-kuvat kirjan PNG-kuviksi.

Käyttö (hakemistossa esimerkit/): make kuvat
Esimerkit kirjoittavat kuvansa hakemistoon esimerkit/bin/. Kuvat
suurennetaan kokonaisluvulla ilman suodatusta, jotta pikselit pysyvät
terävinä, ja osa asetetaan rinnakkain. PNG:t ovat versionhallinnassa,
joten tätä ei ajeta testeissä.
"""

from pathlib import Path

from PIL import Image

JUURI = Path(__file__).resolve().parent.parent
BIN = JUURI / "esimerkit" / "bin"
KUVAT = JUURI / "kuvat"
VALI = (90, 90, 90)


def lue(nimi: str, kerroin: int) -> Image.Image:
    kuva = Image.open(BIN / f"{nimi}.ppm")
    return kuva.resize((kuva.width * kerroin, kuva.height * kerroin),
                       Image.NEAREST)


def rinnakkain(nimet: list[str], kerroin: int, vali: int = 8) -> Image.Image:
    osat = [lue(n, kerroin) for n in nimet]
    leveys = sum(o.width for o in osat) + vali * (len(osat) - 1)
    tulos = Image.new("RGB", (leveys, osat[0].height), VALI)
    x = 0
    for osa in osat:
        tulos.paste(osa, (x, 0))
        x += osa.width + vali
    return tulos


def main() -> None:
    for nimi in ("03-kolmio", "06-syvyys", "11-varjokartta",
                 "11-viivastetty"):
        lue(nimi, 4).save(KUVAT / f"{nimi}.png", optimize=True)
    rinnakkain(["05-lahin", "05-lineaarinen"], 4).save(
        KUVAT / "05-suodatus.png", optimize=True)
    rinnakkain(["11-g-albedo", "11-g-normaali", "11-g-sijainti"], 2).save(
        KUVAT / "11-gpuskuri.png", optimize=True)


if __name__ == "__main__":
    main()
