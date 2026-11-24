"""Tiivistää Yosysin `stat -width` -raportin: kertojat, summaimet,
multiplekserien ja kiikkujen bitit. Yosys ajetaan karkealla tasolla
(proc, opt, wreduce), joten luvut kuvaavat RTL:n rakennetta eivätkä
vielä tiettyä FPGA- tai ASIC-kirjastoa."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def tiivista(raportti: str) -> list[str]:
    solut: dict[str, list[tuple[int, int]]] = {}
    for osuma in re.finditer(r"^\s+\$(\w+?)_(\d+)\s+(\d+)$", raportti,
                             re.MULTILINE):
        laji, leveys, kpl = osuma.groups()
        solut.setdefault(laji, []).append((int(leveys), int(kpl)))

    def maara(*lajit: str) -> int:
        return sum(m for laji in lajit for _, m in solut.get(laji, []))

    def bitit(*lajit: str) -> int:
        return sum(w * m for laji in lajit for w, m in solut.get(laji, []))

    kertojat = ", ".join(f"{m} x {w} bittiä"
                         for w, m in sorted(solut.get("mul", [])))
    kiikut = [laji for laji in solut if "dff" in laji]
    return [f"kertojat {maara('mul')}" + (f" ({kertojat})" if kertojat
                                          else ""),
            f"summaimet ja vähentimet {maara('add', 'sub')}",
            f"multiplekserit {bitit('mux', 'pmux')} bittiä",
            f"kiikut {bitit(*kiikut)} bittiä"]


if __name__ == "__main__":
    print("\n".join(tiivista(Path(sys.argv[1]).read_text("utf-8"))))
