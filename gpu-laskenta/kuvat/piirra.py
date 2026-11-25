"""Piirtää algoritmien periaatekuvat ja roofline-kuvaajan.
Käyttö: make kuvat

Algoritmikuvat lasketaan tässä pienille syötteille (8–16 alkiota)
samoilla indeksisäännöillä kuin lukujen varjostimissa; funktioiden
kommentit kertovat, mitä varjostinta kukin vastaa. Roofline-kuvaajan
luvut luetaan luvun 10 mittaustaulukosta. Kuvat ovat versionhallinnassa,
joten skriptiä ei ajeta testeissä.
"""

from pathlib import Path

import numpy as np
from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Rectangle

KOROSTUS = "#4552B0"
TOINEN = "#C0652A"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
TAUSTA = "#E4E6F4"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
JUURI = Path(__file__).resolve().parent.parent


def uusi(leveys: float, korkeus: float) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def tallenna(fig: Figure, nimi: str) -> None:
    fig.savefig(JUURI / "kuvat" / nimi, metadata=METATIEDOT)


def solu(ax, x, y, teksti, vari="white", reuna=HARMAA, koko=8, w=0.9,
         h=0.6, tekstivari="black") -> None:
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, facecolor=vari,
                           edgecolor=reuna, linewidth=0.7))
    ax.text(x, y, str(teksti), ha="center", va="center", fontsize=koko,
            color=tekstivari)


def nuoli(ax, a, b, vari=HARMAA, leveys=0.7, kaari=0.0) -> None:
    ax.add_patch(FancyArrowPatch(
        a, b, arrowstyle="-|>", mutation_scale=6, color=vari,
        linewidth=leveys, shrinkA=0, shrinkB=0,
        connectionstyle=f"arc3,rad={kaari}"))


def rivi(ax, y, arvot, varit=None, nimi=None, **kw) -> None:
    for i, v in enumerate(arvot):
        solu(ax, i, y, v, vari=(varit[i] if varit else "white"), **kw)
    if nimi:
        ax.text(-0.75, y, nimi, ha="right", va="center", fontsize=7,
                color=HARMAA)


def tyoryhmat() -> None:
    """Ajo, työryhmät ja säikeet: 20 alkiota, työryhmän koko 8.
    Globaali indeksi = työryhmän numero * koko + paikallinen indeksi;
    viimeisen ryhmän ylimääräiset säikeet ohittavat työn (i >= n)."""
    n, koko, ryhmia = 20, 8, 3
    fig = uusi(5.6, 1.7)
    ax = fig.add_subplot()
    for r in range(ryhmia):
        x0 = r * (koko + 0.6)
        ax.add_patch(Rectangle((x0 - 0.55, -0.55), koko + 0.1, 1.75,
                               fill=False, edgecolor=KOROSTUS,
                               linewidth=1.1))
        ax.text(x0 + koko / 2 - 0.5, 1.45, f"gl_WorkGroupID = {r}",
                ha="center", fontsize=7, color=KOROSTUS)
        for s in range(koko):
            i = r * koko + s
            mukana = i < n
            solu(ax, x0 + s, 0.55, s, koko=6, vari="white",
                 reuna=VAALEA, h=0.5)
            solu(ax, x0 + s, 0, i, koko=6,
                 vari=TAUSTA if mukana else "#EEEEEE",
                 tekstivari="black" if mukana else VAALEA, h=0.5)
    ax.text(-0.9, 0.55, "paikallinen", ha="right", va="center", fontsize=7,
            color=HARMAA)
    ax.text(-0.9, 0, "globaali", ha="right", va="center", fontsize=7,
            color=HARMAA)
    x_loppu = 2 * (koko + 0.6) + 5.5
    ax.annotate("indeksi ≥ n:\nsäie ei tee mitään", (x_loppu, -0.3),
                (x_loppu - 2.5, -1.25), fontsize=7, color=TOINEN,
                ha="center",
                arrowprops={"arrowstyle": "-|>", "color": TOINEN,
                            "linewidth": 0.7})
    ax.text(4, -1.2, f"data: n = {n} alkiota, työryhmän koko {koko}, "
            f"ryhmiä ⌈{n}/{koko}⌉ = {ryhmia}", fontsize=7, ha="center")
    ax.set(xlim=(-3.2, ryhmia * (koko + 0.6)), ylim=(-1.5, 1.8))
    ax.axis("off")
    tallenna(fig, "02-tyoryhmat.png")


