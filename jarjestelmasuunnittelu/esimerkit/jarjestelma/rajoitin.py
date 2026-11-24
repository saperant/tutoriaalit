"""Nopeusrajoitus token bucket -menetelmällä.

Sankoon mahtuu `koko` merkkiä, ja sinne valuu `nopeus` merkkiä
sekunnissa. Pyyntö kuluttaa merkin; tyhjästä sangosta pyyntö hylätään.
Pitkän ajan nopeus on siis `nopeus`, mutta `koko` merkin purske
sallitaan kerralla.
"""

from __future__ import annotations

from collections.abc import Callable


# @alku sanko
class Sanko:
    def __init__(self, nopeus: float, koko: float,
                 kello: Callable[[], float]) -> None:
        if nopeus <= 0 or koko < 1:
            raise ValueError("nopeuden on oltava > 0 ja koon >= 1")
        self.nopeus, self.koko, self._kello = nopeus, koko, kello
        self._merkit = koko
        self._aika = kello()

    def salli(self, hinta: float = 1.0) -> bool:
        nyt = self._kello()
        kulunut = max(0.0, nyt - self._aika)  # kello ei saa peruuttaa
        self._merkit = min(self.koko, self._merkit + kulunut * self.nopeus)
        self._aika = nyt
        if self._merkit >= hinta:
            self._merkit -= hinta
            return True
        return False
# @loppu sanko


# @alku lua
# Sama sanko Redisissä: skripti suoritetaan atomisesti, joten kaikki
# palvelininstanssit jakavat saman rajan. Aika tulee Redisin kellosta,
# jotta palvelinten kellojen erot eivät vaikuta.
SANKO_LUA = """
local avain = KEYS[1]
local nopeus = tonumber(ARGV[1])
local koko = tonumber(ARGV[2])
local t = redis.call('TIME')
local nyt = tonumber(t[1]) + tonumber(t[2]) / 1e6
local tila = redis.call('HMGET', avain, 'merkit', 'aika')
local merkit = tonumber(tila[1]) or koko
local aika = tonumber(tila[2]) or nyt
merkit = math.min(koko, merkit + math.max(0, nyt - aika) * nopeus)
local sallittu = 0
if merkit >= 1 then
  merkit = merkit - 1
  sallittu = 1
end
redis.call('HSET', avain, 'merkit', merkit, 'aika', nyt)
redis.call('PEXPIRE', avain, math.ceil(koko / nopeus * 1000) + 1000)
return sallittu
"""
# @loppu lua
