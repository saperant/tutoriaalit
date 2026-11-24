"""Flash-vedoksen käytetyt alueet: yhtenäiset jaksot, jotka eivät ole
tyhjää flashia (0xFF).

Käyttö: python3 alueet.py VEDOS [VÄLI]

Lyhyemmät kuin VÄLI tavun (oletus 64) tyhjät kohdat yhdistetään
viereisiin alueisiin.
"""
import sys


def alueet(data: bytes, vali: int) -> list[tuple[int, int]]:
    tulos: list[tuple[int, int]] = []
    i = 0
    while i < len(data):
        if data[i] == 0xFF:
            i += 1
            continue
        alku = i
        tyhjia = 0
        while i < len(data) and tyhjia < vali:
            tyhjia = tyhjia + 1 if data[i] == 0xFF else 0
            i += 1
        tulos.append((alku, i - tyhjia))
    return tulos


def main() -> None:
    with open(sys.argv[1], "rb") as f:
        data = f.read()
    vali = int(sys.argv[2]) if len(sys.argv) > 2 else 64
    for alku, loppu in alueet(data, vali):
        print(f"{alku:#07x}..{loppu:#07x}  {loppu - alku:6} tavua")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
