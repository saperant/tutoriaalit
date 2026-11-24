"""Vastaanottimen herkkyys ja laitteiden tiedonsiirtotarve."""

import math

# @alku herkkyys
# Herkkyys = kohinalattia kTB + kohinaluku + vaadittu SNR.
# -174 dBm/Hz on kT huoneenlammossa (290 K).
KT_DBM_HZ = -174.0
tapaukset = [
    # nimi, kaista Hz, vaadittu SNR dB
    ("FM-yleisradio mono", 200e3, 12.0),      # kynnyksen ylapuolella
    ("GFSK 38 kbit/s", 38e3, 12.0),           # kaista = R: SNR = Eb/N0
    ("kapea FM, puhe", 12.5e3, 12.0),
    ("kantoaallon havainto", 100.0, 6.0),
]
for kohinaluku in (3.0, 8.0):
    print(f"kohinaluku {kohinaluku:.0f} dB:")
    for nimi, kaista, snr in tapaukset:
        herkkyys = KT_DBM_HZ + 10 * math.log10(kaista) + kohinaluku + snr
        print(f"  {nimi:22} {kaista / 1e3:7.1f} kHz {herkkyys:6.0f} dBm")
# @loppu herkkyys

# @alku vayla
# Naytevirta tietokoneelle: naytetaajuus x tavua/IQ-nayte.
laitteet = [
    ("RTL-SDR", 2.4e6, 2),                    # 8 bit I + 8 bit Q
    ("HackRF One", 20e6, 2),
    ("PlutoSDR", 61.44e6, 4),                 # 12 bit 16 bitin sanoissa
]
USB2_MB_S = 45.0                     # USB 2.0: 60 MB/s, kaytannossa ~45
for nimi, fs, tavua in laitteet:
    mbs = fs * tavua / 1e6
    tila = "mahtuu" if mbs <= USB2_MB_S else "ei mahdu"
    print(f"{nimi:11} {fs / 1e6:6.2f} MS/s: {mbs:6.1f} MB/s, USB 2.0:aan "
          f"{tila}")
# @loppu vayla
