"""Antialiasointisuodattimen kertaluku AD-muuntimen edessä."""

import math

# @alku vaatimus
N_bit, f_s, f_kaista = 12, 48e3, 4e3     # bitit, näytetaajuus, signaali
# Taajuudet, jotka laskostuvat kaistalle 0...f_kaista, alkavat
# kohdasta f_s - f_kaista. Niiden on vaimennuttava kvantisointikohinan
# tasolle: SNR = 6,02 N + 1,76 dB.
vaimennus = 6.02 * N_bit + 1.76
f_esto = f_s - f_kaista
print(f"vaadittu vaimennus {vaimennus:.1f} dB taajuudella "
      f"{f_esto / 1e3:.0f} kHz")
# @loppu vaatimus

# @alku kertaluku
# Butterworth-alipäästön vaimennus rajataajuuden fc yläpuolella on
# 10 log10(1 + (f/fc)^(2n)) dB eli asymptoottisesti 20 n dB/dekadi.
f_c = f_kaista
for n in range(1, 7):
    a = 10 * math.log10(1 + (f_esto / f_c) ** (2 * n))
    riittaa = "  riittää" if a >= vaimennus else ""
    print(f"  n = {n}: {a:5.1f} dB{riittaa}")
# Ylinäytteistys siirtää rajaa: 4-kertaisella näytetaajuudella
# 192 kHz estokaista alkaa 188 kHz:stä.
n_yli = math.ceil(vaimennus / (20 * math.log10((4 * f_s - f_kaista) / f_c)))
print(f"4-kertaisella ylinäytteistyksellä riittää n = {n_yli}")
# @loppu kertaluku
