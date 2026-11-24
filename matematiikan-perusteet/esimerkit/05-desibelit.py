"""Desibelit: tehosuhde, amplitudisuhde ja logaritmiasteikko."""

import math


# @alku desibelit
def db_teho(suhde: float) -> float:
    return 10 * math.log10(suhde)


def db_amplitudi(suhde: float) -> float:
    """Teho on verrannollinen amplitudin neliöön: 10 lg(A^2) = 20 lg A."""
    return 20 * math.log10(suhde)


for suhde in [2, 10, 100, 0.5, 0.001]:
    print(f"suhde {suhde:7g}: teho {db_teho(suhde):+7.2f} dB, "
          f"amplitudi {db_amplitudi(suhde):+7.2f} dB")
# @loppu desibelit

# @alku ketju
# Vahvistimet ja vaimennukset ketjussa: desibelit summautuvat.
ketju = {"esivahvistin": 20.0, "kaapeli": -3.0, "vahvistin": 12.0}
yhteensa = sum(ketju.values())
kertoimet = [10 ** (db / 20) for db in ketju.values()]
print(f"yhteensä {yhteensa:+.1f} dB = amplitudi x{math.prod(kertoimet):.2f}")
print(f"tarkistus: 20 lg {math.prod(kertoimet):.4f} = "
      f"{db_amplitudi(math.prod(kertoimet)):.1f} dB")
# @loppu ketju
