"""QEMU:n hallintarajapinta QMP: käynnistetään kone pysäytettynä,
kysytään sen tila, annetaan sen jatkaa ja luetaan paluuarvo.

Hallintatyökalut (libvirt, OpenStack, Proxmox) ohjaavat QEMU:a juuri
tällä JSON-protokollalla Unix-pistokkeen yli.
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


# @alku qmp
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
# @loppu qmp


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        hak = Path(tmp)
        vieras = hak / "hei.elf"
        subprocess.run([VIERAAT / "rakenna.sh", VIERAAT / "hei.c",
                        vieras], check=True)
        # @alku kaynnistys
        qemu = subprocess.Popen(
            ["qemu-system-x86_64", "-machine", "pc", "-accel", "tcg",
             "-m", "16M", "-display", "none", "-monitor", "none",
             "-serial", f"file:{hak / 'sarja.txt'}",
             "-device", "isa-debug-exit,iobase=0xf4,iosize=0x04",
             "-qmp", f"unix:{hak / 'qmp.sock'},server=on,wait=off",
             "-S",                      # älä käynnistä suoritinta vielä
             "-kernel", str(vieras)])
        # @loppu kaynnistys
        try:
            # @alku hallinta
            qmp = Qmp(hak / "qmp.sock")
            tila = qmp.komento("query-status")
            print("tila ennen käynnistystä:", tila["status"])
            for cpu in qmp.komento("query-cpus-fast"):
                print(f"vCPU {cpu['cpu-index']}: {cpu['target']}")
            print("KVM käytössä:", qmp.komento("query-kvm")["enabled"])
            qmp.komento("cont")             # suoritin käyntiin
            koodi = qemu.wait(timeout=30)
            print("vieras sammutti koneen, paluuarvo", koodi)
            # @loppu hallinta
            print("sarjaportti:", (hak / "sarja.txt").read_text().strip())
        finally:
            if qemu.poll() is None:
                qemu.kill()
                qemu.wait()
    return 0


if __name__ == "__main__":
    sys.exit(main())
