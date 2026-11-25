"""Funktioiden kasvunopeus ja O-merkintä: taulukko, raja ja mittaus."""

from math import log2

# @alku taulukko
# Tavallisimmat kasvunopeudet: askelten määrä syötteen koon funktiona.
print(f"{'n':>6} {'log2 n':>7} {'n log2 n':>9} {'n^2':>10} {'2^n':>9}")
for n in (10, 100, 1000, 10_000):
    kaksi_n = f"{2**n:.1e}" if n <= 1000 else "-"
    print(f"{n:>6} {log2(n):>7.1f} {n * log2(n):>9.0f} {n * n:>10}",
          f"{kaksi_n:>9}")
# @loppu taulukko


# @alku raja
# Väite 3n^2 + 10n + 5 = O(n^2): vakiot c = 4 ja n0 = 11 kelpaavat,
# sillä 10n + 5 <= n^2, kun n >= 11.
def f(n: int) -> int:
    return 3 * n * n + 10 * n + 5


print("f(n) <= 4n^2, kun n >= 11:",
      all(f(n) <= 4 * n * n for n in range(11, 100_000)))
print("pätee jo arvolla n = 10:", f(10) <= 4 * 10 * 10)
# @loppu raja


# @alku mittaus
# Sama tehtävä kahdella tavalla: onko listassa kaksi samaa alkiota?
def toistoja_parit(lista: list[int]) -> tuple[bool, int]:
    """Vertaa jokaista paria: pahimmillaan n(n - 1)/2 vertailua."""
    askelia = 0
    for i, a in enumerate(lista):
        for b in lista[i + 1:]:
            askelia += 1
            if a == b:
                return True, askelia
    return False, askelia


def toistoja_joukko(lista: list[int]) -> tuple[bool, int]:
    """Muistaa nähdyt alkiot joukossa: enintään n jäsenyystestiä."""
    nahdyt: set[int] = set()
    askelia = 0
    for a in lista:
        askelia += 1
        if a in nahdyt:
            return True, askelia
        nahdyt.add(a)
    return False, askelia


for n in (100, 1000, 10_000):
    lista = list(range(n))            # pahin tapaus: ei toistoja
    _, parit = toistoja_parit(lista)
    _, joukko = toistoja_joukko(lista)
    print(f"n = {n:>5}: parit {parit:>8} askelta, joukko {joukko:>5}")
# @loppu mittaus