def aliryhmat() -> None:
    """Sama 32 säikeen työryhmä jaettuna aliryhmiin eri leveyksillä."""
    fig = uusi(5.2, 1.5)
    ax = fig.add_subplot()
    for j, leveys in enumerate((4, 8, 16)):
        y = -j
        for s in range(32):
            ryhma = s // leveys
            ax.add_patch(Rectangle((s, y - 0.3), 1, 0.6,
                                   facecolor=TAUSTA if ryhma % 2 == 0
                                   else "#F4E6DA",
                                   edgecolor="white", linewidth=0.4))
        for r in range(32 // leveys):
            ax.text(r * leveys + leveys / 2, y, str(r), ha="center",
                    va="center", fontsize=6)
        ax.text(-0.5, y, f"leveys {leveys}", ha="right", va="center",
                fontsize=7, color=HARMAA)
    ax.text(16, 0.75, "työryhmän 32 säiettä (gl_LocalInvocationIndex "
            "0–31); numero on gl_SubgroupID", ha="center", fontsize=7)
    ax.set(xlim=(-5, 32.5), ylim=(-2.6, 1.1))
    ax.axis("off")
    tallenna(fig, "03-aliryhmat.png")


def reduktiopuu() -> None:
    """Puu jaetussa muistissa kuten varjostimessa reduktio_jaettu.comp:
    8 säiettä lataa 16 alkiota (säie i alkiot i ja i + 8), ja tasolla
    'askel' säikeet oma < askel lisäävät alkion oma + askel."""
    x = [3, 1, 7, 0, 4, 1, 6, 3, 2, 5, 1, 2, 0, 3, 1, 4]
    s = [x[i] + x[i + 8] for i in range(8)]
    tasot = [("lataus: x[i] + x[i + 8]", list(s), 8)]
    askel = 4
    while askel > 0:
        for i in range(askel):
            s[i] += s[i + askel]
        tasot.append((f"askel {askel}", list(s), askel))
        askel //= 2
    fig = uusi(4.8, 2.5)
    ax = fig.add_subplot()
    for t, (nimi, arvot, aktiivisia) in enumerate(tasot):
        y = -1.25 * t
        edellinen = tasot[t - 1][2] if t else 8
        for i in range(8):
            elossa = i < (aktiivisia if t else 8)
            kaytossa = i < edellinen
            solu(ax, i, y, arvot[i] if kaytossa else "",
                 vari=TAUSTA if elossa else "white",
                 reuna=HARMAA if kaytossa else VAALEA)
        ax.text(-0.75, y, nimi, ha="right", va="center", fontsize=7,
                color=HARMAA)
        if t:
            for i in range(aktiivisia):
                nuoli(ax, (i + aktiivisia, y + 0.92), (i + 0.12, y + 0.32),
                      KOROSTUS, kaari=0.12)
            ax.plot([-0.5, 7.5], [y + 0.62, y + 0.62], color=TOINEN,
                    linewidth=0.7, linestyle="--")
    ax.text(7.7, -0.62, "barrier()", color=TOINEN, fontsize=7, va="center")
    for i in range(8):
        ax.text(i, 0.55, f"säie {i}", ha="center", fontsize=6, color=HARMAA)
    ax.text(0, -1.25 * 3 - 0.65, f"summa {tasot[-1][1][0]}", ha="center",
            fontsize=7, color=KOROSTUS)
    ax.set(xlim=(-4.6, 9.3), ylim=(-4.8, 0.9))
    ax.axis("off")
    tallenna(fig, "04-reduktiopuu.png")


def skannaus() -> None:
    """Hillis–Steele (skannaus_hs.comp) ja Blelloch
    (skannaus_lohko.comp) kahdeksalle alkiolle."""
    syote = [3, 1, 7, 0, 4, 1, 6, 3]
    n = len(syote)
    fig = uusi(5.8, 4.0)
    # --- Hillis–Steele: kattava skannaus, log2(n) kierrosta
    ax = fig.add_subplot(1, 2, 1)
    t = list(syote)
    rivi(ax, 0, t, nimi="syöte")
    d, y = 1, 0.0
    while d < n:
        uusi_t = [t[i] + (t[i - d] if i >= d else 0) for i in range(n)]
        y -= 1.3
        for i in range(d, n):
            nuoli(ax, (i - d + 0.1, y + 0.98), (i - 0.1, y + 0.32), KOROSTUS,
                  0.5)
        rivi(ax, y, uusi_t, varit=[TAUSTA if i >= d else "white"
                                   for i in range(n)], nimi=f"d = {d}")
        t = uusi_t
        d *= 2
    ax.text(3.5, 0.75, "Hillis–Steele (kattava)", ha="center", fontsize=8)
    ax.text(3.5, y - 0.75, "3 kierrosta, 7 + 6 + 4 = 17 yhteenlaskua",
            ha="center", fontsize=7, color=HARMAA)
    ax.set(xlim=(-2.2, 7.7), ylim=(-10.4, 1.1))
    ax.axis("off")
    # --- Blelloch: poissulkeva skannaus, ylös- ja alasvaihe
    ax = fig.add_subplot(1, 2, 2)
    t = list(syote)
    rivi(ax, 0, t, nimi="syöte")
    y, vali, laskuja = 0.0, 1, 0
    aktiivisia = n // 2
    while aktiivisia > 0:   # ylösvaihe
        y -= 1.3
        muuttuneet = set()
        for oma in range(aktiivisia):
            vasen = vali * (2 * oma + 1) - 1
            oikea = vali * (2 * oma + 2) - 1
            t[oikea] += t[vasen]
            laskuja += 1
            muuttuneet.add(oikea)
            nuoli(ax, (vasen + 0.1, y + 0.98), (oikea - 0.1, y + 0.32),
                  KOROSTUS, 0.5)
        rivi(ax, y, t, varit=[TAUSTA if i in muuttuneet else "white"
                              for i in range(n)],
             nimi="ylös" if aktiivisia == n // 2 else None)
        vali *= 2
        aktiivisia //= 2
    y -= 1.0
    t[n - 1] = 0
    rivi(ax, y, t, varit=["#F4E6DA" if i == n - 1 else "white"
                          for i in range(n)], nimi="juuri = 0")
    aktiivisia = 1
    while aktiivisia < n:   # alasvaihe
        vali //= 2
        y -= 1.3
        muuttuneet = set()
        for oma in range(aktiivisia):
            vasen = vali * (2 * oma + 1) - 1
            oikea = vali * (2 * oma + 2) - 1
            v = t[vasen]
            t[vasen] = t[oikea]
            t[oikea] += v
            laskuja += 1
            muuttuneet.update((vasen, oikea))
            nuoli(ax, (oikea - 0.1, y + 0.98), (vasen + 0.1, y + 0.32),
                  TOINEN, 0.5)
        rivi(ax, y, t, varit=[TAUSTA if i in muuttuneet else "white"
                              for i in range(n)],
             nimi="alas" if aktiivisia == 1 else None)
        aktiivisia *= 2
    assert t == [sum(syote[:i]) for i in range(n)]
    ax.text(3.5, 0.75, "Blelloch (poissulkeva)", ha="center", fontsize=8)
    ax.text(3.5, y - 0.75, f"6 kierrosta, {laskuja} yhteenlaskua",
            ha="center", fontsize=7, color=HARMAA)
    ax.set(xlim=(-2.2, 7.7), ylim=(-10.4, 1.1))
    ax.axis("off")
    tallenna(fig, "05-skannaus.png")


def tiivistys() -> None:
    """Virran tiivistys: liput, poissulkeva skannaus ja hajautus
    (liputa.comp, skannaus, tiivista.comp). Ehto: jaollinen kolmella."""
    data = [7, 3, 12, 5, 9, 4, 6, 10]
    liput = [1 if v % 3 == 0 else 0 for v in data]
    paikat = [sum(liput[:i]) for i in range(len(data))]
    tulos = [v for v, lippu in zip(data, liput) if lippu]
    fig = uusi(4.6, 2.3)
    ax = fig.add_subplot()
    valittu = [TAUSTA if lippu else "white" for lippu in liput]
    rivi(ax, 0, data, varit=valittu, nimi="data")
    rivi(ax, -1, liput, varit=valittu, nimi="liput")
    rivi(ax, -2, paikat, varit=valittu, nimi="skannaus")
    for i, lippu in enumerate(liput):
        if lippu:
            nuoli(ax, (i, -2.32), (paikat[i], -3.68), KOROSTUS, 0.8)
    rivi(ax, -4, tulos + [""] * (len(data) - len(tulos)),
         varit=[TAUSTA] * len(tulos) + ["white"] * (len(data) - len(tulos)),
         nimi="tulos")
    ax.text(len(tulos) + 2, -4.75, f"määrä = viimeinen skannattu arvo + "
            f"viimeinen lippu = {paikat[-1]} + {liput[-1]}", fontsize=7,
            ha="center", color=HARMAA)
    ax.set(xlim=(-2.6, 7.7), ylim=(-5.1, 0.5))
    ax.axis("off")
    tallenna(fig, "05-tiivistys.png")


def bitoninen() -> None:
    """Bitoninen lajitteluverkko kahdeksalle alkiolle samalla säännöllä
    kuin bitoninen.comp: askeleessa (k, j) alkio i verrataan alkioon
    i ^ j, ja suunta riippuu bitistä i & k."""
    n = 8
    a = [5, 2, 7, 0, 6, 3, 1, 4]
    fig = uusi(5.8, 2.6)
    ax = fig.add_subplot()
    x = 0.0
    sarakkeet = [(x, list(a))]
    k = 2
    while k <= n:
        alku = x + 0.6
        j = k // 2
        while j > 0:
            x += 1.3
            for i in range(n):
                pari = i ^ j
                if pari > i:
                    nouseva = (i & k) == 0
                    if (a[i] > a[pari]) == nouseva:
                        a[i], a[pari] = a[pari], a[i]
                    # nuolen kärki osoittaa suuremman arvon paikkaan
                    siirto = 0.2 * (i % j) - 0.1 * (j - 1)
                    y0, y1 = (i, pari) if nouseva else (pari, i)
                    nuoli(ax, (x + siirto, -y0), (x + siirto, -y1),
                          KOROSTUS if nouseva else TOINEN, 0.9)
            j //= 2
        x += 1.1
        sarakkeet.append((x, list(a)))
        ax.text((alku + x - 0.5) / 2, 0.85, f"k = {k}", ha="center",
                fontsize=7, color=HARMAA)
        k *= 2
    assert a == sorted(a)
    for i in range(n):
        ax.plot([0.35, x - 0.35], [-i, -i], color=VAALEA, linewidth=0.6,
                zorder=0)
    for sx, arvot in sarakkeet:
        for i, v in enumerate(arvot):
            solu(ax, sx, -i, v, w=0.6, h=0.62, koko=7)
    ax.text(0, 0.85, "syöte", ha="center", fontsize=7, color=HARMAA)
    ax.text(x + 1.3, -1.5, "nuoli osoittaa\nsuuremman arvon\npaikkaan",
            fontsize=6.5, color=HARMAA, va="center")
    ax.plot([x + 0.7, x + 1.1], [-3.4, -3.4], color=KOROSTUS, linewidth=1.2)
    ax.text(x + 1.2, -3.4, "nouseva", fontsize=6.5, va="center")
    ax.plot([x + 0.7, x + 1.1], [-4.1, -4.1], color=TOINEN, linewidth=1.2)
    ax.text(x + 1.2, -4.1, "laskeva", fontsize=6.5, va="center")
    ax.set(xlim=(-0.6, x + 3.2), ylim=(-7.6, 1.2))
    ax.axis("off")
    tallenna(fig, "07-bitoninen.png")


def kantaluku() -> None:
    """Kantalukulajittelun yksi kierros: numeroiden histogrammi,
    poissulkeva skannaus ja vakaa hajautus. Kahdeksan avainta, numerona
    kaksi alinta bittiä (neljä lokeroa)."""
    avaimet = [13, 6, 9, 4, 3, 10, 7, 5]
    numerot = [a & 3 for a in avaimet]
    histo = [numerot.count(d) for d in range(4)]
    alku = [sum(histo[:d]) for d in range(4)]
    seuraava = list(alku)
    paikka = []
    for d in numerot:
        paikka.append(seuraava[d])
        seuraava[d] += 1
    tulos = [0] * 8
    for a, p in zip(avaimet, paikka):
        tulos[p] = a
    varit4 = ["#E4E6F4", "#F4E6DA", "#DDEBDD", "#EEE6F2"]
    fig = uusi(5.4, 2.7)
    ax = fig.add_subplot()
    varit = [varit4[d] for d in numerot]
    rivi(ax, 0, avaimet, varit=varit, nimi="avaimet")
    rivi(ax, -1, numerot, varit=varit, nimi="numero (avain & 3)")
    for d in range(4):
        solu(ax, 9.6 + d, 0, d, vari=varit4[d], koko=7)
        solu(ax, 9.6 + d, -1, histo[d], koko=7)
        solu(ax, 9.6 + d, -2, alku[d], koko=7)
    ax.text(11.1, 0.6, "lokero", ha="center", fontsize=7, color=HARMAA)
    ax.text(13.3, -1, "histogrammi", va="center", fontsize=7, color=HARMAA)
    ax.text(13.3, -2, "skannaus:\naloituspaikka", va="center", fontsize=7,
            color=HARMAA)
    rivi(ax, -2.2, paikka, varit=varit, nimi="paikka = aloitus + sija")
    for i, p in enumerate(paikka):
        nuoli(ax, (i, -2.52), (p, -3.88), HARMAA, 0.6)
    rivi(ax, -4.2, tulos, varit=[varit4[a & 3] for a in tulos],
         nimi="kierroksen tulos")
    ax.set(xlim=(-4.6, 16.2), ylim=(-4.8, 1.0))
    ax.axis("off")
    tallenna(fig, "07-kantaluku.png")


def transpoosi() -> None:
    """Suoran transpoosin muistiliikenne: yhden aallon kahdeksan kaistaa
    lukevat rivin peräkkäisiä alkioita mutta kirjoittavat sarakkeen
    alkioihin, jotka ovat kukin eri rivillä."""
    n = 8
    fig = uusi(4.6, 2.3)
    for osa, (nimi, solut) in enumerate((
            ("luku: rivin 2 alkiot\nperäkkäin, 1 segmentti",
             [(2, c) for c in range(n)]),
            ("kirjoitus: sarakkeen 2 alkiot,\n8 eri riviä, 8 segmenttiä",
             [(r, 2) for r in range(n)]))):
        ax = fig.add_subplot(1, 2, osa + 1)
        for r in range(n):
            for c in range(n):
                osuma = (r, c) in solut
                ax.add_patch(Rectangle((c, -r - 1), 1, 1,
                                       facecolor=(KOROSTUS if osa == 0
                                                  else TOINEN) if osuma
                                       else "white",
                                       alpha=0.75 if osuma else 1,
                                       edgecolor=VAALEA, linewidth=0.5))
        for kaista, (r, c) in enumerate(solut):
            ax.text(c + 0.5, -r - 0.5, str(kaista), ha="center",
                    va="center", fontsize=6, color="white")
        ax.set(xlim=(-0.2, n + 0.2), ylim=(-n - 0.2, 0.2), aspect="equal")
        ax.set_title(nimi, fontsize=7)
        ax.axis("off")
    tallenna(fig, "08-transpoosi.png")


def roofline() -> None:
    """Roofline luvun 10 mittaustaulukosta (lavapipe, suuntaa-antava)."""
    teksti = (JUURI / "luvut" / "10-mittaaminen.md").read_text()
    alku = teksti.index("| Toistot | Laskut/tavu |")
    rivit = []
    for r in teksti[alku:].splitlines()[2:]:
        if not r.startswith("|"):
            break
        rivit.append([float(s.strip().replace(",", "."))
                      for s in r.strip("|").split("|")])
    t = np.array(rivit)
    assert t.shape == (5, 4), t.shape
    intensiteetti, glaskua, gtavua = t[:, 1], t[:, 2], t[:, 3]
    kaista = gtavua.max()           # Gt/s, muistiraja
    huippu = glaskua.max()          # Glaskua/s, laskentaraja
    fig = uusi(4.4, 2.7)
    ax = fig.add_subplot()
    x = np.logspace(-1, 2.2, 100)
    ax.loglog(x, np.minimum(kaista * x, huippu), color=HARMAA,
              linewidth=1.2, label="malli: min(kaista × intensiteetti, "
              "huippu)")
    ax.loglog(intensiteetti, glaskua, "o", color=KOROSTUS, markersize=5,
              label="mitattu (kuorma.comp)")
    harjanne = huippu / kaista
    ax.axvline(harjanne, color=TOINEN, linewidth=0.7, linestyle=":")
    ax.text(harjanne * 0.9, 6.6, "harjanne", color=TOINEN, fontsize=7,
            ha="right")
    ax.text(0.11, 1.05, "muistisidonnainen", fontsize=7, color=HARMAA,
            rotation=38)
    ax.text(8, huippu * 1.18, "laskentasidonnainen", fontsize=7,
            color=HARMAA)
    ax.set(xlabel="laskentaintensiteetti (laskua/tavu)",
           ylabel="Glaskua/s", ylim=(0.3, 9))
    ax.set_yticks([0.5, 1, 2, 4, 8], ["0,5", "1", "2", "4", "8"])
    ax.set_xticks([0.1, 1, 10, 100], ["0,1", "1", "10", "100"])
    ax.minorticks_off()
    ax.legend(frameon=False, fontsize=7, loc="lower right")
    tallenna(fig, "10-roofline.png")


if __name__ == "__main__":
    tyoryhmat()
    aliryhmat()
    reduktiopuu()
    skannaus()
    tiivistys()
    bitoninen()
    kantaluku()
    transpoosi()
    roofline()
