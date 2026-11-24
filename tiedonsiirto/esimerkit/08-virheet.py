"""Kantoaallon vaihe- ja taajuusvirheen vaikutus konstellaatioon."""

import numpy as np

rng = np.random.default_rng(12)
n = 200_000
EbN0_dB = 8.0


def gray_qam16() -> np.ndarray:
    tasot = np.array([-3, -1, 1, 3]) / np.sqrt(10)
    koodi = [0, 1, 3, 2]
    p = np.empty(16, dtype=complex)
    for i in range(4):
        for q in range(4):
            p[(koodi[i] << 2) | koodi[q]] = tasot[i] + 1j * tasot[q]
    return p


# @alku vaihe
konstellaatiot = {
    "QPSK": np.exp(1j * (np.pi / 4 + np.pi / 2 * np.array([0, 1, 3, 2]))),
    "16-QAM": gray_qam16(),
}
print("vaihevirhe    QPSK BER   16-QAM BER")
tulokset: dict[float, list[float]] = {}
for p in konstellaatiot.values():
    k = len(p).bit_length() - 1
    N0 = 1 / (k * 10 ** (EbN0_dB / 10))
    nimiot = rng.integers(0, len(p), n)
    kohina = np.sqrt(N0 / 2) * (rng.standard_normal(n)
                                + 1j * rng.standard_normal(n))
    for asteet in (0.0, 5.0, 10.0, 20.0, 30.0):
        r = p[nimiot] * np.exp(1j * np.radians(asteet)) + kohina
        ilm = np.argmin(np.abs(r[:, None] - p[None, :]), axis=1)
        ber = np.unpackbits((nimiot ^ ilm).astype(np.uint8)).sum() / (k * n)
        tulokset.setdefault(asteet, []).append(float(ber))
for asteet, (q, m) in tulokset.items():
    print(f"{asteet:5.0f} astetta  {q:9.2e}   {m:9.2e}")
# @loppu vaihe

# @alku taajuus
# Taajuusvirhe df kiertää konstellaatiota 360 * df / Rs astetta/symboli.
Rs, df = 1e6, 200.0                           # 1 Msymbol/s, 200 Hz virhe
for symboleja in (100, 1_000, 10_000):
    print(f"taajuusvirhe {df:.0f} Hz: {symboleja:6d} symbolin jälkeen"
          f" kiertynyt {360 * df / Rs * symboleja:6.1f} astetta")
# @loppu taajuus
