"""Pieni kokoonpuristumattoman virtauksen ratkaisija opetuskäyttöön.

Porrastettu hila suorakulmiossa: paine p ruutujen keskellä (nx, ny),
vaakanopeus u pystypinnoilla (nx + 1, ny) ja pystynopeus v vaakapinnoilla
(nx, ny + 1). Tiheys on 1, joten p on paine jaettuna tiheydellä.
Aika-askel on projektiomenetelmä: ennustus ilman painetta, paineyhtälö,
korjaus."""

from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt
import scipy.sparse as sp
from scipy.sparse.linalg import splu

Taulukko = npt.NDArray[np.float64]
Maski = npt.NDArray[np.bool_]


# @alku tehtava
@dataclass(frozen=True)
class Reuna:
    """Alueen yhden sivun reunaehto.

    laji: "seinä" (tarttuva; nopeus on seinän oma nopeus sivun suuntaan),
    "liukuva" (symmetriataso), "sisään" (nopeus on sisäänvirtauksen
    profiili, vain vasen sivu) tai "ulos" (vain oikea sivu)."""
    laji: str = "seinä"
    nopeus: float | Taulukko = 0.0


@dataclass(frozen=True)
class Tehtava:
    nx: int
    ny: int
    lx: float
    ly: float
    nu: float                          # kinemaattinen viskositeetti
    vasen: Reuna = field(default_factory=Reuna)
    oikea: Reuna = field(default_factory=Reuna)
    ala: Reuna = field(default_factory=Reuna)
    yla: Reuna = field(default_factory=Reuna)
    este: Maski | None = None          # kiinteät ruudut (nx, ny)
    vastavirta: float = 0.0            # 0 = keskeis, 1 = vastavirta

    @property
    def dx(self) -> float:
        return self.lx / self.nx

    @property
    def dy(self) -> float:
        return self.ly / self.ny


@dataclass
class Tila:
    u: Taulukko
    v: Taulukko
    p: Taulukko
    t: float = 0.0
    edellinen: tuple[Taulukko, Taulukko] | None = None   # kiihtyvyydet
# @loppu tehtava


# @alku operaattorit
def divergenssi(teht: Tehtava, u: Taulukko, v: Taulukko) -> Taulukko:
    """Ruudusta lähtevä tilavuusvirta tilavuutta kohden."""
    tulos: Taulukko = ((u[1:, :] - u[:-1, :]) / teht.dx
                       + (v[:, 1:] - v[:, :-1]) / teht.dy)
    return tulos


def vuo(a: Taulukko, b: Taulukko, kuljettaja: Taulukko, gamma: float
        ) -> Taulukko:
    """Suureen vuo pinnan läpi puolelta a puolelle b.

    gamma = 0: pinnan arvo on keskiarvo. gamma = 1: arvo otetaan
    tulosuunnasta. Väliarvot sekoittavat kaaviot."""
    tulos: Taulukko = (kuljettaja * 0.5 * (a + b)
                       + gamma * np.abs(kuljettaja) * 0.5 * (a - b))
    return tulos
# @loppu operaattorit


