"""Mittaussignaalin analyysi NumPylla: tunnusluvut, liukuva keskiarvo,
häiriöpiikkien tunnistus ja hallitseva taajuus."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]


# @alku signaali
def mittaus(n: int, taajuus_hz: float, fs_hz: float,
            siemen: int) -> Taulukko:
    """50 Hz:n sinisignaali, kohinaa ja kolme häiriöpiikkiä."""
    rng = np.random.default_rng(siemen)     # toistettava satunnaisuus
    t = np.arange(n) / fs_hz
    x = 1.5 * np.sin(2 * np.pi * taajuus_hz * t)
    x += rng.normal(0.0, 0.05, n)
    x[[120, 470, 880]] += np.array([2.0, -2.5, 3.0])
    return x
# @loppu signaali


# @alku analyysi
def liukuva_keskiarvo(x: Taulukko, ikkuna: int) -> Taulukko:
    return np.convolve(x, np.ones(ikkuna) / ikkuna, mode="valid")


def piikit(x: Taulukko, kynnys: float) -> npt.NDArray[np.intp]:
    """Näytteet, jotka poikkeavat paikallisesta mediaanista eniten."""
    ikkunat = np.lib.stride_tricks.sliding_window_view(
        np.pad(x, 2, mode="edge"), 5)
    poikkeama = np.abs(x - np.median(ikkunat, axis=1))
    return np.flatnonzero(poikkeama > kynnys)


def hallitseva_taajuus(x: Taulukko, fs_hz: float) -> float:
    spektri = np.abs(np.fft.rfft(x - x.mean()))
    taajuudet = np.fft.rfftfreq(x.size, d=1 / fs_hz)
    return float(taajuudet[np.argmax(spektri)])
# @loppu analyysi


def main() -> None:
    fs = 1000.0
    x = mittaus(1000, 50.0, fs, siemen=42)
    print(f"keskiarvo {x.mean():+.3f}, RMS {np.sqrt(np.mean(x**2)):.3f}, "
          f"huippu {np.abs(x).max():.3f}")
    print("häiriöpiikit:", piikit(x, kynnys=1.0))
    print(f"hallitseva taajuus {hallitseva_taajuus(x, fs):.1f} Hz")
    tasoitettu = liukuva_keskiarvo(x, 20)   # 20 ms = yksi jakso
    print(f"liukuva keskiarvo: {tasoitettu.size} arvoa, "
          f"vaihteluväli {np.ptp(tasoitettu):.3f}")


if __name__ == "__main__":
    main()
