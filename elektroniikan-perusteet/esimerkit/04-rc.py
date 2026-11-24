"""RC-lataus: analyyttinen ratkaisu verrattuna SPICEn transienttiin."""

import math

from spice import lopeta, simuloi, vertaa

# @alku kasin
U, R, C = 5.0, 10e3, 100e-9
tau = R * C                       # aikavakio, 1 ms


def u_c(t: float) -> float:
    """Kondensaattorin jännite: u(t) = U (1 - e^(-t/tau))."""
    return U * (1 - math.exp(-t / tau))
# @loppu kasin


tulos = simuloi("04-rc.cir")
print("RC-lataus, tau = 1 ms:")
vertaa("t(63 %)", tulos.arvot["t63"], tau, "s")
vertaa("u(1 ms)", tulos.arvot["u1ms"], u_c(1e-3), "V")
vertaa("u(5 ms)", tulos.arvot["u5ms"], u_c(5e-3), "V")
# @alku energia
energia = 0.5 * C * U**2          # kondensaattoriin varastoituu 1/2 C U^2
print(f"  energia täysin ladattuna {1e6 * energia:.3f} uJ")
# @loppu energia
lopeta()
