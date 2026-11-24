"""Asetustiedostot: TOML (tomllib), vanha INI (configparser) ja JSON.

Asetukset luetaan kerran ohjelman reunalla tyypitetyiksi olioiksi ja
tarkistetaan heti. Muu ohjelma käsittelee vain valmiita olioita, eikä
sen tarvitse arvailla, puuttuuko jokin avain tai onko luku merkkijono.
"""

import configparser
import json
import sys
import tomllib
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

HAK = Path(__file__).parent


# @alku mallit
@dataclass(frozen=True)
class Testi:
    nimi: str
    siemenet: tuple[int, ...]
    argumentit: tuple[str, ...] = ()


@dataclass(frozen=True)
class Asetukset:
    simulaattori: str
    rinnakkain: int
    aikaraja_s: int
    testit: tuple[Testi, ...] = field(default=())

    def __post_init__(self) -> None:
        if self.simulaattori not in {"verilator", "icarus", "questa"}:
            raise ValueError(f"tuntematon simulaattori {self.simulaattori}")
        if not 1 <= self.rinnakkain <= 64:
            raise ValueError("rinnakkain: 1..64")
# @loppu mallit


# @alku toml
def lue_toml(polku: Path) -> Asetukset:
    with polku.open("rb") as f:          # tomllib vaatii binääritilan
        data: dict[str, Any] = tomllib.load(f)
    ajo = data["ajo"]
    testit = tuple(
        Testi(t["nimi"], tuple(t["siemenet"]),
              tuple(t.get("argumentit", ())))
        for t in data.get("testi", []))
    return Asetukset(ajo["simulaattori"], ajo["rinnakkain"],
                     ajo["aikaraja_s"], testit)
# @loppu toml


# @alku ini
def lue_ini(polku: Path) -> Asetukset:
    ini = configparser.ConfigParser()
    ini.read(polku, encoding="utf-8")
    ajo = ini["ajo"]
    testit = tuple(
        Testi(osio.removeprefix("testi:"),
              tuple(int(s) for s in ini[osio]["siemenet"].split(",")))
        for osio in ini.sections() if osio.startswith("testi:"))
    return Asetukset(ajo["simulaattori"], ini.getint("ajo", "rinnakkain"),
                     ini.getint("ajo", "aikaraja_s"), testit)
# @loppu ini


def main() -> int:
    for nimi, a in (("TOML", lue_toml(HAK / "04-asetukset.toml")),
                    ("INI", lue_ini(HAK / "04-vanha.ini"))):
        print(f"{nimi}: {a.simulaattori}, {a.rinnakkain} rinnakkain, "
              f"aikaraja {a.aikaraja_s} s")
        for t in a.testit:
            print("  " + json.dumps(asdict(t), ensure_ascii=False))
    try:
        Asetukset("modelsim", 4, 60)
    except ValueError as e:
        print(f"hylätty: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
