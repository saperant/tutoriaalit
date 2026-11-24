"""Zener-säätimen lähtö pysyy lähes vakiona syötön vaihdellessa."""

from spice import simuloi

# @alku zener
data = simuloi("06-zener.cir").data["zener"]
print("syöttö   lähtö    zener-virta")
for syotto, ulos, _, izener in data:
    print(f"{syotto:5.1f} V  {ulos:5.3f} V  {1e3 * izener:5.1f} mA")
muutos = 1e3 * (data[-1, 1] - data[0, 1])
print(f"lähtö muuttuu {muutos:.0f} mV, kun syöttö muuttuu 3 V")
# @loppu zener
