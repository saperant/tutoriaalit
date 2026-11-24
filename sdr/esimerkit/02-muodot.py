"""IQ-tallenteiden muodot cu8, ci16 ja cf32 seka SigMF-metatiedot."""

import json
from pathlib import Path

import numpy as np

rng = np.random.default_rng(4)
fs = 2.4e6
z = 0.25 * (rng.standard_normal(4096) + 1j * rng.standard_normal(4096))


# @alku muunnokset
def cu8(x: np.ndarray) -> np.ndarray:
    """RTL-SDR: etumerkiton 8 bit, nolla = 127,5 (I, Q, I, Q, ...)."""
    lomitettu = np.column_stack([x.real, x.imag]).ravel()
    tulos: np.ndarray = np.clip(np.round(lomitettu * 127.5 + 127.5),
                                0, 255).astype(np.uint8)
    return tulos


def ci16(x: np.ndarray) -> np.ndarray:
    """Pluto, USRP: etumerkillinen 16 bit pikkupaattyisena."""
    lomitettu = np.column_stack([x.real, x.imag]).ravel()
    tulos: np.ndarray = np.clip(np.round(lomitettu * 32767),
                                -32768, 32767).astype("<i2")
    return tulos


def lue(raaka: np.ndarray) -> np.ndarray:
    """Mika tahansa kolmesta muodosta takaisin kompleksiluvuiksi."""
    if raaka.dtype == np.uint8:
        x = (raaka.astype(np.float64) - 127.5) / 127.5
    elif raaka.dtype == np.dtype("<i2"):
        x = raaka.astype(np.float64) / 32767
    else:
        x = raaka.astype(np.float64)
    tulos: np.ndarray = x[0::2] + 1j * x[1::2]
    return tulos
# @loppu muunnokset


# @alku vertailu
muodot = {
    "cu8": cu8(z),
    "ci16_le": ci16(z),
    "cf32_le": np.column_stack([z.real, z.imag]).ravel().astype("<f4"),
}
for nimi, raaka in muodot.items():
    virhe = lue(raaka) - z
    sqnr = 10 * np.log10(np.mean(np.abs(z) ** 2) / np.mean(np.abs(virhe)**2))
    mbs = fs * raaka.itemsize * 2 / 1e6
    print(f"{nimi:8} {raaka.itemsize * 2} tavua/nayte, {mbs:5.1f} MB/s "
          f"2,4 MS/s:lla, kvantisointi SQNR {sqnr:5.1f} dB")
# @loppu vertailu

# @alku sigmf
polku = Path("kohina.sigmf-data")
muodot["cf32_le"].tofile(polku)
meta = {
    "global": {
        "core:datatype": "cf32_le",
        "core:sample_rate": fs,
        "core:version": "1.0.0",
        "core:description": "Synteettinen kohinatallenne",
        "core:recorder": "sdr-esimerkit",
    },
    "captures": [{"core:sample_start": 0, "core:frequency": 433.92e6,
                  "core:datetime": "2026-11-24T12:00:00Z"}],
    "annotations": [{"core:sample_start": 0, "core:sample_count": len(z),
                     "core:label": "kohina"}],
}
polku.with_suffix(".sigmf-meta").write_text(json.dumps(meta, indent=2))
luettu = json.loads(polku.with_suffix(".sigmf-meta").read_text())
naytteita = polku.stat().st_size // 8
print(f"{polku}: {naytteita} naytetta, "
      f"{luettu['captures'][0]['core:frequency'] / 1e6:.2f} MHz, "
      f"{luettu['global']['core:datatype']}")
# @loppu sigmf
