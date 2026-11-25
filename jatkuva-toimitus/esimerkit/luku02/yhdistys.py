"""Kolme yhdistämistä: siisti, ristiriitainen ja siisti mutta rikkinäinen.

Jokainen tapaus tehdään omaan väliaikaiseen repositorioon: yhteinen
lähtötilanne, yksi muutos haarassa ja yksi rungossa, sitten yhdistys.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

from toimitus.gitapu import alusta, git, tallenna

LASKUT = '''\
ALV = 24


def summa(rivit):
    return sum(rivit)
'''
RAPORTTI = '''\
from laskut import summa

print("yhteensä", summa([10, 20, 30]))
'''


def kokeile(nimi: str, haara: dict[str, str], runko: dict[str, str],
            ajettava: str) -> None:
    """Tekee muutokset haaraan ja runkoon, yhdistää ja ajaa ohjelman."""
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        alusta(hak)
        (hak / "laskut.py").write_text(LASKUT, "utf-8")
        (hak / "raportti.py").write_text(RAPORTTI, "utf-8")
        tallenna(hak, "Lähtötilanne")
        git(hak, "checkout", "-q", "-b", "haara")
        for tiedosto, sisalto in haara.items():
            (hak / tiedosto).write_text(sisalto, "utf-8")
        tallenna(hak, "Muutos haarassa")
        git(hak, "checkout", "-q", "main")
        for tiedosto, sisalto in runko.items():
            (hak / tiedosto).write_text(sisalto, "utf-8")
        tallenna(hak, "Muutos rungossa")
        # @alku yhdistys
        yhdistys = git(hak, "merge", "-q", "--no-edit", "haara",
                       saa_epaonnistua=True)
        print(f"{nimi}:")
        if yhdistys.returncode != 0:
            print("  yhdistys: RISTIRIITA, ihmisen on ratkaistava")
            return
        ajo = subprocess.run([sys.executable, "-B", ajettava], cwd=hak,
                             capture_output=True, text=True, check=False)
        virhe = ajo.stderr.strip().splitlines()[-1:] or ["-"]
        print("  yhdistys: siisti")
        print(f"  ohjelma yhdistyksen jälkeen: "
              f"{'toimii' if ajo.returncode == 0 else 'VIRHE'}")
        if ajo.returncode != 0:
            print(f"  {virhe[0].split(' (')[0]}")
        # @loppu yhdistys


kokeile("eri tiedostot",
        haara={"raportti.py": RAPORTTI.replace("yhteensä", "summa")},
        runko={"laskut.py": LASKUT.replace("return", "# huom\n    return")},
        ajettava="raportti.py")
kokeile("sama rivi",
        haara={"laskut.py": LASKUT.replace("ALV = 24", "ALV = 25.5")},
        runko={"laskut.py": LASKUT.replace("ALV = 24", "ALV = 14")},
        ajettava="raportti.py")
# Runko nimeää funktion uudelleen ja päivittää kaikki tuntemansa kutsut.
# Haara lisää samaan aikaan uuden kutsun vanhalla nimellä.
kokeile("uudelleennimeäminen ja uusi kutsu",
        haara={"kooste.py": "from laskut import summa\n\n"
                            "print(summa([1, 2]))\n"},
        runko={"laskut.py": LASKUT.replace("summa", "yhteensa"),
               "raportti.py": RAPORTTI.replace("summa", "yhteensa")},
        ajettava="kooste.py")
