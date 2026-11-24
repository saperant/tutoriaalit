"""Pieni TCP-vikaproxy (Toxiproxyn periaate).

Välittää portin 8666 yhteydet kohteeseen KOHDE=isäntä:portti.
Hallinta HTTP:llä portissa 8474:

POST /viive?ms=N   viivästää jokaista välitettyä datapalaa N ms
POST /katkaise     sulkee nykyiset yhteydet ja hylkää uudet
POST /palauta      poistaa viiveen ja katkon
"""

from __future__ import annotations

import asyncio
import os
from typing import ClassVar
from urllib.parse import parse_qs, urlparse


class Tila:
    viive_s = 0.0
    katki = False
    yhteydet: ClassVar[set[asyncio.StreamWriter]] = set()


# @alku valitys
async def siirra(lukija: asyncio.StreamReader,
                 kirjoittaja: asyncio.StreamWriter) -> None:
    try:
        while data := await lukija.read(65536):
            if Tila.viive_s:
                await asyncio.sleep(Tila.viive_s)
            kirjoittaja.write(data)
            await kirjoittaja.drain()
    except (ConnectionError, OSError):
        pass
    finally:
        kirjoittaja.close()


async def asiakas(lukija: asyncio.StreamReader,
                  kirjoittaja: asyncio.StreamWriter) -> None:
    if Tila.katki:
        kirjoittaja.close()
        return
    isanta, portti = os.environ["KOHDE"].rsplit(":", 1)
    try:
        k_lukija, k_kirjoittaja = await asyncio.open_connection(
            isanta, int(portti))
    except OSError:
        kirjoittaja.close()
        return
    Tila.yhteydet.update({kirjoittaja, k_kirjoittaja})
    await asyncio.gather(siirra(lukija, k_kirjoittaja),
                         siirra(k_lukija, kirjoittaja))
    Tila.yhteydet.difference_update({kirjoittaja, k_kirjoittaja})
# @loppu valitys


async def hallinta(lukija: asyncio.StreamReader,
                   kirjoittaja: asyncio.StreamWriter) -> None:
    pyynto = (await lukija.readline()).decode().split()
    while (await lukija.readline()).strip():
        pass  # otsakkeet ohitetaan
    osat = urlparse(pyynto[1] if len(pyynto) > 1 else "/")
    koodi = "200 OK"
    if osat.path == "/viive":
        Tila.viive_s = int(parse_qs(osat.query)["ms"][0]) / 1000
    elif osat.path == "/katkaise":
        Tila.katki = True
        for w in list(Tila.yhteydet):
            w.close()
    elif osat.path == "/palauta":
        Tila.viive_s, Tila.katki = 0.0, False
    elif osat.path != "/terveys":
        koodi = "404 Not Found"
    kirjoittaja.write(f"HTTP/1.1 {koodi}\r\nContent-Length: 0\r\n"
                      "Connection: close\r\n\r\n".encode())
    await kirjoittaja.drain()
    kirjoittaja.close()


async def main() -> None:
    valitys = await asyncio.start_server(asiakas, "0.0.0.0", 8666)
    ohjaus = await asyncio.start_server(hallinta, "0.0.0.0", 8474)
    print("vikaproxy valmis", flush=True)
    async with valitys, ohjaus:
        await asyncio.gather(valitys.serve_forever(),
                             ohjaus.serve_forever())


if __name__ == "__main__":
    asyncio.run(main())
