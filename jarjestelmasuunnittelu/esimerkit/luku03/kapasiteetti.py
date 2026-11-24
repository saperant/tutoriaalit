"""Montako palvelinta tarvitaan? Littlen laki ja M/M/c-jono.

Kuorma 2 400 pyyntöä sekunnissa, yksi pyyntö vie palvelimelta 20 ms
laskenta-aikaa ja palvelimella on 8 työsäiettä. Yksi palvelin
käsittelee siis enintään 8 / 0.020 = 400 pyyntöä sekunnissa.
Erlangin C-kaava kertoo, kuinka moni pyyntö joutuu jonoon ja kuinka
kauan se odottaa, kun palvelimia on c. Malli olettaa satunnaiset
(Poisson-) saapumiset ja eksponentiaaliset palveluajat.
"""

import math

KUORMA = 2400.0          # pyyntöä/s
PALVELUAIKA = 0.020      # s
SAIKEITA = 8             # rinnakkaisia pyyntöjä palvelinta kohden


# @alku erlang
def erlang_c(palvelijoita: int, kuorma_erlangeina: float) -> float:
    """Todennäköisyys, että saapuva pyyntö joutuu odottamaan."""
    a, c = kuorma_erlangeina, palvelijoita
    if a >= c:
        return 1.0
    summa = sum(a ** k / math.factorial(k) for k in range(c))
    viimeinen = a ** c / math.factorial(c) * c / (c - a)
    return viimeinen / (summa + viimeinen)


def vasteaika(palvelimia: int) -> tuple[float, float, float]:
    """Palauttaa käyttöasteen, jonotustodennäköisyyden ja keskimääräisen
    vasteajan (jonotus + palvelu) sekunteina."""
    c = palvelimia * SAIKEITA
    a = KUORMA * PALVELUAIKA          # Littlen laki: L = lambda * W
    if a >= c:
        return a / c, 1.0, math.inf
    p = erlang_c(c, a)
    jono = p * PALVELUAIKA / (c - a)
    return a / c, p, jono + PALVELUAIKA
# @loppu erlang


def main() -> None:
    a = KUORMA * PALVELUAIKA
    print(f"kuorma {KUORMA:.0f}/s x {PALVELUAIKA * 1000:.0f} ms ="
          f" {a:.0f} pyyntöä käsittelyssä keskimäärin (Littlen laki)")
    print(f"{'palvelimia':>10}{'käyttöaste':>12}{'jonoon':>9}"
          f"{'jonotus':>10}")
    for palvelimia in range(6, 11):
        aste, p, w = vasteaika(palvelimia)
        jono = "ylikuorma" if math.isinf(w) \
            else f"{(w - PALVELUAIKA) * 1000:.2f} ms"
        print(f"{palvelimia:>10}{aste:>12.0%}{p:>9.1%}{jono:>10}")
    tarve = next(n for n in range(2, 100) if vasteaika(n - 1)[0] <= 0.7)
    print(f"käyttöaste <= 70 % vielä yhden palvelimen kaaduttua:"
          f" {tarve} palvelinta")


if __name__ == "__main__":
    main()
