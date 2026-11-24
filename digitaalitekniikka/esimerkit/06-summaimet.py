"""Ripple-carry- ja carry-lookahead-summaimen viive porttisimulaattorilla.

Jokaisen portin viive on yksi aikayksikkö. Pahin tapaus: a = 11…1,
b = 0 ja b0 vaihtuu ykköseksi, jolloin muistibitti etenee koko
summaimen läpi.
"""

from porttisim import Piiri


# @alku taysisummain
def taysisummain(p: Piiri, a: str, b: str, c: str,
                 s: str, cout: str) -> None:
    p.portti("XOR", [a, b], f"x_{s}")
    p.portti("XOR", [f"x_{s}", c], s)
    p.portti("AND", [a, b], f"g_{s}")
    p.portti("AND", [f"x_{s}", c], f"t_{s}")
    p.portti("OR", [f"g_{s}", f"t_{s}"], cout)


def ripple_carry(p: Piiri, n: int) -> None:
    for i in range(n):
        taysisummain(p, f"a{i}", f"b{i}", f"c{i}", f"s{i}", f"c{i + 1}")
# @loppu taysisummain


# @alku cla
def cla_lohko(p: Piiri, k: int) -> None:
    """Neljän bitin lookahead-lohko bittien 4k…4k+3 yli. Lohkon
    sisäiset muistibitit lasketaan kaksitasoisella AND–OR-logiikalla
    suoraan lohkon tulomuistista: c(i+1) = g(i) + p(i)g(i-1) + …"""
    b0 = 4 * k
    for i in range(b0, b0 + 4):
        p.portti("AND", [f"a{i}", f"b{i}"], f"g{i}")
        p.portti("XOR", [f"a{i}", f"b{i}"], f"p{i}")
    for i in range(b0, b0 + 4):
        termit = []
        for j in range(b0 - 1, i + 1):        # j = b0-1 tarkoittaa c(b0)
            tekijat = [f"p{m}" for m in range(j + 1, i + 1)]
            alku = f"c{b0}" if j == b0 - 1 else f"g{j}"
            nimi = f"t{i}_{j}"
            if tekijat:
                p.portti("AND", [alku, *tekijat], nimi)
            else:
                p.portti("OR", [alku], nimi)  # pelkkä g(i): puskuri
            termit.append(nimi)
        p.portti("OR", termit, f"c{i + 1}")
        p.portti("XOR", [f"p{i}", f"c{i}"], f"s{i}")


def carry_lookahead(p: Piiri, n: int) -> None:
    for k in range(n // 4):
        cla_lohko(p, k)
# @loppu cla


# @alku mittaus
def asettumisaika(rakenna: str, n: int) -> int:
    p = Piiri()
    (ripple_carry if rakenna == "rca" else carry_lookahead)(p, n)
    for i in range(n):
        p.alusta(f"a{i}", 1)
    p.asetu()
    p.aseta("b0", 1, aika=0)                 # muistibitti lähtee liikkeelle
    p.aja(10_000)
    summa = sum(p.arvot[f"s{i}"] << i for i in range(n))
    summa += p.arvot[f"c{n}"] << n
    assert summa == (2**n - 1) + 1, "summa on väärä"
    return max(aika for aika, _, _ in p.muutokset)
# @loppu mittaus


def main() -> None:
    print("bittejä  ripple-carry  lookahead (4 bitin lohkot)")
    for n in (4, 8, 16, 32):
        rca = asettumisaika("rca", n)
        cla = asettumisaika("cla", n)
        print(f"{n:7}  {rca:12}  {cla:9}")


if __name__ == "__main__":
    main()
