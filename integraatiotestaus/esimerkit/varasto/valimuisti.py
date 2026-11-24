"""Hintojen välimuisti Redisissä (cache-aside)."""

from __future__ import annotations

import json
from typing import Protocol

import redis

from varasto.hinnat import Hinta


class Hintalahde(Protocol):
    def hae(self, sku: str) -> Hinta: ...


# @alku valimuisti
class HintaValimuisti:
    """Cache-aside: katso ensin Redisistä, muuten hae lähteestä ja
    tallenna vanhenemisajan (TTL) kanssa. Avaimen alussa on versio,
    jotta tallennusmuodon muutos ei lue vanhoja arvoja."""

    AVAIN = "hinta:v1:{}"

    def __init__(self, r: redis.Redis, lahde: Hintalahde,
                 ttl_s: int = 60) -> None:
        self.r = r
        self.lahde = lahde
        self.ttl_s = ttl_s

    def hae(self, sku: str) -> Hinta:
        avain = self.AVAIN.format(sku.lower())
        raaka = self.r.get(avain)
        if isinstance(raaka, bytes):
            d = json.loads(raaka)
            return Hinta(d["sku"], d["hinta_snt"], d["valuutta"])
        hinta = self.lahde.hae(sku)
        self.r.set(avain, json.dumps(hinta.__dict__), ex=self.ttl_s)
        return hinta

    def unohda(self, sku: str) -> None:
        self.r.delete(self.AVAIN.format(sku.lower()))
# @loppu valimuisti
