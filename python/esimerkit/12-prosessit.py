"""Prosessit laskentaan: jokaisella prosessilla on oma GIL."""

from concurrent.futures import ProcessPoolExecutor


# @alku prosessit
def alkulukuja(alku: int, loppu: int) -> int:
    """Laskee alkuluvut välillä [alku, loppu) kokeilujaolla."""
    maara = 0
    for n in range(max(alku, 2), loppu):
        if all(n % d for d in range(2, int(n**0.5) + 1)):
            maara += 1
    return maara


def main() -> None:
    raja = 200_000
    palat = [(a, min(a + 50_000, raja)) for a in range(0, raja, 50_000)]
    with ProcessPoolExecutor(max_workers=4) as pooli:
        tulokset = list(pooli.map(alkulukuja, *zip(*palat, strict=True)))
    print(tulokset, sum(tulokset))


if __name__ == "__main__":     # pakollinen: lapsiprosessit tuovat moduulin
    main()
# @loppu prosessit
