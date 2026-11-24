"""Eulerin ja Hamiltonin polut: helppo ja vaikea ongelma rinnakkain."""

from collections import Counter
from itertools import permutations
from math import factorial

Kaaret = list[tuple[str, str]]


# @alku euler
def euler_polku(kaaret: Kaaret) -> list[str] | None:
    """Hierholzerin algoritmi: kulkee jokaisen kaaren tasan kerran.

    Polku on olemassa (yhtenäisessä graafissa) täsmälleen, kun
    paritonasteisia solmuja on 0 tai 2.
    """
    aste = Counter(s for k in kaaret for s in k)
    parittomat = sorted(s for s, a in aste.items() if a % 2)
    if len(parittomat) not in (0, 2):
        return None
    jaljella: dict[str, list[str]] = {s: [] for s in aste}
    for a, b in kaaret:
        jaljella[a].append(b)
        jaljella[b].append(a)
    pino = [parittomat[0] if parittomat else min(aste)]
    polku = []
    while pino:
        s = pino[-1]
        if jaljella[s]:
            t = jaljella[s].pop()
            jaljella[t].remove(s)
            pino.append(t)
        else:
            polku.append(pino.pop())
    return polku[::-1]
# @loppu euler


# @alku konigsberg
# Königsbergin seitsemän siltaa: kaikilla neljällä maa-alueella on
# pariton aste, joten kävelyä ei ole (Euler 1736).
konigsberg = [("A", "B"), ("A", "B"), ("A", "C"), ("A", "C"),
              ("A", "D"), ("B", "D"), ("C", "D")]
print("Königsberg:", euler_polku(konigsberg))
# Kuoren piirtäminen nostamatta kynää paperista
kirjekuori = [("1", "2"), ("2", "3"), ("3", "4"), ("4", "1"),
              ("1", "3"), ("2", "4"), ("3", "5"), ("4", "5")]
print("kirjekuori:", euler_polku(kirjekuori))
# @loppu konigsberg


# @alku hamilton
# Hamiltonin kehä käy jokaisessa solmussa kerran. Tehokasta algoritmia
# ei tunneta: tässä kokeillaan kaikki (n-1)! järjestystä.
def hamilton_keha(kaaret: Kaaret) -> tuple[list[str] | None, int]:
    solmut = sorted({s for k in kaaret for s in k})
    yhteys = {frozenset(k) for k in kaaret}
    kokeiltu = 0
    for loput in permutations(solmut[1:]):
        kokeiltu += 1
        keha = [solmut[0], *loput, solmut[0]]
        parit = zip(keha, keha[1:], strict=False)
        if all(frozenset(p) in yhteys for p in parit):
            return keha[:-1], kokeiltu
    return None, kokeiltu


keha, kokeiltu = hamilton_keha(kirjekuori)
print(f"kirjekuoren Hamiltonin kehä: {keha} ({kokeiltu} kokeilua)")
print(f"20 solmun graafissa järjestyksiä olisi {factorial(19):,}"
      .replace(",", " "))
# @loppu hamilton
