"""Neljä mittaria kahden tiimin julkaisuhistoriasta.

Historia luodaan Git-repositorioon: muutokset ovat commiteja, julkaisut
tageja julkaisu-N ja epäonnistuneen julkaisun korjaus tagi korjaus-N.
Mittarit lasketaan repositoriosta, ei käsin pidetystä taulukosta.
"""

import tempfile
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path

from toimitus.dora import OTSIKKO, Julkaisu, laske, rivi
from toimitus.gitapu import alusta, git

ALKU = datetime.fromisoformat("2026-03-02T00:00:00+00:00")   # maanantai
VIIKKOJA = 6


def hetki(paiva: int, tunti: float) -> datetime:
    return ALKU + timedelta(days=paiva, hours=tunti)


def luo_historia(repo: Path, julkaisupaivat: set[int],
                 viat: dict[int, float]) -> None:
    """Kaksi muutosta joka arkipäivä; julkaisu valittuina päivinä klo 16."""
    alusta(repo)
    nro = 0
    for paiva in range(VIIKKOJA * 7):
        if paiva % 7 >= 5:                       # viikonloppu
            continue
        for tunti in (10, 14):
            aika = hetki(paiva, tunti).isoformat()
            git(repo, "commit", "-q", "--allow-empty", "-m",
                f"Muutos {paiva}/{tunti}", aika=aika)
        if paiva % 7 in julkaisupaivat:
            nro += 1
            julkaistu = hetki(paiva, 16)
            git(repo, "tag", "-a", f"julkaisu-{nro:02}", "-m", "Julkaisu",
                aika=julkaistu.isoformat())
            if nro in viat:                      # korjaus tunteja myöhemmin
                korjaus = (julkaistu
                           + timedelta(hours=viat[nro])).isoformat()
                git(repo, "commit", "-q", "--allow-empty", "-m",
                    f"Korjaus julkaisuun {nro}", aika=korjaus)
                git(repo, "tag", "-a", f"korjaus-{nro:02}", "-m", "Korjaus",
                    aika=korjaus)


# @alku lue
def lue_historia(repo: Path) -> list[Julkaisu]:
    """Lukee julkaisut, niiden muutokset ja korjaukset tageista."""
    tagit = dict(
        rivi.split(" ", 1) for rivi in git(
            repo, "for-each-ref", "refs/tags",
            "--format=%(refname:short) %(creatordate:iso-strict)",
        ).stdout.splitlines())
    julkaisut = []
    edellinen = ""
    for nimi in sorted(t for t in tagit if t.startswith("julkaisu-")):
        vali = f"{edellinen}..{nimi}" if edellinen else nimi
        loki = git(repo, "log", "--format=%aI %s", vali).stdout.splitlines()
        muutokset = tuple(datetime.fromisoformat(r.split(" ", 1)[0])
                          for r in loki if " Muutos " in r)
        korjaus = tagit.get(nimi.replace("julkaisu", "korjaus"))
        julkaisut.append(Julkaisu(
            datetime.fromisoformat(tagit[nimi]), muutokset,
            datetime.fromisoformat(korjaus) if korjaus else None))
        edellinen = nimi
    return julkaisut
# @loppu lue


def pilko(julkaisut: list[Julkaisu], osia: int) -> list[Julkaisu]:
    """Sama viikkojulkaisu ilmoitettuna viitenä: mittarin pelaamista."""
    tulos = []
    for j in julkaisut:
        for osa in range(osia):
            tulos.append(replace(
                j, hetki=j.hetki + timedelta(minutes=10 * osa),
                muutokset=j.muutokset[osa::osia],
                korjattu=j.korjattu if osa == 0 else None))
    return tulos


with tempfile.TemporaryDirectory() as tmp:
    viikoittain = Path(tmp) / "viikoittain"
    paivittain = Path(tmp) / "paivittain"
    luo_historia(viikoittain, {4}, viat={2: 22, 5: 65})
    luo_historia(paivittain, {0, 1, 2, 3, 4}, viat={7: 1, 19: 2})
    viikko = lue_historia(viikoittain)
    paiva = lue_historia(paivittain)

print(OTSIKKO)
print(rivi("viikkojulkaisu", laske(viikko, VIIKKOJA)))
print(rivi("julkaisu joka päivä", laske(paiva, VIIKKOJA)))
print(rivi("viikko, pilkottu 5:ksi", laske(pilko(viikko, 5), VIIKKOJA)))
