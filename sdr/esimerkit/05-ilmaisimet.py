"""FM-ilmaisimet: polaari-ilmaisin, kvadratuuri-ilmaisin ja vasteet."""

import numpy as np

fs = 228e3


# @alku ilmaisimet
def polaari(z: np.ndarray) -> np.ndarray:
    """arg(z[n] z*[n-1]): tarkka vaihe-ero, vaatii arkustangentin."""
    tulos: np.ndarray = np.angle(z[1:] * np.conj(z[:-1]))
    return tulos


def kvadratuuri(z: np.ndarray) -> np.ndarray:
    """(I dQ - Q dI) / |z|^2 = Im(z[n] z*[n-1]) / |z|^2 = sin(vaihe-ero).

    Ei arkustangenttia: sopii FPGA:lle ja pienelle prosessorille, mutta
    sin(x) ~ x vain, kun vaihe-ero naytevalilla on pieni."""
    tulo = z[1:] * np.conj(z[:-1])
    tulos: np.ndarray = tulo.imag / (np.abs(z[1:]) * np.abs(z[:-1]))
    return tulos
# @loppu ilmaisimet


# @alku vertailu
# Vakiotaajuus f: oikea vaihe-ero naytevalilla on 2 pi f / fs.
for f in (10e3, 50e3, 75e3, 100e3):
    n = np.arange(1000)
    z = 0.3 * np.exp(2j * np.pi * f * n / fs)     # amplitudi ei vaikuta
    oikea = 2 * np.pi * f / fs
    # round(..) + 0.0 muuttaa pyoristyksen -0.00:n nollaksi.
    virhe_p = round(100 * (polaari(z).mean() / oikea - 1), 2) + 0.0
    virhe_k = round(100 * (kvadratuuri(z).mean() / oikea - 1), 2) + 0.0
    print(f"{f / 1e3:5.0f} kHz: polaari {virhe_p:+6.2f} %, "
          f"kvadratuuri {virhe_k:+6.2f} %")
# @loppu vertailu

# @alku vaste
# Vaihe-ero on taajuuden keskiarvo naytevalin yli: suotimen vaste
# sinc(f / fs). Moduloivan signaalin f, ei kantoaallon taajuus.
for f in (1e3, 15e3, 19e3, 38e3, 57e3):
    db = round(20 * np.log10(np.sinc(f / fs)), 2) + 0.0
    print(f"moduloiva {f / 1e3:4.0f} kHz: vaste {np.sinc(f / fs):.4f} = "
          f"{db:5.2f} dB")
# @loppu vaste
