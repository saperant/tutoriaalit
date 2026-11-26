"""Mittaripalvelu valvojan alla: sokettiaktivointi, valmiuden ilmoitus,
lokirivien vakavuus ja uudelleenkäynnistys käynnistysrajalla."""

import select
import socket
import tempfile
from pathlib import Path

from valvoja import Palvelu, Valvoja, python_komento

MITTARI = Path(__file__).with_name("mittari.py")


def kysy(portti: int, komento: str) -> str:
    with socket.create_connection(("127.0.0.1", portti), timeout=10) as s:
        s.sendall((komento + "\n").encode())
        return s.makefile().readline().strip()


def sokettiaktivointi() -> None:
    print("== sokettiaktivointi")
    valvoja = Valvoja()
    kuuntelu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    kuuntelu.bind(("127.0.0.1", 0))      # vapaa portti
    kuuntelu.listen()
    portti = kuuntelu.getsockname()[1]
    palvelu = Palvelu(python_komento(MITTARI))
    print(f"valvoja kuuntelee, palvelu: {palvelu.tila}")

    # @alku aktivointi
    # Asiakas ottaa yhteyden, vaikka palvelu ei ole käynnissä: ydin
    # panee yhteyden jonoon kuuntelusokettiin.
    asiakas = socket.create_connection(("127.0.0.1", portti), timeout=10)
    asiakas.sendall(b"tila\n")
    select.select([kuuntelu], [], [], 10)
    print("yhteys jonossa, käynnistetään palvelu")

    valvoja.kaynnista(palvelu, kuuntelu)
    print(f"käynnistetty, palvelu: {palvelu.tila}")
    valvoja.odota_valmiutta(palvelu)
    print(f"READY=1 saatu, palvelu: {palvelu.tila}")
    # @loppu aktivointi
    print("jonossa odottanut asiakas sai:",
          asiakas.makefile().readline().strip())
    asiakas.close()
    print("toinen pyyntö:", kysy(portti, "tila"))
    print("väärä pyyntö:", kysy(portti, "tilaa"))
    koodi = valvoja.pysayta(palvelu)
    print(f"SIGTERM, paluuarvo {koodi}, viimeisin tila: {palvelu.viesti}")
    print("loki:")
    for rivi in valvoja.loki:
        taso, _, teksti = rivi[1:].partition(">")
        print(f"  PRIORITY={taso} MESSAGE={teksti}")
    kuuntelu.close()
    valvoja.sulje()


# @alku kaynnistysraja
def kaynnistysraja() -> None:
    with tempfile.TemporaryDirectory() as tyo:
        laskuri = Path(tyo) / "kaatumisia"
        for kaatumisia in (2, 5):
            print(f"== palvelu kaatuu {kaatumisia} kertaa käynnistyessään")
            laskuri.write_text(str(kaatumisia))
            valvoja = Valvoja()
            palvelu = Palvelu(python_komento(MITTARI),
                              {"MITTARI_KAATUMISIA": str(laskuri),
                               "MITTARI_PORTTI": "0"})
            for rivi in valvoja.aja_kaynnistyskaytannolla(palvelu, raja=3):
                print(rivi)
            if palvelu.tila == "active":
                valvoja.pysayta(palvelu)
            valvoja.sulje()
# @loppu kaynnistysraja


if __name__ == "__main__":
    sokettiaktivointi()
    kaynnistysraja()
