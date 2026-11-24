"""QPSK:n kantoaallon palautus: Costas-silmukka eli vaihelukittu silmukka."""

import numpy as np

rng = np.random.default_rng(13)


# @alku vahvistukset
def silmukka(BnT: float, zeta: float, Kd: float) -> tuple[float, float]:
    """Toisen asteen silmukan PI-vahvistukset kaistasta ja vaimennuksesta."""
    theta = BnT / (zeta + 1 / (4 * zeta))
    jakaja = 1 + 2 * zeta * theta + theta**2
    return 4 * zeta * theta / jakaja / Kd, 4 * theta**2 / jakaja / Kd
# @loppu vahvistukset


# @alku silmukka
def costas(r: np.ndarray, Kp: float, Ki: float) -> tuple[np.ndarray,
                                                          np.ndarray]:
    """Palauttaa vaihekorjatut symbolit ja vaihe-estimaatit."""
    y = np.empty_like(r)
    vaiheet = np.empty(len(r))
    vaihe = integraali = 0.0
    for i, ri in enumerate(r):
        y[i] = ri * np.exp(-1j * vaihe)
        # QPSK-vaiheilmaisin: virhe on nolla, kun symboli on akseleiden
        # välissä (45, 135, ... astetta). Neljän kulman epävarmuus jää.
        e = (np.sign(y[i].real) * y[i].imag - np.sign(y[i].imag) * y[i].real)
        integraali += Ki * e
        vaihe += Kp * e + integraali          # NCO: vaiheen kertymä
        vaiheet[i] = vaihe
    return y, vaiheet
# @loppu silmukka


# @alku koe
n = 4_000
bitit = rng.integers(0, 2, (2, n))
s = ((1 - 2 * bitit[0]) + 1j * (1 - 2 * bitit[1])) / np.sqrt(2)
f, phi = 0.002, 1.0                           # sykliä/symboli ja rad
todellinen = 2 * np.pi * f * np.arange(n) + phi
EsN0 = 10 ** (15 / 10)
kohina = np.sqrt(1 / (2 * EsN0)) * (rng.standard_normal(n)
                                    + 1j * rng.standard_normal(n))
r = s * np.exp(1j * todellinen) + kohina
Kp, Ki = silmukka(0.02, 0.707, np.sqrt(2))
for nimi, ki in (("1. aste", 0.0), ("2. aste", Ki)):
    y, vaiheet = costas(r, Kp, ki)
    # Virhe 90 asteen monikertojen suhteen (QPSK:n epävarmuus).
    virhe = np.angle(np.exp(4j * (todellinen - vaiheet))) / 4
    loppu = virhe[n // 2:]
    # Lukittunut: 50 peräkkäistä symbolia lähellä lopullista virhettä.
    lahella = np.abs(virhe - np.mean(loppu)) < 0.1
    lukittu = int(np.argmax(np.convolve(lahella, np.ones(50), "valid") == 50))
    print(f"{nimi}: lukittui {lukittu:4d} symbolin jälkeen,"
          f" jäännösvirhe {np.degrees(np.mean(loppu)):5.1f}"
          f" +- {np.degrees(np.std(loppu)):4.1f} astetta")
# @loppu koe

# @alku epavarmuus
# Lukittunut silmukka voi olla 0, 90, 180 tai 270 astetta väärässä.
# Tunnettu tahdistussana (128 symbolia) kertoo, mikä kierto on oikea.
alku = 2_000
sana = slice(alku, alku + 128)
kierrot = [np.exp(1j * np.pi / 2 * k) for k in range(4)]
paras = max(range(4), key=lambda k: np.real(np.vdot(s[sana],
                                                    y[sana] * kierrot[k])))
oikaistu = y[alku:] * kierrot[paras]
virheita = np.count_nonzero(np.sign(oikaistu.real) != np.sign(s[alku:].real))
virheita += np.count_nonzero(np.sign(oikaistu.imag) != np.sign(s[alku:].imag))
print(f"kierto {90 * paras} astetta, bittivirheitä {virheita} /"
      f" {2 * (n - alku)}")
# @loppu epavarmuus
