"""Esimerkkijärjestelmän palvelut prosesseina.

Tuotannossa Redis, PostgreSQL, HAProxy ja omat palvelut ajettaisiin
kontteina (ks. luku 12 ja compose.yaml). Testeissä ne käynnistetään
tavallisina prosesseina omaan väliaikaishakemistoon. Ne kuuntelevat
vain osoitetta 127.0.0.1 käyttöjärjestelmän antamissa vapaissa
porteissa, ja ne pysäytetään aina, myös virheen sattuessa.

    with Ymparisto() as ymp:
        redis = ymp.redis()
        api = ymp.palvelu("jarjestelma.taustapalvelu", "--nimi", "a")
"""

from __future__ import annotations

import contextlib
import glob
import os
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

from jarjestelma.resp import Redis

ESIMERKIT = Path(__file__).resolve().parent.parent


def vapaa_portti() -> int:
    """Pyytää käyttöjärjestelmältä vapaan portin. Portti vapautetaan
    heti, joten toinen prosessi voi ehtiä väliin; testeissä riski on
    pieni, ja palvelun käynnistys epäonnistuu silloin selvästi."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def portti_auki(portti: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", portti), timeout=0.5):
            return True
    except OSError:
        return False


def odota(ehto: Callable[[], bool], kuvaus: str,
          aikaraja: float = 30.0) -> None:
    """Odottaa, kunnes ehto täyttyy, tai nostaa TimeoutError-virheen."""
    loppu = time.monotonic() + aikaraja
    while time.monotonic() < loppu:
        if ehto():
            return
        time.sleep(0.05)
    raise TimeoutError(f"ei valmistunut {aikaraja:.0f} s:ssa: {kuvaus}")


def _pg_bin(ohjelma: str) -> str:
    """PostgreSQLin ohjelmat eivät ole Debianissa PATHissa."""
    loydetyt = sorted(glob.glob(f"/usr/lib/postgresql/*/bin/{ohjelma}"))
    if loydetyt:
        return loydetyt[-1]
    polku = shutil.which(ohjelma)
    if polku is None:
        raise FileNotFoundError(f"PostgreSQL-ohjelmaa ei löydy: {ohjelma}")
    return polku


def _pg_kayttajana() -> list[str]:
    """PostgreSQL ei suostu käynnistymään pääkäyttäjänä (esim. kehitys-
    kontissa), joten se ajetaan silloin käyttäjänä postgres."""
    return ["runuser", "-u", "postgres", "--"] if os.geteuid() == 0 else []


@dataclass
class Palvelu:
    """Käynnistetty oma palvelu: portti ja prosessi."""
    nimi: str
    portti: int
    prosessi: subprocess.Popen[str]


@dataclass
class Postgres:
    portti: int
    data: Path


class Ymparisto(contextlib.AbstractContextManager["Ymparisto"]):
    def __init__(self) -> None:
        self.hakemisto = Path(tempfile.mkdtemp(prefix="jarjestelma-"))
        self.hakemisto.chmod(0o755)
        self._pinot = contextlib.ExitStack()
        # SIGTERM (esim. timeout-komento) siivoaa kuten virhe: palvelut
        # pysäytetään eikä orpoja prosesseja jää.
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(143))

    def __exit__(self, tyyppi: type[BaseException] | None,
                 virhe: BaseException | None,
                 jalki: TracebackType | None) -> None:
        try:
            self._pinot.close()
        finally:
            shutil.rmtree(self.hakemisto, ignore_errors=True)

    def _kaynnista(self, komento: list[str], loki: Path,
                   ymparisto: dict[str, str] | None = None
                   ) -> subprocess.Popen[str]:
        with loki.open("w") as tiedosto:
            prosessi = subprocess.Popen(
                komento, stdout=tiedosto, stderr=subprocess.STDOUT,
                text=True, env={**os.environ, **(ymparisto or {})})
        self._pinot.callback(_lopeta, prosessi)
        return prosessi

    # @alku redis
    def redis(self, *asetukset: str) -> int:
        """Käynnistää Redisin ilman pysyvyyttä ja palauttaa portin."""
        portti = vapaa_portti()
        hak = self.hakemisto / f"redis-{portti}"
        hak.mkdir()
        self._kaynnista(
            ["redis-server", "--port", str(portti), "--bind", "127.0.0.1",
             "--save", "", "--appendonly", "no", "--dir", str(hak),
             *asetukset], hak / "loki")

        def vastaa() -> bool:
            try:
                with Redis(portti) as r:
                    return r.komento("PING") == "PONG"
            except OSError:
                return False

        odota(vastaa, "redis-server")
        return portti
    # @loppu redis

    def postgres(self) -> Postgres:
        """Käynnistää tyhjän PostgreSQL-klusterin."""
        portti = vapaa_portti()
        data = self._pg_hakemisto(f"pg-{portti}")
        _aja([*_pg_kayttajana(), _pg_bin("initdb"), "-D", str(data),
              "-U", "tutoriaali", "--auth=trust", "-E", "UTF8",
              "--locale=C", "--no-sync"])
        return self._pg_kaynnista(data, portti)

    # @alku replika
    def replika(self, ensisijainen: Postgres, viive: str) -> Postgres:
        """Kopioi klusterin pg_basebackupilla ja käynnistää sen
        lukureplikaksi, joka soveltaa muutokset viiveellä."""
        portti = vapaa_portti()
        data = self._pg_hakemisto(f"pg-{portti}")
        _aja([*_pg_kayttajana(), _pg_bin("pg_basebackup"),
              "-h", "127.0.0.1", "-p", str(ensisijainen.portti),
              "-U", "tutoriaali", "-D", str(data), "-R", "-X", "stream",
              "--no-sync"])
        with (data / "postgresql.auto.conf").open("a") as asetukset:
            asetukset.write(f"recovery_min_apply_delay = '{viive}'\n")
        return self._pg_kaynnista(data, portti)
    # @loppu replika

    def _pg_hakemisto(self, nimi: str) -> Path:
        hak = self.hakemisto / nimi
        hak.mkdir(mode=0o700)
        if os.geteuid() == 0:
            shutil.chown(hak, "postgres", "postgres")
        return hak

    def _pg_kaynnista(self, data: Path, portti: int) -> Postgres:
        asetukset = (f"-p {portti} -k {data} -c listen_addresses=127.0.0.1"
                     " -c fsync=off")
        try:
            _aja([*_pg_kayttajana(), _pg_bin("pg_ctl"), "-D", str(data),
                  "-l", str(data / "loki"), "-o", asetukset, "-w", "start"])
        except RuntimeError as virhe:
            loki = (data / "loki").read_text(errors="replace")
            raise RuntimeError(f"{virhe}\nPostgreSQLin loki:\n{loki}") \
                from None
        self._pinot.callback(
            _aja, [*_pg_kayttajana(), _pg_bin("pg_ctl"), "-D", str(data),
                   "-m", "immediate", "-w", "stop"])
        return Postgres(portti, data)

    def haproxy(self, asetus: Path, ymparisto: dict[str, str]) -> Path:
        """Käynnistää HAProxyn. Asetustiedosto lukee portit ympäristö-
        muuttujista; palauttaa hallintasoketin polun."""
        hallinta = self.hakemisto / f"haproxy-{vapaa_portti()}.sock"
        ymp = {**ymparisto, "HALLINTA": str(hallinta)}
        _aja(["haproxy", "-c", "-q", "-f", str(asetus)], ymp)
        self._kaynnista(["haproxy", "-db", "-f", str(asetus)],
                        self.hakemisto / f"{hallinta.stem}.loki", ymp)
        odota(hallinta.exists, "HAProxyn hallintasoketti")
        return hallinta

    def palvelu(self, moduuli: str, *argumentit: str) -> Palvelu:
        """Käynnistää oman Python-palvelun. Palvelu valitsee portin itse
        ja kertoo sen ensimmäisellä tulosterivillään."""
        loki = self.hakemisto / f"{moduuli}-{vapaa_portti()}.loki"
        with loki.open("w") as virheet:
            prosessi = subprocess.Popen(
                [sys.executable, "-m", moduuli, *argumentit],
                stdout=subprocess.PIPE, stderr=virheet, text=True,
                env={**os.environ, "PYTHONPATH": str(ESIMERKIT)})
        self._pinot.callback(_lopeta, prosessi)
        rivi = prosessi.stdout.readline().split() if prosessi.stdout else []
        if len(rivi) != 2 or rivi[0] != "PORTTI":
            raise RuntimeError(f"{moduuli} ei käynnistynyt:\n"
                               + loki.read_text(errors="replace"))
        return Palvelu(moduuli, int(rivi[1]), prosessi)


def kaada(palvelu: Palvelu) -> None:
    """Tappaa palvelun varoittamatta (SIGKILL), kuin kone kaatuisi."""
    palvelu.prosessi.send_signal(signal.SIGKILL)
    palvelu.prosessi.wait()


def _aja(komento: list[str], ymparisto: dict[str, str] | None = None) -> None:
    tulos = subprocess.run(komento, capture_output=True, text=True,
                           env={**os.environ, **(ymparisto or {})},
                           check=False)
    if tulos.returncode != 0:
        raise RuntimeError(f"{' '.join(komento)}:\n{tulos.stdout}"
                           f"{tulos.stderr}")


def _lopeta(prosessi: subprocess.Popen[str]) -> None:
    if prosessi.poll() is None:
        prosessi.terminate()
        try:
            prosessi.wait(timeout=10)
        except subprocess.TimeoutExpired:
            prosessi.kill()
            prosessi.wait()
    if prosessi.stdout is not None:
        prosessi.stdout.close()
