"""Istunnot: arvaamaton tunniste, vanheneminen ja vaihto kirjautuessa."""

import secrets
from dataclasses import dataclass

TYHJAKAYNTI = 30 * 60        # sekuntia ilman toimintaa
ENIMMAISIKA = 8 * 60 * 60    # sekuntia luomisesta


@dataclass
class Istunto:
    kayttaja: str | None
    luotu: float
    kaytetty: float


# @alku istunnot
class Istunnot:
    def __init__(self) -> None:
        self._istunnot: dict[str, Istunto] = {}

    def luo(self, nyt: float, kayttaja: str | None = None) -> str:
        tunniste = secrets.token_urlsafe(32)   # 256 bittiä satunnaista
        self._istunnot[tunniste] = Istunto(kayttaja, nyt, nyt)
        return tunniste

    def hae(self, tunniste: str, nyt: float) -> Istunto | None:
        i = self._istunnot.get(tunniste)
        if i is None:
            return None
        if (nyt - i.kaytetty > TYHJAKAYNTI
                or nyt - i.luotu > ENIMMAISIKA):
            del self._istunnot[tunniste]
            return None
        i.kaytetty = nyt
        return i

    def kirjaudu(self, vanha: str, kayttaja: str, nyt: float) -> str:
        """Uusi tunniste aina, kun oikeudet muuttuvat (session fixation)."""
        self._istunnot.pop(vanha, None)
        return self.luo(nyt, kayttaja)

    def kirjaudu_ulos(self, tunniste: str) -> None:
        self._istunnot.pop(tunniste, None)   # mitätöinti palvelimella
# @loppu istunnot


s = Istunnot()
# Hyökkääjä hankkii anonyymin istunnon ja houkuttelee uhrin käyttämään
# sitä. Kirjautuminen vaihtaa tunnisteen, joten hyökkääjän kopio ei
# saa uhrin oikeuksia.
hyokkaajan = s.luo(nyt=0)
uhrin = s.kirjaudu(hyokkaajan, "aino", nyt=10)
print("hyökkääjän tunniste kirjautumisen jälkeen:", s.hae(hyokkaajan, 20))
istunto = s.hae(uhrin, 20)
print("uhrin istunto:", istunto.kayttaja if istunto else None)
print("tyhjäkäynnin jälkeen:", s.hae(uhrin, 20 + TYHJAKAYNTI + 1))
