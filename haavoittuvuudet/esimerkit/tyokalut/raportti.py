"""Tiivistää sanitoijan tai glibc:n virheraportin vertailukelpoiseksi.

Käyttö:  ohjelma 2>&1 | python3 raportti.py

Raportit sisältävät osoitteita, prosessinumeroita ja kirjastojen
sisäisiä kehyksiä, jotka vaihtelevat ajosta ja koneesta toiseen.
Tiivistelmään jäävät virheen laji, luku- tai kirjoitusoperaation koko,
virheen kohta omassa koodissa sekä muistialue, jota virhe koskee.
"""

from __future__ import annotations

import re
import sys
import textwrap

# @alku kuviot
VIRHE = re.compile(r"ERROR: AddressSanitizer: "
                   r"(attempting [\w-]+|[\w-]+)")
OPERAATIO = re.compile(r"^(READ|WRITE) of size (\d+)")
KEHYS = re.compile(r"^\s+#\d+ 0x[0-9a-f]+ in (\S+) (\S+?):(\d+)")
ALUE = re.compile(r"is located (\d+) bytes (after|before|inside of) "
                  r"(\d+)-byte region")
MUUTTUJA = re.compile(r"\[\d+, \d+\) '(\w+)'.*<== Memory access")
UBSAN = re.compile(r"([\w.-]+\.c):(\d+):\d+: runtime error: (.*)")
GLIBC = re.compile(r"^(\*\*\* .* \*\*\*|(?:free|malloc|realloc)\(\): .*)")
# @loppu kuviot

OTSIKOT = {
    "freed by thread": "vapautettu",
    "previously allocated by thread": "varattu",
    "allocated by thread": "varattu",
}


def oma_kehys(rivi: str) -> str | None:
    """Palauttaa muodon 'funktio (tiedosto.c:rivi)', jos kehys on
    esimerkin omassa lähdekoodissa eikä sanitoijan tai C-kirjaston."""
    osuma = KEHYS.match(rivi)
    if osuma is None:
        return None
    funktio, polku, numero = osuma.groups()
    tiedosto = polku.rsplit("/", 1)[-1]
    if not tiedosto.endswith(".c") or "sanitizer" in polku:
        return None
    if funktio.startswith(("__", "_start")):
        return None
    return f"{funktio} ({tiedosto}:{numero})"


def tiivista(rivit: list[str]) -> list[str]:
    tulos: list[str] = []
    odotettu: str | None = "kohta"   # mitä seuraava oma kehys tarkoittaa
    for rivi in rivit:
        if m := VIRHE.search(rivi):
            tulos.append(f"ASan: {m.group(1)}")
        elif m := OPERAATIO.match(rivi):
            tulos.append(f"  {m.group(1)} of size {m.group(2)}")
        elif m := ALUE.search(rivi):
            tulos.append(f"  alue: {m.group(3)} tavun varaus, "
                         f"{m.group(1)} tavua {suunta(m.group(2))}")
        elif m := MUUTTUJA.search(rivi):
            tulos.append(f"  muuttuja: {m.group(1)}")
        elif m := UBSAN.search(rivi):
            tulos.append(f"UBSan: {m.group(1)}:{m.group(2)}: "
                         f"{m.group(3)}")
        elif m := GLIBC.match(rivi.strip()):
            tulos.append(f"glibc: {m.group(1)}")
        elif otsikko := next((v for k, v in OTSIKOT.items()
                              if rivi.startswith(k)), None):
            odotettu = otsikko
        elif odotettu is not None and (kehys := oma_kehys(rivi)):
            tulos.append(f"  {odotettu}: {kehys}")
            odotettu = None
    return tulos


def suunta(sana: str) -> str:
    return {"after": "lopun jälkeen", "before": "ennen alkua",
            "inside of": "alueen sisällä"}[sana]


def main() -> int:
    rivit = sys.stdin.read().splitlines()
    for rivi in tiivista(rivit):
        sisennys = " " * (len(rivi) - len(rivi.lstrip()) + 4)
        print(textwrap.fill(rivi, width=76, subsequent_indent=sisennys,
                            break_on_hyphens=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
