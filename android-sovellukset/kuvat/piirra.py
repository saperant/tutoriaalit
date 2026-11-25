"""Kokoaa tutoriaalin kuvat testien tuottamista kuvakaappauksista.

Kuvakaappaukset tekee KuvakaappausTest (Robolectric + Roborazzi)
hakemistoon esimerkit/app/build/kuvat; tämä skripti kehystää ne ja
yhdistää parit rinnakkain. Aja: make kuvat (paketin juuressa).
"""

from pathlib import Path

from PIL import Image, ImageDraw

JUURI = Path(__file__).resolve().parent
LAHDE = JUURI.parent / "esimerkit" / "app" / "build" / "kuvat"
KEHYS = (184, 196, 200)
NUOLI = (91, 107, 112)
VALI = 96


def ruutu(nimi: str) -> Image.Image:
    """Kuvakaappaus ohuella kehyksellä, jotta vaalea tausta erottuu."""
    kuva = Image.open(LAHDE / f"{nimi}.png").convert("RGB")
    kehystetty = Image.new("RGB", (kuva.width + 4, kuva.height + 4), KEHYS)
    kehystetty.paste(kuva, (2, 2))
    return kehystetty


def rinnakkain(vasen: Image.Image, oikea: Image.Image,
               nuoli: bool = False) -> Image.Image:
    korkeus = max(vasen.height, oikea.height)
    kuva = Image.new("RGB", (vasen.width + VALI + oikea.width, korkeus),
                     "white")
    kuva.paste(vasen, (0, 0))
    kuva.paste(oikea, (vasen.width + VALI, 0))
    if nuoli:
        piirto = ImageDraw.Draw(kuva)
        y = korkeus // 3
        x0, x1 = vasen.width + 16, vasen.width + VALI - 16
        piirto.line([(x0, y), (x1, y)], fill=NUOLI, width=6)
        piirto.polygon([(x1 + 8, y), (x1 - 16, y - 16), (x1 - 16, y + 16)],
                       fill=NUOLI)
    return kuva


def main() -> None:
    ruutu("lista").save(JUURI / "lista.png", optimize=True)
    ruutu("lista-viesti").save(JUURI / "viesti.png", optimize=True)
    ruutu("maaravalitsin").save(JUURI / "maaravalitsin.png", optimize=True)
    rinnakkain(ruutu("lista"), ruutu("lista-tumma")).save(
        JUURI / "teemat.png", optimize=True)
    rinnakkain(ruutu("lista"), ruutu("tuote"), nuoli=True).save(
        JUURI / "navigointi.png", optimize=True)
    for tiedosto in sorted(JUURI.glob("*.png")):
        print(f"{tiedosto.name}: {tiedosto.stat().st_size // 1024} kt")


if __name__ == "__main__":
    main()
