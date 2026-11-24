"""Hajota ja hallitse: T(n) = aT(n/b) + f(n) mitattuna ja laskettuna."""

import math

vertailuja = 0


# @alku lomitus
def lomituslajittelu(lista: list[int]) -> list[int]:
    """T(n) = 2T(n/2) + n: kaksi puolikasta ja lineaarinen lomitus."""
    global vertailuja
    if len(lista) <= 1:
        return lista
    keski = len(lista) // 2
    vasen = lomituslajittelu(lista[:keski])
    oikea = lomituslajittelu(lista[keski:])
    tulos = []
    i = j = 0
    while i < len(vasen) and j < len(oikea):
        vertailuja += 1
        if vasen[i] <= oikea[j]:
            tulos.append(vasen[i])
            i += 1
        else:
            tulos.append(oikea[j])
            j += 1
    return tulos + vasen[i:] + oikea[j:]
# @loppu lomitus


# @alku mittaus
for k in (4, 8, 12, 16):
    n = 2**k
    # Sekoitettu syöte: i·7919 mod n käy läpi kaikki luvut 0…n-1,
    # koska 7919 on pariton ja n kahden potenssi.
    sekoitettu = [i * 7919 % n for i in range(n)]
    vertailuja = 0
    assert lomituslajittelu(sekoitettu) == list(range(n))
    print(f"n = {n:>6}: vertailuja {vertailuja:>7},",
          f"n·log2(n) = {n * k:>7}, suhde {vertailuja / (n * k):.2f}")
# @loppu mittaus


# @alku master
def n_potenssi(e: float) -> str:
    if e == 0:
        return "1"
    return "n" if e == 1 else f"n^{e:.3g}"


def master(a: int, b: int, d: float) -> str:
    """T(n) = aT(n/b) + Θ(n^d): mitä kolmesta tapauksesta sovelletaan."""
    kriittinen = math.log(a, b)
    if math.isclose(d, kriittinen):
        return "Θ(log n)" if d == 0 else f"Θ({n_potenssi(d)} log n)"
    if d > kriittinen:
        return f"Θ({n_potenssi(d)})"
    return f"Θ({n_potenssi(kriittinen)})"


tapaukset = [
    ("binäärihaku", 1, 2, 0), ("lomituslajittelu", 2, 2, 1),
    ("puun läpikäynti", 2, 2, 0), ("Karatsuban kertolasku", 3, 2, 1),
    ("naiivi matriisitulo", 8, 2, 2), ("Strassen", 7, 2, 2),
    ("pikavalinta (keskimäärin)", 1, 2, 1),
]
for nimi, a, b, d in tapaukset:
    f = n_potenssi(d)
    print(f"  {nimi:<26} T(n) = {a}T(n/{b}) + {f}: {master(a, b, d)}")
# @loppu master
