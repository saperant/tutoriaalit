"""Pieni valvoja, joka tekee palvelulle saman kuin systemd.

Tämä ei korvaa systemd:tä. Se toteuttaa testiä varten ne kolme asiaa,
joista palvelun ja valvojan välinen sopimus koostuu: kuuntelusoketin
välitys (LISTEN_FDS), valmiuden odotus (NOTIFY_SOCKET) ja
uudelleenkäynnistys käynnistysrajalla.
"""

import os
import select
import signal
import socket
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Palvelu:
    komento: list[str]
    ymparisto: dict[str, str] = field(default_factory=dict)
    pid: int = 0
    tila: str = "inactive"
    viesti: str = ""                     # viimeisin STATUS=


class Valvoja:
    def __init__(self) -> None:
        self.hakemisto = tempfile.TemporaryDirectory()
        self.ilmoitukset = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.osoite = str(Path(self.hakemisto.name) / "notify")
        self.ilmoitukset.bind(self.osoite)
        self._lokidata = b""
        self._lokiputki = -1

    @property
    def loki(self) -> list[str]:
        """Palvelun vakiovirheeseen kirjoittamat rivit."""
        return self._lokidata.decode().splitlines()

    def sulje(self) -> None:
        self.ilmoitukset.close()
        self.hakemisto.cleanup()

    # @alku kaynnista
    def kaynnista(self, p: Palvelu,
                  kuuntelu: socket.socket | None = None) -> None:
        """fork ja exec: lapsi saa soketin kuvaajana 3 ja ympäristön."""
        loki_r, loki_w = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.dup2(loki_w, 2)           # vakiovirhe lokiin
            ymp = {**os.environ, **p.ymparisto,
                   "NOTIFY_SOCKET": self.osoite}
            if kuuntelu is not None:
                os.dup2(kuuntelu.fileno(), 3)
                os.set_inheritable(3, True)
                ymp["LISTEN_FDS"] = "1"
                ymp["LISTEN_PID"] = str(os.getpid())
            os.execve(p.komento[0], p.komento, ymp)
        os.close(loki_w)
        p.pid, p.tila = pid, "activating"
        self._lokiputki = loki_r
    # @loppu kaynnista

    # @alku odota
    def odota_valmiutta(self, p: Palvelu, aikaraja_s: float = 10.0) -> bool:
        """Type=notify: palvelu on käynnissä vasta, kun se sanoo READY=1."""
        while p.tila == "activating":
            valmiit, _, _ = select.select(
                [self.ilmoitukset.fileno(), self._lokiputki], [], [],
                aikaraja_s)
            if not valmiit:
                os.kill(p.pid, signal.SIGKILL)
                p.tila = "failed (timeout)"
            for lahde in valmiit:
                if lahde == self.ilmoitukset.fileno():
                    self._kasittele_ilmoitus(p)
                elif not self._lue_lokia():      # putki sulkeutui
                    _, status = os.waitpid(p.pid, 0)
                    koodi = os.waitstatus_to_exitcode(status)
                    p.tila = f"failed (exit-code {koodi})"
        return p.tila == "active"
    # @loppu odota

    def _kasittele_ilmoitus(self, p: Palvelu) -> None:
        for rivi in self.ilmoitukset.recv(4096).decode().splitlines():
            avain, _, arvo = rivi.partition("=")
            if avain == "READY" and arvo == "1":
                p.tila = "active"
            elif avain == "STATUS":
                p.viesti = arvo
            elif avain == "STOPPING":
                p.tila = "deactivating"

    def _lue_lokia(self) -> bool:
        data = os.read(self._lokiputki, 65536)
        self._lokidata += data           # rivi voi tulla kahdessa osassa
        return bool(data)

    def pysayta(self, p: Palvelu) -> int:
        """SIGTERM ja odotus; palauttaa paluuarvon."""
        os.kill(p.pid, signal.SIGTERM)
        while self._lue_lokia():
            pass
        os.close(self._lokiputki)
        while select.select([self.ilmoitukset], [], [], 0)[0]:
            self._kasittele_ilmoitus(p)
        _, status = os.waitpid(p.pid, 0)
        p.tila = "inactive"
        return os.waitstatus_to_exitcode(status)

    # @alku uudelleen
    def aja_kaynnistyskaytannolla(self, p: Palvelu,
                                  raja: int = 3) -> list[str]:
        """Restart=on-failure ja StartLimitBurst=raja."""
        tapahtumat = []
        for yritys in range(1, raja + 1):
            self.kaynnista(p)
            if self.odota_valmiutta(p):
                tapahtumat.append(f"yritys {yritys}: active")
                return tapahtumat
            os.close(self._lokiputki)
            tapahtumat.append(f"yritys {yritys}: {p.tila}")
        p.tila = "failed (käynnistysraja täynnä)"
        tapahtumat.append(f"ei enää yrityksiä: {p.tila}")
        return tapahtumat
    # @loppu uudelleen


def python_komento(skripti: Path) -> list[str]:
    return [sys.executable, str(skripti)]
