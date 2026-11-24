"""Kaistan ja viiveen tulo: kuinka paljon dataa on matkalla."""

# @alku bdp
yhteydet = [
    ("kotiverkko", 1e9, 0.5e-3),
    ("Helsinki-Frankfurt", 1e9, 30e-3),
    ("Helsinki-Tokio", 1e9, 250e-3),
    ("GEO-satelliitti", 100e6, 600e-3),
]
IKKUNA = 64 * 1024        # TCP:n ikkuna ilman skaalausta (tavua)
for nimi, kaista, rtt in yhteydet:
    bdp_tavua = kaista * rtt / 8
    rajoitettu = min(kaista, IKKUNA * 8 / rtt)
    print(f"{nimi:<19} BDP {bdp_tavua / 1024:6.0f} KiB,"
          f" ikkunalla 64 KiB {rajoitettu / 1e6:6.1f} Mbit/s")
# @loppu bdp
