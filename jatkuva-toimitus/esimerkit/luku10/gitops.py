"""GitOps pienoiskoossa: Git on haluttu tila, agentti täsmäyttää.

Repositoriossa on tiedosto tila.json. Agentti lukee sen rungon
kärjestä, vertaa klusterin tilaan ja korjaa erot. Käyttöönotto on
commit, peruminen on revert, ja käsin tehty muutos korjautuu itsestään.
"""

import json
import tempfile
from pathlib import Path

from toimitus.gitapu import alusta, git, tallenna
from toimitus.tasmaytys import Tila, toteuta, tulosta


# @alku agentti
def tasmayta(repo: Path, klusteri: Tila) -> None:
    """Yksi kierros: lue haluttu tila Gitistä ja korjaa erot."""
    haluttu: Tila = json.loads(git(repo, "show", "HEAD:tila.json").stdout)
    viesti = git(repo, "log", "-1", "--format=%s").stdout.strip()
    print(f"täsmäytys (rungon kärki: {viesti})")
    tulosta(toteuta(haluttu, klusteri))
# @loppu agentti


def muuta(repo: Path, tila: Tila, viesti: str, aika: str) -> None:
    (repo / "tila.json").write_text(json.dumps(tila, indent=2) + "\n")
    tallenna(repo, viesti, aika=aika)


with tempfile.TemporaryDirectory() as tmp:
    repo = Path(tmp)
    alusta(repo)
    klusteri: Tila = {}

    tila: Tila = {"verkkopalvelu": {"kopioita": 2, "versio": "1.4.0"}}
    muuta(repo, tila, "Verkkopalvelu 1.4.0", "2026-03-02T09:00:00+00:00")
    tasmayta(repo, klusteri)
    tasmayta(repo, klusteri)                 # mikään ei muuttunut

    klusteri["verkkopalvelu"]["kopioita"] = 5    # käsin, Gitin ohi
    tasmayta(repo, klusteri)

    tila["verkkopalvelu"]["versio"] = "1.5.0"
    muuta(repo, tila, "Verkkopalvelu 1.5.0", "2026-03-03T09:00:00+00:00")
    tasmayta(repo, klusteri)

    # Versio 1.5.0 on viallinen: peruminen on tavallinen Git-muutos.
    git(repo, "revert", "--no-edit", "HEAD",
        aika="2026-03-03T09:20:00+00:00")
    tasmayta(repo, klusteri)
    historia = git(repo, "log", "--reverse", "--format=%s").stdout
    print("historia:")
    for rivi in historia.splitlines():
        print(f"  {rivi}")
