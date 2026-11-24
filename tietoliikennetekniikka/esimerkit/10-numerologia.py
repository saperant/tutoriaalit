"""5G NR:n numerologia: alikantoaaltoväli, aikaväli ja resurssilohkot."""

# @alku numerologia
print(" µ   väli (kHz)  aikaväli (ms)  symboli (µs)  RB (kHz)")
for mu in range(5):
    vali_khz = 15 * 2 ** mu
    aikavali_ms = 1 / 2 ** mu          # 14 OFDM-symbolia
    symboli_us = 1000 / vali_khz       # ilman syklistä etuliitettä
    rb_khz = 12 * vali_khz             # resurssilohko = 12 alikantoa
    print(f"{mu:>2} {vali_khz:>12} {aikavali_ms:>14.4f}"
          f" {symboli_us:>13.2f} {rb_khz:>9}")
# @loppu numerologia

# @alku kaista
# Montako resurssilohkoa mahtuu kanavaan (TS 38.101-1, taulukko 5.3.2-1).
KAISTAT = {(15, 20): 106, (30, 20): 51, (30, 100): 273, (60, 100): 135}
for (vali, kaista), lohkoja in KAISTAT.items():
    kaytossa = lohkoja * 12 * vali / 1000
    print(f"{kaista:>3} MHz, {vali} kHz: {lohkoja:>3} RB ="
          f" {kaytossa:5.1f} MHz ({kaytossa / kaista:.0%} kaistasta)")
# @loppu kaista
