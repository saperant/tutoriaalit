"""ExitStack: vaihteleva määrä resursseja yhdellä with-lauseella."""

import contextlib
from pathlib import Path

# @alku exitstack
nimet = ["a.txt", "b.txt", "c.txt"]
for i, nimi in enumerate(nimet):
    Path(nimi).write_text(f"rivi {i}\n", encoding="utf-8")

with contextlib.ExitStack() as pino:
    tiedostot = [pino.enter_context(open(n, encoding="utf-8"))
                 for n in nimet]
    print([t.readline().strip() for t in tiedostot])
    pino.callback(print, "kaikki suljetaan")    # oma siivoustoimenpide
print(all(t.closed for t in tiedostot))
# @loppu exitstack
