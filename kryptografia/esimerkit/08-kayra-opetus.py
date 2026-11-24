"""Opetusesimerkki: elliptisen käyrän ryhmälaki pienessä kunnassa.

Käyrä y² = x³ + 2x + 2 kunnassa F₁₇. Pisteitä on 19 (äärettömyyspiste
mukaan lukien), ja G = (5, 1) tuottaa ne kaikki.
"""

P, A_KERROIN = 17, 2
Piste = tuple[int, int] | None    # None on äärettömyyspiste (nolla)


# @alku ryhmalaki
def summa(p1: Piste, p2: Piste) -> Piste:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    (x1, y1), (x2, y2) = p1, p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None                               # P + (−P) = 0
    if p1 == p2:
        k = (3 * x1 * x1 + A_KERROIN) * pow(2 * y1, -1, P)   # tangentti
    else:
        k = (y2 - y1) * pow(x2 - x1, -1, P)                  # sekantti
    x3 = (k * k - x1 - x2) % P
    return x3, (k * (x1 - x3) - y1) % P


def kerro(n: int, piste: Piste) -> Piste:
    """Skalaarikertolasku tuplaa ja lisää -menetelmällä: O(log n)."""
    tulos: Piste = None
    while n:
        if n & 1:
            tulos = summa(tulos, piste)
        piste = summa(piste, piste)
        n >>= 1
    return tulos
# @loppu ryhmalaki


def main() -> None:
    G = (5, 1)
    print("2G =", kerro(2, G), " 3G =", kerro(3, G), " 19G =", kerro(19, G))
    # @alku ecdh
    a, b = 3, 7                                   # salaiset skalaarit
    A, B = kerro(a, G), kerro(b, G)               # julkiset pisteet
    print("yhteinen piste:", kerro(a, B), kerro(b, A))
    # @loppu ecdh


if __name__ == "__main__":
    main()
