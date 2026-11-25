"""Luo esimerkkiyrityksen Git-historian ja lukee sen takaisin.

Historia arvotaan kiinteällä siemenellä, joten tulos on aina sama.
Omassa projektissa tarvitaan vain funktiota lue_loki: analyysit
käyttävät pelkkää git log -komennon tulostetta.
"""

import os
import random
import subprocess
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from organisaatio import KERROKSET, OMINAISUUDET, OSAT

YMPARISTO = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
             "GIT_CONFIG_NOSYSTEM": "1", "TZ": "UTC"}
ALKU = date(2026, 1, 5)

# Kolme kehittäjää ominaisuutta kohden ja heidän osuutensa muutoksista.
TEKIJAT = {
    "haku": (["Aino", "Eero", "Ilona"], [1, 1, 1]),
    "kori": (["Juho", "Kaisa", "Lauri"], [2, 1, 1]),
    "tilaus": (["Minna", "Niko", "Outi"], [3, 2, 1]),
    "maksu": (["Pekka", "Riitta", "Sami"], [17, 2, 1]),
}


@dataclass(frozen=True)
class Muutos:
    tekija: str
    osat: tuple[str, ...]


def suunnitelma(siemen: int = 7, maara: int = 160) -> list[Muutos]:
    """Arpoo muutokset: enimmäkseen yhden ominaisuuden sisäisiä."""
    rng = random.Random(siemen)
    kerrosyhdistelmat = [("ui", "api", "db"), ("ui", "api"), ("api", "db"),
                         ("ui",), ("api",), ("db",)]
    muutokset = []
    for _ in range(maara):
        ominaisuus = rng.choices(OMINAISUUDET, [3, 3, 2, 2])[0]
        nimet, painot = TEKIJAT[ominaisuus]
        tekija = rng.choices(nimet, painot)[0]
        laji = rng.random()
        if laji < 0.70:        # ominaisuuden kehitys tai korjaus
            kerrokset = rng.choices(kerrosyhdistelmat,
                                    [40, 25, 20, 5, 5, 5])[0]
            osat = tuple(f"{ominaisuus}/{k}" for k in kerrokset)
        elif laji < 0.85:      # kahden ominaisuuden rajapinta
            osat = rng.choice([("tilaus/api", "maksu/api"),
                               ("tilaus/api", "tilaus/db", "maksu/api"),
                               ("kori/api", "haku/api")])
        else:                  # koko kerroksen läpi menevä muutos
            kerros = rng.choice(KERROKSET)
            osat = tuple(f"{o}/{kerros}" for o in OMINAISUUDET)
        muutokset.append(Muutos(tekija, tuple(sorted(osat))))
    return muutokset


def git(*argumentit: str, tekija: str = "", paiva: int = 0) -> str:
    hetki = f"{ALKU + timedelta(days=paiva)}T12:00:00+00:00"
    osoite = f"{tekija.lower()}@example.org"
    ymparisto = {**YMPARISTO, "GIT_AUTHOR_DATE": hetki,
                 "GIT_COMMITTER_DATE": hetki, "GIT_AUTHOR_NAME": tekija,
                 "GIT_AUTHOR_EMAIL": osoite, "GIT_COMMITTER_NAME": tekija,
                 "GIT_COMMITTER_EMAIL": osoite}
    return subprocess.run(["git", *argumentit], env=ymparisto, check=True,
                          capture_output=True, text=True).stdout


def luo_repositorio() -> None:
    """Tekee työhakemistoon repositorion, jossa on suunnitelman historia."""
    git("init", "-q", "-b", "main")
    for o in OMINAISUUDET:
        Path(o).mkdir()
    for nro, muutos in enumerate(suunnitelma()):
        for osa in muutos.osat:
            with Path(f"{osa}.py").open("a", encoding="utf-8") as f:
                f.write(f"# muutos {nro}\n")
        git("add", "-A")
        git("commit", "-q", "-m", f"muutos {nro}", tekija=muutos.tekija,
            paiva=nro // 2)


# @alku loki
def lue_loki() -> list[Muutos]:
    """Jokaisesta muutoksesta tekijä ja muutetut osat."""
    loki = git("log", "--reverse", "--name-only", "--format=@%an")
    muutokset: list[Muutos] = []
    for rivi in loki.splitlines():
        if rivi.startswith("@"):
            muutokset.append(Muutos(rivi[1:], ()))
        elif rivi:
            edellinen = muutokset[-1]
            osa = rivi.removesuffix(".py")
            muutokset[-1] = Muutos(edellinen.tekija, (*edellinen.osat, osa))
    return muutokset
# @loppu loki


if __name__ == "__main__":
    luo_repositorio()
    historia = lue_loki()
    assert historia == suunnitelma()
    assert {osa for m in historia for osa in m.osat} == set(OSAT)
    print(f"muutoksia {len(historia)}, "
          f"tekijöitä {len({m.tekija for m in historia})}, "
          f"tiedostoja {len(OSAT)}")
    useita = sum(len(m.osat) > 1 for m in historia)
    print(f"useaan tiedostoon koskevia muutoksia {useita}")
