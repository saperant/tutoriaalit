"""Mittarit versionhallinnan historiasta: muutoksen koko ja kiertoaika.

Esimerkki luo ensin pienen repositorion, jotta tulos on aina sama.
Omassa projektissa riittää jälkimmäinen puolisko: git log ja laskenta.
"""

import os
import statistics
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

YMPARISTO = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull,
             "GIT_CONFIG_NOSYSTEM": "1", "TZ": "UTC",
             "GIT_AUTHOR_NAME": "Tiimi", "GIT_AUTHOR_EMAIL": "t@example.org",
             "GIT_COMMITTER_NAME": "Tiimi",
             "GIT_COMMITTER_EMAIL": "t@example.org"}
ALKU = date(2026, 3, 2)     # maanantai


def git(*argumentit: str, paiva: int = 0) -> str:
    hetki = f"{ALKU + timedelta(days=paiva)}T12:00:00+00:00"
    ymparisto = {**YMPARISTO, "GIT_AUTHOR_DATE": hetki,
                 "GIT_COMMITTER_DATE": hetki}
    return subprocess.run(["git", *argumentit], env=ymparisto, check=True,
                          capture_output=True, text=True).stdout


# (päivä, tehtävä, tiedosto, lisättäviä rivejä)
MUUTOKSET = [
    (0, "T-1", "haku.py", 40), (1, "T-1", "haku.py", 25),
    (1, "T-2", "kori.py", 60), (2, "T-1", "testit.py", 30),
    (3, "T-2", "kori.py", 20), (4, "T-3", "maksu.py", 420),
    (8, "T-2", "testit.py", 35), (9, "T-4", "haku.py", 15),
    (10, "T-4", "testit.py", 10), (11, "T-5", "tuonti.py", 80),
    (15, "T-5", "tuonti.py", 45), (16, "T-3", "maksu.py", 150),
    (17, "T-6", "kori.py", 30), (18, "T-6", "testit.py", 25),
    (22, "T-5", "testit.py", 40), (23, "T-3", "testit.py", 90),
]

git("init", "-q", "-b", "main")
for paiva, tehtava, tiedosto, riveja in MUUTOKSET:
    with Path(tiedosto).open("a", encoding="utf-8") as f:
        f.writelines(f"# {tehtava} rivi {i}\n" for i in range(riveja))
    git("add", tiedosto)
    git("commit", "-q", "-m", f"{tehtava}: muutos", paiva=paiva)

# @alku loki
# Yksi otsikkorivi muutosta kohden ja sen perässä tiedostojen rivimäärät.
loki = git("log", "--reverse", "--numstat", "--format=@%aI %s")
muutokset: list[tuple[datetime, str, int]] = []
for rivi in loki.splitlines():
    if rivi.startswith("@"):
        aika, tehtava = rivi[1:].split(" ")[:2]
        muutokset.append((datetime.fromisoformat(aika),
                          tehtava.rstrip(":"), 0))
    elif rivi:
        lisatty, poistettu = rivi.split("\t")[:2]
        hetki, tehtava, koko = muutokset[-1]
        muutokset[-1] = (hetki, tehtava, koko + int(lisatty) + int(poistettu))
# @loppu loki

# @alku mittarit
koot = sorted(koko for _, _, koko in muutokset)
viikot = {hetki.isocalendar().week for hetki, _, _ in muutokset}
print(f"muutoksia {len(koot)}, viikossa {len(koot) / len(viikot):.1f}")
print(f"muutoksen koko: mediaani {statistics.median(koot):.0f} riviä, "
      f"suurin {koot[-1]} riviä")
print(f"yli 200 rivin muutoksia {sum(k > 200 for k in koot)}")

# Tehtävän kiertoaika: ensimmäisestä muutoksesta viimeiseen.
ajat: dict[str, list[datetime]] = {}
for hetki, tehtava, _ in muutokset:
    ajat.setdefault(tehtava, []).append(hetki)
kierrot = {t: (max(a) - min(a)).days + 1 for t, a in ajat.items()}
for tunnus, kierto in sorted(kierrot.items()):
    print(f"  {tunnus}: {kierto:2d} pv, {len(ajat[tunnus])} muutosta")
print(f"kiertoajan mediaani {statistics.median(kierrot.values()):.1f} pv")
# @loppu mittarit
