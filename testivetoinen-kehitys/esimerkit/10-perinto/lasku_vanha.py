"""Laskun tulostus sellaisena kuin se löytyi: toimii, mutta kukaan ei
uskalla koskea siihen."""


# @alku vanha
def lasku(nimi: str, t: int, rivit: list[tuple[str, int, int]],
          k: str) -> str:
    s = "LASKU " + nimi + "\n"
    y = 0
    for r in rivit:
        h = r[1] * r[2]
        if r[2] >= 10:
            h = h - h // 10
        y = y + h
        s = s + r[0] + " x" + str(r[2]) + "  " + str(h // 100) + "," \
            + ("0" + str(h % 100))[-2:] + "\n"
    a = 0
    if t == 2:
        a = 5
        if y > 10000:
            a = 10
    if k == "KESA":
        if a < 10:
            a = 10
        else:
            a = 15
    elif k != "":
        s = s + "Tuntematon koodi " + k + "\n"
    if a > 0:
        al = y * a // 100
        s = s + "Alennus " + str(a) + " %  -" + str(al // 100) + "," \
            + ("0" + str(al % 100))[-2:] + "\n"
        y = y - al
    tm = 590
    if y >= 5000:
        tm = 0
    if t == 2 and y >= 3000:
        tm = 0
    if len(rivit) == 0:
        tm = 0
    s = s + "Toimitus  " + str(tm // 100) + "," \
        + ("0" + str(tm % 100))[-2:] + "\n"
    y = y + tm
    s = s + "YHTEENSÄ  " + str(y // 100) + "," \
        + ("0" + str(y % 100))[-2:] + "\n"
    return s
# @loppu vanha
