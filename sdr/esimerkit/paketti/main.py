"""Anturipakettien vastaanotto synteettisesta tallenteesta."""

import numpy as np

import lahetin as lh
import vastaanotin as va

# @alku tallenne
rng = np.random.default_rng(433)
viestit = [
    (0.004, b"T=21.5C H=40%", 18.0, +3_100.0),
    (0.020, b"T=21.6C H=41%", 11.0, -1_800.0),
    (0.036, b"T=21.6C H=41%", 18.0, +3_100.0),
    (0.0365, b"OVI AUKI", 16.0, -9_000.0),   # toinen laite samaan aikaan
    (0.052, b"PARISTO OK", 7.0, +500.0),
]
x = lh.tallenne(viestit, kesto=0.07, keskitaajuus=-150e3, rng=rng)
# @loppu tallenne

# @alku vastaanota
for p in va.vastaanota(x, -150e3):
    tila = "CRC ok " if p.crc_ok else "CRC VIRHE"
    teksti = p.data.decode("ascii", "replace") if p.crc_ok else "-"
    print(f"{p.alku_ms:5.1f} ms  {p.taajuusvirhe_hz / 1e3:+5.1f} kHz  "
          f"{tila:9}  {teksti}")
# @loppu vastaanota
