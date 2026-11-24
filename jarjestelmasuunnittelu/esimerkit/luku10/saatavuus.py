"""Saatavuuden laskeminen osien saatavuuksista.

Sarjaan kytketyt osat (pyyntö tarvitsee kaikki) kertovat
saatavuutensa: A = A1 * A2 * ... Rinnakkaiset kopiot (riittää yksi)
kertovat epäsaatavuutensa: 1 - A = (1 - A1) * (1 - A2) * ...
Kaava olettaa, että viat ovat riippumattomia, eikä vikaantuminen
yleensä ole: yhteinen konesali, sama ohjelmistoversio tai sama
asetusvirhe kaataa kopiot yhtä aikaa.
"""

import math

MINUUTTEJA_KUUKAUDESSA = 30 * 24 * 60


# @alku kaavat
def sarja(*osat: float) -> float:
    return math.prod(osat)


def rinnan(*kopiot: float) -> float:
    return 1 - math.prod(1 - a for a in kopiot)


def yhteisvika(kopio: float, kopioita: int, yhteinen: float) -> float:
    """Kopiot ovat riippumattomia, mutta niillä on yhteinen osa (esim.
    sama saatavuusvyöhyke), jonka saatavuus on `yhteinen`."""
    return sarja(yhteinen, rinnan(*[kopio] * kopioita))
# @loppu kaavat


def kuvaa(nimi: str, a: float) -> None:
    yhdeksikot = -math.log10(1 - a)
    katko = (1 - a) * MINUUTTEJA_KUUKAUDESSA
    teksti = f"{katko:.1f} min" if katko >= 1 else f"{katko * 60:.1f} s"
    print(f"  {nimi:<34}{a:>9.4%}{yhdeksikot:>5.1f}{teksti:>11}")


def main() -> None:
    print(f"  {'kokoonpano':<34}{'saatavuus':>9}{'ysit':>5}"
          f"{'katko/kk':>11}")
    # @alku kokoonpanot
    tasaaja, api, valimuisti, kanta = 0.9995, 0.999, 0.999, 0.9995
    kuvaa("yksi api", api)
    kuvaa("tasaaja + api + muisti + kanta", sarja(tasaaja, api,
                                                    valimuisti, kanta))
    kuvaa("3 api-kopiota rinnan", rinnan(api, api, api))
    kuvaa("3 apia, kanta + replika", sarja(
        tasaaja, rinnan(api, api, api), valimuisti, rinnan(kanta, kanta)))
    kuvaa("sama, muisti ohitettavissa", sarja(
        tasaaja, rinnan(api, api, api), rinnan(kanta, kanta)))
    kuvaa("3 apia yhdessä vyöhykkeessä", yhteisvika(api, 3, 0.9995))
    kuvaa("2 vyöhykettä, 3 apia kummassakin",
          rinnan(yhteisvika(api, 3, 0.9995), yhteisvika(api, 3, 0.9995)))
    # @loppu kokoonpanot

    # @alku budjetti
    print("virhebudjetti 30 päivälle ja hälytysrajat:")
    print(f"  {'SLO':<8}{'budjetti':>10}{'virheitä':>10}{'14.4x':>8}")
    for slo in (0.99, 0.999, 0.9999):
        budjetti = (1 - slo) * MINUUTTEJA_KUUKAUDESSA
        print(f"  {slo:<8.2%}{budjetti:>6.1f} min{1 - slo:>10.2%}"
              f"{14.4 * (1 - slo):>8.2%}")
    print(f"  kulumisnopeus 14.4: {14.4 / 720:.0%} budjetista tunnissa,"
          f" koko budjetti {720 / 14.4:.0f} tunnissa")
    # @loppu budjetti


if __name__ == "__main__":
    main()
