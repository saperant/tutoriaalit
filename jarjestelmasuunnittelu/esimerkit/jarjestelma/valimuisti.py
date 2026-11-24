"""Välimuististrategiat Redisin päällä.

Tietokanta on tässä pelkkä sanakirja, joka laskee hakunsa ja voi
viivästää vastausta. Oikeassa järjestelmässä haku olisi kysely
PostgreSQLiin (ks. luku 12).
"""

from __future__ import annotations

import secrets
import threading
import time

from jarjestelma.resp import Redis, luku, teksti


class Tietokanta:
    def __init__(self, rivit: dict[str, str], viive: float = 0.0) -> None:
        self._rivit = dict(rivit)
        self._viive = viive
        self._lukko = threading.Lock()
        self.hakuja = 0

    def hae(self, avain: str) -> str:
        with self._lukko:
            self.hakuja += 1
        time.sleep(self._viive)
        return self._rivit[avain]

    def paivita(self, avain: str, arvo: str) -> None:
        self._rivit[avain] = arvo


# @alku rinnalla
def hae_rinnalta(r: Redis, kanta: Tietokanta, avain: str,
                 ttl_s: int = 3600) -> str:
    """Cache-aside: sovellus katsoo ensin välimuistista ja hakee
    puuttuvan kannasta. TTL rajaa, kuinka kauan vanhentunut arvo voi
    pahimmillaan elää, jos invalidointi epäonnistuu."""
    arvo = r.komento("GET", avain)
    if arvo is not None:
        return teksti(arvo)
    tuore = kanta.hae(avain)
    r.komento("SET", avain, tuore, "EX", ttl_s)
    return tuore
# @loppu rinnalla


# @alku vuokra
# Vuokra (lease): välimuistihuti saa lyhytaikaisen vuokran, ja vain
# vuokran haltija hakee arvon kannasta. Tallennus onnistuu vain, jos
# vuokra on yhä voimassa. Invalidointi poistaa myös vuokran, joten
# invalidointia ennen haettu vanha arvo ei voi enää päätyä muistiin.
TALLENNA_LUA = """
if redis.call('GET', KEYS[2]) == ARGV[1] then
  redis.call('SET', KEYS[1], ARGV[2], 'EX', ARGV[3])
  redis.call('DEL', KEYS[2])
  return 1
end
return 0
"""


def aloita(r: Redis, avain: str, vuokra_ms: int = 2000) -> str | None:
    """Palauttaa vuokratunnuksen, jos kukaan muu ei ole jo hakemassa."""
    tunnus = secrets.token_hex(8)
    ok = r.komento("SET", f"vuokra:{avain}", tunnus, "NX", "PX", vuokra_ms)
    return tunnus if ok == "OK" else None


def tallenna(r: Redis, avain: str, tunnus: str, arvo: str,
             ttl_s: int = 3600) -> bool:
    return luku(r.komento("EVAL", TALLENNA_LUA, 2, avain,
                          f"vuokra:{avain}", tunnus, arvo, ttl_s)) == 1


def invalidoi(r: Redis, avain: str) -> None:
    r.komento("DEL", avain, f"vuokra:{avain}")


def hae_vuokralla(r: Redis, kanta: Tietokanta, avain: str,
                  odota_s: float = 2.0) -> str:
    loppu = time.monotonic() + odota_s
    while time.monotonic() < loppu:
        arvo = r.komento("GET", avain)
        if arvo is not None:
            return teksti(arvo)
        tunnus = aloita(r, avain)
        if tunnus is not None:
            tuore = kanta.hae(avain)
            tallenna(r, avain, tunnus, tuore)
            return tuore
        time.sleep(0.02)       # joku muu hakee: odotetaan hetki
    return kanta.hae(avain)    # vuokran haltija jumissa: haetaan itse
# @loppu vuokra
