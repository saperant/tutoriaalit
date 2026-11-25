"""ARQ: kolme uudelleenlähetysmenetelmää samalla kanavalla.

Aika on jaettu kehyksen mittaisiin viipaleisiin. Kehys katoaa
todennäköisyydellä p. Lähettäjä saa tiedon viipaleessa t lähetetyn
kehyksen kohtalosta `kierros` viipaletta myöhemmin (kuittaus tai
aikakatkaisu) ja voi käyttää tietoa viipaleessa t + kierros + 1.
Kuittaukset eivät katoa. Tehokkuus on perille järjestyksessä
toimitettujen kehysten osuus viipaleista.
"""

from collections import deque

import numpy as np


# @alku pysahdy
def pysahdy_ja_odota(katoaa: list[bool], kierros: int) -> float:
    """Yksi kehys kerrallaan: seuraava lähtee vasta, kun edellisen
    kohtalo tiedetään."""
    perilla, t = 0, 0
    while t < len(katoaa):
        if not katoaa[t]:
            perilla += 1
        t += 1 + kierros
    return perilla / len(katoaa)
# @loppu pysahdy


# @alku palaa
def palaa_n(katoaa: list[bool], kierros: int) -> float:
    """Go-back-N: lähettäjä lähettää jatkuvasti. Vastaanottaja hyväksyy
    kehykset vain järjestyksessä, joten katoamisen jälkeen lähettäjä
    palaa kadonneeseen kehykseen ja lähettää kaiken siitä eteenpäin
    uudelleen."""
    numero = [0] * len(katoaa)
    palattava = [False] * len(katoaa)
    seuraava = odotettu = 0
    for t in range(len(katoaa)):
        vanha = t - kierros - 1
        if vanha >= 0 and palattava[vanha]:
            seuraava = numero[vanha]
        numero[t] = seuraava
        if seuraava == odotettu:
            if katoaa[t]:
                palattava[t] = True
            else:
                odotettu += 1
        seuraava += 1
    return odotettu / len(katoaa)
# @loppu palaa


# @alku valikoiva
def valikoiva_toisto(katoaa: list[bool], kierros: int) -> tuple[float, int]:
    """Selective repeat: vain kadonnut kehys lähetetään uudelleen.
    Vastaanottaja säilyttää järjestyksestä poikkeavat kehykset
    puskurissa. Palauttaa tehokkuuden ja puskurin suurimman koon."""
    uudelleen: deque[tuple[int, int]] = deque()   # (aikaisintaan, numero)
    puskuri: set[int] = set()
    seuraava = odotettu = suurin = 0
    for t in range(len(katoaa)):
        if uudelleen and uudelleen[0][0] <= t:
            numero = uudelleen.popleft()[1]
        else:
            numero = seuraava
            seuraava += 1
        if katoaa[t]:
            uudelleen.append((t + kierros + 1, numero))
            continue
        puskuri.add(numero)
        while odotettu in puskuri:
            puskuri.remove(odotettu)
            odotettu += 1
        suurin = max(suurin, len(puskuri))
    return odotettu / len(katoaa), suurin
# @loppu valikoiva


def kanava(p: float, viipaleita: int = 400_000) -> list[bool]:
    rng = np.random.default_rng(5)
    return [bool(k) for k in rng.random(viipaleita) < p]


# @alku vertailu
print("kierros     p   pysähdy ja odota     go-back-N   valikoiva toisto"
      "  puskuri")
for kierros in (2, 20):
    for p in (0.01, 0.1):
        katoaa = kanava(p)
        valikoiva, puskuri = valikoiva_toisto(katoaa, kierros)
        print(f"{kierros:>7} {p:>5}"
              f"      {pysahdy_ja_odota(katoaa, kierros):.3f} "
              f"({(1 - p) / (1 + kierros):.3f})"
              f" {palaa_n(katoaa, kierros):.3f} "
              f"({(1 - p) / (1 + kierros * p):.3f})"
              f"      {valikoiva:.3f} ({1 - p:.3f})  {puskuri:>7}")
# @loppu vertailu
