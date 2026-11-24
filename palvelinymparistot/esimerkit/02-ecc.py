"""ECC-muistin periaate: Hamming-koodi ja SECDED.

Palvelinmuisti tallentaa jokaisen 64-bittisen sanan rinnalle 8
tarkistusbittiä. Tässä sama periaate tavulle: Hamming(12,8) korjaa
yhden virheellisen bitin, ja koko koodisanan pariteetti havaitsee
kahden bitin virheen (single error correction, double error detection).
"""

from typing import Literal

PARITEETTIPAIKAT = (1, 2, 4, 8)
DATAPAIKAT = (3, 5, 6, 7, 9, 10, 11, 12)

Tila = Literal["ok", "korjattu", "korjaamaton"]


# @alku koodaus
def koodaa(tavu: int) -> list[int]:
    """Palauttaa 13 bittiä: paikka 0 on koko sanan pariteetti."""
    sana = [0] * 13
    for i, paikka in enumerate(DATAPAIKAT):
        sana[paikka] = (tavu >> i) & 1
    for p in PARITEETTIPAIKAT:
        sana[p] = sum(sana[k] for k in range(1, 13) if k & p) % 2
    sana[0] = sum(sana[1:]) % 2
    return sana


def pura(sana: list[int]) -> tuple[int, Tila]:
    sana = sana.copy()
    oireyhtyma = sum(p for p in PARITEETTIPAIKAT
                     if sum(sana[k] for k in range(1, 13) if k & p) % 2)
    pariteetti_ok = sum(sana) % 2 == 0
    if oireyhtyma and not pariteetti_ok:
        sana[oireyhtyma] ^= 1          # yksi virhe: korjataan
        tila: Tila = "korjattu"
    elif oireyhtyma:
        tila = "korjaamaton"           # kaksi virhettä: vain havaitaan
    elif not pariteetti_ok:
        sana[0] ^= 1                   # virhe itse pariteettibitissä
        tila = "korjattu"
    else:
        tila = "ok"
    tavu = sum(sana[p] << i for i, p in enumerate(DATAPAIKAT))
    return tavu, tila
# @loppu koodaus


def main() -> None:
    # @alku kokeet
    alkuperainen = 0b1011_0010
    sana = koodaa(alkuperainen)
    for kaannetyt in [(), (6,), (11,), (0,), (3, 9)]:
        vioittunut = sana.copy()
        for bitti in kaannetyt:
            vioittunut[bitti] ^= 1
        tavu, tila = pura(vioittunut)
        oikein = "oikein" if tavu == alkuperainen else "VÄÄRIN"
        print(f"käännetyt bitit {kaannetyt!s:7} -> {tila:11} "
              f"data {tavu:08b} ({oikein})")
    # @loppu kokeet


if __name__ == "__main__":
    main()
