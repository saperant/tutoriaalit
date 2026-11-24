"""Paketin viive koostuu neljästä osasta."""

from dataclasses import dataclass

VALON_NOPEUS_KUIDUSSA = 2e8           # m/s, noin 2/3 tyhjiön nopeudesta


@dataclass(frozen=True)
class Linkki:
    nimi: str
    nopeus_bit_s: float
    pituus_m: float
    jono_s: float = 0.0               # keskimääräinen jonotus
    kasittely_s: float = 20e-6        # reitittimen käsittely


# @alku viive
def viiveet(paketti_tavua: int, reitti: list[Linkki]) -> None:
    yhteensa = 0.0
    for linkki in reitti:
        siirto = paketti_tavua * 8 / linkki.nopeus_bit_s
        eteneminen = linkki.pituus_m / VALON_NOPEUS_KUIDUSSA
        yhteensa += (siirto + eteneminen + linkki.jono_s
                     + linkki.kasittely_s)
        print(f"  {linkki.nimi:<18} siirto {siirto * 1e3:6.3f} ms"
              f"  eteneminen {eteneminen * 1e3:5.3f} ms"
              f"  jono {linkki.jono_s * 1e3:4.2f} ms")
    print(f"  yhteensä {yhteensa * 1e3:.2f} ms")


reitti = [
    Linkki("koti (100 Mbit/s)", 100e6, 2_000, jono_s=0.5e-3),
    Linkki("runko (10 Gbit/s)", 10e9, 1_600_000, jono_s=0.1e-3),
    Linkki("konesali (1 Gbit)", 1e9, 500),
]
for koko in (1500, 64):
    print(f"{koko} tavun paketti Helsingistä Frankfurtiin:")
    viiveet(koko, reitti)
# @loppu viive
