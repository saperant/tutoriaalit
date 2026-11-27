"""Piirtää tutoriaalin kuvat.

Käyttö: python3 kuvat/piirra.py KOHDE KVANTTIOHJELMA

Kuvat commitoidaan, joten tätä ei ajeta testeissä. KVANTTIOHJELMA on
esimerkin 11-kvantti käännetty ohjelma (esimerkit/build/11-kvantti/
ohjelma). Se ajetaan jälki päällä (toinen argumentti), jolloin se
tulostaa jokaisen siirron simulaatioajan ja aloittajan oman ajan.
Keskeytyskuvat piirretään suoraan esimerkin 15-keskeytykset testatusta
tulosteesta (tiedosto odotettu).
"""

import os
import subprocess
import sys
from pathlib import Path

from matplotlib import rcParams
from matplotlib.figure import Figure

KOROSTUS = "#B04848"          # alueen Laitteistosuunnittelu väri
TOINEN = "#2F6F8F"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
MUSTE = "#1F2A2E"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
rcParams["text.color"] = MUSTE
rcParams["axes.edgecolor"] = HARMAA
rcParams["axes.labelcolor"] = MUSTE
rcParams["xtick.color"] = HARMAA
rcParams["ytick.color"] = HARMAA

Jalki = dict[str, list[tuple[str, float, float]]]


def aja(ohjelma: Path, kvantti_ns: int) -> Jalki:
    """Ajaa esimerkin jälki päällä ja lukee rivit "J kuka mitä sim oma"."""
    ymparisto = {**os.environ, "SC_COPYRIGHT_MESSAGE": "DISABLE"}
    tuloste = subprocess.run([str(ohjelma), str(kvantti_ns), "jalki"],
                             check=True, capture_output=True, text=True,
                             env=ymparisto).stdout
    jalki: Jalki = {"tuottaja": [], "kuluttaja": []}
    for rivi in tuloste.splitlines():
        if rivi.startswith("J "):
            _, kuka, mita, sim, oma = rivi.split()
            jalki[kuka].append((mita, float(sim), float(oma)))
    return jalki


def kvantti(polku: Path, ohjelma: Path) -> None:
    """Aloittajan oma aika simulaatioajan funktiona kolmella kvantilla.
    Lävistäjällä aloittaja on synkronissa; sen yläpuolella se on edellä."""
    fig = Figure(figsize=(6.4, 2.55), dpi=200, layout="constrained")
    akselit = fig.subplots(1, 3, sharex=True, sharey=True)
    raja = 2400.0
    for ax, (ns, nimi) in zip(akselit, ((0, "kvantti 0"),
                                        (100, "kvantti 100 ns"),
                                        (1000, "kvantti 1 µs")),
                              strict=True):
        jalki = aja(ohjelma, ns)
        ax.plot([0, raja], [0, raja], color=VAALEA, linewidth=0.8)
        for kuka, vari, merkki in (("kuluttaja", TOINEN, "."),
                                   ("tuottaja", KOROSTUS, "o")):
            t = [(s, o) for _, s, o in jalki[kuka] if o <= raja]
            # Aloittaja kulkee ensin omassa ajassaan (pysty) ja siirtää
            # synkronoidessaan simulaatioajan sen tasalle (vaaka).
            ax.plot([s for s, _ in t], [o for _, o in t], "-", color=vari,
                    linewidth=0.7, alpha=0.6, drawstyle="steps-pre")
            ax.plot([s for s, _ in t], [o for _, o in t], merkki,
                    color=vari, markersize=3.2 if merkki == "o" else 2.5,
                    label=kuka)
        uudet = [(s, o) for m, s, o in jalki["kuluttaja"]
                 if m == "uusi" and o <= raja]
        ax.plot([s for s, _ in uudet], [o for _, o in uudet], "v",
                color=MUSTE, markersize=4, label="kuluttaja näkee uuden")
        ax.set_title(nimi, fontsize=8.5)
        ax.set_xlabel("simulaatioaika (ns)")
        ax.set_xlim(0, raja)
        ax.set_ylim(0, raja)
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
        ax.set_xticks([0, 1000, 2000])
        ax.set_yticks([0, 1000, 2000])
    akselit[0].set_ylabel("aloittajan oma aika (ns)")
    akselit[2].annotate("viesti 4 näkyy\nhetkellä 50 ns,\nlähetetty 830 ns",
                        (0, 50), (420, 330), fontsize=6.5,
                        arrowprops={"arrowstyle": "-", "color": HARMAA,
                                    "linewidth": 0.6})
    akselit[0].legend(frameon=False, fontsize=6.5, loc="lower right",
                      handletextpad=0.3)
    fig.savefig(polku, metadata={"Software": None})


