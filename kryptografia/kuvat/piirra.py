"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Avain ja nonce ovat
kiinteät, jotta kuva on joka ajolla sama.
"""

import sys
from pathlib import Path

import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from matplotlib import rcParams
from matplotlib.figure import Figure

rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9

KOKO = 192  # kuvan sivu pikseleinä; rivi on 12 AES-lohkoa


def kuva() -> np.ndarray:
    """Harmaasävykuva, jossa on tasaisia pintoja: ympyrä ja palkki."""
    y, x = np.mgrid[0:KOKO, 0:KOKO]
    pikselit = np.full((KOKO, KOKO), 235, dtype=np.uint8)
    pikselit[(x - 76) ** 2 + (y - 88) ** 2 < 52 ** 2] = 70
    pikselit[(x > 112) & (x < 168) & (y > 104) & (y < 160)] = 150
    return pikselit


def salaa(pikselit: np.ndarray, tila: modes.Mode) -> np.ndarray:
    """Salaa pikselien tavut ja tulkitsee tuloksen takaisin kuvaksi."""
    salain = Cipher(algorithms.AES(bytes(range(32))), tila).encryptor()
    salattu = salain.update(pikselit.tobytes()) + salain.finalize()
    return np.frombuffer(salattu, dtype=np.uint8).reshape(pikselit.shape)


def ecb(polku: Path) -> None:
    """Sama kuva selvätekstinä sekä ECB- ja CTR-tilassa salattuna."""
    alkuperainen = kuva()
    paneelit = [
        ("selväteksti", alkuperainen),
        ("AES-ECB", salaa(alkuperainen, modes.ECB())),  # noqa: S305
        ("AES-CTR", salaa(alkuperainen, modes.CTR(bytes(16)))),
    ]
    kuvio = Figure(figsize=(6.3, 2.3))
    for i, (nimi, data) in enumerate(paneelit):
        ax = kuvio.add_subplot(1, 3, i + 1)
        ax.imshow(data, cmap="gray", vmin=0, vmax=255,
                  interpolation="nearest")
        ax.set_title(nimi)
        ax.set_xticks([])
        ax.set_yticks([])
    kuvio.tight_layout()
    kuvio.savefig(polku / "ecb.png", dpi=200)


def main() -> None:
    polku = Path(sys.argv[1])
    polku.mkdir(exist_ok=True)
    ecb(polku)


if __name__ == "__main__":
    main()
