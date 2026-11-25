"""Piirtää tutoriaalin kuvat. Käyttö: python3 kuvat/piirra.py KOHDE

Kuvat commitoidaan, joten tätä ei ajeta testeissä. Kuvien luvut
lasketaan samoin kuin lukujen testatuissa esimerkeissä (samat siemenet).
"""

import math
import sys
from pathlib import Path

import numpy as np
import numpy.typing as npt
from matplotlib import rcParams
from matplotlib.figure import Figure

KOROSTUS = "#9A6524"
HARMAA = "#5B6B70"
VAALEA = "#B8C4C8"
SININEN = "#2F5D8A"
rcParams["font.family"] = ["Inter", "DejaVu Sans"]
rcParams["font.size"] = 9
rcParams["axes.spines.top"] = False
rcParams["axes.spines.right"] = False
METATIEDOT = {"Software": None}
Taulukko = npt.NDArray[np.float64]


def tallenna(fig: Figure, polku: Path) -> None:
    fig.savefig(polku, metadata=METATIEDOT)


def normaalitiheys(x: Taulukko, mu: float = 0.0,
                   sigma: float = 1.0) -> Taulukko:
    z = (x - mu) / sigma
    return np.asarray(np.exp(-z * z / 2) / (sigma * math.sqrt(2 * math.pi)))


