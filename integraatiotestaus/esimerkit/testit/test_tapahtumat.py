"""Redis Streams: vähintään kerran -toimitus ja kaatunut kuluttaja."""

from __future__ import annotations

import pytest
import redis

from varasto import tapahtumat


# @alku tapahtumatestit
def test_kaatuneen_kuluttajan_viesti_kasitellaan(r: redis.Redis) -> None:
    tapahtumat.luo_ryhma(r)
    for tunnus in (1, 2, 3):
        tapahtumat.julkaise(r, tunnus, "ABC-1", tunnus)

    def kaatuu(viesti: dict[str, str]) -> None:
        raise RuntimeError("kuluttaja A kaatui")

    with pytest.raises(RuntimeError):
        tapahtumat.kasittele(r, "A", kaatuu, kerralla=1)

    kasitellyt: set[str] = set()  # idempotenssi: tunnus kerran
    def kirjaa(viesti: dict[str, str]) -> None:
        kasitellyt.add(viesti["tunnus"])

    # Kuluttaja B saa uudet viestit 2 ja 3 ...
    assert tapahtumat.kasittele(r, "B", kirjaa) == 2
    # ... ja ottaa haltuun A:n kuittaamatta jääneen viestin 1.
    assert tapahtumat.ota_hylatyt(r, "B", kirjaa, 0) == 1
    assert kasitellyt == {"1", "2", "3"}
    assert r.xpending(tapahtumat.VIRTA, tapahtumat.RYHMA)["pending"] == 0
# @loppu tapahtumatestit
