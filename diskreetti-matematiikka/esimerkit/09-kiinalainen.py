"""Kiinalainen jäännöslause: luku jäännöksistä pareittain
keskenään jaottomien modulien suhteen."""

from math import gcd, prod


# @alku crt
def kiinalainen(jaannokset: list[int], modulit: list[int]) -> int:
    """x ≡ r_i (mod m_i) kaikilla i; modulit pareittain jaottomia."""
    assert all(gcd(a, b) == 1 for i, a in enumerate(modulit)
               for b in modulit[i + 1:])
    m = prod(modulit)
    x = 0
    for r, mi in zip(jaannokset, modulit, strict=True):
        muut = m // mi
        x += r * muut * pow(muut, -1, mi)
    return x % m


# Mikä luku antaa jakojäännökset 2, 3 ja 4 luvuilla 5, 7 ja 11?
x = kiinalainen([2, 3, 4], [5, 7, 11])
print(f"x ≡ 2 (mod 5), x ≡ 3 (mod 7), x ≡ 4 (mod 11): x = {x}")
print("tarkistus:", x % 5, x % 7, x % 11)
# Jokainen jäännöskolmikko vastaa täsmälleen yhtä lukua 0…384.
kolmikot = {(n % 5, n % 7, n % 11) for n in range(5 * 7 * 11)}
print(f"erilaisia kolmikoita: {len(kolmikot)} = 5·7·11")
# @loppu crt

# @alku rsa
# Sama lause nopeuttaa RSA-salauksen purkua: lasketaan erikseen
# mod p ja mod q pienillä luvuilla ja yhdistetään (ks. Kryptografia).
p, q, e = 61, 53, 17
n, phi = p * q, (p - 1) * (q - 1)
d = pow(e, -1, phi)
viesti = 1234
salattu = pow(viesti, e, n)
suoraan = pow(salattu, d, n)
crt = kiinalainen([pow(salattu, d % (p - 1), p),
                   pow(salattu, d % (q - 1), q)], [p, q])
print(f"purku suoraan {suoraan}, CRT:llä {crt}")
# @loppu rsa
