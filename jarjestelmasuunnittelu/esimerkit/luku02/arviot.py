"""Selkäpuolen arvio kuvanjakopalvelulle.

Lähtötiedot ovat oletuksia, ja arvio on niin hyvä kuin ne. Siksi
oletukset kirjoitetaan näkyviin ja arvio lasketaan ohjelmalla: kun
oletus muuttuu, kaikki seuraukset päivittyvät.
"""

from jarjestelma.arvio import (
    SEKUNTIA_PAIVASSA,
    SEKUNTIA_VUODESSA,
    bitit_s,
    maara,
    pyorista,
    tavut,
)

# @alku oletukset
PAIVITTAISET_KAYTTAJAT = 2_000_000
LATAUKSIA_PAIVASSA = 0.5          # kuvaa käyttäjää kohden
KATSELUJA_PAIVASSA = 40           # kuvaa käyttäjää kohden
HUIPPUKERROIN = 3                 # vilkkain tunti / keskiarvo
KUVAN_KOKO = 400_000              # tavua, pakattu alkuperäinen
ESIKATSELUN_KOKO = 30_000         # tavua, katselu näyttää esikatselun
METATIEDOT = 1_000                # tavua kuvaa kohden tietokannassa
SAILYTYS_VUOSINA = 5
KOPIOITA = 3                      # replikointi tai hajautuskoodaus
KUUMA_OSUUS = 0.2                 # päivän katseluista toistuu 80 %
# @loppu oletukset


def main() -> None:
    # @alku laskut
    lataukset_s = PAIVITTAISET_KAYTTAJAT * LATAUKSIA_PAIVASSA \
        / SEKUNTIA_PAIVASSA
    katselut_s = PAIVITTAISET_KAYTTAJAT * KATSELUJA_PAIVASSA \
        / SEKUNTIA_PAIVASSA
    kuvia_vuodessa = lataukset_s * SEKUNTIA_VUODESSA
    tallennus = kuvia_vuodessa * SAILYTYS_VUOSINA * KOPIOITA \
        * (KUVAN_KOKO + ESIKATSELUN_KOKO)
    metatiedot = kuvia_vuodessa * SAILYTYS_VUOSINA * METATIEDOT
    sisaan = lataukset_s * HUIPPUKERROIN * KUVAN_KOKO
    ulos = katselut_s * HUIPPUKERROIN * ESIKATSELUN_KOKO
    paivan_esikatselut = PAIVITTAISET_KAYTTAJAT * KATSELUJA_PAIVASSA \
        * ESIKATSELUN_KOKO
    # @loppu laskut

    print("Pyynnöt")
    print(f"  lataukset    {pyorista(lataukset_s):g}/s,"
          f" huipussa {pyorista(lataukset_s * HUIPPUKERROIN):g}/s")
    print(f"  katselut     {pyorista(katselut_s):g}/s,"
          f" huipussa {pyorista(katselut_s * HUIPPUKERROIN):g}/s")
    print(f"  luku:kirjoitus {round(katselut_s / lataukset_s)}:1")
    print("Tallennus")
    print(f"  kuvia        {maara(kuvia_vuodessa)} vuodessa")
    print(f"  kuvat        {tavut(tallennus)}"
          f" ({SAILYTYS_VUOSINA} v, {KOPIOITA} kopiota)")
    print(f"  metatiedot   {tavut(metatiedot)}"
          " (mahtuu yhteen tietokantaan)")
    print("Kaista huipussa")
    print(f"  sisään       {bitit_s(sisaan)}")
    print(f"  ulos         {bitit_s(ulos)}")
    print("Välimuisti")
    print(f"  esikatselut  {tavut(paivan_esikatselut)} päivässä,"
          f" kuuma osa {tavut(paivan_esikatselut * KUUMA_OSUUS)}")


if __name__ == "__main__":
    main()
