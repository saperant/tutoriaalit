"""Pikaoppaan laskurit: yleisimmät kaavat yhdessä paikassa."""

import math


# @alku kaavat
def db(suhde: float) -> float:              # tehosuhde -> dB
    return 10 * math.log10(suhde)


def fspl_db(d_m: float, f_hz: float) -> float:   # vapaan tilan vaimennus
    return 20 * math.log10(4 * math.pi * d_m * f_hz / 3e8)


def kohinataso_dbm(b_hz: float, nf_db: float) -> float:
    return -174 + 10 * math.log10(b_hz) + nf_db


def shannon(b_hz: float, snr_db: float) -> float:
    return b_hz * math.log2(1 + 10 ** (snr_db / 10))


def bdp_tavua(kaista_bit_s: float, rtt_s: float) -> float:
    return kaista_bit_s * rtt_s / 8


def mm1_aika(saapumis: float, palvelu: float) -> float:   # W = 1/(μ-λ)
    return 1 / (palvelu - saapumis)
# @loppu kaavat


print(f"2× teho          {db(2):6.2f} dB")
print(f"FSPL 100 m 5 GHz {fspl_db(100, 5e9):6.1f} dB")
print(f"kohina 20 MHz    {kohinataso_dbm(20e6, 7):6.1f} dBm")
print(f"Shannon 20 MHz   {shannon(20e6, 20) / 1e6:6.1f} Mbit/s @ 20 dB")
print(f"BDP 1 Gbit 30 ms {bdp_tavua(1e9, 0.03) / 1e6:6.2f} Mt")
print(f"M/M/1 ρ=0,9      {mm1_aika(0.9, 1.0):6.1f} palveluaikaa")
