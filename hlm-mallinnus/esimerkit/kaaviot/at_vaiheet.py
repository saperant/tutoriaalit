"""Ajoituskaavio esimerkin 13-at vaihelokista.

Käyttö: python3 kaaviot/at_vaiheet.py 13-at/odotettu > at-vaiheet.json

Lokin rivit ovat muotoa "10 ns  END_REQ    aloittaja  #0". Kaaviossa on
yksi sarake 10 ns:a kohti: pyyntökanavalla siirto näkyy BEGIN_REQ:sta
END_REQ:hun ja vastauskanavalla BEGIN_RESP:stä END_RESP:hen (vähintään
yhden sarakkeen ajan). LT-rivi on sama työ b_transportilla: lokin
viimeisen rivin LT-aika jaetaan tasan siirtojen kesken, koska
LT-siirrot ovat peräkkäisiä ja yhtä pitkiä.
"""

import json
import re
import sys
from collections.abc import Sequence
from typing import Any

ASKEL = 10  # ns


def aika_ns(teksti: str) -> int:
    luku, yksikko = teksti.split()
    return int(float(luku) * {"s": 1e9, "ns": 1, "us": 1e3}[yksikko])


def rivi(nimi: str, jaksot: Sequence[str | None]) -> dict[str, Any]:
    """Sarakkeittainen tunniste (tai None) WaveDrom-riviksi."""
    aalto, data = "", []
    edellinen: str | None = "alku"
    for arvo in jaksot:
        if arvo == edellinen:
            aalto += "."
        elif arvo is None:
            aalto += "z"
        else:
            aalto += "="
            data.append(arvo)
        edellinen = arvo
    return {"name": nimi, "wave": aalto, "data": data}


def main() -> None:
    teksti = open(sys.argv[1], encoding="utf-8").read()
    vaiheet: dict[tuple[str, str], int] = {}
    for m in re.finditer(r"^\s*([\d.]+ \w+)\s+(\w+)\s+\w+\s+(#\d+)$",
                         teksti, re.M):
        vaiheet[(m.group(3), m.group(2))] = aika_ns(m.group(1))
    lt = re.search(r"LT valmis ([\d.]+ \w+)", teksti)
    assert lt is not None, "LT-aika puuttuu lokista"
    lt_loppu = aika_ns(lt.group(1))
    siirrot = sorted({s for s, _ in vaiheet}, key=lambda s: int(s[1:]))
    sarakkeita = lt_loppu // ASKEL
    pyynto: list[str | None] = [None] * sarakkeita
    vastaus: list[str | None] = [None] * sarakkeita
    for s in siirrot:
        a, b = vaiheet[(s, "BEGIN_REQ")], vaiheet[(s, "END_REQ")]
        for k in range(a // ASKEL, b // ASKEL):
            pyynto[k] = s
        a, b = vaiheet[(s, "BEGIN_RESP")], vaiheet[(s, "END_RESP")]
        for k in range(a // ASKEL, max(b, a + ASKEL) // ASKEL):
            vastaus[k] = s
    kesto = lt_loppu // len(siirrot)
    lt_rivi = [siirrot[(k * ASKEL) // kesto] for k in range(sarakkeita)]
    # Aika-akseli 50 ns:n jaksoina.
    aika = [f"{k * ASKEL // 50 * 50} ns" for k in range(sarakkeita)]
    tulos = {"signal": [rivi("aika", aika),
                        ["AT", rivi("pyyntö", pyynto),
                         rivi("vastaus", vastaus)],
                        ["LT", rivi("b_transport", lt_rivi)]],
             "config": {"hscale": 0.55}}
    print(json.dumps(tulos, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
