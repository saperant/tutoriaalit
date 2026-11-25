"""Komentoriviargumentit: python3 09-toista.py Hei 3"""

import sys


def main() -> int:
    if len(sys.argv) != 3 or not sys.argv[2].isdigit():
        print("Käyttö: python3 09-toista.py TEKSTI KERRAT")
        return 2
    teksti = sys.argv[1]
    kerrat = int(sys.argv[2])
    for nro in range(1, kerrat + 1):
        print(f"{nro}: {teksti}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