class Ratkaisija:
    """Kokoaa paineyhtälön kerran ja ottaa aika-askeleita."""

    # @alku pinnat
    def __init__(self, teht: Tehtava) -> None:
        if teht.oikea.laji == "sisään" or "sisään" in (teht.ala.laji,
                                                       teht.yla.laji):
            raise ValueError("sisäänvirtaus on tuettu vain vasemmalla")
        if "ulos" in (teht.vasen.laji, teht.ala.laji, teht.yla.laji):
            raise ValueError("ulosvirtaus on tuettu vain oikealla")
        self.teht = teht
        nx, ny = teht.nx, teht.ny
        neste = (np.ones((nx, ny), dtype=np.bool_) if teht.este is None
                 else ~teht.este)
        self.neste: Maski = neste
        # Avoin pinta: nopeus on tuntematon ja paine korjaa sitä.
        self.auki_u: Maski = np.zeros((nx + 1, ny), dtype=np.bool_)
        self.auki_u[1:-1, :] = neste[:-1, :] & neste[1:, :]
        self.auki_v: Maski = np.zeros((nx, ny + 1), dtype=np.bool_)
        self.auki_v[:, 1:-1] = neste[:, :-1] & neste[:, 1:]
        self.ulos: Maski = np.zeros(ny, dtype=np.bool_)
        if teht.oikea.laji == "ulos":
            self.ulos = neste[-1, :].copy()
        self._lu = splu(self._painematriisi().tocsc())
    # @loppu pinnat

    # @alku painematriisi
    def _painematriisi(self) -> sp.csr_array:
        """-div(grad) avoimien pintojen yli: positiivisesti definiitti."""
        teht = self.teht
        nro = np.arange(teht.nx * teht.ny).reshape(teht.nx, teht.ny)
        rivit, sarakkeet, arvot = [], [], []
        lavistaja = np.zeros((teht.nx, teht.ny))
        for auki, a, b, paino in (
                (self.auki_u[1:-1, :], nro[:-1, :], nro[1:, :], teht.dx**-2),
                (self.auki_v[:, 1:-1], nro[:, :-1], nro[:, 1:], teht.dy**-2)):
            ia, ib = a[auki], b[auki]
            rivit += [ia, ib]
            sarakkeet += [ib, ia]
            arvot += [np.full(ia.size, -paino)] * 2
            np.add.at(lavistaja.ravel(), ia, paino)
            np.add.at(lavistaja.ravel(), ib, paino)
        # Ulosvirtausreunalla paine on nolla puolen ruudun päässä.
        lavistaja[-1, self.ulos] += 2.0 * teht.dx**-2
        # Kiinteissä ruuduissa painetta ei ole: yhtälöksi p = 0.
        lavistaja[~self.neste] = 1.0
        if not self.ulos.any():
            # Pelkät seinät: paine on määrätty vain vakiota vaille, joten
            # yksi ruutu kiinnitetään.
            eka = int(np.flatnonzero(self.neste.ravel())[0])
            lavistaja.ravel()[eka] += teht.dx**-2
        rivit.append(nro.ravel())
        sarakkeet.append(nro.ravel())
        arvot.append(lavistaja.ravel())
        n = teht.nx * teht.ny
        paikat = (np.concatenate(rivit), np.concatenate(sarakkeet))
        return sp.coo_array((np.concatenate(arvot), paikat),
                            shape=(n, n)).tocsr()
    # @loppu painematriisi

    # @alku reunat
    def reunat(self, u: Taulukko, v: Taulukko) -> None:
        """Asettaa nopeudet suljetuille pinnoille: seinät, sisäänvirtaus
        ja esteen pinnat."""
        teht = self.teht
        u[0, :] = teht.vasen.nopeus if teht.vasen.laji == "sisään" else 0.0
        if teht.oikea.laji != "ulos":
            u[-1, :] = 0.0
        v[:, 0] = 0.0
        v[:, -1] = 0.0
        if teht.este is None:
            return
        u[1:-1, :][~self.auki_u[1:-1, :]] = 0.0
        v[:, 1:-1][~self.auki_v[:, 1:-1]] = 0.0
        # Esteen sisällä oleva pinta toimii haamupisteenä: peilikuva
        # viereisestä virtaavasta pinnasta tekee nopeudesta nollan
        # esteen pinnalla.
        sisa_u = np.zeros_like(self.auki_u)
        sisa_u[1:-1, :] = teht.este[:-1, :] & teht.este[1:, :]
        peili = sisa_u[:, :-1] & self.auki_u[:, 1:]
        u[:, :-1][peili] = -u[:, 1:][peili]
        peili = sisa_u[:, 1:] & self.auki_u[:, :-1]
        u[:, 1:][peili] = -u[:, :-1][peili]
        sisa_v = np.zeros_like(self.auki_v)
        sisa_v[:, 1:-1] = teht.este[:, :-1] & teht.este[:, 1:]
        peili = sisa_v[:-1, :] & self.auki_v[1:, :]
        v[:-1, :][peili] = -v[1:, :][peili]
        peili = sisa_v[1:, :] & self.auki_v[:-1, :]
        v[1:, :][peili] = -v[:-1, :][peili]

    def _haamut(self, u: Taulukko, v: Taulukko) -> tuple[Taulukko, Taulukko]:
        """Lisää u:lle haamurivit ala- ja yläreunan taakse ja v:lle
        haamusarakkeet vasemman ja oikean reunan taakse."""
        def haamu(reuna: Reuna, sisin: Taulukko) -> Taulukko:
            if reuna.laji == "seinä":
                tulos: Taulukko = 2.0 * reuna.nopeus - sisin
                return tulos
            if reuna.laji == "sisään":
                return -sisin              # ei sivuttaisnopeutta
            return sisin                   # liukuva ja ulos: gradientti 0

        teht = self.teht
        ue = np.empty((teht.nx + 1, teht.ny + 2))
        ue[:, 1:-1] = u
        ue[:, 0] = haamu(teht.ala, u[:, 0])
        ue[:, -1] = haamu(teht.yla, u[:, -1])
        ve = np.empty((teht.nx + 2, teht.ny + 1))
        ve[1:-1, :] = v
        ve[0, :] = haamu(teht.vasen, v[0, :])
        ve[-1, :] = haamu(teht.oikea, v[-1, :])
        return ue, ve
    # @loppu reunat

    # @alku kiihtyvyys
    def kiihtyvyys(self, u: Taulukko, v: Taulukko
                   ) -> tuple[Taulukko, Taulukko]:
        """Liikemäärän tase ilman painetta: -div(u u) + nu lap(u).

        Palauttaa du/dt sisäpinnoille; reunapintojen arvot ovat nollia."""
        teht = self.teht
        dx, dy, nu, g = teht.dx, teht.dy, teht.nu, teht.vastavirta
        ue, ve = self._haamut(u, v)
        au = np.zeros_like(u)
        av = np.zeros_like(v)

        # u-liikemäärä pinnalla i: vuot ruutujen keskellä ja kulmissa.
        fxx = vuo(u[:-1, :], u[1:, :], 0.5 * (u[:-1, :] + u[1:, :]), g)
        fxy = vuo(ue[1:-1, :-1], ue[1:-1, 1:],
                  0.5 * (ve[1:-2, :] + ve[2:-1, :]), g)
        au[1:-1, :] = (
            -(fxx[1:, :] - fxx[:-1, :]) / dx - (fxy[:, 1:] - fxy[:, :-1]) / dy
            + nu * ((u[2:, :] - 2.0 * u[1:-1, :] + u[:-2, :]) / dx**2
                    + (ue[1:-1, 2:] - 2.0 * ue[1:-1, 1:-1] + ue[1:-1, :-2])
                    / dy**2))

        # v-liikemäärä pinnalla j samalla tavalla.
        fyy = vuo(v[:, :-1], v[:, 1:], 0.5 * (v[:, :-1] + v[:, 1:]), g)
        fyx = vuo(ve[:-1, 1:-1], ve[1:, 1:-1],
                  0.5 * (ue[:, 1:-2] + ue[:, 2:-1]), g)
        av[:, 1:-1] = (
            -(fyy[:, 1:] - fyy[:, :-1]) / dy - (fyx[1:, :] - fyx[:-1, :]) / dx
            + nu * ((ve[2:, 1:-1] - 2.0 * ve[1:-1, 1:-1] + ve[:-2, 1:-1])
                    / dx**2
                    + (v[:, 2:] - 2.0 * v[:, 1:-1] + v[:, :-2]) / dy**2))
        return au, av
    # @loppu kiihtyvyys

    # @alku projektio
    def projisoi(self, u: Taulukko, v: Taulukko) -> Taulukko:
        """Tekee kentästä (u, v) lähteettömän paikallaan ja palauttaa
        potentiaalin phi: u <- u - grad(phi)."""
        teht = self.teht
        oikea = -divergenssi(teht, u, v)
        oikea[~self.neste] = 0.0
        phi: Taulukko = self._lu.solve(oikea.ravel())
        phi = phi.reshape(teht.nx, teht.ny)
        gx = (phi[1:, :] - phi[:-1, :]) / teht.dx
        gy = (phi[:, 1:] - phi[:, :-1]) / teht.dy
        u[1:-1, :][self.auki_u[1:-1, :]] -= gx[self.auki_u[1:-1, :]]
        v[:, 1:-1][self.auki_v[:, 1:-1]] -= gy[self.auki_v[:, 1:-1]]
        # Ulosvirtauspinta: phi = 0 pinnalla, etäisyys dx / 2.
        u[-1, self.ulos] += 2.0 * phi[-1, self.ulos] / teht.dx
        return phi
    # @loppu projektio

    # @alku askel
    def askel(self, tila: Tila, dt: float, kaavio: str = "AB2") -> Tila:
        """Yksi aika-askel. kaavio on "Euler" tai "AB2" (Adams–Bashforth,
        joka käyttää myös edellisen askeleen kiihtyvyyttä)."""
        u, v = tila.u.copy(), tila.v.copy()
        self.reunat(u, v)
        au, av = self.kiihtyvyys(u, v)
        if kaavio == "AB2" and tila.edellinen is not None:
            eu, ev = tila.edellinen
            du, dv = 1.5 * au - 0.5 * eu, 1.5 * av - 0.5 * ev
        else:
            du, dv = au, av
        # 1. Ennustus: liikemäärän tase ilman painetta.
        u[self.auki_u] += dt * du[self.auki_u]
        v[self.auki_v] += dt * dv[self.auki_v]
        if self.ulos.any():
            u[-1, self.ulos] = u[-2, self.ulos]    # ulos: du/dx = 0
        # 2. ja 3. Paineyhtälö ja korjaus.
        phi = self.projisoi(u, v)
        self.reunat(u, v)
        return Tila(u, v, phi / dt, tila.t + dt, (au, av))
    # @loppu askel

    def lepotila(self) -> Tila:
        teht = self.teht
        u = np.zeros((teht.nx + 1, teht.ny))
        v = np.zeros((teht.nx, teht.ny + 1))
        self.reunat(u, v)
        return Tila(u, v, np.zeros((teht.nx, teht.ny)))


