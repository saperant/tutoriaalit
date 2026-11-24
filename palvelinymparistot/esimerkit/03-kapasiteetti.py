"""RAID-tasojen vertailu: käytettävä kapasiteetti ja vikasietoisuus.

Laskee kahdeksan 12 Tt:n levyn ryhmälle, kuinka paljon tilaa jää
käyttöön ja montako levyä saa hajota. RAID 10 kestää varmasti yhden
levyn, ja onnella yhden levyn kustakin peiliparista.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Taso:
    nimi: str
    kaytettavat: int        # datalevyjen määrä
    kestaa: int             # varmasti kestettävät levyviat
    kirjoitusrangaistus: int  # levy-I/O:ta satunnaista kirjoitusta kohti


# @alku tasot
def tasot(n: int) -> list[Taso]:
    return [
        Taso("RAID 0", n, 0, 1),
        Taso("RAID 1 (n-peili)", 1, n - 1, n),
        Taso("RAID 10", n // 2, 1, 2),
        Taso("RAID 5", n - 1, 1, 4),
        Taso("RAID 6", n - 2, 2, 6),
    ]
# @loppu tasot


def main() -> None:
    levyja, koko_tt = 8, 12
    print(f"{levyja} × {koko_tt} Tt = {levyja * koko_tt} Tt raakaa")
    print(f"{'taso':17} {'käytössä':>9} {'osuus':>6} {'kestää':>7} "
          f"{'kirj.×':>7}")
    for t in tasot(levyja):
        tila = t.kaytettavat * koko_tt
        print(f"{t.nimi:17} {tila:>6} Tt {tila / (levyja * koko_tt):>6.0%} "
              f"{t.kestaa:>7} {t.kirjoitusrangaistus:>7}")


if __name__ == "__main__":
    main()
