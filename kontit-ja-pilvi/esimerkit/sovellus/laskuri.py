"""Laskuripalvelu: säilyttää käyntimäärän levyllä.

Ympäristömuuttujat:
  PORTTI          kuunneltava portti (oletus 8080)
  DATA_HAKEMISTO  hakemisto, johon laskurin arvo tallennetaan
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from yhteinen import Kasittelija, Vastaus, aja, asetus, palvelin


class Laskuri:
    """Laskuri, jonka arvo kestää uudelleenkäynnistyksen."""

    def __init__(self, hakemisto: Path) -> None:
        self._tiedosto = hakemisto / "laskuri.txt"
        self._lukko = threading.Lock()

    def arvo(self) -> int:
        try:
            return int(self._tiedosto.read_text())
        except FileNotFoundError:
            return 0

    # @alku kasvata
    def kasvata(self) -> int:
        with self._lukko:
            uusi = self.arvo() + 1
            # Kirjoitus väliaikaistiedostoon ja vaihto yhdellä
            # järjestelmäkutsulla: kaatuminen ei jätä puolikasta arvoa.
            valiaikainen = self._tiedosto.with_suffix(".uusi")
            valiaikainen.write_text(str(uusi))
            os.replace(valiaikainen, self._tiedosto)
            return uusi
    # @loppu kasvata


def kasittelija(laskuri: Laskuri) -> Kasittelija:
    def kasittele(metodi: str, polku: str) -> Vastaus:
        if polku == "/terveys":
            return 200, {"tila": "ok"}
        if polku == "/laskuri" and metodi == "GET":
            return 200, {"arvo": laskuri.arvo()}
        if polku == "/laskuri" and metodi == "POST":
            return 200, {"arvo": laskuri.kasvata()}
        return 404, {"virhe": "ei löydy"}
    return kasittele


if __name__ == "__main__":
    hakemisto = Path(asetus("DATA_HAKEMISTO", "/tmp"))  # noqa: S108
    portti = int(asetus("PORTTI", "8080"))
    aja("laskuri", palvelin(portti, kasittelija(Laskuri(hakemisto))))
