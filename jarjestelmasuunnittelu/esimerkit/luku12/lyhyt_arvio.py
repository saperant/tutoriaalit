"""Lyhytosoitepalvelun mitoitus.

Oletukset ovat harjoituksen vaatimuksista (luku 12): 100 miljoonaa
uutta linkkiä kuukaudessa, luku:kirjoitus 100:1, säilytys 5 vuotta.
"""

import math

from jarjestelma.arvio import (
    SEKUNTIA_PAIVASSA,
    bitit_s,
    maara,
    pyorista,
    tavut,
)

# @alku oletukset
UUSIA_KUUSSA = 100_000_000
LUKUJA_KIRJOITUSTA_KOHDEN = 100
HUIPPUKERROIN = 4
RIVIN_KOKO = 500            # tavua: koodi, osoite, aikaleima, indeksi
SAILYTYS_KK = 60
VASTAUKSEN_KOKO = 400       # tavua: 302-vastaus otsakkeineen
KUUMA_OSUUS = 0.2
# @loppu oletukset


def main() -> None:
    kirjoitukset = UUSIA_KUUSSA / (30 * SEKUNTIA_PAIVASSA)
    luvut = kirjoitukset * LUKUJA_KIRJOITUSTA_KOHDEN
    linkkeja = UUSIA_KUUSSA * SAILYTYS_KK
    print(f"kirjoituksia {pyorista(kirjoitukset):g}/s,"
          f" huipussa {pyorista(kirjoitukset * HUIPPUKERROIN):g}/s")
    print(f"lukuja {pyorista(luvut):g}/s,"
          f" huipussa {pyorista(luvut * HUIPPUKERROIN):g}/s")
    print(f"linkkejä 5 vuodessa {maara(linkkeja)},"
          f" tallennus {tavut(linkkeja * RIVIN_KOKO)}")
    bitteja = math.log2(linkkeja)
    print(f"tunnisteeseen tarvitaan {bitteja:.1f} bittiä; 40 bittiä riittää"
          f" {2 ** 40 / linkkeja:.0f}-kertaisesti")
    print(f"koodin pituus base62:na: {math.ceil(40 / math.log2(62))} merkkiä")
    paivan_luvut = luvut * SEKUNTIA_PAIVASSA
    print(f"lähtevä kaista huipussa"
          f" {bitit_s(luvut * HUIPPUKERROIN * VASTAUKSEN_KOKO)}")
    print(f"välimuisti: päivän luetuista kuumat {KUUMA_OSUUS:.0%}"
          f" = {tavut(paivan_luvut * KUUMA_OSUUS * RIVIN_KOKO)} (yläraja)")


if __name__ == "__main__":
    main()
