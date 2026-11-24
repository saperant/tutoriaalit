"""Regressio testilistasta: tulokset, virheallekirjoitukset ja
yhdistetty kattavuus."""

from __future__ import annotations

import tempfile
from collections import Counter
from pathlib import Path

from vuo.kooste import markdown
from vuo.raportit import lue_kattavuus
from vuo.regressio import aja_regressio, lue_testilista, ryhmittele

JUURI = Path(__file__).resolve().parent


# @alku tulokset
def main() -> None:
    testit = lue_testilista(JUURI / "asetukset" / "regressio.toml")
    with tempfile.TemporaryDirectory() as tmp:
        ajohak = Path(tmp)
        tulokset = aja_regressio(JUURI, ajohak, testit)
        rivit = []
        for testi in testit:
            omat = [t for t in tulokset if t.testi == testi.nimi]
            tilat = Counter(t.tila for t in omat)
            rivit.append((testi.nimi, len(omat), tilat["ok"],
                          tilat["virhe"], tilat["aikakatkaisu"]))
        print(markdown(("Testi", "Ajoja", "Läpi", "Virhe", "Aikakatk."),
                       rivit))
        print()
        for allekirjoitus, ryhma in ryhmittele(tulokset).items():
            siemenet = " ".join(str(t.siemen) for t in ryhma)
            print(f"{len(ryhma)} x {allekirjoitus}")
            print(f"    siemenet: {siemenet}")
        # @loppu tulokset
        # @alku kattavuus
        yhteensa: Counter[str] = Counter()
        for t in tulokset:
            if t.testi == "alu_perus":
                loki = ajohak / "lokit" / f"{t.testi}_{t.siemen}.log"
                yhteensa.update(lue_kattavuus(loki.read_text()))
        osuttu = sum(1 for n in yhteensa.values() if n > 0)
        print(f"\nalu_perus, kattavuus yhdistettynä: {osuttu}/"
              f"{len(yhteensa)} lokeroa, pienin osumamäärä "
              f"{min(yhteensa.values())}")
        # @loppu kattavuus


if __name__ == "__main__":
    main()
