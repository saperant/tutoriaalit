"""Raporttien jäsentäminen yhteiseen malliin ja koosteet siitä.

Syötteinä ovat hakemiston naytteet/ tallennetut raportit, joten
tulos ei riipu työkalujen versioista.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from vuo.kooste import html_taulukko, markdown
from vuo.malli import Raportti
from vuo.raportit import (RaporttiVirhe, lue_kattavuus, lue_simulointi,
                          lue_sta, lue_verilator, lue_yosys_stat)

NAYTTEET = Path(__file__).resolve().parent / "naytteet"


# @alku kokoa
def kokoa() -> Raportti:
    sim_loki = (NAYTTEET / "sim.log").read_text()
    return Raportti(
        lohko="laskuri",
        resurssit=lue_yosys_stat(NAYTTEET / "stat.json"),
        ajoitus=lue_sta((NAYTTEET / "sta.txt").read_text()),
        simuloinnit=[lue_simulointi(sim_loki, "alu_vika", 3)],
        kattavuus=lue_kattavuus(sim_loki),
        varoitukset=lue_verilator((NAYTTEET / "lint.log").read_text()))
# @loppu kokoa


# @alku rivit
def yhteenveto(r: Raportti) -> list[tuple[str, str, str]]:
    """Kooste-taulukon rivit: mittari, arvo ja arvio."""
    assert r.resurssit and r.ajoitus
    osuttu = sum(1 for n in r.kattavuus.values() if n > 0)
    hylatyt = [s for s in r.simuloinnit if s.tila != "ok"]
    return [
        ("solut", str(r.resurssit.solut),
         "OK" if r.resurssit.solut <= 40 else "VIRHE: yli 40"),
        ("kiikut", str(r.resurssit.kiikut), "OK"),
        ("slack (ns)", f"{r.ajoitus.slack:.2f}",
         "OK" if r.ajoitus.kunnossa else "VIRHE: ajoitus"),
        ("simuloinnit", f"{len(r.simuloinnit) - len(hylatyt)}"
         f"/{len(r.simuloinnit)}", "VIRHE: hylättyjä" if hylatyt else "OK"),
        ("kattavuus", f"{osuttu}/{len(r.kattavuus)}",
         "OK" if osuttu == len(r.kattavuus) else "VIRHE: aukkoja"),
        ("lint-varoitukset", str(len(r.varoitukset)),
         "OK" if not r.varoitukset else "VIRHE: varoituksia"),
    ]
# @loppu rivit


def main() -> None:
    raportti = kokoa()
    rivit = yhteenveto(raportti)
    print(markdown(("Mittari", "Arvo", "Arvio"), rivit))
    with tempfile.TemporaryDirectory() as tmp:
        raportti.tallenna(Path(tmp) / "raportti.json")
        data = json.loads((Path(tmp) / "raportti.json").read_text())
        print("JSON-avaimet:", ", ".join(data))
        print("tyypit:", data["resurssit"]["tyypit"])
    sivu = html_taulukko(("Mittari", "Arvo", "Arvio"), rivit)
    korostetut = sivu.count('class="huono"')
    print(f"HTML: {sivu.count('<tr>')} riviä, {korostetut} korostettua")
    # @alku rikki
    try:
        lue_sta((NAYTTEET / "sta_rikki.txt").read_text())
    except RaporttiVirhe as virhe:
        print(f"sta_rikki.txt hylättiin: {virhe}")
    # @loppu rikki


if __name__ == "__main__":
    main()
