"""Vahvistimen kohinabudjetti: tulon ekvivalenttinen kohina ja SNR."""

import math

# @alku budjetti
k_B, T = 1.380649e-23, 300.0
e_n, i_n = 10e-9, 1e-12        # vahvistimen kohina: V/sqrt(Hz), A/sqrt(Hz)
R_s = 10e3                     # lähteen (anturin) resistanssi
kaista = 20e3                  # mittauskaista, Hz
G = 100                        # vahvistus
osat = {
    "vahvistimen jännitekohina": e_n,
    "vahvistimen virtakohina R_s:ssä": i_n * R_s,
    "lähteen terminen kohina": math.sqrt(4 * k_B * T * R_s),
}
yhteensa = math.sqrt(sum(v**2 for v in osat.values()))
for nimi, v in osat.items():
    print(f"  {nimi:<32} {v * 1e9:6.2f} nV/sqrt(Hz)")
print(f"  {'yhteensä (neliösumma)':<32} {yhteensa * 1e9:6.2f} nV/sqrt(Hz)")
u_kohina = yhteensa * math.sqrt(kaista)
print(f"tulon kohina kaistalla {u_kohina * 1e6:.2f} uV rms, "
      f"lähdössä {G * u_kohina * 1e3:.3f} mV rms")
signaali = 1e-3                 # 1 mV rms anturisignaali
print(f"SNR {20 * math.log10(signaali / u_kohina):.1f} dB")
# @loppu budjetti
