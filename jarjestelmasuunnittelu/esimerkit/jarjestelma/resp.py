"""Pieni Redis-asiakas (RESP2-protokolla) vakiokirjastolla.

Tuotannossa käytetään valmista asiakasta (esim. redis-py), jossa on
yhteysallas, uudelleenyhdistäminen ja klusterituki. Tämä riittää
esimerkeille ja näyttää, kuinka yksinkertainen protokolla on: komento
lähetetään merkkijonojen taulukkona, ja vastauksen ensimmäinen tavu
kertoo sen tyypin.
"""

from __future__ import annotations

import socket
from types import TracebackType
from typing import BinaryIO

type Vastaus = int | str | bytes | list[Vastaus] | None


class RedisVirhe(Exception):
    """Redisin virhevastaus, esim. WRONGTYPE tai NOSCRIPT."""


# @alku koodaus
def koodaa(*osat: str | int | float | bytes) -> bytes:
    """Komento RESP-taulukoksi: *<n> ja jokainen osa $<pituus>."""
    tavut = [o if isinstance(o, bytes) else str(o).encode() for o in osat]
    rivit = [b"*%d\r\n" % len(tavut)]
    for t in tavut:
        rivit.append(b"$%d\r\n%s\r\n" % (len(t), t))
    return b"".join(rivit)


def lue(virta: BinaryIO) -> Vastaus:
    """Lukee yhden vastauksen. Tyyppi: + teksti, - virhe, : luku,
    $ tavujono (-1 = puuttuu), * taulukko."""
    rivi = virta.readline()
    if not rivi.endswith(b"\r\n"):
        raise ConnectionError("yhteys katkesi kesken vastauksen")
    tyyppi, sisalto = rivi[:1], rivi[1:-2]
    if tyyppi == b"+":
        return sisalto.decode()
    if tyyppi == b"-":
        raise RedisVirhe(sisalto.decode())
    if tyyppi == b":":
        return int(sisalto)
    if tyyppi == b"$":
        pituus = int(sisalto)
        if pituus < 0:
            return None
        data = virta.read(pituus + 2)
        return data[:-2]
    if tyyppi == b"*":
        maara = int(sisalto)
        return None if maara < 0 else [lue(virta) for _ in range(maara)]
    raise ConnectionError(f"tuntematon vastaustyyppi: {rivi!r}")
# @loppu koodaus


class Redis:
    def __init__(self, portti: int, aikaraja: float = 5.0,
                 isanta: str = "127.0.0.1") -> None:
        self._soketti = socket.create_connection((isanta, portti),
                                                 timeout=aikaraja)
        self._virta = self._soketti.makefile("rb")

    def komento(self, *osat: str | int | float | bytes) -> Vastaus:
        self._soketti.sendall(koodaa(*osat))
        return lue(self._virta)

    def putki(self, komennot: list[tuple[str | int | float | bytes, ...]]
              ) -> list[Vastaus]:
        """Lähettää komennot kerralla ja lukee vastaukset sitten
        (pipelining): yksi kiertoviive monen komennon sijaan."""
        self._soketti.sendall(b"".join(koodaa(*k) for k in komennot))
        return [lue(self._virta) for _ in komennot]

    def close(self) -> None:
        self._virta.close()
        self._soketti.close()

    def __enter__(self) -> Redis:
        return self

    def __exit__(self, tyyppi: type[BaseException] | None,
                 virhe: BaseException | None,
                 jalki: TracebackType | None) -> None:
        self.close()


def teksti(vastaus: Vastaus) -> str:
    """Tavujonovastaus merkkijonoksi."""
    if isinstance(vastaus, bytes):
        return vastaus.decode()
    if isinstance(vastaus, str):
        return vastaus
    raise TypeError(f"ei merkkijono: {vastaus!r}")


def luku(vastaus: Vastaus) -> int:
    if isinstance(vastaus, int):
        return vastaus
    if isinstance(vastaus, bytes):
        return int(vastaus)
    raise TypeError(f"ei luku: {vastaus!r}")


def lista(vastaus: Vastaus) -> list[Vastaus]:
    if isinstance(vastaus, list):
        return vastaus
    if vastaus is None:
        return []
    raise TypeError(f"ei taulukko: {vastaus!r}")
