"""Testidatan rakentajat: deterministiset arvot ja yksilölliset nimet."""

from __future__ import annotations

import uuid

from varasto.malli import Tuote


# @alku rakentajat
def tuote(n: int = 1, **muutokset: object) -> Tuote:
    """Deterministinen tuote numerosta n. Testi muuttaa vain sen,
    mikä on testin kannalta olennaista: tuote(saldo=0)."""
    arvot: dict[str, object] = {"sku": f"T-{n:04d}",
                                "nimi": f"Tuote {n}", "saldo": 10}
    arvot.update(muutokset)
    return Tuote(str(arvot["sku"]), str(arvot["nimi"]),
                 int(str(arvot["saldo"])))


def ainutlaatuinen(etuliite: str) -> str:
    """Nimi, joka ei törmää rinnakkaisten tai aiempien ajojen kanssa."""
    return f"{etuliite}-{uuid.uuid4().hex[:8]}"
# @loppu rakentajat
