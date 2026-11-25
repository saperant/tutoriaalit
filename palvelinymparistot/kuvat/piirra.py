"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Luvut lasketaan
samoilla funktioilla ja lähtötiedoilla kuin lukujen testatuissa
esimerkeissä.
"""

import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path
from statistics import linear_regression
from types import ModuleType

from matplotlib import rcParams
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

ESIMERKIT = Path(__file__).resolve().parent.parent / "esimerkit"

KOROSTUS = "#546676"
TOINEN = "#B07A2A"
HARMAA = "#5B6B70"
VAALEA = "#C9D1D8"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}


def esimerkki(nimi: str) -> ModuleType:
    """Lataa esimerkkitiedoston moduulina (nimissä on yhdysmerkki)."""
    spec = importlib.util.spec_from_file_location(
        nimi.replace("-", "_"), ESIMERKIT / f"{nimi}.py")
    assert spec is not None and spec.loader is not None
    moduuli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(moduuli)
    return moduuli


def uusi(leveys: float = 5.0, korkeus: float = 2.8) -> Figure:
    return Figure(figsize=(leveys, korkeus), dpi=200, layout="constrained")


def raid_asettelut(polku: Path) -> None:
    """Lohkojen sijoittelu neljälle levylle tasoilla 0, 1, 10, 5 ja 6.

    RAID 5:n pariteetin paikka kiertää samalla kaavalla kuin
    esimerkissä 03-pariteetti.py: (levyjä - 1 - raita) mod levyjä.
    """
    levyja, raitoja = 4, 4

    def raid0(raita: int) -> list[str]:
        return [f"D{raita * levyja + i + 1}" for i in range(levyja)]

    def raid1(raita: int) -> list[str]:
        return [f"D{raita + 1}"] * levyja

    def raid10(raita: int) -> list[str]:
        a, b = f"D{2 * raita + 1}", f"D{2 * raita + 2}"
        return [a, a, b, b]

    def raid5(raita: int) -> list[str]:
        p = (levyja - 1 - raita) % levyja
        data = iter(f"D{raita * (levyja - 1) + i + 1}"
                    for i in range(levyja - 1))
        return ["P" if i == p else next(data) for i in range(levyja)]

    def raid6(raita: int) -> list[str]:
        p = (levyja - 1 - raita) % levyja
        q = (p + 1) % levyja
        data = iter(f"D{raita * (levyja - 2) + i + 1}"
                    for i in range(levyja - 2))
        return ["P" if i == p else "Q" if i == q else next(data)
                for i in range(levyja)]

    tasot = [("RAID 0", raid0), ("RAID 1", raid1), ("RAID 10", raid10),
             ("RAID 5", raid5), ("RAID 6", raid6)]
    fig = Figure(figsize=(6.4, 2.0), dpi=200, layout="constrained")
    akselit = fig.subplots(1, len(tasot))
    for ax, (nimi, asettelu) in zip(akselit, tasot, strict=True):
        for raita in range(raitoja):
            for levy, lohko in enumerate(asettelu(raita)):
                pariteetti = lohko in ("P", "Q")
                ax.add_patch(Rectangle(
                    (levy, raitoja - 1 - raita), 0.92, 0.88,
                    facecolor=TOINEN if pariteetti else VAALEA,
                    alpha=0.85 if pariteetti else 1.0, edgecolor="none"))
                ax.text(levy + 0.46, raitoja - 1 - raita + 0.44, lohko,
                        ha="center", va="center", fontsize=7,
                        color="white" if pariteetti else "#1F2A2E")
        ax.set_xlim(-0.1, levyja)
        ax.set_ylim(-0.1, raitoja)
        ax.set_xticks([i + 0.46 for i in range(levyja)],
                      [f"levy {i}" if i == 0 else str(i)
                       for i in range(levyja)], fontsize=7)
        ax.set_yticks([])
        ax.tick_params(length=0)
        for reuna in ax.spines.values():
            reuna.set_visible(False)
        ax.set_title(nimi, fontsize=9, color=HARMAA)
    fig.savefig(polku, metadata=METATIEDOT)


def ure(polku: Path) -> None:
    """Lukuvirheen todennäköisyys uudelleenrakennuksessa levykoon mukaan."""
    m = esimerkki("03-ure")
    koot = [k / 2 for k in range(2, 49)]            # 1–24 Tt
    fig = uusi(5.0, 3.2)
    ax = fig.add_subplot()
    for levyja, viiva in ((4, "-"), (8, "--")):
        for nimi, taso, vari in (("10⁻¹⁴ (kuluttaja)", 1e-14, TOINEN),
                                 ("10⁻¹⁵ (yritys)", 1e-15, KOROSTUS)):
            p = [100 * m.ure_todennakoisyys((levyja - 1) * k * m.TT, taso)
                 for k in koot]
            ax.plot(koot, p, viiva, color=vari, lw=1.5,
                    label=f"{levyja} levyä, URE {nimi}")
    ax.axvline(12, color=HARMAA, lw=0.6, ls=":")
    ax.text(11.7, 3, "esimerkin\n12 Tt", fontsize=8, color=HARMAA,
            ha="right")
    ax.set_xlabel("levyn koko, Tt")
    ax.set_ylabel("lukuvirhe rakennuksen aikana, %")
    ax.set_ylim(0, 102)
    ax.set_xlim(1, 24)
    fig.legend(frameon=False, fontsize=7.5, loc="outside lower center",
               ncols=2)
    fig.savefig(polku, metadata=METATIEDOT)


def rpo_rto(polku: Path) -> None:
    """Aikajana: viimeinen kopio, häiriö ja palautuksen valmistuminen."""
    fig = Figure(figsize=(5.4, 1.5), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    kopio, hairio, valmis = 2.0, 5.0, 9.0
    ax.plot([0.3, 10.3], [0, 0], color=HARMAA, lw=1.0)
    for x, teksti in ((kopio, "viimeinen\nkopio"), (hairio, "häiriö"),
                      (valmis, "palvelu\ntoimii taas")):
        ax.plot([x, x], [-0.18, 0.18], color="#1F2A2E", lw=1.2)
        ax.text(x, -0.32, teksti, ha="center", va="top", fontsize=8)
    for alku, loppu, teksti, vari in (
            (kopio, hairio, "menetetty data ≤ RPO", TOINEN),
            (hairio, valmis, "katko ≤ RTO", KOROSTUS)):
        ax.annotate("", xy=(loppu, 0.42), xytext=(alku, 0.42),
                    arrowprops={"arrowstyle": "<->", "color": vari,
                                "lw": 1.4})
        ax.text((alku + loppu) / 2, 0.55, teksti, ha="center",
                va="bottom", fontsize=8.5, color=vari)
    ax.text(10.6, 0, "aika", va="center", fontsize=8, color=HARMAA)
    ax.set_xlim(0, 11.4)
    ax.set_ylim(-1.0, 1.0)
    ax.axis("off")
    fig.savefig(polku, metadata=METATIEDOT)


def gfs(polku: Path) -> None:
    """Porrastetussa säilytyksessä jäävät kopiot aikajanalla."""
    m = esimerkki("05-rotaatio")
    tanaan = date(2026, 11, 24)
    kopiot = [tanaan - timedelta(days=n) for n in range(4 * 365)]
    jaa = sorted(m.sailytettavat(kopiot))
    fig = Figure(figsize=(5.6, 2.3), dpi=200, layout="constrained")
    yla, ala = fig.subplots(2, 1)
    for ax, paivia, otsikko in (
            (yla, 4 * 365, "neljä vuotta: kuukausien ja vuosien kopiot"),
            (ala, 45, "viimeiset 45 päivää: päivien ja viikkojen kopiot")):
        ikkuna = [d for d in kopiot if (tanaan - d).days < paivia]
        ax.vlines([-(tanaan - d).days for d in ikkuna], 0, 1,
                  color=VAALEA, lw=0.4 if paivia > 100 else 2.0)
        ax.vlines([-(tanaan - d).days for d in jaa
                   if (tanaan - d).days < paivia], 0, 1,
                  color=KOROSTUS, lw=1.0 if paivia > 100 else 2.4)
        ax.set_xlim(-paivia, 1)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(otsikko, loc="left", fontsize=8.5, color=HARMAA)
    yla.set_xticks([-365 * v for v in range(4, -1, -1)],
                   ["−4 v", "−3 v", "−2 v", "−1 v", "tänään"])
    ala.set_xticks([-42, -35, -28, -21, -14, -7, 0],
                   ["−6 vk", "−5 vk", "−4 vk", "−3 vk", "−2 vk", "−1 vk",
                    "tänään"])
    fig.savefig(polku, metadata=METATIEDOT)


def palaminen(polku: Path) -> None:
    """Virhebudjetin kuluminen eri palamisnopeuksilla 30 päivän jaksolla."""
    jakso_h = 30 * 24
    fig = uusi()
    ax = fig.add_subplot()
    for nopeus, vari, teksti in (
            (1.0, VAALEA, "×1: budjetti riittää tasan jakson"),
            (6.0, KOROSTUS, "×6: loppuu 5 päivässä (tiketti)"),
            (14.4, TOINEN, "×14,4: loppuu 50 tunnissa (päivystäjä)")):
        loppu_h = jakso_h / nopeus
        ax.plot([0, loppu_h / 24], [100, 0], color=vari, lw=1.6,
                label=teksti)
    ax.set_xlabel("päiviä jakson alusta")
    ax.set_ylabel("virhebudjettia jäljellä, %")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 102)
    ax.legend(frameon=False, fontsize=8)
    fig.savefig(polku, metadata=METATIEDOT)


def kapasiteetti(polku: Path) -> None:
    """Käyttöhistoria, sovitettu suora ja rajojen ylityshetket."""
    m = esimerkki("11-kapasiteetti")
    kaytto = m.KAYTTO
    kk = list(range(len(kaytto)))
    kulma, vakio = linear_regression(kk, kaytto)
    raja_tt = m.RAJA * m.KAPASITEETTI_TT
    raja_kk = m.kuukausi_jolloin(kaytto, raja_tt)
    taysi_kk = m.kuukausi_jolloin(kaytto, m.KAPASITEETTI_TT)
    tilaus_kk = raja_kk - m.HANKINTA_KK
    fig = uusi(5.2, 3.0)
    ax = fig.add_subplot()
    ax.plot([0, taysi_kk], [vakio, vakio + kulma * taysi_kk], color=KOROSTUS,
            lw=1.2, label=f"sovitettu suora, {kulma:.2f} Tt/kk")
    ax.plot(kk, kaytto, "o", color="#1F2A2E", ms=3.5, label="mitattu käyttö")
    ax.axhline(raja_tt, color=TOINEN, lw=0.9, ls="--")
    ax.text(0.3, raja_tt + 1.2, f"hälytysraja {m.RAJA:.0%}", fontsize=8,
            color=TOINEN)
    ax.axhline(m.KAPASITEETTI_TT, color=HARMAA, lw=0.9)
    ax.text(0.3, m.KAPASITEETTI_TT + 1.2, "kapasiteetti 120 Tt", fontsize=8,
            color=HARMAA)
    for x, y, teksti in ((raja_kk, raja_tt, f"raja ylittyy\n{m.nimi(raja_kk)}"),
                         (taysi_kk, m.KAPASITEETTI_TT,
                          f"tila loppuu\n{m.nimi(taysi_kk)}")):
        ax.plot([x], [y], "o", color=KOROSTUS, ms=4)
        ax.text(x + 0.5, y - 10, teksti, fontsize=8, ha="left",
                color=KOROSTUS)
    ax.axvline(tilaus_kk, color=TOINEN, lw=0.9, ls=":")
    ax.text(tilaus_kk - 0.3, 62, f"tilaa viimeistään\n{m.nimi(tilaus_kk)}",
            fontsize=8, ha="right", color=TOINEN)
    ax.set_xticks([0, 6, 12, 18, 24], ["1/2026", "7/2026", "1/2027",
                                       "7/2027", "1/2028"])
    ax.set_ylabel("käytössä, Tt")
    ax.set_ylim(55, 130)
    ax.set_xlim(-0.5, taysi_kk + 5)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    fig.savefig(polku, metadata=METATIEDOT)


def main() -> None:
    kohde = Path(sys.argv[1])
    kohde.mkdir(parents=True, exist_ok=True)
    raid_asettelut(kohde / "03-raid-asettelut.png")
    ure(kohde / "03-ure.png")
    rpo_rto(kohde / "05-rpo-rto.png")
    gfs(kohde / "05-gfs.png")
    palaminen(kohde / "10-palaminen.png")
    kapasiteetti(kohde / "11-kapasiteetti.png")


if __name__ == "__main__":
    main()
