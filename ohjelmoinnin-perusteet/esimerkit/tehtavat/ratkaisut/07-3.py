"""Malliratkaisu 07-3: Korjaa kaatuva ohjelma."""

import sys

tulokset: dict[str, int] = {}
for nro, rivi in enumerate(sys.stdin, start=1):
    if not rivi.strip():
        continue
    nimi, pisteet = rivi.split()
    try:
        tulokset[nimi] = int(pisteet)
    except ValueError:
        print(f"Rivi {nro}: virheelliset pisteet '{pisteet}'")

if not tulokset:
    print("Ei tuloksia.")
    sys.exit(0)

keskiarvo = sum(tulokset.values()) / len(tulokset)
paras = max(tulokset, key=lambda nimi: tulokset[nimi])
print(f"Keskiarvo: {keskiarvo:.1f}")
print(f"Paras: {paras} ({tulokset[paras]})")
