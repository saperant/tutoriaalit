"""HAProxyn ajonaikainen hallintarajapinta (Runtime API).

Komennot lähetetään hallintasokettiin tekstinä, ja vastaus luetaan,
kunnes HAProxy sulkee yhteyden.
"""

from __future__ import annotations

import socket
from pathlib import Path


def komento(hallinta: Path, rivi: str) -> str:
    with socket.socket(socket.AF_UNIX) as s:
        s.settimeout(5)
        s.connect(str(hallinta))
        s.sendall(rivi.encode() + b"\n")
        osat = []
        while data := s.recv(65536):
            osat.append(data)
    return b"".join(osat).decode()


def tilat(hallinta: Path, taustaosa: str) -> dict[str, str]:
    """Palvelinten tilat (UP, DOWN, MAINT ...) `show stat` -CSV:stä."""
    rivit = komento(hallinta, "show stat").splitlines()
    otsikot = rivit[0].lstrip("# ").split(",")
    tulos = {}
    for rivi in rivit[1:]:
        kentat = dict(zip(otsikot, rivi.split(","), strict=False))
        if kentat.get("pxname") == taustaosa and \
                kentat.get("svname") not in ("FRONTEND", "BACKEND"):
            tulos[kentat["svname"]] = kentat["status"].split()[0]
    return tulos
