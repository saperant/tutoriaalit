"""Osiointi avainalueilla ja tiivisteellä sekä kuuma avain.

Tilaukset saavat kasvavan tunnisteen (aikaleima tai sekvenssi), ja ne
jaetaan neljään osioon. Avainalueittain jaettuna uudet tilaukset
osuvat kaikki viimeiseen osioon; tiivisteellä jaettuna kirjoitukset
tasaantuvat, mutta peräkkäisten tilausten haku joutuu kysymään kaikkia
osioita. Lopuksi yksi kuuma avain ylikuormittaa osionsa, vaikka jako
on muuten tasainen.
"""

import random
from collections import Counter

from jarjestelma.hajautus import tiiviste

OSIOITA = 4
VANHAT = 1_000_000            # tilaukset 0 ... 999 999 on jo jaettu
UUDET = range(VANHAT, VANHAT + 100_000)


# @alku jaot
def alue(tunnus: int) -> int:
    """Avainalueet päätettiin, kun tilauksia oli miljoona."""
    return min(tunnus * OSIOITA // VANHAT, OSIOITA - 1)


def tiivisteella(avain: str) -> int:
    return tiiviste(avain) % OSIOITA
# @loppu jaot


def osuudet(osiot: Counter[int]) -> str:
    yhteensa = sum(osiot.values())
    return " ".join(f"{osiot[i] / yhteensa:4.0%}" for i in range(OSIOITA))


def main() -> None:
    print("uudet kirjoitukset osioittain:")
    print("  avainalue  ", osuudet(Counter(alue(t) for t in UUDET)))
    print("  tiiviste   ",
          osuudet(Counter(tiivisteella(str(t)) for t in UUDET)))
    haku = range(VANHAT - 100, VANHAT)           # 100 viimeisintä
    print("100 peräkkäisen haku, kysyttäviä osioita:")
    print(f"  avainalue  {len({alue(t) for t in haku})}")
    print(f"  tiiviste   {len({tiivisteella(str(t)) for t in haku})}")

    # @alku kuuma
    s = random.Random(7)
    kayttajat = [f"k{i}" for i in range(10_000)]
    def pyynto() -> str:                         # 30 % yhdelle tilille
        return "julkkis" if s.random() < 0.3 else s.choice(kayttajat)
    pyynnot = [pyynto() for _ in range(100_000)]
    print("kuuma avain, kuorma osioittain:")
    print("  tiiviste   ",
          osuudet(Counter(tiivisteella(a) for a in pyynnot)))
    # Suolaus: kuuma avain jaetaan 8 alla-avaimeen. Kirjoitus menee
    # yhteen (tässä satunnaiseen), luku kokoaa kaikki 8.
    suolattu = [f"{a}#{s.randrange(8)}" if a == "julkkis" else a
                for a in pyynnot]
    print("  suolattuna ",
          osuudet(Counter(tiivisteella(a) for a in suolattu)))
    # @loppu kuuma


if __name__ == "__main__":
    main()
