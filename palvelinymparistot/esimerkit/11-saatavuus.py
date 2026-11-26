"""Saatavuuden laskenta: "yhdeksiköt", sarjaan ja rinnakkain.

Palvelu, joka tarvitsee kaikki osansa (sarjaan kytketty), on
heikompi kuin heikoin osansa. Rinnakkaiset kopiot, joista yksi
riittää, nostavat saatavuutta. Laskut olettavat viat
riippumattomiksi; yhteinen sähkönsyöttö tai ohjelmistovika rikkoo
oletuksen.
"""

import math

MINUUTTEJA_KK = 30 * 24 * 60
MINUUTTEJA_V = 365 * 24 * 60


# @alku kaavat
def sarjaan(*osat: float) -> float:
    return math.prod(osat)


def rinnakkain(osa: float, kopioita: int) -> float:
    return 1 - (1 - osa) ** kopioita
# @loppu kaavat


def katko(saatavuus: float) -> str:
    kk = (1 - saatavuus) * MINUUTTEJA_KK
    v = (1 - saatavuus) * MINUUTTEJA_V / 60
    return f"{kk:7.1f} min/kk {v:6.1f} h/v"


def main() -> None:
    for s in (0.99, 0.999, 0.9999):
        print(f"{s:.2%}: sallittu katko {katko(s)}")
    # @alku esimerkki
    kuormantasaaja, sovellus, tietokanta = 0.9995, 0.995, 0.999
    yksi = sarjaan(kuormantasaaja, sovellus, tietokanta)
    kolme = sarjaan(kuormantasaaja, rinnakkain(sovellus, 3), tietokanta)
    print(f"yksi sovelluspalvelin:   {yksi:.4%} ({katko(yksi)})")
    print(f"kolme sovelluspalvelinta: {kolme:.4%} ({katko(kolme)})")
    # @loppu esimerkki


if __name__ == "__main__":
    main()
