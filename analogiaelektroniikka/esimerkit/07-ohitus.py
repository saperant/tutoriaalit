"""Ohituskondensaattori: syötön notkahdus virtapiikissä."""

from spice import lopeta, simuloi, vertaa

# @alku kasin
U, L, R, I_p, t_r, t_p = 3.3, 20e-9, 0.1, 0.1, 2e-9, 20e-9
L_esl, C = 1e-9, 100e-9
# Ilman ohitusta virran nousu kulkee johtimen induktanssin kautta:
# notkahdus on L di/dt (nousun aikana) plus resistiivinen häviö.
ilman = L * I_p / t_r + R * I_p
# Ohituskondensaattori antaa virran. Nousun aikana notkahdus on sen oma
# ESL di/dt, ja pulssin aikana varaus vähenee I t_p / C. Ne eivät osu
# samaan hetkeen, joten pahin notkahdus on suurempi niistä.
kanssa = max(L_esl * I_p / t_r, I_p * t_p / C)
print(f"ilman ohitusta noin {ilman:.2f} V, ohituksella noin "
      f"{kanssa * 1e3:.0f} mV")
# @loppu kasin

tulos = simuloi("07-ohitus.cir").arvot
vertaa("ilman", U - tulos["ilman"], ilman, "V", 0.1)
vertaa("ohituksella", U - tulos["kanssa"], kanssa, "V", 0.25)
lopeta()