def diskreetit(polku: Path) -> None:
    """Bin(100; 0,02) ja Poisson(2): pistetodennäköisyydet ja häntä."""
    n, p, lam = 100, 0.02, 2.0
    k = np.arange(10)
    binomi = np.array([math.comb(n, i) * p**i * (1 - p) ** (n - i)
                       for i in k])
    poisson = np.array([lam**i * math.exp(-lam) / math.factorial(i)
                        for i in k])
    fig = Figure(figsize=(4.6, 2.7), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    varit = [KOROSTUS if i >= 5 else VAALEA for i in k]
    ax.bar(k - 0.2, binomi, width=0.4, color=varit, label="Bin(100; 0,02)")
    ax.bar(k + 0.2, poisson, width=0.4, facecolor="none", edgecolor=HARMAA,
           linewidth=1.0, label="Poisson(2)")
    hanta = 1 - binomi[:5].sum()
    ax.annotate(f"P(X ≥ 5) = {hanta:.3f}".replace(".", ","), xy=(5.6, 0.03),
                xytext=(5.2, 0.14), color=KOROSTUS, fontsize=8,
                arrowprops={"arrowstyle": "-", "color": KOROSTUS,
                            "linewidth": 0.7})
    ax.set(xlabel="hävinneitä paketteja k", ylabel="P(X = k)")
    ax.set_xticks(list(k))
    ax.legend(frameon=False, fontsize=8)
    tallenna(fig, polku)


def jatkuvat(polku: Path) -> None:
    """Exp(3): tiheysfunktio ja kertymäfunktio, sama väli molemmissa."""
    lam, a, b = 3.0, 0.2, 0.6
    t = np.linspace(0.0, 1.6, 400)
    fig = Figure(figsize=(6.2, 2.5), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    ax1.plot(t, lam * np.exp(-lam * t), color=HARMAA, linewidth=1.3)
    vali = (t >= a) & (t <= b)
    ax1.fill_between(t[vali], lam * np.exp(-lam * t[vali]), color=KOROSTUS,
                     alpha=0.35)
    pa = math.exp(-lam * a) - math.exp(-lam * b)
    ax1.text(0.42, 1.15, f"pinta-ala\n{pa:.3f}".replace(".", ","),
             color=KOROSTUS, fontsize=8)
    ax1.set(xlabel="väliaika t (s)", ylabel="tiheys f(t)", ylim=(0, 3.1))
    ax1.set_title("tiheysfunktio", fontsize=8.5)
    kertyma = 1 - np.exp(-lam * t)
    ax2.plot(t, kertyma, color=HARMAA, linewidth=1.3)
    fa, fb = 1 - math.exp(-lam * a), 1 - math.exp(-lam * b)
    for x, f in ((a, fa), (b, fb)):
        ax2.plot([x, x, 0], [0, f, f], color=KOROSTUS, linewidth=0.8,
                 linestyle=":")
    ax2.annotate("", xy=(0.04, fb), xytext=(0.04, fa),
                 arrowprops={"arrowstyle": "<->", "color": KOROSTUS,
                             "linewidth": 1.0})
    ax2.text(0.72, (fa + fb) / 2 - 0.03,
             "F(0,6) − F(0,2)\n= " + f"{fb - fa:.3f}".replace(".", ","),
             color=KOROSTUS, fontsize=8)
    ax2.set(xlabel="väliaika t (s)", ylabel="F(t) = P(T ≤ t)",
            ylim=(0, 1.05), xlim=(0, 1.6))
    ax2.set_title("kertymäfunktio", fontsize=8.5)
    tallenna(fig, polku)


def normaali(polku: Path) -> None:
    """N(10; 2^2): yhden, kahden ja kolmen keskihajonnan alueet."""
    mu, sigma = 10.0, 2.0
    x = np.linspace(mu - 4 * sigma, mu + 4 * sigma, 600)
    y = normaalitiheys(x, mu, sigma)
    fig = Figure(figsize=(4.8, 2.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    for k, alfa in ((3, 0.15), (2, 0.3), (1, 0.5)):
        alue = np.abs(x - mu) <= k * sigma
        ax.fill_between(x[alue], y[alue], color=KOROSTUS, alpha=alfa,
                        linewidth=0)
    ax.plot(x, y, color=HARMAA, linewidth=1.2)
    for k, korkeus in ((1, 0.215), (2, 0.228), (3, 0.241)):
        osuus = math.erf(k / math.sqrt(2))
        ax.annotate("", xy=(mu - k * sigma, korkeus),
                    xytext=(mu + k * sigma, korkeus),
                    arrowprops={"arrowstyle": "<->", "color": HARMAA,
                                "linewidth": 0.7})
        ax.text(mu, korkeus + 0.002,
                f"±{k}σ: {100 * osuus:.1f} %".replace(".", ","),
                ha="center", fontsize=7.5)
    ax.set(xlabel="x", ylabel="tiheys", ylim=(0, 0.26))
    ax.set_xticks([mu + k * sigma for k in range(-3, 4)])
    tallenna(fig, polku)


def bayes(polku: Path) -> None:
    """P(sairas | +) esiintyvyyden funktiona, herkkyys 99 %, tarkkuus 95 %."""
    herkkyys, tarkkuus = 0.99, 0.95
    e = np.logspace(-4, 0, 400)[:-1]
    post = herkkyys * e / (herkkyys * e + (1 - tarkkuus) * (1 - e))
    fig = Figure(figsize=(4.6, 2.7), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.semilogx(e, post, color=HARMAA, linewidth=1.3)
    for arvo in (0.001, 0.01, 0.1):
        p = herkkyys * arvo / (herkkyys * arvo
                               + (1 - tarkkuus) * (1 - arvo))
        ax.plot([arvo], [p], "o", color=KOROSTUS, markersize=4)
        ax.text(arvo * 0.8, p + 0.035, f"{p:.3f}".replace(".", ","),
                color=KOROSTUS, fontsize=8, ha="right")
    ax.set(xlabel="esiintyvyys P(sairas)", ylabel="P(sairas | positiivinen)",
           ylim=(0, 1.02))
    ax.set_xticks([1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_xticklabels(["0,01 %", "0,1 %", "1 %", "10 %", "100 %"])
    tallenna(fig, polku)


def korrelaatio(polku: Path) -> None:
    """Hajontakuvioita eri korrelaatioilla; viimeisessä Y = X^2."""
    rng = np.random.default_rng(314)
    n = 1500
    fig = Figure(figsize=(6.8, 1.7), dpi=200, layout="constrained")
    ruudut = fig.subplots(1, 5)
    tapaukset: list[tuple[Taulukko, Taulukko]] = []
    for rho in (0.9, 0.5, 0.0, -0.7):
        x = rng.normal(size=n)
        tapaukset.append((x, rho * x
                          + math.sqrt(1 - rho**2) * rng.normal(size=n)))
    x = rng.normal(size=n)
    tapaukset.append((x, x**2 - 1))
    for ax, (x, y) in zip(ruudut, tapaukset, strict=True):
        r = float(np.corrcoef(x, y)[0, 1])
        ax.plot(x, y, ".", color=HARMAA, markersize=1.2)
        ax.set(xlim=(-3.5, 3.5), ylim=(-3.5, 3.5))
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(f"r = {round(r, 2) + 0.0:+.2f}".replace(".", ","),
                     fontsize=8.5)
    ruudut[-1].set_xlabel("Y = X² − 1", fontsize=8)
    tallenna(fig, polku)


def regressio(polku: Path) -> None:
    """Luvun regressioesimerkit: suora ja jäännökset kahdelle aineistolle."""
    rng = np.random.default_rng(12)
    kuorma = rng.uniform(50.0, 400.0, 60)
    cpu = 8.0 + 0.15 * kuorma + rng.normal(0.0, 4.0, kuorma.size)
    kuorma2 = np.linspace(50.0, 400.0, 60)
    vaste = (20.0 / (1 - kuorma2 / 500.0)
             + rng.normal(0.0, 3.0, kuorma2.size))
    fig = Figure(figsize=(6.4, 4.0), dpi=200, layout="constrained")
    ruudut = fig.subplots(2, 2, sharex=True,
                          gridspec_kw={"height_ratios": [2, 1]})
    aineistot = ((kuorma, cpu, "käyttöaste (%)", "%-yks."),
                 (kuorma2, vaste, "vasteaika (ms)", "ms"))
    for sarake, (x, y, nimi, yksikko) in enumerate(aineistot):
        b = float(np.cov(x, y)[0, 1]) / float(np.var(x, ddof=1))
        a = float(y.mean()) - b * float(x.mean())
        ylä, ala = ruudut[0, sarake], ruudut[1, sarake]
        xs = np.array([40.0, 410.0])
        ylä.plot(x, y, "o", color="black", markersize=2.5)
        ylä.plot(xs, a + b * xs, color=KOROSTUS, linewidth=1.2)
        ylä.set_ylabel(nimi)
        jaannos = y - (a + b * x)
        ala.axhline(0, color=KOROSTUS, linewidth=1.0)
        ala.vlines(x, 0, jaannos, color=VAALEA, linewidth=0.8)
        ala.plot(x, jaannos, "o", color="black", markersize=2.5)
        ala.set(xlabel="kuorma (pyyntöä/s)", ylabel=f"jäännös ({yksikko})")
    tallenna(fig, polku)


def suuret_luvut(polku: Path) -> None:
    """Juokseva keskiarvo: noppa asettuu, Cauchy ei."""
    rng = np.random.default_rng(1)
    heitot = rng.integers(1, 7, size=1_000_000)
    c = rng.standard_cauchy(1_000_000)
    n = np.arange(1, heitot.size + 1)
    poiminta = np.unique(np.logspace(0, 6, 1500).astype(int)) - 1
    fig = Figure(figsize=(4.8, 2.7), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.axhline(3.5, color=VAALEA, linewidth=2.0)
    ax.semilogx(n[poiminta], (np.cumsum(heitot) / n)[poiminta],
                color=KOROSTUS, linewidth=1.1, label="noppa (odotusarvo 3,5)")
    ax.semilogx(n[poiminta], (np.cumsum(c) / n)[poiminta], color=SININEN,
                linewidth=1.1, label="Cauchy (ei odotusarvoa)")
    ax.set(xlabel="havaintoja n", ylabel="keskiarvo", ylim=(-4.5, 6.5))
    ax.legend(frameon=False, fontsize=8, loc="lower right")
    tallenna(fig, polku)


def raja_arvo(polku: Path) -> None:
    """Summien jakaumat: tasajakauma (n = 1, 2, 12) ja Exp (n = 1, 5, 50)."""
    rng = np.random.default_rng(8)
    fig = Figure(figsize=(6.6, 3.4), dpi=200, layout="constrained")
    ruudut = fig.subplots(2, 3, sharex=True, sharey=True)
    z = np.linspace(-3.5, 3.5, 300)
    for ax, n in zip(ruudut[0], (1, 2, 12), strict=True):
        s = rng.random((200_000, n)).sum(axis=1)
        ax.hist((s - n / 2) / math.sqrt(n / 12), bins=60, range=(-3.5, 3.5),
                density=True, color=VAALEA)
        ax.set_title(f"tasajakauma, n = {n}", fontsize=8.5)
    for ax, n in zip(ruudut[1], (1, 5, 50), strict=True):
        s = rng.exponential(1.0, (200_000, n)).sum(axis=1)
        ax.hist((s - n) / math.sqrt(n), bins=60, range=(-3.5, 3.5),
                density=True, color=VAALEA)
        ax.set_title(f"eksponenttijakauma, n = {n}", fontsize=8.5)
        ax.set_xlabel("standardoitu summa")
    for ax in ruudut.flat:
        ax.plot(z, normaalitiheys(z), color=KOROSTUS, linewidth=1.0)
        ax.set_ylim(0, 0.62)
    tallenna(fig, polku)


def luottamusvalit(polku: Path) -> tuple[int, int]:
    """Sata 95 %:n luottamusväliä; palauttaa (ohi menneet, kaikki)."""
    rng = np.random.default_rng(64)
    x = rng.normal(12.0, 3.0, size=(100, 40))
    ka = x.mean(axis=1)
    kv = x.std(axis=1, ddof=1) / math.sqrt(40)
    ohi = np.abs(ka - 12.0) > 1.96 * kv
    fig = Figure(figsize=(4.8, 3.6), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.axvline(12.0, color=HARMAA, linewidth=1.0)
    for i in range(100):
        vari = KOROSTUS if ohi[i] else VAALEA
        ax.plot([ka[i] - 1.96 * kv[i], ka[i] + 1.96 * kv[i]], [i, i],
                color=vari, linewidth=1.2 if ohi[i] else 0.9)
        ax.plot([ka[i]], [i], ".", color=vari if ohi[i] else HARMAA,
                markersize=2.5)
    ax.set(xlabel="mittauksen keskiarvo ja 95 %:n luottamusväli",
           ylabel="koe")
    ax.set_yticks([])
    tallenna(fig, polku)
    return int(ohi.sum()), 100


def pii(polku: Path) -> None:
    """Piin Monte Carlo -arvio: pisteet ja virhe otoskoon funktiona."""
    rng = np.random.default_rng(2718)
    koot, virheet = [], []
    for k in range(2, 7):
        n = 10**k
        arviot = [4 * float(np.mean((rng.random(n) ** 2
                                     + rng.random(n) ** 2) <= 1.0))
                  for _ in range(20)]
        koot.append(n)
        virheet.append(float(np.sqrt(np.mean((np.array(arviot)
                                              - math.pi) ** 2))))
    pisteet = np.random.default_rng(3).random((1500, 2))
    sisalla = (pisteet**2).sum(axis=1) <= 1.0
    fig = Figure(figsize=(6.2, 2.7), dpi=200, layout="constrained")
    ax1, ax2 = fig.subplots(1, 2)
    ax1.set_aspect("equal")
    ax1.plot(pisteet[sisalla, 0], pisteet[sisalla, 1], ".", color=KOROSTUS,
             markersize=2.5)
    ax1.plot(pisteet[~sisalla, 0], pisteet[~sisalla, 1], ".", color=VAALEA,
             markersize=2.5)
    t = np.linspace(0, math.pi / 2, 100)
    ax1.plot(np.cos(t), np.sin(t), color=HARMAA, linewidth=1.0)
    ax1.set(xlim=(0, 1), ylim=(0, 1))
    ax1.set_title(f"1500 pistettä: arvio "
                  f"{4 * sisalla.mean():.3f}".replace(".", ","), fontsize=8.5)
    ax2.loglog(koot, [1.6 / math.sqrt(n) for n in koot], color=VAALEA,
               linewidth=2.5, label="1,6 / √n")
    ax2.loglog(koot, virheet, "o", color=KOROSTUS, markersize=4,
               label="virhe (20 toiston neliöllinen keskiarvo)")
    ax2.set(xlabel="pisteitä n", ylabel="virhe")
    ax2.legend(frameon=False, fontsize=7.5)
    tallenna(fig, polku)


def vasteajat(polku: Path) -> None:
    """Luvun Mittausten tulkinta vasteaikajakauma logaritmisella akselilla."""
    rng = np.random.default_rng(1234)
    n = 100_000
    nopea = rng.lognormal(mean=np.log(20.0), sigma=0.3, size=n)
    hidas = rng.lognormal(mean=np.log(400.0), sigma=0.5, size=n)
    x = np.where(rng.random(n) < 0.02, hidas, nopea)
    p50, p99 = np.percentile(x, [50, 99])
    fig = Figure(figsize=(5.2, 2.7), dpi=200, layout="constrained")
    ax = fig.add_subplot()
    ax.hist(x, bins=np.logspace(np.log10(5), np.log10(3000), 90),
            color=VAALEA)
    for arvo, nimi, vari, korkeus in (
            (float(p50), "mediaani", SININEN, 0.84),
            (float(x.mean()), "keskiarvo", KOROSTUS, 0.98),
            (float(p99), "p99", HARMAA, 0.98)):
        ax.axvline(arvo, color=vari, linewidth=1.2)
        vasen = nimi == "mediaani"
        ax.text(arvo * (0.93 if vasen else 1.08), korkeus,
                f"{nimi}\n{arvo:.0f} ms", color=vari, fontsize=8,
                transform=ax.get_xaxis_transform(), va="top",
                ha="right" if vasen else "left")
    ax.set(xscale="log", yscale="log", xlabel="vasteaika (ms)",
           ylabel="pyyntöjä", ylim=(0.8, 6e5))
    tallenna(fig, polku)


def main() -> None:
    kohde = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("kuvat")
    for nimi, piirra in (("diskreetit", diskreetit), ("jatkuvat", jatkuvat),
                         ("normaali", normaali), ("bayes", bayes),
                         ("korrelaatio", korrelaatio),
                         ("regressio", regressio),
                         ("suuret-luvut", suuret_luvut),
                         ("raja-arvo", raja_arvo), ("pii", pii),
                         ("vasteajat", vasteajat)):
        piirra(kohde / f"{nimi}.png")
    ohi, kaikki = luottamusvalit(kohde / "luottamusvalit.png")
    print(f"luottamusvälit: {ohi}/{kaikki} ei sisällä todellista arvoa")


if __name__ == "__main__":
    main()
