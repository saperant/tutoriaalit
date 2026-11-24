"""Kohinanpoisto: keskiarvo, Gauss, mediaani ja bilateraalinen suodin."""

from collections.abc import Callable

import cv2
import numpy as np

# @alku kuvat
# Puhdas kuva: kaksi tasaista aluetta ja niiden välissä terävä reuna.
puhdas = np.full((128, 128), 70, np.uint8)
puhdas[:, 64:] = 180
rng = np.random.default_rng(seed=21)
gauss = np.clip(puhdas + rng.normal(0, 15, puhdas.shape), 0, 255)
gauss = gauss.astype(np.uint8)
suola = puhdas.copy()
paikat = rng.random(puhdas.shape)
suola[paikat < 0.05] = 0                         # pippuri
suola[paikat > 0.95] = 255                       # suola
# @loppu kuvat


# @alku mittarit
def psnr(kuva: np.ndarray) -> float:
    """Huippusignaali-kohinasuhde puhtaaseen kuvaan desibeleinä."""
    return float(cv2.PSNR(puhdas, kuva))


def reunan_leveys(kuva: np.ndarray) -> int:
    """Pikselit, joilla rivien keskiarvo on reunan 10-90 %:n välissä."""
    profiili = kuva.astype(np.float32).mean(axis=0)
    ala, yla = 70 + 0.1 * 110, 70 + 0.9 * 110
    return int(np.count_nonzero((profiili > ala) & (profiili < yla)))
# @loppu mittarit


# @alku vertailu
suotimet: dict[str, Callable[[np.ndarray], np.ndarray]] = {
    "keskiarvo 5x5": lambda k: cv2.blur(k, (5, 5)),
    "Gauss 5x5": lambda k: cv2.GaussianBlur(k, (5, 5), 0),
    "mediaani 5": lambda k: cv2.medianBlur(k, 5),
    "bilateraali": lambda k: cv2.bilateralFilter(k, 9, 60, 5),
}
print(f"{'':15s} {'Gauss-kohina':>13s} {'suola':>7s} {'reuna':>6s}")
print(f"{'ei suodatusta':15s} {psnr(gauss):10.1f} dB {psnr(suola):7.1f}"
      f" {reunan_leveys(gauss):6d}")
for nimi, suodin in suotimet.items():
    print(f"{nimi:15s} {psnr(suodin(gauss)):10.1f} dB"
          f" {psnr(suodin(suola)):7.1f} {reunan_leveys(suodin(gauss)):6d}")
# @loppu vertailu
