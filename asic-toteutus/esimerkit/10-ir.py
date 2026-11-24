"""Tehoverkon jännitehäviö (IR-pudotus) vastusverkkona.

Ydin on ruudukko, jonka solmut kuluttavat virtaa ja jonka solmujen
väliset metalliliuskat ovat vastuksia. Syöttö tulee reunojen
nastoista. Solmujännitteet ratkaistaan Gauss–Seidel-iteraatiolla:
jokainen solmu on naapuriensa painotettu keskiarvo miinus oman
virran aiheuttama pudotus. Toimiva piiri vaatii tyypillisesti alle
5 %:n pudotuksen.
"""

V_SYOTTO = 1.8          # V


# @alku ratkaisu
def ratkaise(n: int, r_lius: float, i_solmu: float,
             syotot: set[tuple[int, int]]) -> list[list[float]]:
    """n×n solmua, liuskan vastus r_lius (Ω), virta solmua kohden (A).
    Syöttösolmut pidetään jännitteessä V_SYOTTO."""
    v = [[V_SYOTTO] * n for _ in range(n)]
    g = 1.0 / r_lius
    for _ in range(5000):
        muutos = 0.0
        for y in range(n):
            for x in range(n):
                if (x, y) in syotot:
                    continue
                naapurit = [v[b][a] for a, b in ((x - 1, y), (x + 1, y),
                                                 (x, y - 1), (x, y + 1))
                            if 0 <= a < n and 0 <= b < n]
                uusi = (g * sum(naapurit) - i_solmu) / (g * len(naapurit))
                muutos = max(muutos, abs(uusi - v[y][x]))
                v[y][x] = uusi
        if muutos < 1e-9:
            break
    return v
# @loppu ratkaisu


def main() -> None:
    n = 11
    # @alku vertailu
    kulmat = {(0, 0), (0, n - 1), (n - 1, 0), (n - 1, n - 1)}
    reunat = {(i, j) for i in range(0, n, 2)
              for j in (0, n - 1)} | {(j, i) for i in range(0, n, 2)
                                       for j in (0, n - 1)}
    for nimi, syotot, r in [("4 kulmanastaa", kulmat, 0.5),
                            ("reunarengas", reunat, 0.5),
                            ("reunarengas, leveät liuskat", reunat, 0.2)]:
        v = ratkaise(n, r, 0.006, syotot)    # 6 mA solmua kohden
        pienin = min(min(rivi) for rivi in v)
        pudotus = V_SYOTTO - pienin
        print(f"{nimi:31} pahin pudotus {pudotus * 1000:5.0f} mV "
              f"({pudotus / V_SYOTTO:4.1%})")
    # @loppu vertailu


if __name__ == "__main__":
    main()
