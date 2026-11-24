"""Virhebudjetti: FIR-suodattimen sanaleveydet kohinamallista ja
tarkistus bittitarkalla simuloinnilla."""

import numpy as np
import numpy.typing as npt

Liuku = npt.NDArray[np.float64]
Kokonaiset = npt.NDArray[np.int64]


def alipaasto(pituus: int, raja: float) -> Liuku:
    n = np.arange(pituus) - (pituus - 1) / 2
    h = 2 * raja * np.sinc(2 * raja * n) * np.hamming(pituus)
    return np.asarray(h / h.sum(), dtype=np.float64)


def koodit(x: Liuku, bitit: int) -> Kokonaiset:
    return np.asarray(np.round(x * (1 << (bitit - 1))), dtype=np.int64)


H = alipaasto(41, 0.1)


def valkoinen(maara: int) -> Liuku:
    """Toistettava valkoinen kohina välillä [-0,9, 0,9] (LCG)."""
    tila, arvot = 12345, []
    for _ in range(maara):
        tila = (tila * 1103515245 + 12345) % (1 << 32)
        arvot.append(0.9 * ((tila >> 8) / (1 << 23) - 1.0))
    return np.asarray(arvot, dtype=np.float64)


X = valkoinen(1 << 14)
VIITE = np.convolve(X, H)


# @alku malli
def ennuste_db(bx: int, bh: int, by: int) -> float:
    """SQNR kohinamallista: syötteen ja tuloksen pyöristys sekä
    kertoimien kvantisointi ovat toisistaan riippumattomia lähteitä."""
    hq = koodit(H, bh) / (1 << (bh - 1))
    qx, qy = 2.0 ** (1 - bx), 2.0 ** (1 - by)
    kohina = (qx**2 / 12 * np.sum(hq**2)          # syöte suodattimen läpi
              + np.var(X) * np.sum((hq - H) ** 2)  # kertoimien virhe
              + qy**2 / 12)                        # tuloksen pyöristys
    return float(10 * np.log10(np.var(VIITE) / kohina))
# @loppu malli


# @alku simulointi
def mitattu_db(bx: int, bh: int, by: int) -> float:
    """Bittitarkka laskenta kokonaisluvuilla; tulos pyöristetään
    by-bittiseen Q1.(by-1)-muotoon."""
    kertyma = np.convolve(koodit(X, bx), koodit(H, bh))
    siirto = (bx - 1) + (bh - 1) - (by - 1)
    y = (kertyma + (1 << (siirto - 1))) >> siirto      # lähimpään
    virhe = y / (1 << (by - 1)) - VIITE
    return float(10 * np.log10(np.var(VIITE) / np.mean(virhe**2)))
# @loppu simulointi


# @alku taulukko
print(f"{'syöte':>5} {'kert.':>5} {'tulos':>5} {'ennuste':>8} "
      f"{'mitattu':>8}")
for bx, bh, by in [(12, 12, 12), (16, 12, 16), (12, 16, 16),
                   (16, 16, 12), (16, 16, 16)]:
    print(f"{bx:>5} {bh:>5} {by:>5} {ennuste_db(bx, bh, by):>8.1f} "
          f"{mitattu_db(bx, bh, by):>8.1f}")
# @loppu taulukko

# @alku haku
# Pienin bittien kokonaismäärä, jolla ennuste ylittää 80 dB.
paras = min(((bx, bh, by) for bx in range(8, 21) for bh in range(8, 21)
             for by in range(8, 21) if ennuste_db(bx, bh, by) >= 80),
            key=lambda b: (sum(b), b))
print(f"80 dB: syöte {paras[0]}, kertoimet {paras[1]}, tulos {paras[2]}"
      f" bittiä; mitattu {mitattu_db(*paras):.1f} dB")
# @loppu haku
