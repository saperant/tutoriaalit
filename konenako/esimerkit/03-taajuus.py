"""2D-DFT: raitojen taajuus, alipäästö ja aliasointi pienennettäessä."""

import cv2
import numpy as np

# @alku raidat
# Vinot raidat: 12 jaksoa vaakasuunnassa ja 5 pystysuunnassa.
n = 128
y, x = np.mgrid[0:n, 0:n].astype(np.float32)
raidat = 127.5 + 127.5 * np.cos(2 * np.pi * (12 * x + 5 * y) / n)
# rfft2 laskee vain puolet tasosta (kx >= 0): reaalikuvan spektri on
# symmetrinen, joten toinen puoli on peilikuva.
spektri = np.abs(np.fft.rfft2(raidat))
spektri[0, 0] = 0                                 # ohitetaan keskiarvo
ky, kx_s = np.unravel_index(int(np.argmax(spektri)), spektri.shape)
ky_s = ky if ky < n // 2 else ky - n              # etumerkillinen taajuus
print(f"huippu taajuudella (kx, ky) = ({kx_s}, {ky_s}) jaksoa/kuva")
kulma = np.degrees(np.arctan2(ky_s, kx_s))
print(f"raitojen normaalin suunta {kulma:.1f} astetta")
# @loppu raidat

# @alku pienennys
# Tiheät raidat (40 jaksoa leveydellä) pienennetään neljäsosaan.
# Uuden kuvan Nyquist-raja on 32/2 = 16 jaksoa, joten 40 jaksoa ei
# mahdu, ja ilman alipäästöä se laskostuu matalammaksi taajuudeksi.
tiheat = (127.5 + 127.5 * np.cos(2 * np.pi * 40 * x / n)).astype(np.uint8)
for nimi, tapa in (("INTER_NEAREST", cv2.INTER_NEAREST),
                   ("INTER_LINEAR", cv2.INTER_LINEAR),
                   ("INTER_AREA", cv2.INTER_AREA)):
    pieni = cv2.resize(tiheat, (32, 32), interpolation=tapa)
    rivi = pieni[0].astype(np.float32) - float(pieni[0].mean())
    s = np.abs(np.fft.rfft(rivi))
    huippu = int(np.argmax(s))
    print(f"{nimi:14s} huippu {huippu:2d} jaksoa,"
          f" vaihtelu {float(pieni.std()):5.1f}")
# @loppu pienennys
