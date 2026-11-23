"""EAFP vs. LBYL: Pythonissa poikkeus on tavallinen ohjausvuon keino."""

from pathlib import Path

hinnasto = {"kahvi": 2.5, "tee": 2.0}

# @alku lbyl
# LBYL (look before you leap): kaksi hakua ja kilpatilanteen mahdollisuus
if "pulla" in hinnasto:
    print(hinnasto["pulla"])
else:
    print("ei hintaa")
# @loppu lbyl

# @alku eafp
# EAFP (easier to ask forgiveness than permission): yksi haku
try:
    print(hinnasto["pulla"])
except KeyError:
    print("ei hintaa")
# @loppu eafp

# @alku tiedosto
# Tiedoston olemassaolon tarkistus ennen avausta on kilpatilanne:
# tiedosto voi kadota tarkistuksen ja avauksen välissä.
try:
    sisalto = Path("asetukset.ini").read_text(encoding="utf-8")
except FileNotFoundError:
    sisalto = "[oletus]"
print(sisalto)
# @loppu tiedosto
