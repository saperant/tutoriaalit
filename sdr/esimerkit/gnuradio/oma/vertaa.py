"""Vertaa GNU Radion lohkokaavion tulosta tutoriaalin omaan
vastaanottimeen: samat savelet, sama kohina, sama kanavan taso."""

import sys
from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "fm"))
import lahetin  # noqa: E402
import vastaanotin as va  # noqa: E402

Reaali = NDArray[np.float64]


def lue(polku: str) -> Reaali:
    x: Reaali = np.fromfile(polku, dtype="<f4").astype(np.float64)
    return x


# @alku kohdista
def kohdista(a: Reaali, b: Reaali) -> tuple[int, float]:
    """Viive, jolla b seuraa a:ta, ja jaannoksen taso desibeleina, kun
    viive ja vahvistusero on poistettu."""
    n = min(len(a), len(b))
    keski = slice(n // 4, 3 * n // 4)              # transientit pois
    ristikorrelaatio = signal.correlate(b[keski], a[keski], "full")
    viive = int(np.argmax(ristikorrelaatio)) - (keski.stop - keski.start - 1)
    a2 = a[keski]
    b2 = b[keski.start + viive:keski.stop + viive]
    k = float(np.dot(a2, b2) / np.dot(a2, a2))     # vahvistusero
    jaannos = b2 - k * a2
    return viive, float(10 * np.log10(np.mean(jaannos ** 2)
                                      / np.mean(b2 ** 2)))
# @loppu kohdista


if __name__ == "__main__":
    viite, gr = lue("viite.f32"), lue("gr.f32")
    print("                      oma    GNU Radio")
    print(f"kesto (s)          {len(viite) / va.FS_AANI:6.2f}   "
          f"{len(gr) / va.FS_AANI:6.2f}")
    for hz in (lahetin.VASEN_HZ, lahetin.OIKEA_HZ):
        (a1, s1), (a2, s2) = (va.sinad(x, va.FS_AANI, hz)
                              for x in (viite, gr))
        print(f"savel {hz:4.0f} Hz      {a1:6.3f}   {a2:6.3f}")
    # SINAD yhden savelen suhteen: toinen savel on "muuta", joten
    # verrataan kohinaa kaistalla, jolla ei ole kumpaakaan.
    for nimi, x in (("oma", viite), ("GNU Radio", gr)):
        x = x[len(x) // 4:]
        f, p = signal.welch(x, va.FS_AANI, nperseg=4096)
        kaista = (f > 3_000) & (f < 14_000)
        print(f"kohina 3-14 kHz, {nimi:9} "
              f"{10 * np.log10(np.sum(p[kaista]) * (f[1] - f[0])):4.0f} dB")
    viive, jaannos = kohdista(viite, gr)
    print(f"GNU Radion viive omaan nahden {viive} naytetta "
          f"({1e3 * viive / va.FS_AANI:.2f} ms)")
    print(f"jaannos kohdistuksen jalkeen {jaannos:.0f} dB")
    taso = np.fromfile("taso.f32", dtype="<f4")
    oma_taso = float(Path("viite-taso.txt").read_text("utf-8"))
    print(f"kanavan taso: oma {oma_taso:.1f} dBFS, tehomittarilohko "
          f"{float(np.mean(taso[len(taso) // 2:])):.1f} dBFS "
          f"({len(taso)} arvoa)")
