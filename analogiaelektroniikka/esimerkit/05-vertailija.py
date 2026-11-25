"""Vertailija ja hystereesi: kynnykset ja kohisevan tulon vaihtojen määrä."""

import numpy as np

from spice import HAKEMISTO, lopeta, simuloi, vertaa

# @alku kynnykset
U_CC, U_REF, R1, R2 = 3.3, 1.65, 10e3, 100e3


def kynnys(u_ulos: float) -> float:
    """Plus-tulon jännite: referenssin ja lähdön painotettu keskiarvo."""
    return (U_REF * R2 + u_ulos * R1) / (R1 + R2)


ylempi, alempi = kynnys(U_CC), kynnys(0.0)
# @loppu kynnykset

piiri = (HAKEMISTO / "05-vertailija.cir").read_text("utf-8")
tulos = simuloi(piiri).arvot
vertaa("ylempi kynnys", tulos["ylempi"], ylempi, "V")
vertaa("alempi kynnys", tulos["alempi"], alempi, "V")
print(f"  hystereesi {1e3 * (ylempi - alempi):.0f} mV")

# @alku kohina
# Hitaasti nouseva tulo, jonka päällä on kohinaa +-60 mV. Arvo vaihtuu
# 20 us:n välein (kiinteä siemen: tulos on toistettava).
rng = np.random.default_rng(2026)
t = np.arange(500) * 20e-6
u = 1.2 + 0.9 * t / t[-1] + rng.uniform(-0.06, 0.06, t.size)
pwl = " ".join(f"{a:.6e} {b:.4f} {a + 19e-6:.6e} {b:.4f}"
               for a, b in zip(t, u, strict=True))


def vaihdot(r2: str) -> int:
    """Lähdön tilanvaihtojen määrä, kun takaisinkytkentävastus on r2."""
    netlist = (piiri.replace(".param R2=100k", f".param R2={r2}")
               .replace("PULSE(0 3.3 0 10m 10m 1u 20m)", f"PWL({pwl})")
               .replace("tran 2u 20m", "tran 1u 10m"))
    # Kynnysten mittaukset kuuluvat vain kolmioaaltoajoon.
    netlist = "\n".join(rivi for rivi in netlist.splitlines()
                        if not rivi.startswith("meas")) + "\n"
    ulos = simuloi(netlist).data["vertailija"][:, 3]
    return int(np.count_nonzero(np.diff(ulos > U_CC / 2)))


# Ilman hystereesiä lähtö vaihtuu aina, kun tulo ylittää referenssin:
ylitykset = int(np.count_nonzero(np.diff(u > U_REF)))
print(f"tulo ylittää referenssin {ylitykset} kertaa")
print(f"ilman hystereesiä (R2 = 1 Gohm): {vaihdot('1G')} tilanvaihtoa")
print(f"hystereesin kanssa (R2 = 100 kohm): {vaihdot('100k')} tilanvaihto")
# @loppu kohina
lopeta()
