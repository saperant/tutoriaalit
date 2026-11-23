"""Laskee kulut luokittain CSV-muotoisesta syötteestä."""

import csv
import sys
from collections import defaultdict
from decimal import Decimal


def main() -> int:
    summat: dict[str, Decimal] = defaultdict(Decimal)
    lukija = csv.DictReader(sys.stdin)
    for rivi in lukija:
        summat[rivi["luokka"]] += Decimal(rivi["summa"])

    for luokka, summa in sorted(summat.items(), key=lambda p: -p[1]):
        print(f"{luokka:<12}{summa:>10.2f} €")
    print(f"{'yhteensä':<12}{sum(summat.values()):>10.2f} €")
    return 0


if __name__ == "__main__":
    sys.exit(main())
