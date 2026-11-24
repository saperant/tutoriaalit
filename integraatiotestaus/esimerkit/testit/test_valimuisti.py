"""Hintojen välimuisti oikeaa Redisiä vasten."""

from __future__ import annotations

import redis

from varasto.hinnat import Hinta
from varasto.valimuisti import HintaValimuisti


class LaskevaLahde:
    """Vakoilija: laskee, montako kertaa lähteeseen mentiin."""

    def __init__(self) -> None:
        self.haut = 0

    def hae(self, sku: str) -> Hinta:
        self.haut += 1
        return Hinta(sku.upper(), 990, "EUR")


# @alku valimuistitestit
def test_toinen_haku_tulee_valimuistista(r: redis.Redis) -> None:
    lahde = LaskevaLahde()
    muisti = HintaValimuisti(r, lahde, ttl_s=60)
    assert muisti.hae("abc-1") == muisti.hae("ABC-1")
    assert lahde.haut == 1
    assert 0 < int(r.ttl("hinta:v1:abc-1")) <= 60


def test_unohda_pakottaa_uuden_haun(r: redis.Redis) -> None:
    lahde = LaskevaLahde()
    muisti = HintaValimuisti(r, lahde)
    muisti.hae("ABC-1")
    muisti.unohda("abc-1")
    muisti.hae("ABC-1")
    assert lahde.haut == 2
# @loppu valimuistitestit