KESKEYTYKSET = (Path(__file__).resolve().parent.parent / "esimerkit" /
                "15-keskeytykset" / "odotettu")


def lue_loki() -> list[tuple[int, str]]:
    """Tapahtumaloki (aika ns, teksti) esimerkin 15-keskeytykset
    tulosteen ensimmäisestä osasta."""
    tapahtumat = []
    for rivi in KESKEYTYKSET.read_text("utf-8").splitlines():
        osat = rivi.split(None, 1)
        if rivi.startswith("== kvantin"):
            break
        if len(osat) == 2 and osat[0].isdigit():
            tapahtumat.append((int(osat[0]), osat[1]))
    return tapahtumat


def lue_taulukko() -> list[tuple[int, str, int, int, int, int]]:
    """Rivit (kvantti ns, tila, pienin viive, suurin viive, käskyjä,
    menetetyt) tulosteen vertailutaulukosta."""
    rivit = []
    mukana = False
    for rivi in KESKEYTYKSET.read_text("utf-8").splitlines():
        if rivi.startswith("== koe"):
            break
        osat = rivi.split()
        if mukana and len(osat) == 8 and osat[0].isdigit():
            pienin, suurin = osat[4].split("..")
            rivit.append((int(osat[0]), osat[1], int(pienin), int(suurin),
                          int(osat[5]), int(osat[3])))
        mukana = mukana or rivi.startswith("kvantti ")
    return rivit


def valit(tapahtumat: list[tuple[int, str]], alku: str,
          loppu: str) -> list[tuple[int, int]]:
    """Parit (alkuhetki, loppuhetki) tapahtumille, joiden teksti alkaa
    annetuilla merkkijonoilla."""
    tulos, auki = [], None
    for aika, teksti in tapahtumat:
        if teksti.startswith(alku) and auki is None:
            auki = aika
        elif teksti.startswith(loppu) and auki is not None:
            tulos.append((auki, aika))
            auki = None
    return tulos


def keskeytykset(polku: Path) -> None:
    """Aikajana tapahtumalokista: koko ajo ja suurennos kohdasta, jossa
    ajastimen tikki osuu sarjaportin käsittelijän päälle."""
    tapahtumat = lue_loki()
    ajastin = valit(tapahtumat, "ajastin: linja ylös", "ajastin: kuitattu")
    uart = valit(tapahtumat, "uart: merkki", "uart: luettu")
    kasittelija = valit(tapahtumat, "prosessori: keskeytys",
                        "prosessori: paluu")
    loppu = tapahtumat[-1][0]
    fig = Figure(figsize=(6.4, 2.7), dpi=200, layout="constrained")
    koko, lahi = fig.subplots(1, 2, width_ratios=[1.25, 1])
    rivit = (("ajastimen linja", ajastin, KOROSTUS),
             ("sarjaportin linja", uart, TOINEN),
             ("käsittelijä", kasittelija, MUSTE))

    for ax, (a, b), yksikko in ((koko, (0, loppu), 1000.0),
                               (lahi, (51900, 54100), 1.0)):
        for i, (nimi, jaksot, vari) in enumerate(rivit):
            y = len(rivit) - 1 - i
            ax.plot([a / yksikko, b / yksikko], [y, y], color=VAALEA,
                    linewidth=0.8, zorder=1)
            for alku, paa in jaksot:
                if paa < a or alku > b:
                    continue
                if yksikko > 1:      # koko ajo: pulssit ovat viivoja
                    ax.plot([alku / yksikko] * 2, [y, y + 0.55],
                            color=vari, linewidth=1.3, zorder=2)
                else:
                    ax.fill_between([alku, paa], y, y + 0.55, color=vari,
                                    alpha=0.85, linewidth=0, zorder=2)
            if yksikko > 1:
                ax.text(a / yksikko, y + 0.68, nimi, fontsize=7,
                        va="bottom")
            else:            # suurennoksessa nimi oikeaan reunaan
                ax.text(b, y + 0.12, nimi, fontsize=7, va="bottom",
                        ha="right")
        ax.set_ylim(-0.25, len(rivit) + 0.15)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_xlim(a / yksikko, b / yksikko)
    koko.set_xlabel("simulaatioaika (µs)")
    koko.set_title("koko ajo: kymmenen tikkiä ja kolme merkkiä",
                   fontsize=8.5)
    koko.axvspan(51.9, 54.1, color=VAALEA, alpha=0.5, linewidth=0)
    lahi.set_xlabel("simulaatioaika (ns)")
    lahi.set_title("suurennos: tikki kesken käsittelijän", fontsize=8.5)
    lahi.set_xticks([52000, 52500, 53000, 53500])
    # Tikin nousu ja hetki, jolloin prosessori ottaa sen.
    nousu = next(t for t, s in tapahtumat
                 if s.startswith("ajastin: linja ylös") and t > 52000)
    otto = next(t for t, s in tapahtumat
                if s.startswith("prosessori: keskeytys 7") and t > nousu)
    lahi.annotate("", (otto, 2.68), (nousu, 2.68),
                  arrowprops={"arrowstyle": "<->", "color": HARMAA,
                              "linewidth": 0.7})
    lahi.text((nousu + otto) / 2, 2.75, f"viive {otto - nousu} ns",
              fontsize=6.5, ha="center", va="bottom", color=HARMAA)
    fig.savefig(polku, metadata={"Software": None})


