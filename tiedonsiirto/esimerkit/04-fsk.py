"""FSK: taajuuksien ortogonaalisuus ja jatkuvan vaiheen etu (MSK)."""

import numpy as np

sps = 32                                      # näytettä symbolia kohti
n = np.arange(sps)

# @alku ortogonaalisuus
# Kaksi sävyä symbolin aikana T. Ne ovat ortogonaaliset, kun niiden
# korrelaatio on nolla: koherentisti dfT = 1/2, epäkoherentisti dfT = 1.
print("dfT    koherentti   epäkoherentti")
t = (np.arange(1_000) + 0.5) / 1_000         # symbolin aika 0..T tiheästi
for dfT in (0.25, 0.5, 0.75, 1.0):
    s0 = np.exp(2j * np.pi * (-dfT / 2) * t)
    s1 = np.exp(2j * np.pi * (+dfT / 2) * t)
    rho = np.vdot(s0, s1) / len(t)
    print(f"{dfT:4.2f}   {abs(rho.real):10.3f}   {abs(rho):13.3f}")
# @loppu ortogonaalisuus


# @alku vaihe
def fsk(bitit: np.ndarray, dfT: float, jatkuva: bool) -> np.ndarray:
    """2-FSK kantataajuudella. Jatkuva vaihe: CPFSK, dfT = 1/2 on MSK."""
    rng = np.random.default_rng(6)
    paloja = []
    vaihe = 0.0
    for b in bitit:
        f = (dfT / 2 if b else -dfT / 2) / sps    # syklejä näytettä kohti
        if not jatkuva:
            vaihe = rng.uniform(0, 2 * np.pi)     # erilliset oskillaattorit
        paloja.append(np.exp(1j * (vaihe + 2 * np.pi * f * n)))
        vaihe += 2 * np.pi * f * sps
    return np.concatenate(paloja)


bitit = np.random.default_rng(5).integers(0, 2, 4_000)
for nimi, jatkuva in (("hyppivä vaihe", False), ("jatkuva (MSK)", True)):
    x = fsk(bitit, 0.5, jatkuva)
    S = np.abs(np.fft.fft(x)) ** 2
    f = np.fft.fftfreq(len(x)) * sps          # taajuus symbolinopeuden 1/T
    for raja in (1.0, 2.0):
        ulkona = S[np.abs(f) > raja].sum() / S.sum()
        print(f"{nimi}: teho |f| > {raja:.0f}/T"
              f" {10 * np.log10(ulkona):6.1f} dB")
# @loppu vaihe
