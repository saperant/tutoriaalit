"""FM-stereovastaanotin synteettisella tallenteella alusta loppuun."""

from pathlib import Path

import numpy as np

import lahetin
import vastaanotin as va

# @alku tallenne
rng = np.random.default_rng(2026)
z = lahetin.tallenne(kesto=1.2, cnr_db=35.0, rng=rng)
polku = Path("asema.cu8")
lahetin.kirjoita_cu8(polku, z, taysi=4 * np.std(z))
print(f"tallenne {polku}: {polku.stat().st_size} tavua, "
      f"{lahetin.FS_IQ / 1e3:.0f} kS/s")
# @loppu tallenne

# @alku vastaanota
aani, data, virhe_hz = va.vastaanota(va.lue_cu8(polku), lahetin.FS_IQ,
                                      200e3, lahetin.POIKKEAMA)
print(f"pilotti lukittu, taajuusvirhe {virhe_hz:+.2f} Hz")
for nimi, kanava, oma, toinen in (
        ("vasen", aani.vasen, lahetin.VASEN_HZ, lahetin.OIKEA_HZ),
        ("oikea", aani.oikea, lahetin.OIKEA_HZ, lahetin.VASEN_HZ)):
    a, sinad = va.sinad(kanava, va.FS_AANI, oma)
    vuoto, _ = va.sinad(kanava, va.FS_AANI, toinen)
    print(f"{nimi}: amplitudi {a:.3f}, SINAD {sinad:.0f} dB, "
          f"kanavaerotus {20 * np.log10(a / vuoto):.0f} dB")
print(f"RDS: PI {data.pi:04X}, asemanimi '{data.asemanimi}', "
      f"lohkoja {data.ehjat} ehjaa, {data.virheelliset} virheellista")
va.kirjoita_wav(Path("asema.wav"), aani)
print(f"asema.wav: {len(aani.vasen) / va.FS_AANI:.2f} s stereo 48 kHz")
# @loppu vastaanota
