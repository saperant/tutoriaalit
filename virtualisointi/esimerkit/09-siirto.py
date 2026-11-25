"""Virtuaalikoneen siirto toiseen QEMU-prosessiin.

Lähdekone pysäytetään, sen koko tila (muisti, suoritin, laitteet)
tallennetaan siirtovirtana, ja kohdekone jatkaa samasta kohdasta. Elävä
siirto (live migration) tekee saman koneen käydessä: muisti kopioidaan
ensin ja muuttuneet sivut uudelleen, kunnes jäljellä on niin vähän, että
lyhyt pysäytys riittää.
"""

import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

VIERAAT = Path(__file__).resolve().parent / "vieras" / "lahteet"


class Qmp:
    """Pieni QMP-asiakas: rivi JSONia kumpaankin suuntaan."""

    def __init__(self, polku: Path) -> None:
        self.pistoke = socket.socket(socket.AF_UNIX)
        for _ in range(100):
            try:
                self.pistoke.connect(str(polku))
                break
            except (FileNotFoundError, ConnectionRefusedError):
                time.sleep(0.05)
        else:
            raise TimeoutError("QMP-pistoke ei avautunut")
        self.rivit = self.pistoke.makefile("r", encoding="utf-8")
        tervehdys = json.loads(self.rivit.readline())
        assert "QMP" in tervehdys
        self.komento("qmp_capabilities")

    def komento(self, nimi: str, **argumentit: Any) -> Any:
        pyynto = {"execute": nimi, "arguments": argumentit}
        self.pistoke.sendall(json.dumps(pyynto).encode() + b"\n")
        while True:
            vastaus = json.loads(self.rivit.readline())
            if "event" in vastaus:      # tapahtumat tulevat väliin
                continue
            if "error" in vastaus:
                raise RuntimeError(vastaus["error"]["desc"])
            return vastaus["return"]


def qemu(hak: Path, nimi: str, vieras: Path,
         *lisat: str) -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        ["qemu-system-x86_64", "-machine", "pc", "-accel", "tcg",
         "-m", "16M", "-display", "none", "-monitor", "none",
         "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
         "-qmp", f"unix:{hak / (nimi + '.sock')},server=on,wait=off",
         "-kernel", str(vieras), *lisat])


def odota(ehto: Any, aikaraja: float = 30) -> None:
    loppu = time.monotonic() + aikaraja
    while not ehto():
        if time.monotonic() > loppu:
            raise TimeoutError("aikaraja ylittyi")
        time.sleep(0.05)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        vieras = hak / "odota.elf"
        subprocess.run([VIERAAT / "rakenna.sh", VIERAAT / "odota.c",
                        vieras], check=True)
        loki = hak / "lahde.txt"
        tila = hak / "tila.bin"
        prosessit = []
        try:
            # @alku lahde
            lahde = qemu(hak, "lahde", vieras, "-serial", f"file:{loki}")
            prosessit.append(lahde)
            odota(lambda: loki.exists() and loki.read_text().endswith("\n"))
            print("lähde:", loki.read_text().strip())
            qmp = Qmp(hak / "lahde.sock")
            qmp.komento("stop")
            qmp.komento("migrate", uri=f"exec:cat > {tila}")
            odota(lambda: qmp.komento("query-migrate").get("status")
                  == "completed")
            qmp.komento("quit")
            lahde.wait(timeout=30)
            print("lähde pysäytetty, tila siirretty tiedostoon")
            # @loppu lahde

            # @alku kohde
            sarja = hak / "sarja.sock"
            kohde = qemu(hak, "kohde", vieras,
                         "-chardev",
                         f"socket,id=s0,path={sarja},server=on,wait=off",
                         "-serial", "chardev:s0",
                         "-incoming", f"exec:cat {tila}")
            prosessit.append(kohde)
            qmp2 = Qmp(hak / "kohde.sock")
            odota(lambda: qmp2.komento("query-status")["status"]
                  != "inmigrate")
            print("kohteen tila siirron jälkeen:",
                  qmp2.komento("query-status")["status"])
            yhteys = socket.socket(socket.AF_UNIX)
            yhteys.connect(str(sarja))
            qmp2.komento("cont")
            yhteys.sendall(b"X")                # syöte vieraalle
            koodi = kohde.wait(timeout=30)
            vastaus = yhteys.makefile("r", encoding="utf-8").readline()
            print("kohde:", vastaus.strip())
            print("paluuarvo", koodi, "(laskuri jatkui siirron yli)"
                  if koodi == 11 else "(laskuri nollautui!)")
            # @loppu kohde
        finally:
            for p in prosessit:
                if p.poll() is None:
                    p.kill()
                    p.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
