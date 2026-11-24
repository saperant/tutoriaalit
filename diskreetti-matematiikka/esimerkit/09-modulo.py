"""Modulaariaritmetiikka: jäännökset, käänteisalkiot ja potenssit."""

# @alku jaannos
# Pythonin % palauttaa jakajan merkkisen jäännöksen; C:n % ja
# math.fmod jakajan sijasta jaettavan merkkisen.
import math

for a in (17, -17):
    print(f"{a:>3} % 5 = {a % 5}, math.fmod({a}, 5) = {math.fmod(a, 5):g}")
# Kellon aika: 3 tuntia ennen kello 1:tä
print("1 - 3 (mod 24) =", (1 - 3) % 24)
# @loppu jaannos

# @alku kaanteis
# a:lla on käänteisalkio mod m täsmälleen, kun syt(a, m) = 1.
m = 26
for a in (3, 7, 13):
    try:
        print(f"{a}^-1 mod {m} = {pow(a, -1, m)}")
    except ValueError:
        print(f"{a}:lla ei ole käänteisalkiota mod {m}",
              f"(syt = {math.gcd(a, m)})")
# @loppu kaanteis


# @alku potenssi
def modpot(kanta: int, eksponentti: int, m: int) -> int:
    """Neliöi ja kerro: O(log eksponentti) kertolaskua, luvut < m²."""
    tulos = 1
    kanta %= m
    while eksponentti:
        if eksponentti & 1:
            tulos = tulos * kanta % m
        kanta = kanta * kanta % m
        eksponentti >>= 1
    return tulos


p = 1_000_000_007
print("modpot == pow:", all(modpot(b, e, p) == pow(b, e, p)
                            for b in range(2, 40) for e in range(0, 500, 7)))
# Fermat'n pieni lause: a^(p-1) ≡ 1 (mod p), kun p on alkuluku.
print("Fermat, p alkuluku:", all(modpot(a, p - 1, p) == 1
                                 for a in range(2, 200)))
# Lause ei päde yhdistetyille luvuille (paitsi Carmichaelin luvuille).
print("2^(n-1) mod n, n = 91:", modpot(2, 90, 91))
print("2^(n-1) mod n, n = 561 (Carmichael):", modpot(2, 560, 561))
# @loppu potenssi
