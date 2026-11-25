"""Näppäilty kieli: aaltoyhtälö keskeisdifferensseillä.

Kieli (pituus 1, aallon nopeus 1) vedetään kolmioksi kohdasta 0,3 ja
päästetään irti. Tarkka ratkaisu toistuu jaksolla 2: jakson jälkeen
kielen pitää olla täsmälleen alkuasennossaan."""

import numpy as np
import numpy.typing as npt

Taulukko = npt.NDArray[np.float64]
N = 100                          # välejä; h = 1/N


def alkuasento() -> Taulukko:
    x = np.linspace(0.0, 1.0, N + 1)
    u: Taulukko = np.where(x < 0.3, x / 0.3, (1.0 - x) / 0.7) * 0.01
    return u


# @alku askel
def aloitus(u0: Taulukko, c: float) -> Taulukko:
    """Ensimmäinen askel levosta: Taylorin kehitelmä, jossa u_tt on
    korvattu yhtälöstä. c on Courantin luku (aallon nopeus) dt / h."""
    u1 = u0.copy()
    u1[1:-1] += 0.5 * c * c * (u0[2:] - 2.0 * u0[1:-1] + u0[:-2])
    return u1


def askel(u: Taulukko, vanha: Taulukko, c: float) -> Taulukko:
    """u_uusi = 2u - u_vanha + c² (toinen differenssi). Päät kiinni."""
    uusi = np.zeros_like(u)
    uusi[1:-1] = (2.0 * u[1:-1] - vanha[1:-1]
                  + c * c * (u[2:] - 2.0 * u[1:-1] + u[:-2]))
    return uusi
# @loppu askel


# @alku energia
def energia(u: Taulukko, vanha: Taulukko, c: float) -> float:
    """Kaavion säilyttämä diskreetti energia (yksikkötiheys ja -jännitys).
    Liike-energia on askelten välissä, potentiaalienergia kahden
    peräkkäisen muodon tulona."""
    h = 1.0 / N
    dt = c * h
    liike = 0.5 * float(np.sum(((u - vanha) / dt) ** 2)) * h
    potentiaali = 0.5 * float(np.sum(np.diff(u) * np.diff(vanha))) / h
    return liike + potentiaali
# @loppu energia


# @alku koe
print("Courant  askelia/jakso  virhe jakson jälkeen  energian muutos")
for c, askelia in ((1.0, 200), (0.8, 250), (0.5, 400)):
    vanha = alkuasento()
    u = aloitus(vanha, c)
    e0 = energia(u, vanha, c)
    suurin_muutos = 0.0
    for _ in range(askelia - 1):
        u, vanha = askel(u, vanha, c), u
        suurin_muutos = max(suurin_muutos,
                            abs(energia(u, vanha, c) - e0) / e0)
    virhe = float(np.max(np.abs(u - alkuasento()))) / 0.01
    # Pyöristysvirheen tasoiset luvut vaihtelevat koneittain.
    v = f"{virhe:.1e}" if virhe > 1e-12 else "alle 1e-12"
    e = "alle 1e-12" if suurin_muutos < 1e-12 else f"{suurin_muutos:.1e}"
    print(f"{c:7.1f} {askelia:14d} {v:>21} {e:>16}")
# @loppu koe
