"""HTTP-rajapinnan käsittelijä.

Käsittelijä on tavallinen funktio, joka saa pyynnön osat ja palauttaa
vastauksen. Verkkokerros (esimerkiksi ``http.server``) on erikseen,
joten rajapinnan kuvaus voidaan tarkistaa toteutusta vasten ilman
verkkoa: ks. ``openapi/tarkista.py``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from saa.lukema import Lukema, LukemaVirhe, jasenna_rivi
from saa.tilasto import yhteenveto

#: Rajapinnan reitit: (metodi, polun malli). Sama luettelo on
#: OpenAPI-kuvauksessa, ja tarkistin vertaa niitä.
REITIT = (
    ("GET", "/lukemat"),
    ("POST", "/lukemat"),
    ("GET", "/asemat/{asema}/yhteenveto"),
)


@dataclass(frozen=True)
class Vastaus:
    """HTTP-vastaus.

    Attributes:
        tila: Tilakoodi, esimerkiksi 200.
        runko: JSON-muotoon muunnettava runko.
    """

    tila: int
    runko: Any


@dataclass
class Palvelu:
    """Lukemat muistissa säilyttävä palvelu.

    Attributes:
        lukemat: Tallennetut lukemat saapumisjärjestyksessä.
    """

    lukemat: list[Lukema] = field(default_factory=list)

    # @alku kasittele
    def kasittele(self, metodi: str, polku: str,
                  runko: dict[str, Any] | None = None,
                  kysely: dict[str, str] | None = None) -> Vastaus:
        """Käsittelee yhden pyynnön.

        Args:
            metodi: HTTP-metodi isoin kirjaimin.
            polku: Pyynnön polku ilman kyselyosaa.
            runko: Pyynnön JSON-runko tai ``None``.
            kysely: Kyselyparametrit tai ``None``.

        Returns:
            Vastaus. Tuntematon reitti tuottaa tilan 404 ja
            virheellinen lukema tilan 422.
        """
        osat = polku.strip("/").split("/")
        if (metodi, polku) == ("GET", "/lukemat"):
            asema = (kysely or {}).get("asema")
            return Vastaus(200, [_json(x) for x in self.lukemat
                                 if asema in (None, x.asema)])
        if (metodi, polku) == ("POST", "/lukemat"):
            return self._lisaa(runko or {})
        if metodi == "GET" and len(osat) == 3 and \
                (osat[0], osat[2]) == ("asemat", "yhteenveto"):
            tulos = yhteenveto(osat[1], self.lukemat)
            if tulos is None:
                return _virhe(404, f"asemaa {osat[1]} ei ole")
            return Vastaus(200, asdict(tulos))
        return _virhe(404, "tuntematon reitti")
    # @loppu kasittele

    def _lisaa(self, runko: dict[str, Any]) -> Vastaus:
        kosteus = runko.get("kosteus")
        rivi = ";".join([str(runko.get("asema", "")),
                         str(runko.get("aika", "")),
                         str(runko.get("lampotila_c", "")),
                         "" if kosteus is None else str(kosteus)])
        try:
            lukema = jasenna_rivi(rivi)
        except LukemaVirhe as virhe:
            return _virhe(422, str(virhe))
        self.lukemat.append(lukema)
        return Vastaus(201, _json(lukema))


def _json(lukema: Lukema) -> dict[str, Any]:
    return {"asema": lukema.asema, "aika": lukema.aika.isoformat(),
            "lampotila_c": lukema.lampotila_c, "kosteus": lukema.kosteus}


def _virhe(tila: int, viesti: str) -> Vastaus:
    return Vastaus(tila, {"virhe": viesti})
