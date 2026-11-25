"""Bittikasvu: montako bittiä summa ja tulo tarvitsevat? Tyhjentävä
tarkistus pienillä leveyksillä."""


# @alku tarve
def tarvittavat_bitit(pienin: int, suurin: int) -> int:
    """Pienin etumerkillinen leveys, johon arvot [pienin, suurin] mahtuvat."""
    b = 1
    while not (-(2 ** (b - 1)) <= pienin and suurin <= 2 ** (b - 1) - 1):
        b += 1
    return b
# @loppu tarve


# @alku tarkistus
for n in range(2, 9):
    arvot = range(-(2 ** (n - 1)), 2 ** (n - 1))
    tulot = [a * b for a in arvot for b in arvot]
    ilman_kulmaa = [a * b for a in arvot for b in arvot
                    if not (a == b == -(2 ** (n - 1)))]
    summat = [a + b for a in arvot for b in arvot]
    print(f"n={n}: summa {tarvittavat_bitit(min(summat), max(summat))}"
          f" = n+1, tulo {tarvittavat_bitit(min(tulot), max(tulot))}"
          f" = 2n, ilman (-2^(n-1))^2: "
          f"{tarvittavat_bitit(min(ilman_kulmaa), max(ilman_kulmaa))}"
          f" = 2n-1")
# @loppu tarkistus

# @alku kertyma
# K tulon summa tarvitsee lisäksi ceil(log2 K) vartijabittiä.
for k in (2, 16, 64, 256, 1000):
    vartija = (k - 1).bit_length()
    suurin = k * (2**15) ** 2               # K kertaa (-1 * -1) Q2.30:ssa
    print(f"K={k:5}: tarvitaan {tarvittavat_bitit(-suurin, suurin)} "
          f"bittiä, sääntö 32 + {vartija} = {32 + vartija}")
# @loppu kertyma

# @alku sekamuodot
# Etumerkitön a-bittinen ja etumerkillinen b-bittinen samassa laskussa:
# etumerkitön tarvitsee yhden bitin lisää ennen kuin se on etumerkillinen.
for a, b in ((4, 4), (8, 4), (4, 8)):
    u, s = range(2**a), range(-(2 ** (b - 1)), 2 ** (b - 1))
    summat = [x + y for x in u for y in s]
    tulot = [x * y for x in u for y in s]
    print(f"UQ{a} ja Q{b}: summa "
          f"{tarvittavat_bitit(min(summat), max(summat))}"
          f" = max({a}+1, {b})+1, tulo "
          f"{tarvittavat_bitit(min(tulot), max(tulot))} = {a}+{b}")
# @loppu sekamuodot
