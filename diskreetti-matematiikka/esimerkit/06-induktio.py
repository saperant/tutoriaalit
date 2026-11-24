"""Induktiolla todistettujen kaavojen tarkistus ja vastaesimerkin haku."""

# @alku kaavat
# Väite: 1 + 2 + ... + n = n(n + 1)/2. Induktio todistaa sen kaikille
# n; ohjelma tarkistaa tuhat ensimmäistä tapausta.
print("summakaava:", all(sum(range(1, n + 1)) == n * (n + 1) // 2
                         for n in range(1000)))
# Väite: 1 + 2 + 4 + ... + 2^(n-1) = 2^n - 1 (binääriluvun 111…1 arvo).
print("geometrinen:", all(sum(2**k for k in range(n)) == 2**n - 1
                          for n in range(200)))
# Väite: n^3 - n on jaollinen kolmella.
print("n³ - n jaollinen 3:lla:", all((n**3 - n) % 3 == 0
                                     for n in range(1000)))
# @loppu kaavat

# @alku vastaesimerkki
# Esimerkit eivät todista: n² + n + 41 on alkuluku arvoilla 0…39,
# mutta ei kaikilla n.


def alkuluku(m: int) -> bool:
    return m >= 2 and all(m % d for d in range(2, int(m**0.5) + 1))


ensimmainen = next(n for n in range(1000) if not alkuluku(n * n + n + 41))
print(f"n² + n + 41 ei ole alkuluku, kun n = {ensimmainen}:",
      f"{ensimmainen**2 + ensimmainen + 41} = 41·41")
# @loppu vastaesimerkki


# @alku vahva
# Vahva induktio: jokainen n ≥ 2 on alkulukujen tulo. Oletetaan väite
# kaikille pienemmille luvuille; joko n on alkuluku tai n = a·b, jossa
# a, b < n. Rekursio noudattaa todistusta askel askeleelta.
def tekijat(n: int) -> list[int]:
    for a in range(2, int(n**0.5) + 1):
        if n % a == 0:
            return tekijat(a) + tekijat(n // a)
    return [n]


for luku in (360, 1001, 65537, 2**10 * 3**4):
    print(f"{luku} = {' · '.join(map(str, tekijat(luku)))}")
# @loppu vahva
