"""Silmukkainvariantti ohjelman oikeellisuuden perusteluna."""


# @alku binaarihaku
def ensimmainen_vahintaan(lista: list[int], arvo: int) -> int:
    """Ensimmäinen indeksi i, jolla lista[i] >= arvo (lista järjestetty).

    Invariantti: kaikki indeksit < ala ovat < arvo, ja kaikki
    indeksit >= yla ovat >= arvo. Alussa väli on koko lista, ja
    jokainen kierros pienentää väliä, joten silmukka päättyy.
    """
    ala, yla = 0, len(lista)
    while ala < yla:
        assert all(x < arvo for x in lista[:ala])
        assert all(x >= arvo for x in lista[yla:])
        keski = (ala + yla) // 2
        if lista[keski] < arvo:
            ala = keski + 1
        else:
            yla = keski
    # Nyt ala == yla, ja invariantti antaa vastauksen suoraan.
    return ala
# @loppu binaarihaku


hinnat = [3, 5, 5, 8, 13, 21, 21, 34]
for haku in (0, 5, 6, 21, 40):
    print(f"ensimmäinen >= {haku}: indeksi",
          ensimmainen_vahintaan(hinnat, haku))


# @alku potenssi
def potenssi(kanta: int, eksponentti: int) -> int:
    """Nopea potenssi. Invariantti: tulos · k^e == kanta^eksponentti."""
    tulos, k, e = 1, kanta, eksponentti
    while e > 0:
        assert tulos * k**e == kanta**eksponentti
        if e % 2 == 1:
            tulos *= k
        k *= k
        e //= 2
    return tulos
# @loppu potenssi


print("3^13 =", potenssi(3, 13), "=", 3**13)
print("tarkistus:", all(potenssi(b, e) == b**e
                        for b in range(-3, 6) for e in range(20)))
