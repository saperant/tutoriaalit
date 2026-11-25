"""Apufunktiot esimerkkien väliaikaisille Git-repositorioille.

Tekijä, aika ja asetukset kiinnitetään, jotta historia on sama joka
koneella. Käyttäjän omat Git-asetukset eivät vaikuta ajoon.
"""

import os
import subprocess
from pathlib import Path

KIINTEA = {
    "GIT_AUTHOR_NAME": "Esimerkki",
    "GIT_AUTHOR_EMAIL": "esimerkki@example.invalid",
    "GIT_COMMITTER_NAME": "Esimerkki",
    "GIT_COMMITTER_EMAIL": "esimerkki@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "LC_ALL": "C",
    "TZ": "UTC",
}
ALKUHETKI = "2026-03-02T08:00:00+00:00"


def git(hak: Path, *argumentit: str, aika: str = ALKUHETKI,
        saa_epaonnistua: bool = False) -> subprocess.CompletedProcess[str]:
    """Ajaa git-komennon hakemistossa kiinteällä ympäristöllä."""
    ymparisto = {**os.environ, **KIINTEA,
                 "GIT_AUTHOR_DATE": aika, "GIT_COMMITTER_DATE": aika}
    tulos = subprocess.run(["git", *argumentit], cwd=hak, env=ymparisto,
                           capture_output=True, text=True, check=False)
    if tulos.returncode != 0 and not saa_epaonnistua:
        raise RuntimeError(f"git {' '.join(argumentit)}: {tulos.stderr}")
    return tulos


def alusta(hak: Path) -> None:
    """Luo tyhjän repositorion, jonka päähaara on main."""
    hak.mkdir(parents=True, exist_ok=True)
    git(hak, "init", "-q", "-b", "main")


def tallenna(hak: Path, viesti: str, aika: str = ALKUHETKI) -> None:
    """Lisää kaikki muutokset ja tekee commitin."""
    git(hak, "add", "-A")
    git(hak, "commit", "-q", "-m", viesti, aika=aika)
