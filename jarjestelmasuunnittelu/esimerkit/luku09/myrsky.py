"""Uudelleenyritysmyrsky ja metastabiili ylikuorma.

Palvelu ehtii 100 pyyntöä sekunnissa, ja kuorma on 80/s. Sekunneilla
10-20 kapasiteetti putoaa puoleen (esim. tietokannan varmuuskopio).
Asiakkaat luopuvat pyynnöstä sekunnin jälkeen ja yrittävät uudelleen.
Palvelin ei tiedä asiakkaan luopuneen, joten se käsittelee jonossa
odottavan pyynnön silti: työ menee hukkaan.

Kolme asiakasta ja palvelinta:
  naiivi     enintään 3 uusintaa heti aikakatkaisun jälkeen
  budjetti   uusintoja enintään 10 % pyynnöistä, viive ja hajonta
  määräaika  budjetti + palvelin pudottaa vanhentuneet pyynnöt
             käsittelemättä (deadline propagation)
Simulaatio etenee 100 ms askelin ja on deterministinen.
"""

from collections import deque
from dataclasses import dataclass

ASKEL = 0.1
KAPASITEETTI = 100          # /s
HAIRIO = (10.0, 20.0)       # kapasiteetti puolittuu
KUORMA = 80                 # /s, uusia pyyntöjä
AIKARAJA = 1.0              # s


@dataclass
class Pyynto:
    saapui: float
    yritys: int
    luovuttu: bool = False


# @alku simulaatio
def simuloi(strategia: str) -> list[float]:
    """Palauttaa onnistuneet vastaukset sekunnissa viiden sekunnin
    jaksoissa."""
    jono: deque[Pyynto] = deque()
    odottavat: list[tuple[float, int]] = []   # (lähtöaika, yritys)
    onnistuneet = [0] * 12
    budjetti = 0.0
    for askel in range(600):
        nyt = askel * ASKEL
        jono.extend(Pyynto(nyt, 0) for _ in range(int(KUORMA * ASKEL)))
        budjetti = min(10.0, budjetti + 0.1 * KUORMA * ASKEL)
        lahtevat = [o for o in odottavat if o[0] <= nyt]
        odottavat = [o for o in odottavat if o[0] > nyt]
        jono.extend(Pyynto(nyt, yritys) for _, yritys in lahtevat)

        # Asiakkaat luopuvat aikarajan ylittäneistä ja yrittävät uudelleen.
        for p in jono:
            if not p.luovuttu and nyt - p.saapui > AIKARAJA:
                p.luovuttu = True
                if strategia == "naiivi" and p.yritys < 3:
                    odottavat.append((nyt, p.yritys + 1))
                elif strategia != "naiivi" and budjetti >= 1:
                    budjetti -= 1
                    viive = 0.5 * 2 ** p.yritys * (1 + (askel % 7) / 7)
                    odottavat.append((nyt + viive, p.yritys + 1))

        hairio = HAIRIO[0] <= nyt < HAIRIO[1]
        kapasiteetti = KAPASITEETTI * ASKEL / (2 if hairio else 1)
        tehty = 0
        while jono and tehty < kapasiteetti:
            p = jono.popleft()
            if p.luovuttu and strategia == "määräaika":
                continue                      # pudotetaan, ei maksa
            tehty += 1
            if not p.luovuttu:
                onnistuneet[int(nyt // 5)] += 1
    return [n / 5 for n in onnistuneet]
# @loppu simulaatio


def main() -> None:
    print("onnistuneet vastaukset/s viiden sekunnin jaksoissa"
          " (kuorma 80/s)")
    print(f"{'aika s':<11}" + "".join(f"{5 * i:>5}" for i in range(12)))
    for strategia in ("naiivi", "budjetti", "määräaika"):
        rivi = simuloi(strategia)
        print(f"{strategia:<11}" + "".join(f"{n:>5.0f}" for n in rivi))


if __name__ == "__main__":
    main()
