"""Kolikoiden laskeminen synteettisestä kuvasta: kynnystys ja alueet."""

import cv2
import numpy as np

# @alku kuva
# Synteettinen kuva: tumma pöytä, vaaleita kolikoita ja kohinaa.
# Kiinteä siemen tekee kuvasta joka ajossa saman, ja koska kolikot on
# piirretty itse, oikea vastaus tunnetaan.
rng = np.random.default_rng(seed=2026)
kuva = np.full((240, 320), 60, np.uint8)
kolikot = [((60, 60), 22), ((150, 70), 30), ((250, 60), 22),
           ((80, 170), 30), ((180, 170), 22), ((270, 175), 30)]
for keskipiste, sade in kolikot:
    cv2.circle(kuva, keskipiste, sade, 190, thickness=-1)
kohina = rng.normal(0.0, 12.0, kuva.shape)
kuva = np.clip(kuva + kohina, 0, 255).astype(np.uint8)
# @loppu kuva

# @alku analyysi
# 1. Tasoitus vaimentaa kohinan, 2. Otsu valitsee kynnyksen
# histogrammista, 3. yhtenäiset alueet ovat kolikoita.
tasoitettu = cv2.GaussianBlur(kuva, (5, 5), 0)
kynnys, maski = cv2.threshold(tasoitettu, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)
n, _, tilastot, keskipisteet = cv2.connectedComponentsWithStats(maski)
print(f"Otsun kynnys: {kynnys:.0f}")
print(f"alueita taustan lisäksi: {n - 1}")
for i in range(1, n):
    ala = int(tilastot[i, cv2.CC_STAT_AREA])
    x, y = keskipisteet[i]
    luokka = "iso" if ala > 2000 else "pieni"
    print(f"  ({x:5.1f}, {y:5.1f})  ala {ala:4d} px  -> {luokka}")
# @loppu analyysi

# @alku tarkistus
odotetut = sorted(round(np.pi * r * r) for _, r in kolikot)
mitatut = sorted(int(tilastot[i, cv2.CC_STAT_AREA]) for i in range(1, n))
suurin = max(abs(m - o) / o for m, o in zip(mitatut, odotetut,
                                             strict=True))
print(f"suurin pinta-alan virhe: {100 * suurin:.1f} %")
# @loppu tarkistus
