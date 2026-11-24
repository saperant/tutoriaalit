"""Kehystahdistus: tunnetun alkuosan etsiminen korrelaatiolla."""

import numpy as np

rng = np.random.default_rng(15)

# @alku barker
barker = np.array([1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1], dtype=float)
autokorrelaatio = np.correlate(barker, barker, "full")
sivu = np.max(np.abs(autokorrelaatio[: len(barker) - 1]))
print(f"Barker-13: huippu {autokorrelaatio.max():.0f}, suurin sivukeila"
      f" {sivu:.0f}")
satunnainen = 1.0 - 2 * rng.integers(0, 2, 13)
ak = np.correlate(satunnainen, satunnainen, "full")
print(f"satunnainen 13: huippu {ak.max():.0f}, suurin sivukeila"
      f" {np.max(np.abs(ak[:12])):.0f}")
# @loppu barker


# @alku etsi
def qpsk(n: int) -> np.ndarray:
    b = rng.integers(0, 2, (2, n))
    s: np.ndarray = ((1 - 2 * b[0]) + 1j * (1 - 2 * b[1])) / np.sqrt(2)
    return s


alku = np.tile(barker, 4) * (1 + 1j) / np.sqrt(2)     # 52 symbolin alkuosa
kehykset, data = [], 300
virta = [qpsk(137)]                           # vastaanotto alkaa kesken
for _ in range(5):
    kehykset.append(sum(len(v) for v in virta))
    virta += [alku, qpsk(data)]
r = np.concatenate(virta)
vaihe = np.exp(1j * (0.7 + 2 * np.pi * 0.001 * np.arange(len(r))))
r = r * vaihe + 0.5 * (rng.standard_normal(len(r))
                       + 1j * rng.standard_normal(len(r)))   # Es/N0 3 dB

# Itseisarvo: tuntematon vaihe ei haittaa. Normitus energialla tekee
# kynnyksestä riippumattoman signaalin tasosta.
c = np.abs(np.correlate(r, alku, "valid")) / len(alku)
energia = np.sqrt(np.convolve(np.abs(r) ** 2, np.ones(len(alku)), "valid")
                  / len(alku))
mitta = c / energia
kynnys = 0.5
loydetyt = []
i = 0
while i < len(mitta):
    if mitta[i] > kynnys:
        paras = i + int(np.argmax(mitta[i: i + len(alku)]))
        loydetyt.append(paras)
        i = paras + len(alku)
    else:
        i += 1
print("kehykset alkavat:", kehykset)
print("löydetyt:        ", loydetyt)
muualla = np.delete(mitta, [k + d for k in kehykset for d in range(-60, 60)
                            if 0 <= k + d < len(mitta)])
print(f"mitta kehyksen kohdalla >= {min(mitta[kehykset]):.2f},"
      f" muualla <= {muualla.max():.2f}")
# @loppu etsi
