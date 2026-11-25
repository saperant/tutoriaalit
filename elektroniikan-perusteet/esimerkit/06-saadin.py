"""Lineaarisäädin ja zener-säädin: lähtöjännite, häviö ja hyötysuhde."""

from spice import lopeta, simuloi, vertaa

tulos = simuloi("06-saadin.cir")
# @alku haviot
U_IN, U_OUT, I_Q = 12.0, 5.0, 50e-6


def havio_lin(i_kuorma: float) -> float:
    """Lineaarisäätimen häviö: jännite-ero kertaa kuormavirta ja lepovirta."""
    return (U_IN - U_OUT) * i_kuorma + U_IN * I_Q
# @loppu haviot


# @alku vertailu
print("kuorma   lineaarisäädin               zener-säädin")
print("         lähtö    häviö  hyötys.      lähtö    häviö  hyötys.")
for lin, zen in zip(tulos.data["lin"], tulos.data["zen"], strict=True):
    rivi = f"{1e3 * lin[0]:3.0f} mA "
    for virta, ulos, otto in ((lin[0], lin[1], -lin[3]),
                              (zen[0], zen[1], -zen[3])):
        p_sisaan, p_kuorma = U_IN * otto, max(ulos, 0.0) * virta
        rivi += (f" {ulos:6.2f} V {1e3 * (p_sisaan - p_kuorma):5.0f} mW "
                 f"{100 * p_kuorma / p_sisaan:4.0f} %    ")
    print(rivi.rstrip())
# @loppu vertailu

lin20 = tulos.data["lin"][2]
vertaa("häviö 20 mA", U_IN * -lin20[3] - lin20[1] * lin20[0],
       havio_lin(20e-3), "W")
# @alku pudotus
print("lineaarisäätimen lähtö, kun syöttö laskee:")
print("  " + "  ".join(f"{u_in:.2f} V -> {u_out:.2f} V"
                       for u_in, u_out in tulos.data["pudotus"][::2]))
# @loppu pudotus
lopeta()
