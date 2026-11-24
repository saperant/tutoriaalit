"""Regressiohistoria SQLitessä: trendi, ensimmäinen hylkäävä versio ja
epävakaat testit."""

from __future__ import annotations

import tempfile
from dataclasses import replace
from pathlib import Path

from vuo.historia import avaa, ensimmainen_hylkays, epavakaat, kirjaa, trendi
from vuo.kooste import markdown
from vuo.regressio import Testi, aja_regressio

JUURI = Path(__file__).resolve().parent

# @alku versiot
# Simuloitu versiohistoria: vika tulee koodiin versiossa c3.
VERSIOT = [("c1", ()), ("c2", ()), ("c3", ("VIKA",)), ("c4", ("VIKA",))]
# @loppu versiot


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        yhteys = avaa(Path(tmp) / "historia.db")
        # @alku kirjaus
        for jarjestys, (versio, maarittelyt) in enumerate(VERSIOT, 1):
            testi = Testi("alu", tuple(range(1, 9)), maara=12,
                          maarittelyt=maarittelyt)
            tulokset = aja_regressio(JUURI, Path(tmp) / "ajo", [testi])
            kirjaa(yhteys, versio, jarjestys, tulokset)
        # Uusinta-ajo versiolla c4: siemen 7 meni nyt läpi. Esimerkissä
        # tulos on kirjoitettu käsin; oikeassa vuossa syynä voisi olla
        # vaikkapa kilpatilanne testipenkissä tai aikakatkaisu kuormassa.
        uusinta = [replace(t, tila="ok", viestit=()) if t.siemen == 7
                   else t for t in tulokset]
        kirjaa(yhteys, "c4", len(VERSIOT), uusinta)
        # @loppu kirjaus
        # @alku kyselyt
        print(markdown(("Versio", "Läpi", "Ajoja", "Osuus"),
                       [(v, ok, n, f"{100 * ok // n} %")
                        for v, ok, n in trendi(yhteys)]))
        print("\nensimmäinen hylkäävä versio:")
        for allekirjoitus, versio, maara in ensimmainen_hylkays(yhteys):
            print(f"  {versio}: {allekirjoitus} ({maara} kertaa)")
        print("\nepävakaat (sama versio ja siemen, eri tulos):")
        for testi_nimi, siemen, versio in epavakaat(yhteys):
            print(f"  {testi_nimi} siemen {siemen} versiossa {versio}")
        yhteys.close()
        # @loppu kyselyt


if __name__ == "__main__":
    main()
