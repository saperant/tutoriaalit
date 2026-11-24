"""Pieni DPLL-ratkaisija ja graafin väritys SAT-ongelmana.

Kaava on konjunktiivisessa normaalimuodossa: lista lausekkeita, joista
jokainen on lista literaaleja. Literaali on nollasta poikkeava
kokonaisluku: 3 tarkoittaa muuttujaa x3 ja -3 sen negaatiota (sama
esitys kuin DIMACS-tiedostomuodossa).
"""

Lauseke = list[int]
Kaava = list[Lauseke]


# @alku dpll
def sievenna(kaava: Kaava, literaali: int) -> Kaava | None:
    """Asettaa literaalin todeksi. None, jos lauseke tyhjenee."""
    tulos: Kaava = []
    for lauseke in kaava:
        if literaali in lauseke:
            continue                      # lauseke toteutui
        uusi = [x for x in lauseke if x != -literaali]
        if not uusi:
            return None                   # ristiriita
        tulos.append(uusi)
    return tulos


def dpll(kaava: Kaava, malli: dict[int, bool],
         askeleet: list[int]) -> dict[int, bool] | None:
    askeleet[0] += 1
    # Yksikköpropagointi: yhden literaalin lauseke pakottaa arvon.
    while yksiko := next((k for k in kaava if len(k) == 1), None):
        x = yksiko[0]
        malli[abs(x)] = x > 0
        sievennetty = sievenna(kaava, x)
        if sievennetty is None:
            return None
        kaava = sievennetty
    if not kaava:
        return malli                      # kaikki lausekkeet toteutuivat
    x = kaava[0][0]                       # haarautuminen
    for valinta in (x, -x):
        sievennetty = sievenna(kaava, valinta)
        if sievennetty is not None:
            tulos = dpll(sievennetty, malli | {abs(x): valinta > 0},
                         askeleet)
            if tulos is not None:
                return tulos
    return None
# @loppu dpll


# @alku varitys
def varitys_cnf(solmut: list[str], kaaret: list[tuple[str, str]],
                vareja: int) -> Kaava:
    """Muuttuja (solmu i, väri c) on numero i·värit + c + 1."""
    def muuttuja(s: str, c: int) -> int:
        return solmut.index(s) * vareja + c + 1

    kaava: Kaava = []
    for s in solmut:
        # Vähintään yksi väri ja enintään yksi väri.
        kaava.append([muuttuja(s, c) for c in range(vareja)])
        for c in range(vareja):
            for d in range(c + 1, vareja):
                kaava.append([-muuttuja(s, c), -muuttuja(s, d)])
    for a, b in kaaret:                   # naapureilla eri värit
        for c in range(vareja):
            kaava.append([-muuttuja(a, c), -muuttuja(b, c)])
    return kaava


# Tentit, joilla on yhteisiä opiskelijoita, eivät voi olla samaan aikaan.
tentit = ["matikka", "fysiikka", "ohjelmointi", "kemia", "tilastot"]
ristiriidat = [("matikka", "fysiikka"), ("matikka", "ohjelmointi"),
               ("fysiikka", "ohjelmointi"), ("fysiikka", "kemia"),
               ("ohjelmointi", "tilastot"), ("kemia", "tilastot")]
for vareja in (2, 3):
    kaava = varitys_cnf(tentit, ristiriidat, vareja)
    askeleet = [0]
    malli = dpll(kaava, {}, askeleet)
    print(f"{vareja} aikaväliä: {len(kaava)} lauseketta, "
          f"{askeleet[0]} kutsua -> ", end="")
    if malli is None:
        print("ei ratkaisua")
        continue
    print("ratkaisu")
    for i, tentti in enumerate(tentit):
        vari = next(c for c in range(vareja)
                    if malli.get(i * vareja + c + 1))
        print(f"  {tentti:<12} aikaväli {vari + 1}")
# @loppu varitys
