"""logging: hierarkkiset lokittajat, tasot ja muotoilu."""

import logging
import sys
from types import TracebackType

type Poikkeustieto = (
    tuple[type[BaseException], BaseException, TracebackType | None]
    | tuple[None, None, None])


# @alku asetus
class TiiviMuotoilija(logging.Formatter):
    """Poikkeus yhdelle riville: tyyppi ja viesti ilman pinoa."""

    def formatException(self, ei: Poikkeustieto) -> str:
        tyyppi, arvo, _ = ei
        nimi = tyyppi.__name__ if tyyppi else "?"
        return f"  {nimi}: {arvo}"


def maarita_lokitus(taso: int) -> None:
    """Kutsutaan kerran sovelluksen käynnistyksessä, ei kirjastossa."""
    kasittelija = logging.StreamHandler(sys.stdout)
    kasittelija.setFormatter(
        TiiviMuotoilija("%(levelname)-7s %(name)s: %(message)s"))
    logging.basicConfig(level=taso, handlers=[kasittelija])
# @loppu asetus


# @alku kaytto
loki = logging.getLogger("kauppa.tilaus")      # yleensä __name__


def kasittele(tilaus_id: int, maara: str) -> None:
    loki.debug("käsitellään tilausta %d", tilaus_id)  # laiska muotoilu
    try:
        kappaleet = int(maara)
    except ValueError:
        loki.exception("tilaus %d hylätty", tilaus_id)
        return
    loki.info("tilaus %d: %d kpl", tilaus_id, kappaleet)


maarita_lokitus(logging.INFO)
logging.getLogger("kauppa").setLevel(logging.DEBUG)  # vain tämä osa
kasittele(101, "3")
kasittele(102, "kolme")
logging.getLogger("kauppa.maksu").warning("maksupalvelu hidas")
# @loppu kaytto
