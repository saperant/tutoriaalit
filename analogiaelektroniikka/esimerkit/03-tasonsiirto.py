"""Tasonsiirto: kaksisuuntainen anturisignaali yksipuoliselle ADC:lle."""

from spice import lopeta, simuloi, vertaa

# @alku mitoitus
U_kesk, G = 1.65, 1.5                 # ADC:n alueen keskikohta, vahvistus
# Plus-tulon jännite on tulon ja referenssin keskiarvo (R1 = R2), joten
# u_ulos = (u_in + U_ref) / 2 * k, missä k = 1 + R4/R3.
# Vahvistus G = k/2 ja keskikohta U_ref * k/2 = U_kesk.
k = 2 * G
R3 = 10e3
R4 = R3 * (k - 1)
U_ref = 2 * U_kesk / k
print(f"R4 = {R4 / 1e3:.0f} kohm, U_ref = {U_ref:.2f} V, "
      f"alue {U_kesk - G:.2f} ... {U_kesk + G:.2f} V")
# @loppu mitoitus

for u_in, u_sim in zip((-1.0, 0.0, 1.0), simuloi("03-tasonsiirto.cir")
                       .sarjat["v(out)"], strict=True):
    vertaa(f"u_in = {u_in:+.0f} V", u_sim, (u_in + U_ref) / 2 * k, "V",
           0.002)
lopeta()
