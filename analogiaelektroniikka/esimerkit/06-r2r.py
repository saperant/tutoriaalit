"""R-2R-tikapuu-DA-muunnin: lineaarisuus ja vastusten epäsovitus.

Kaikki 16 koodia simuloidaan yhdellä ngspice-ajolla: netlistissä on
16 kopiota muuntimesta, joiden bittilähteet asettavat eri koodin.
"""

from spice import lopeta, simuloi, vertaa

# @alku netlist
N, U_ref, R = 4, 2.5, 10e3


def tikapuu(koodi: int, k: int, msb_virhe: float) -> list[str]:
    """Muunnin k: bitti i kytkee 2R-vastuksen U_ref:iin tai maahan.
    Ylimmän bitin 2R-vastus voi poiketa suhteellisesti msb_virhe."""
    rivit = []
    for i in range(N):
        u = U_ref if koodi >> i & 1 else 0.0
        r2 = 2 * R * (1 + msb_virhe) if i == N - 1 else 2 * R
        rivit += [f"Vb{k}_{i} b{k}_{i} 0 DC {u}",
                  f"R2_{k}_{i} b{k}_{i} n{k}_{i} {r2:.6g}"]
        if i < N - 1:
            rivit.append(f"R_{k}_{i} n{k}_{i} n{k}_{i + 1} {R:.6g}")
    rivit.append(f"Rt{k} n{k}_0 0 {2 * R:.6g}")   # päätevastus
    return rivit


def simuloi_muunnin(msb_virhe: float) -> list[float]:
    rivit = ["r-2r"]
    for koodi in range(2**N):
        rivit += tikapuu(koodi, koodi, msb_virhe)
    rivit += [".control", "op"]
    rivit += [f"print v(n{k}_{N - 1})" for k in range(2**N)]
    rivit += [".endc", ".end"]
    arvot = simuloi("\n".join(rivit) + "\n").arvot
    return [arvot[f"v(n{k}_{N - 1})"] for k in range(2**N)]
# @loppu netlist


# @alku vertailu
lsb = U_ref / 2**N
ihanne = simuloi_muunnin(0.0)
for koodi in (1, 7, 8, 15):
    vertaa(f"koodi {koodi}", ihanne[koodi], koodi * lsb, "V", 1e-6)

# DNL: kahden peräkkäisen koodin välin poikkeama yhdestä LSB:stä.
for virhe in (0.01, 0.05):
    u = simuloi_muunnin(virhe)
    dnl = [(u[k + 1] - u[k]) / lsb - 1 for k in range(2**N - 1)]
    pahin = max(range(len(dnl)), key=lambda k: abs(dnl[k]))
    print(f"MSB-vastus +{virhe * 100:.0f} %: pahin DNL {dnl[pahin]:+.3f} LSB "
          f"koodien {pahin} ja {pahin + 1} välissä")
# @loppu vertailu
lopeta()
