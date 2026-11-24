"""Hallittu pääsy: TDMA ja vuoromerkki (Token Ring) vaihtelevalla
kuormalla. Aika mitataan kehysaikoina."""

import numpy as np

ASEMIA = 10
MERKIN_SIIRTO = 0.05            # vuoromerkin siirto seuraavalle asemalle


# @alku vuorot
def simuloi(menetelma: str, kuorma: float, aikaa: int = 20_000,
            siemen: int = 9) -> tuple[float, float]:
    """Palauttaa (läpäisyn osuus kapasiteetista, keskiviiveen)."""
    rng = np.random.default_rng(siemen)
    jonot: list[list[float]] = [[] for _ in range(ASEMIA)]
    t, lahetetty, viiveet = 0.0, 0, []
    seuraava_saapuminen = rng.exponential(1 / kuorma, ASEMIA)
    asema = 0
    while t < aikaa:
        for a in range(ASEMIA):                    # uudet kehykset jonoon
            while seuraava_saapuminen[a] <= t:
                jonot[a].append(float(seuraava_saapuminen[a]))
                seuraava_saapuminen[a] += rng.exponential(
                    ASEMIA / kuorma)
        if jonot[asema]:
            viiveet.append(t + 1 - jonot[asema].pop(0))
            lahetetty += 1
            t += 1
        else:                                      # tyhjä vuoro
            t += 1 if menetelma == "TDMA" else MERKIN_SIIRTO
        if menetelma == "vuoromerkki":
            t += MERKIN_SIIRTO
        asema = (asema + 1) % ASEMIA
    return lahetetty / t, float(np.mean(viiveet))
# @loppu vuorot


print("kuorma   TDMA: läpäisy viive   vuoromerkki: läpäisy viive")
for kuorma in (0.1, 0.5, 0.8):
    tdma = simuloi("TDMA", kuorma)
    merkki = simuloi("vuoromerkki", kuorma)
    print(f"{kuorma:>6}   {tdma[0]:>13.2f} {tdma[1]:>6.1f}"
          f"   {merkki[0]:>20.2f} {merkki[1]:>6.1f}")