def keskeytysviive(polku: Path) -> None:
    """Keskeytysviive ja suoritettujen käskyjen määrä kvantin funktiona
    esimerkin vertailutaulukosta."""
    rivit = lue_taulukko()
    kvantit = sorted({r[0] for r in rivit})
    nimet = ["0" if k == 0 else f"{k // 1000} µs" for k in kvantit]
    fig = Figure(figsize=(6.4, 2.5), dpi=200, layout="constrained")
    viive, kaskyt = fig.subplots(1, 2)
    for siirto, tila, vari in ((-0.17, "kysely", KOROSTUS),
                               (0.17, "wfi", TOINEN)):
        omat = {r[0]: r for r in rivit if r[1] == tila}
        for i, k in enumerate(kvantit):
            _, _, pienin, suurin, kaskyja, menetetyt = omat[k]
            viive.plot([i + siirto] * 2, [pienin, suurin], color=vari,
                       linewidth=5, solid_capstyle="butt",
                       label=tila if i == 0 else None)
            if pienin == suurin:
                viive.plot([i + siirto], [pienin], "s", color=vari,
                           markersize=4.5)
            if menetetyt:
                viive.text(i + siirto, suurin * 1.3,
                           f"{menetetyt} tikkiä\nmenetetty", fontsize=6.5,
                           ha="center", va="bottom", color=vari)
            kaskyt.bar(i + siirto, kaskyja, width=0.32, color=vari,
                       label=tila if i == 0 else None)
            kaskyt.text(i + siirto, kaskyja * 1.12, str(kaskyja),
                        fontsize=6.5, ha="center", va="bottom")
    # Yläraja: irrotettu prosessori näkee linjan viimeistään kvantin
    # päässä (nollakvantilla yhden käskyn päässä).
    for i, k in enumerate(kvantit):
        if k:
            viive.plot([i - 0.42, i + 0.42], [k, k], color=HARMAA,
                       linewidth=0.8, linestyle="--",
                       label="kvantti" if i == 1 else None)
    for ax in (viive, kaskyt):
        ax.set_yscale("log")
        ax.set_xticks(range(len(kvantit)), nimet)
        ax.set_xlabel("kvantti")
        ax.grid(axis="y", alpha=0.3)
    viive.set_ylim(3, 3e5)
    viive.set_ylabel("keskeytysviive (ns)")
    viive.set_title("viive linjan noususta ottoon", fontsize=8.5)
    viive.legend(frameon=False, fontsize=6.5, loc="upper left")
    kaskyt.set_ylim(100, 6e4)
    kaskyt.set_ylabel("suoritettuja käskyjä")
    kaskyt.set_title("sama ohjelma, kymmenen tikkiä", fontsize=8.5)
    kaskyt.legend(frameon=False, fontsize=6.5, loc="upper left")
    fig.savefig(polku, metadata={"Software": None})


def main() -> None:
    kohde, ohjelma = Path(sys.argv[1]), Path(sys.argv[2])
    kvantti(kohde / "kvantti.png", ohjelma)
    print("kvantti.png")
    keskeytykset(kohde / "keskeytykset.png")
    print("keskeytykset.png")
    keskeytysviive(kohde / "keskeytysviive.png")
    print("keskeytysviive.png")


if __name__ == "__main__":
    main()
