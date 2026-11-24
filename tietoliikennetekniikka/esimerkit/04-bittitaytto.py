"""Kehystys bittitäytöllä (HDLC): lippu 01111110 ei esiinny datassa."""

LIPPU = "01111110"


# @alku taytto
def tayta(bitit: str) -> str:
    """Viiden ykkösen jälkeen lisätään nolla."""
    tulos, ykkosia = [], 0
    for b in bitit:
        tulos.append(b)
        ykkosia = ykkosia + 1 if b == "1" else 0
        if ykkosia == 5:
            tulos.append("0")
            ykkosia = 0
    return "".join(tulos)


def pura(bitit: str) -> str:
    """Viiden ykkösen jälkeinen nolla poistetaan."""
    tulos, ykkosia, ohita = [], 0, False
    for b in bitit:
        if ohita:
            ohita = False
            ykkosia = 0
            continue
        tulos.append(b)
        ykkosia = ykkosia + 1 if b == "1" else 0
        if ykkosia == 5:
            ohita = True
    return "".join(tulos)


def kehys(data: str) -> str:
    return LIPPU + tayta(data) + LIPPU


def kehyksen_data(linja: str) -> str:
    alku = linja.index(LIPPU) + len(LIPPU)
    loppu = linja.index(LIPPU, alku)
    return pura(linja[alku:loppu])
# @loppu taytto


data = "0111111101111110111110"
linja = kehys(data)
print("data    ", data)
print("linjalla", linja)
print("lisättyjä nollia", len(linja) - len(data) - 2 * len(LIPPU))
print("purettu oikein:", kehyksen_data(linja) == data)
