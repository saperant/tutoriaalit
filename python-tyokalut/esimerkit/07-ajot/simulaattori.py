"""Simulaattorin korvike esimerkkejä varten: käyttäytyy kuin oikea
komentorivisimulaattori (loki tulosteeseen, paluuarvo 0 tai 1), mutta
on nopea ja deterministinen."""

import argparse
import sys
import time


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("testi")
    p.add_argument("--siemen", type=int, default=1)
    args = p.parse_args()
    print(f"UVM_INFO @ 0ns: [ALKU] {args.testi}, siemen {args.siemen}")
    if args.testi == "fifo_jumi":
        time.sleep(30)                      # simulaatio jumittuu
    if args.testi == "uart_virheet" and args.siemen % 2:
        print("UVM_ERROR @ 2us: [VERTAILU] odotettu 0x3f, saatu 0x3e")
        print("TESTI EPÄONNISTUI")
        return 1
    if args.testi == "kaatuu":
        print("lisenssipalvelin ei vastaa", file=sys.stderr)
        return 3
    print(f"UVM_INFO @ {args.siemen * 100}us: [LOPPU] TESTI LÄPI")
    return 0


if __name__ == "__main__":
    sys.exit(main())
