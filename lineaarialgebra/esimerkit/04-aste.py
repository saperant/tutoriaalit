"""Astevaltaisuus ja ratkaisujen määrä tarkoilla murtoluvuilla."""

from fractions import Fraction

Matriisi = list[list[Fraction]]


# @alku porras
def porrasmuoto(m: Matriisi) -> tuple[Matriisi, list[int]]:
    """Redusoitu porrasmuoto ja tukisarakkeet. Murtoluvut ovat tarkkoja,
    joten pyöristysvirhe ei sotke astetta."""
    m = [rivi[:] for rivi in m]
    tuet: list[int] = []
    r = 0
    for s in range(len(m[0])):
        p = next((i for i in range(r, len(m)) if m[i][s] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        m[r] = [x / m[r][s] for x in m[r]]
        for i in range(len(m)):
            if i != r and m[i][s] != 0:
                k = m[i][s]
                m[i] = [x - k * y for x, y in zip(m[i], m[r], strict=True)]
        tuet.append(s)
        r += 1
        if r == len(m):
            break
    return m, tuet
# @loppu porras


# @alku luokittelu
def luokittele(a: list[list[int]], b: list[int]) -> str:
    kerroin = [[Fraction(x) for x in rivi] for rivi in a]
    laajennettu = [rivi + [Fraction(bi)]
                   for rivi, bi in zip(kerroin, b, strict=True)]
    aste_a = len(porrasmuoto(kerroin)[1])
    aste_ab = len(porrasmuoto(laajennettu)[1])
    n = len(a[0])
    if aste_a < aste_ab:
        return f"ei ratkaisua (aste A = {aste_a}, aste [A|b] = {aste_ab})"
    if aste_a == n:
        return f"yksikäsitteinen ratkaisu (aste {aste_a} = n)"
    return f"äärettömästi ratkaisuja ({n - aste_a} vapaata muuttujaa)"


A = [[1, 1, 1], [1, 2, 3], [2, 3, 4]]   # 3. rivi = 1. + 2. rivi
print("b = (6, 14, 20):", luokittele(A, [6, 14, 20]))
print("b = (6, 14, 21):", luokittele(A, [6, 14, 21]))
print("täysiasteinen: ", luokittele([[2, 1], [1, 3]], [3, 5]))
# @loppu luokittelu
