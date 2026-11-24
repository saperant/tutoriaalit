"""Reaalinen sekoitus tuottaa peilikuvan, kompleksinen (IQ) ei."""

import numpy as np

fs = 1_000_000.0
t = np.arange(10_000) / fs
lo = 200_000.0                                # paikallisoskillaattori


def teho_dB(x: np.ndarray, f: float) -> str:
    """Signaalin teho (dB) taajuudella f, korrelaatiolla."""
    a = abs(np.mean(x * np.exp(-2j * np.pi * f * t)))
    if a < 1e-5:
        return "  -inf"                       # vain pyöristysvirhettä
    return f"{20 * np.log10(a):6.1f}"


# @alku kuva
haluttu = np.cos(2 * np.pi * 210_000 * t)     # 10 kHz LO:n yläpuolella
peili = np.cos(2 * np.pi * 190_000 * t)       # 10 kHz LO:n alapuolella
for nimi, rf in (("haluttu", haluttu), ("peili", peili)):
    reaali = rf * np.cos(2 * np.pi * lo * t)            # yksi sekoitin
    iq = rf * np.exp(-2j * np.pi * lo * t)              # I- ja Q-haara
    print(f"{nimi:8s} reaalinen: +10 kHz {teho_dB(reaali, 10e3)} dB,"
          f" -10 kHz {teho_dB(reaali, -10e3)} dB")
    print(f"{'':8s} IQ:        +10 kHz {teho_dB(iq, 10e3)} dB,"
          f" -10 kHz {teho_dB(iq, -10e3)} dB")
# @loppu kuva
