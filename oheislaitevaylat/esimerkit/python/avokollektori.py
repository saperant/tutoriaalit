"""Avokollektoriväylä: johdotettu JA ja vetovastuksen mitoitus."""


# @alku ja
def vayla(*lahdot: int) -> int:
    """1 = lähtö vapauttaa linjan, 0 = vetää sen alas."""
    return min(lahdot)


print("A B -> vayla")
for a in (0, 1):
    for b in (0, 1):
        print(f"{a} {b} -> {vayla(a, b)}")
# @loppu ja

# @alku mitoitus
# I2C-määrittely (UM10204): nousuaika 30 % -> 70 % enintään tr, ja
# alataso enintään 0,4 V virralla IOL.
TILAT = [  # nimi, tr (ns), IOL (mA), suurin väylän kapasitanssi (pF)
    ("Standard 100 kHz", 1000, 3.0, 400),
    ("Fast 400 kHz", 300, 3.0, 400),
    ("Fast+ 1 MHz", 120, 20.0, 550),
]
VDD, VOL = 3.3, 0.4

print()
print(f"{'tila':18} {'Cb pF':>6} {'Rp min':>8} {'Rp max':>8}")
for nimi, tr, iol, cb_max in TILAT:
    rp_min = (VDD - VOL) / (iol / 1000)  # alataso ei saa nousta
    for cb in (50, 200, cb_max):
        # RC-nousu 30 %:sta 70 %:iin kestää ln(7/3) * R * C = 0,847 RC
        rp_max = tr * 1e-9 / (0.8473 * cb * 1e-12)
        huom = "" if rp_max >= rp_min else "  ei ratkaisua"
        print(f"{nimi:18} {cb:6} {rp_min:7.0f}R {rp_max:7.0f}R{huom}")
# @loppu mitoitus