# @alku apu
def keskinopeudet(u: Taulukko, v: Taulukko) -> tuple[Taulukko, Taulukko]:
    """Nopeudet ruutujen keskipisteissä pintojen keskiarvoina."""
    return 0.5 * (u[:-1, :] + u[1:, :]), 0.5 * (v[:, :-1] + v[:, 1:])


def liike_energia(teht: Tehtava, u: Taulukko, v: Taulukko) -> float:
    uc, vc = keskinopeudet(u, v)
    return 0.5 * float(np.sum(uc**2 + vc**2)) * teht.dx * teht.dy


def virtafunktio(teht: Tehtava, u: Taulukko) -> Taulukko:
    """psi ruutujen kulmissa (nx + 1, ny + 1): u = d(psi)/dy, psi = 0
    alareunalla. Tasa-arvokäyrät ovat virtaviivoja."""
    psi = np.zeros((teht.nx + 1, teht.ny + 1))
    psi[:, 1:] = np.cumsum(u, axis=1) * teht.dy
    return psi


def pyorteisyys(teht: Tehtava, u: Taulukko, v: Taulukko) -> Taulukko:
    """dv/dx - du/dy alueen sisäkulmissa (nx - 1, ny - 1)."""
    tulos: Taulukko = ((v[1:, 1:-1] - v[:-1, 1:-1]) / teht.dx
                       - (u[1:-1, 1:] - u[1:-1, :-1]) / teht.dy)
    return tulos


