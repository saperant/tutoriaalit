"""Staattinen 1-hasardi kahden syötteen multiplekserissä ja sen korjaus.

y = a·s' + b·s. Kun a = b = 1, lähdön pitäisi pysyä ykkösenä s:n
vaihtuessa. Invertterin viiveen takia molemmat tulotermit ovat hetken
nollia, ja lähtöön syntyy piikki.
"""

from porttisim import Piiri


# @alku mux
def multiplekseri(korjattu: bool) -> Piiri:
    p = Piiri()
    p.portti("NOT", ["s"], "s_n", viive=2)
    p.portti("AND", ["a", "s_n"], "t0")
    p.portti("AND", ["b", "s"], "t1")
    if korjattu:
        p.portti("AND", ["a", "b"], "t2")     # konsensustermi ab
        p.portti("OR", ["t0", "t1", "t2"], "y")
    else:
        p.portti("OR", ["t0", "t1"], "y")
    return p
# @loppu mux


def main() -> None:
    for korjattu in (False, True):
        # @alku koe
        p = multiplekseri(korjattu)
        for syote in ("a", "b", "s"):
            p.alusta(syote, 1)
        p.asetu()
        p.aseta("s", 0, aika=3)               # valinta vaihtuu
        p.aja(12)
        # @loppu koe
        otsikko = "konsensustermin kanssa" if korjattu else "alkuperäinen"
        print(f"{otsikko}:")
        print(p.aaltomuoto(["s", "s_n", "t0", "t1", "y"], 12))
        print()


if __name__ == "__main__":
    main()
