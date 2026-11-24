"""Klassinen luokittelija: muotopiirteet, k-NN ja arviointi testijoukolla."""

import cv2
import numpy as np

LUOKAT = ("kolmio", "nelio", "ympyra")
Aineisto = tuple[np.ndarray, np.ndarray]        # piirteet, luokat


# @alku data
def muoto(luokka: int, koko: float, rng: np.random.Generator) -> np.ndarray:
    """Kiertynyt ja siirtynyt muoto 64 x 64 -kuvaan."""
    kuva = np.zeros((64, 64), np.uint8)
    kulma = rng.uniform(0, 2 * np.pi)
    keski = rng.uniform(26, 38, 2)
    if luokka == 2:
        cv2.circle(kuva, (int(keski[0]), int(keski[1])), int(koko), 255, -1)
        return kuva
    kulmia = 3 if luokka == 0 else 4
    t = kulma + 2 * np.pi * np.arange(kulmia) / kulmia
    pisteet = keski + koko * np.stack([np.cos(t), np.sin(t)], 1)
    cv2.fillPoly(kuva, [np.round(pisteet).astype(np.int32)], 255)
    return kuva


def piirteet(kuva: np.ndarray) -> np.ndarray:
    """Pyöreys, täyttöaste, kuperuus ja Hu1: eivät riipu koosta."""
    c = max(cv2.findContours(kuva, cv2.RETR_EXTERNAL,
                             cv2.CHAIN_APPROX_NONE)[0], key=cv2.contourArea)
    ala, piiri = cv2.contourArea(c), cv2.arcLength(c, True)
    kupera = cv2.contourArea(cv2.convexHull(c))
    _, (w, h), _ = cv2.minAreaRect(c)
    hu1 = float(cv2.HuMoments(cv2.moments(c))[0, 0])
    return np.array([4 * np.pi * ala / piiri**2, ala / (w * h),
                     ala / kupera, -np.log10(hu1)], np.float32)


rng = np.random.default_rng(seed=37)


def aineisto(n: int, pienin: float, suurin: float) -> Aineisto:
    y = rng.integers(0, 3, n)
    X = [piirteet(muoto(int(k), rng.uniform(pienin, suurin), rng))
         for k in y]
    return np.array(X, np.float32), y


# Opetus- ja testijoukko samasta jakaumasta (koko 10-26 px) sekä toinen
# testijoukko, jossa muodot ovat pieniä (3-6 px): jakauma on muuttunut.
X_opetus, y_opetus = aineisto(400, 10, 26)
X_testi, y_testi = aineisto(200, 10, 26)
X_pienet, y_pienet = aineisto(200, 3, 6)
# @loppu data


# @alku opetus
def knn(opetus: np.ndarray, nimiot: np.ndarray, kysely: np.ndarray,
        k: int = 5) -> np.ndarray:
    """k lähintä naapuria: enemmistön luokka euklidisella etäisyydellä."""
    etaisyys = np.linalg.norm(kysely[:, None] - opetus[None], axis=2)
    lahimmat = nimiot[np.argsort(etaisyys, axis=1)[:, :k]]
    return np.array([np.bincount(r, minlength=3).argmax() for r in lahimmat])


# Piirteet samaan mittakaavaan: k-NN mittaa etäisyyksiä.
keskiarvo, hajonta = X_opetus.mean(0), X_opetus.std(0)
for nimi, X_t, y_t in (("testi, sama jakauma", X_testi, y_testi),
                       ("testi, pienet muodot", X_pienet, y_pienet)):
    ennuste = knn((X_opetus - keskiarvo) / hajonta, y_opetus,
                  (X_t - keskiarvo) / hajonta)
    sekaannus = np.zeros((3, 3), int)
    for oikea, arvio in zip(y_t, ennuste, strict=True):
        sekaannus[oikea, arvio] += 1
    print(f"{nimi}: osuvuus {np.trace(sekaannus) / len(y_t):.2f}")
    print("  sekaannusmatriisi (rivi = oikea, sarake = ennuste):")
    for i, luokka in enumerate(LUOKAT):
        print(f"    {luokka:7s}", " ".join(f"{v:4d}" for v in sekaannus[i]))
# @loppu opetus
