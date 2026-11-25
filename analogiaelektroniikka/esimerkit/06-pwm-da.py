"""PWM ja RC-suodin DA-muuntimena: rippelin ja asettumisajan kompromissi."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kompromissi
U, D, T, R, N = 3.3, 0.25, 50e-6, 10e3, 8      # 8-bittinen PWM, 20 kHz
lsb = U / 2**N


def rippeli(tau: float) -> float:
    """Huipusta huippuun, kun tau >> T: kondensaattoria ladataan ajan
    D*T virralla (1 - D) U / R."""
    return U * D * (1 - D) * T / tau


def asettuminen(tau: float) -> float:
    """Aika, jossa askelvaste on puolen LSB:n päässä loppuarvosta."""
    return tau * math.log(2 ** (N + 1))
# @loppu kompromissi


tulos = simuloi("06-pwm-da.cir").sarjat
for k, c in enumerate((100e-9, 1e-6)):
    tau = R * c
    print(f"C = {c * 1e9:.0f} nF, tau = {tau * 1e3:.0f} ms:")
    vertaa("keskiarvo", tulos["keski"][k], D * U, "V")
    vertaa("rippeli", tulos["ylin"][k] - tulos["alin"][k], rippeli(tau),
           "V", 0.03)
    print(f"  rippeli {rippeli(tau) / lsb:.2f} LSB, asettuminen "
          f"{asettuminen(tau) * 1e3:.0f} ms")
lopeta()
