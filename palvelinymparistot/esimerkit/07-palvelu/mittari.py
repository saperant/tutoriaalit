"""Mittari: pieni TCP-palvelu, joka noudattaa systemd:n käytäntöjä.

Palvelu ei riipu systemd:stä, mutta käyttää sen kolmea rajapintaa, jos
ne on tarjolla: valmiuden ilmoitus (NOTIFY_SOCKET), valmiina annettu
kuuntelusoketti (LISTEN_FDS) ja lokirivin vakavuus rivin alussa (<N>).
"""

import os
import select
import signal
import socket
import sys
from pathlib import Path
from types import FrameType

# @alku ilmoitus
def ilmoita(viesti: str) -> None:
    """sd_notify: yksi datagrammi osoitteeseen NOTIFY_SOCKET."""
    osoite = os.environ.get("NOTIFY_SOCKET")
    if not osoite:
        return                           # ajetaan ilman valvojaa
    if osoite.startswith("@"):           # abstrakti nimiavaruus
        osoite = "\0" + osoite[1:]
    with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
        s.sendto(viesti.encode(), osoite)
# @loppu ilmoitus


# @alku loki
INFO, VIRHE = 6, 3


def loki(taso: int, teksti: str) -> None:
    """Lokirivi vakiovirtaan; <N> rivin alussa on syslog-vakavuus."""
    print(f"<{taso}>{teksti}", file=sys.stderr, flush=True)
# @loppu loki


# @alku soketti
ENSIMMAINEN_FD = 3                       # SD_LISTEN_FDS_START


def kuuntelusoketti() -> socket.socket:
    """Valvojan antama soketti, tai oma, jos sellaista ei annettu."""
    if (os.environ.get("LISTEN_PID") == str(os.getpid())
            and int(os.environ.get("LISTEN_FDS", "0")) >= 1):
        loki(INFO, "kuuntelusoketti saatu valvojalta")
        return socket.socket(fileno=ENSIMMAINEN_FD)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("127.0.0.1", int(os.environ.get("MITTARI_PORTTI", "9108"))))
    s.listen()
    loki(INFO, "kuuntelusoketti avattu itse")
    return s
# @loppu soketti


def ymparisto() -> str:
    """Kertoo, miltä kovennus näyttää palvelun sisältä."""
    uid = os.getuid()
    kuka = ("root" if uid == 0
            else "dynaaminen" if 61184 <= uid <= 65519 else "tavallinen")
    kirjoitus = "sallittu" if os.access("/etc", os.W_OK) else "estetty"
    tila = os.environ.get("STATE_DIRECTORY", "")
    oma = "sallittu" if tila and os.access(tila, os.W_OK) else "ei ole"
    return f"käyttäjä={kuka} /etc={kirjoitus} tilahakemisto={oma}"


def kaadu_jos_pyydetty() -> None:
    """Testejä varten: tiedostossa on jäljellä olevien kaatumisten määrä."""
    polku = os.environ.get("MITTARI_KAATUMISIA")
    if not polku:
        return
    jaljella = int(Path(polku).read_text())
    if jaljella > 0:
        Path(polku).write_text(str(jaljella - 1))
        loki(VIRHE, "asetusten luku epäonnistui")
        sys.exit(1)


# @alku paaohjelma
def main() -> None:
    # SIGTERM on pyyntö lopettaa siististi. Käsittelijä herättää
    # pääsilmukan kirjoittamalla putkeen.
    heratys_r, heratys_w = os.pipe()

    def sigterm(_signaali: int, _kehys: FrameType | None) -> None:
        os.write(heratys_w, b"x")

    signal.signal(signal.SIGTERM, sigterm)
    kaadu_jos_pyydetty()
    kuuntelu = kuuntelusoketti()
    vahti_us = int(os.environ.get("WATCHDOG_USEC", "0"))
    odotus = vahti_us / 2e6 if vahti_us else 1.0
    pyyntoja = 0
    ilmoita("READY=1\nSTATUS=valmis, pyyntöjä 0")
    loki(INFO, "valmis")
    while True:
        valmiit, _, _ = select.select([kuuntelu.fileno(), heratys_r],
                                      [], [], odotus)
        if heratys_r in valmiit:
            break
        ilmoita("WATCHDOG=1")            # elonmerkki, jos sitä odotetaan
        if not valmiit:
            continue
        yhteys, _ = kuuntelu.accept()
        with yhteys:
            komento = yhteys.makefile().readline().strip()
            pyyntoja += 1
            if komento == "tila":
                vastaus = f"ok pyyntöjä={pyyntoja}"
            elif komento == "ymparisto":
                vastaus = ymparisto()
            else:
                vastaus = "virhe tuntematon komento"
                loki(VIRHE, f"tuntematon komento: {komento!r}")
            yhteys.sendall((vastaus + "\n").encode())
        ilmoita(f"STATUS=valmis, pyyntöjä {pyyntoja}")
    ilmoita("STOPPING=1")
    loki(INFO, f"lopetetaan, pyyntöjä {pyyntoja}")
# @loppu paaohjelma


if __name__ == "__main__":
    main()
