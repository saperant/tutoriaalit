"""NumPyn perusteet mittausdatan käsittelyyn: taulukot, tietotyypit,
vektorointi, broadcast ja maskit."""

import numpy as np

# @alku tyypit
# Taulukolla on yksi tietotyyppi ja kiinteä muoto.
raaka = np.array([[100, -200, 32000], [5, 6, 7]], dtype=np.int16)
print(raaka.shape, raaka.dtype, raaka.nbytes, "tavua")
# int16 kiertää ylivuodossa hiljaa, kuten C. Muunna ennen laskentaa.
print("int16:", raaka[0] + np.int16(1000))
print("int32:", raaka[0].astype(np.int32) + 1000)
print("float32 vs float64:", np.float32(0.1) + np.float32(0.2),
      0.1 + 0.2)
# @loppu tyypit

# @alku vektorointi
# AD-muuntimen raakalukemat (12 bittiä) jännitteiksi: kerroin ja
# siirtymä kanavittain. Ei silmukkaa: operaatio koskee koko taulukkoa.
lukemat = np.array([[0, 2048, 4095],
                    [100, 2100, 4000],
                    [50, 1990, 4090]], dtype=np.uint16)
kerroin = np.array([3.3 / 4095, 3.3 / 4095, 5.0 / 4095])   # (3,)
siirtyma = np.array([[0.0], [0.01], [-0.02]])               # (3, 1)
# Broadcast: (3, 3) * (3,) kertoo sarakkeittain, + (3, 1) riveittäin.
jannite = lukemat * kerroin + siirtyma
print(np.round(jannite, 3))
# @loppu vektorointi

# @alku maskit
naytteet = np.array([0.1, 0.4, 2.9, 3.1, 0.2, 3.3, 3.2, 0.0])
yli = naytteet > 3.0                     # totuusarvotaulukko
print("ylitykset:", np.flatnonzero(yli), "osuus", yli.mean())
# Nouseva reuna: edellinen alle, nykyinen yli.
reunat = np.flatnonzero(~yli[:-1] & yli[1:]) + 1
print("nousevat reunat:", reunat)
leikattu = np.clip(naytteet, 0.0, 3.0)
print("leikattu:", leikattu)
# @loppu maskit

# @alku nakymat
a = np.arange(10)
nakyma = a[2:5]          # viipale on näkymä samaan muistiin
kopio = a[[2, 3, 4]]     # indeksilista tekee kopion
nakyma[0] = -1
kopio[1] = -1
print(a, np.shares_memory(a, nakyma), np.shares_memory(a, kopio))
# @loppu nakymat
