"""Linkkibudjetti: riittääkö signaali vastaanottimelle?"""

import math

TERMINEN_KOHINA_DBM_HZ = -174.0     # kT huoneenlämmössä


def kohinataso_dbm(kaista_hz: float, kohinaluku_db: float) -> float:
    return TERMINEN_KOHINA_DBM_HZ + 10 * math.log10(kaista_hz) \
        + kohinaluku_db


def fspl_db(etaisyys_m: float, taajuus_hz: float) -> float:
    return 20 * math.log10(4 * math.pi * etaisyys_m * taajuus_hz / 3e8)


# @alku budjetti
def snr_db(teho_dbm: float, antennit_dbi: float, etaisyys_m: float,
           taajuus_hz: float, muut_hukat_db: float, kaista_hz: float,
           kohinaluku_db: float) -> float:
    vastaanotettu = (teho_dbm + antennit_dbi
                     - fspl_db(etaisyys_m, taajuus_hz) - muut_hukat_db)
    return vastaanotettu - kohinataso_dbm(kaista_hz, kohinaluku_db)


# Wi-Fi: 20 dBm, antennit yht. 4 dBi, seinät 15 dB, 20 MHz, NF 7 dB.
# LoRa: 14 dBm, antennit 4 dBi, seinät 15 dB, 125 kHz, NF 6 dB.
for nimi, teho, kaista, nf, vaadittu in [
        ("Wi-Fi", 20.0, 20e6, 7.0, 25.0),     # 64-QAM tarvitsee ~25 dB
        ("LoRa SF12", 14.0, 125e3, 6.0, -20.0)]:
    for d in (50, 500, 5000, 50000):
        s = snr_db(teho, 4.0, d, 868e6 if "LoRa" in nimi else 2.4e9,
                   15.0, kaista, nf)
        tila = "ok" if s >= vaadittu else "ei"
        print(f"{nimi:<9} {d:>6} m: SNR {s:6.1f} dB"
              f" (vaadittu {vaadittu:5.1f}) {tila}")
# @loppu budjetti
