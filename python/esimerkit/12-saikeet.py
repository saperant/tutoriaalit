"""Säikeet I/O-odotukseen: GIL vapautuu odotuksen ajaksi."""

import threading
import time
from concurrent.futures import ThreadPoolExecutor


# @alku saikeet
def hae(osoite: str) -> str:
    """Simuloi verkkopyyntöä: odottaa 0,2 s."""
    time.sleep(0.2)
    return f"{osoite}: 200"


osoitteet = [f"https://palvelu.example/{n}" for n in range(8)]
alku = time.perf_counter()
with ThreadPoolExecutor(max_workers=8) as pooli:
    tulokset = list(pooli.map(hae, osoitteet))   # järjestys säilyy
kesto = time.perf_counter() - alku
print(tulokset[0], tulokset[-1])
print("rinnakkain:", kesto < 0.2 * len(osoitteet) / 2)
# @loppu saikeet


# @alku lukko
class Laskuri:
    def __init__(self) -> None:
        self._arvo = 0
        self._lukko = threading.Lock()

    def kasvata(self) -> None:
        with self._lukko:          # += ei ole atominen
            self._arvo += 1

    @property
    def arvo(self) -> int:
        with self._lukko:
            return self._arvo


laskuri = Laskuri()
with ThreadPoolExecutor(max_workers=4) as pooli:
    for _ in range(10_000):
        pooli.submit(laskuri.kasvata)
print(laskuri.arvo)
# @loppu lukko
