"""Peräkkäisapproksimaatiomuunnin (SAR): binäärihaku vertailijalla."""

# @alku sar
U_ref, N, U_in = 3.3, 8, 1.234


def sar(u_in: float) -> int:
    """Kokeilee bitit ylimmästä alkaen: bitti jää päälle, jos DA-muuntimen
    jännite ei ylitä tuloa. N vertailua, yksi kellojakso kutakin kohden."""
    koodi = 0
    for bitti in reversed(range(N)):
        koe = koodi | (1 << bitti)
        u_da = U_ref * koe / 2**N
        pidetaan = u_da <= u_in
        print(f"  bitti {bitti}: koe {koe:08b} = {u_da:.4f} V -> "
              f"{'1' if pidetaan else '0'}")
        if pidetaan:
            koodi = koe
    return koodi


koodi = sar(U_in)
lsb = U_ref / 2**N
print(f"koodi {koodi} = {koodi:08b}, LSB {lsb * 1e3:.2f} mV, "
      f"kvantisointivirhe {(U_in - koodi * lsb) * 1e3:.2f} mV")
assert koodi == int(U_in / lsb)   # sama kuin pyöristys alaspäin
# @loppu sar
