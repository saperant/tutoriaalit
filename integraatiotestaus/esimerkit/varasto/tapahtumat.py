"""Varaustapahtumat Redis Streamsin kautta (vähintään kerran -toimitus)."""

from __future__ import annotations

from collections.abc import Callable
from typing import cast

import redis

VIRTA = "varaukset"
RYHMA = "laskutus"


# @alku julkaise
def julkaise(r: redis.Redis, tunnus: int, sku: str, maara: int) -> None:
    """Lisää tapahtuman virtaan. Tunnus tekee käsittelystä
    idempotentin: sama tapahtuma voi tulla kahdesti."""
    r.xadd(VIRTA, {"tunnus": tunnus, "sku": sku, "maara": maara})


def luo_ryhma(r: redis.Redis) -> None:
    try:
        r.xgroup_create(VIRTA, RYHMA, id="0", mkstream=True)
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
# @loppu julkaise


# @alku kasittele
Kasittelija = Callable[[dict[str, str]], None]
Viestit = list[tuple[bytes, dict[bytes, bytes]]]


def _kentat(raaka: dict[bytes, bytes]) -> dict[str, str]:
    return {k.decode(): v.decode() for k, v in raaka.items()}


def kasittele(r: redis.Redis, kuluttaja: str, kasittelija: Kasittelija,
              kerralla: int = 10) -> int:
    """Lukee uudet viestit ryhmän nimissä ja kuittaa ne vasta, kun
    käsittelijä on onnistunut. Jos kuluttaja kaatuu ennen kuittausta,
    viesti jää odottavaksi (pending) ja toinen kuluttaja voi ottaa sen."""
    vastaus = cast(list[tuple[bytes, Viestit]], r.xreadgroup(
        RYHMA, kuluttaja, {VIRTA: ">"}, count=kerralla))
    maara = 0
    for _virta, viestit in vastaus:
        for viesti_id, kentat in viestit:
            kasittelija(_kentat(kentat))
            r.xack(VIRTA, RYHMA, viesti_id)
            maara += 1
    return maara


def ota_hylatyt(r: redis.Redis, kuluttaja: str, kasittelija: Kasittelija,
                vanhempi_kuin_ms: int) -> int:
    """Ottaa haltuun ja käsittelee viestit, jotka ovat odottaneet
    kuittausta liian kauan (kaatunut kuluttaja)."""
    _seuraava, viestit, _poistetut = cast(
        tuple[bytes, Viestit, list[bytes]],
        r.xautoclaim(VIRTA, RYHMA, kuluttaja,
                     min_idle_time=vanhempi_kuin_ms))
    for viesti_id, kentat in viestit:
        kasittelija(_kentat(kentat))
        r.xack(VIRTA, RYHMA, viesti_id)
    return len(viestit)
# @loppu kasittele
