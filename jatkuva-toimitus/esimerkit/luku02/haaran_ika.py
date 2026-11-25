"""Ristiriidan todennäköisyys haaran iän funktiona.

Ensin mallin sääntö tarkistetaan oikealla Gitillä pienissä
repositorioissa, sitten mallilla lasketaan suuri määrä haaroja.
"""

import random
import tempfile
from pathlib import Path

from toimitus.gitapu import alusta, git, tallenna
from toimitus.haarat import Repo, Rivi, kokeile, muutokset, ristiriidat


def kirjoita(hak: Path, repo: Repo, muutetut: set[Rivi], kuka: str) -> None:
    """Kirjoittaa tiedostot niin, että muutetuilla riveillä on uusi teksti."""
    for tiedosto in range(repo.tiedostoja):
        rivit = [f"{kuka} {rivi}" if (tiedosto, rivi) in muutetut
                 else f"rivi {rivi}" for rivi in range(repo.riveja)]
        (hak / f"t{tiedosto}.txt").write_text("\n".join(rivit) + "\n")


def git_ristiriita(repo: Repo, runko: set[Rivi], haara: set[Rivi]) -> bool:
    """Tekee samat muutokset oikeaan repositorioon ja yhdistää."""
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        alusta(hak)
        kirjoita(hak, repo, set(), "")
        tallenna(hak, "Lähtötilanne")
        git(hak, "checkout", "-q", "-b", "haara")
        kirjoita(hak, repo, haara, "haara")
        tallenna(hak, "Haaran muutokset")
        git(hak, "checkout", "-q", "main")
        kirjoita(hak, repo, runko, "runko")
        tallenna(hak, "Rungon muutokset")
        tulos = git(hak, "merge", "-q", "--no-edit", "haara",
                    saa_epaonnistua=True)
        return tulos.returncode != 0


# @alku tarkistus
pieni = Repo(tiedostoja=2, riveja=12)
arpa = random.Random(7)
samat = ristiriitaisia = 0
for _ in range(12):
    runko = muutokset(arpa, pieni, 3)
    haara = muutokset(arpa, pieni, 2) - runko or {(0, 0)}
    malli = ristiriidat(runko, haara) > 0
    samat += malli == git_ristiriita(pieni, runko, haara)
    ristiriitaisia += malli
print(f"malli ja Git samaa mieltä: {samat}/12 "
      f"(ristiriitaisia {ristiriitaisia})")
# @loppu tarkistus

# @alku taulukko
repo = Repo()
print(f"\n{repo.tiedostoja} tiedostoa, {repo.riveja} riviä kussakin")
print(f"muutettuja rivejä päivässä: runkoon {repo.runko_paivassa}, "
      f"haaraan {repo.haara_paivassa}")
print(f"{'haaran ikä':>10}{'ristiriita':>12}{'kohtia ka.':>12}")
for ika in (1, 2, 3, 5, 8, 13):
    osuus, kohtia = kokeile(repo, ika, toistoja=2000)
    print(f"{ika:>8} pv{osuus:>11.0%}{kohtia:>12.2f}")
# @loppu taulukko
