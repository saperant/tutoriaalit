"""Asiakas ulkoiseen hintapalveluun (HTTP + JSON)."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True)
class Hinta:
    sku: str
    hinta_snt: int
    valuutta: str


class HintaVirhe(Exception):
    """Hintaa ei saatu (palvelu ei vastaa, virheellinen vastaus)."""


# @alku asiakas
class HintaAsiakas:
    """Hakee hinnan osoitteesta GET {perus}/hinnat/{sku}.

    Jokaisella yrityksellä on aikaraja, ja yhteys- ja palvelinvirheet
    (5xx) yritetään uudelleen kasvavin tauoin. Asiakasvirheitä (4xx)
    ei yritetä uudelleen: sama pyyntö epäonnistuisi taas."""

    def __init__(self, perus: str, aikaraja: float = 1.0,
                 yritykset: int = 3, tauko: float = 0.1) -> None:
        self.perus = perus.rstrip("/")
        self.aikaraja = aikaraja
        self.yritykset = yritykset
        self.tauko = tauko

    def hae(self, sku: str) -> Hinta:
        viimeisin: Exception | None = None
        for yritys in range(self.yritykset):
            if yritys:
                time.sleep(self.tauko * 2 ** (yritys - 1))
            try:
                return self._hae_kerran(sku)
            except urllib.error.HTTPError as e:
                if e.code < 500:
                    raise HintaVirhe(f"{sku}: HTTP {e.code}") from e
                viimeisin = e
            except (urllib.error.URLError, TimeoutError,
                    ConnectionError) as e:
                viimeisin = e
        raise HintaVirhe(f"{sku}: ei vastausta {self.yritykset} "
                         f"yrityksellä") from viimeisin

    def _hae_kerran(self, sku: str) -> Hinta:
        osoite = f"{self.perus}/hinnat/{sku}"
        with urllib.request.urlopen(osoite,
                                    timeout=self.aikaraja) as vastaus:
            data = json.loads(vastaus.read())
        try:
            return Hinta(str(data["sku"]), int(data["hinta_snt"]),
                         str(data["valuutta"]))
        except (KeyError, TypeError, ValueError) as e:
            raise HintaVirhe(f"{sku}: virheellinen vastaus") from e
# @loppu asiakas
