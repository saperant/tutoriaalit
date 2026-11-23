"""Lukee mittauksia syötteestä ja raportoi virheelliset rivit."""

import sys


# @alku syote
def lue_mittaukset(rivit: list[str]) -> tuple[list[float], list[str]]:
    arvot: list[float] = []
    virheet: list[str] = []
    for numero, rivi in enumerate(rivit, start=1):
        rivi = rivi.strip()
        if not rivi or rivi.startswith("#"):
            continue
        try:
            arvot.append(float(rivi.replace(",", ".")))
        except ValueError:
            virheet.append(f"rivi {numero}: ei luku: {rivi!r}")
    return arvot, virheet


arvot, virheet = lue_mittaukset(sys.stdin.readlines())
print(f"{len(arvot)} mittausta, keskiarvo {sum(arvot) / len(arvot):.2f}")
for virhe in virheet:
    print(virhe, file=sys.stderr)
# @loppu syote