def tasapainoon(ratkaisija: Ratkaisija, tila: Tila, dt: float,
                raja: float = 1e-6, kaavio: str = "AB2",
                enintaan: int = 200_000) -> tuple[Tila, int]:
    """Ottaa askelia, kunnes nopeuden muutosnopeus on alle rajan.
    Palauttaa tilan ja otettujen askelten määrän."""
    for k in range(1, enintaan + 1):
        uusi = ratkaisija.askel(tila, dt, kaavio)
        muutos = max(float(np.max(np.abs(uusi.u - tila.u))),
                     float(np.max(np.abs(uusi.v - tila.v)))) / dt
        tila = uusi
        if muutos < raja:
            return tila, k
    raise RuntimeError("tasapainoa ei saavutettu")


def vakaa_askel(teht: Tehtava, suurin_nopeus: float, kaavio: str = "AB2"
                ) -> float:
    """Aika-askel kaavion stabiilisuusrajoista varmuusvaralla.

    Diffuusio: Euler h² / (4 nu), AB2 puolet siitä. Advektio
    keskeisdifferenssillä: Euler 2 nu / U², AB2 Courantin luku."""
    h = min(teht.dx, teht.dy)
    if kaavio == "Euler":
        return min(0.2 * h**2 / teht.nu, teht.nu / suurin_nopeus**2)
    return min(0.1 * h**2 / teht.nu, 0.3 * h / suurin_nopeus)
# @loppu apu
