"""Tiivistää kääntäjän ja clang-tidyn varoitukset muotoon
"rivi N [tunnus]" (ja CWE-luokka, jos työkalu kertoo sen).

Käyttö:  gcc ... 2>&1 | python3 varoitukset.py
"""

from __future__ import annotations

import re
import sys

VAROITUS = re.compile(r"^[^:]+:(\d+):\d+: warning: .*?((?:\[[^]]+\] ?)+)$")


def main() -> int:
    nahdyt: set[tuple[int, str]] = set()
    for rivi in sys.stdin.read().splitlines():
        osuma = VAROITUS.match(rivi)
        if osuma is None:
            continue
        tunnukset = re.findall(r"\[([^]]+)\]", osuma.group(2))
        tunnukset.sort(key=lambda t: t.startswith("CWE"))
        nahdyt.add((int(osuma.group(1)), ", ".join(tunnukset)))
    for numero, tunnus in sorted(nahdyt):
        print(f"rivi {numero} [{tunnus}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
