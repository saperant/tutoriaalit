"""Opetusesimerkki: RSA pienillä luvuilla. Ei turvallinen!"""

from math import gcd


def main() -> None:
    # @alku avaimet
    p, q = 61, 53                 # oikeasti 1536-bittisiä alkulukuja
    n = p * q                     # julkinen moduli: 3233
    phi = (p - 1) * (q - 1)       # 3120, salainen
    e = 17                        # julkinen eksponentti
    assert gcd(e, phi) == 1
    d = pow(e, -1, phi)           # salainen eksponentti: e·d ≡ 1 (mod φ)
    print(f"julkinen avain (n={n}, e={e}), salainen d={d}")
    # @loppu avaimet

    # @alku salaus
    m = 65
    c = pow(m, e, n)              # salaus: c = m^e mod n
    print(f"salattu {m} -> {c}, purettu {pow(c, d, n)}")
    # @loppu salaus

    # @alku heikkoudet
    # 1. Deterministinen: sama viesti, sama salattu teksti.
    print("sama viesti tunnistetaan:", pow(65, e, n) == c)
    # 2. Muokattava: salattu kerrottuna luvulla 2^e on viesti 2m salattuna.
    c2 = (c * pow(2, e, n)) % n
    print("muokattu purkautuu arvoksi:", pow(c2, d, n))
    # 3. Pieni moduli jaetaan tekijöihin hetkessä.
    tekija = next(k for k in range(2, n) if n % k == 0)
    print("n:n tekijä löytyi:", tekija)
    # @loppu heikkoudet

    # @alku allekirjoitus
    s = pow(m, d, n)              # allekirjoitus salaisella avaimella
    print("allekirjoitus kelpaa:", pow(s, e, n) == m)
    # @loppu allekirjoitus


if __name__ == "__main__":
    main()
