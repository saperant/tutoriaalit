"""CI-putki vuon kuvauksesta: työt, riippuvuudet ja GitHub Actions -YAML."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from vuo.vaiheet import Vuo


# @alku tyo
@dataclass(frozen=True)
class Tyo:
    nimi: str
    kohde: str | None = None          # vuon vaihe tai
    komento: str | None = None        # oma komento
    tarvitsee: tuple[str, ...] = ()
    lisenssi: bool = False
    vain_yoajo: bool = False
    valimuisti: tuple[str, ...] = ()  # tiedostot, joista avain lasketaan

    @property
    def ajo(self) -> str:
        return self.komento or f"python3 aja_vuo.py --ajohak ajo {self.kohde}"


def lue_putki(polku: Path) -> tuple[dict[str, str], list[Tyo]]:
    data = tomllib.loads(polku.read_text(encoding="utf-8"))
    tyot = [Tyo(t["nimi"], t.get("kohde"), t.get("komento"),
                tuple(t.get("tarvitsee", [])), t.get("lisenssi", False),
                t.get("vain_yoajo", False), tuple(t.get("valimuisti", [])))
            for t in data["tyo"]]
    return data["putki"], tyot
# @loppu tyo


# @alku tarkista
def tarkista(tyot: list[Tyo], vuo: Vuo) -> list[str]:
    """Jokaisen vaiheen, jonka työ tarvitsee ja jonka toinen työ tekee,
    on tultava tarvitsee-listan kautta: muuten vaihe ajetaan kahdesti
    tai tulos puuttuu."""
    virheet = []
    tekija = {t.kohde: t.nimi for t in tyot if t.kohde}
    nimet = {t.nimi for t in tyot}
    for t in tyot:
        for n in t.tarvitsee:
            if n not in nimet:
                virheet.append(f"{t.nimi}: tuntematon työ '{n}'")
        if t.kohde is None:
            continue
        if t.kohde not in vuo.vaiheet:
            virheet.append(f"{t.nimi}: vuossa ei ole vaihetta '{t.kohde}'")
            continue
        for vaihe in (v for taso in vuo.tasot(t.kohde) for v in taso):
            muu = tekija.get(vaihe)
            if muu and muu != t.nimi and muu not in t.tarvitsee:
                virheet.append(f"{t.nimi}: vaihe {vaihe} tulee työstä "
                               f"{muu}, joka puuttuu tarvitsee-listasta")
    return virheet
# @loppu tarkista


# @alku yaml
def yaml(putki: dict[str, str], tyot: list[Tyo]) -> str:
    r = ["# Tuotettu tiedostosta asetukset/ci.toml komennolla",
         "# python3 10-ci.py --kirjoita. Älä muokkaa käsin.",
         "name: laitteisto", "on:", "  push:", "  pull_request:",
         "  schedule:", f"    - cron: '{putki['yoajo']}'", "",
         "jobs:"]
    for t in tyot:
        r += [f"  {t.nimi}:", "    runs-on: ubuntu-24.04",
              f"    container: {putki['kuva']}"]
        if t.tarvitsee:
            r.append(f"    needs: [{', '.join(t.tarvitsee)}]")
        if t.vain_yoajo:
            r.append("    if: github.event_name == 'schedule'")
        if t.lisenssi:
            r += ["    env:",
                  "      LM_LICENSE_FILE: ${{ secrets.LM_LICENSE_FILE }}"]
        r += ["    defaults:", "      run:",
              "        working-directory: eda-skriptaus/esimerkit",
              "    steps:", "      - uses: actions/checkout@v4"]
        for n in t.tarvitsee:
            r += ["      - uses: actions/download-artifact@v4",
                  f"        with: {{name: {n}, "
                  "path: eda-skriptaus/esimerkit/ajo}"]
        if t.valimuisti:
            # Avaimessa ovat työkalukuvan versio ja lähteiden tiiviste:
            # kumpikin muutos tekee vanhasta välimuistista käyttökelvottoman.
            versio = putki["kuva"].rsplit(":", 1)[-1]
            tiedostot = ",\n".join(f"            '{p}'"
                                    for p in t.valimuisti)
            r += ["      - uses: actions/cache@v4", "        with:",
                  "          path: eda-skriptaus/esimerkit/ajo",
                  "          key: >-",
                  f"            {t.nimi}-{versio}-${{{{ hashFiles(",
                  f"{tiedostot}) }}}}"]
        r.append(f"      - run: {t.ajo}")
        if t.kohde:
            # Ajohakemisto leimoineen seuraaville töille, myös hylättynä.
            r += ["      - uses: actions/upload-artifact@v4",
                  "        if: always()",
                  f"        with: {{name: {t.nimi}, "
                  "path: eda-skriptaus/esimerkit/ajo}"]
    return "\n".join(r) + "\n"
# @loppu yaml
