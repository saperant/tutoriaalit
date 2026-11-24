"""Uudelleenrakennuksen riski: lukuvirhe (URE) ja rakennusaika.

Kun RAID 5:stä hajoaa levy, kaikki jäljelle jääneet levyt luetaan
kokonaan. Jos yksikin sektori on lukukelvoton (unrecoverable read
error), RAID 5 ei voi rakentaa sitä osaa uudelleen. Valmistajat
ilmoittavat URE-tason muodossa "1 virhe / 10^14 luettua bittiä".
"""

import math

TT = 10**12  # tavua


# @alku ure
def ure_todennakoisyys(luettavat_tavut: float, ure_per_bitti: float
                       ) -> float:
    """Todennäköisyys vähintään yhdelle lukuvirheelle (Poisson)."""
    return 1 - math.exp(-luettavat_tavut * 8 * ure_per_bitti)


def rakennusaika_h(levyn_tavut: float, mt_per_s: float,
                   kuormitus: float) -> float:
    """Kesto tunteina, kun tuotantokuorma vie osan kaistasta."""
    return levyn_tavut / (mt_per_s * 1e6 * (1 - kuormitus)) / 3600
# @loppu ure


def main() -> None:
    koko = 12 * TT
    for levyja in (4, 8):
        luettava = (levyja - 1) * koko
        for nimi, taso in (("kuluttaja 10^-14", 1e-14),
                           ("yritys 10^-15", 1e-15)):
            p = ure_todennakoisyys(luettava, taso)
            print(f"RAID 5, {levyja} × 12 Tt, {nimi}: "
                  f"lukuvirhe rakennuksen aikana {p:.0%}")
    aika = rakennusaika_h(koko, mt_per_s=200, kuormitus=0.5)
    print(f"rakennusaika 12 Tt, 200 Mt/s, puolet kaistasta kuormalla: "
          f"{aika:.0f} h")


if __name__ == "__main__":
    main()
