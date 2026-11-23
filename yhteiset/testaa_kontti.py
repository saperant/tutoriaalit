#!/usr/bin/env python3
"""Testaa tutoriaalin esimerkit sen omassa kehityskontissa.

Käyttö:  python3 yhteiset/testaa_kontti.py <tutoriaali> [<tutoriaali> ...]
         python3 yhteiset/testaa_kontti.py --kaikki

Lukee tiedoston .devcontainer/<tutoriaali>/devcontainer.json, rakentaa
sen kuvaamasta Dockerfilesta kuvan samoilla rakennusargumenteilla ja
ajaa kontissa `make -C <tutoriaali> testaa`. Näin varmistetaan, että
lukijalle tarjottu kehityskontti todella riittää esimerkkien
kääntämiseen ja ajamiseen.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
VALITYS = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
           "no_proxy", "NO_PROXY"]


def testaa(tutoriaali: str) -> bool:
    konfiguraatio = JUURI / ".devcontainer" / tutoriaali / "devcontainer.json"
    asetukset = json.loads(konfiguraatio.read_text("utf-8"))
    rakennus = asetukset["build"]
    dockerfile = (konfiguraatio.parent / rakennus["dockerfile"]).resolve()
    konteksti = (konfiguraatio.parent / rakennus.get("context", ".")).resolve()
    kuva = f"tutoriaalit-{tutoriaali}"

    komento = ["docker", "build", "-q", "-t", kuva, "-f", str(dockerfile)]
    for avain, arvo in rakennus.get("args", {}).items():
        komento += ["--build-arg", f"{avain}={arvo}"]
    for avain in VALITYS:
        if avain in os.environ:
            komento += ["--build-arg", f"{avain}={os.environ[avain]}"]
    komento.append(str(konteksti))
    print(f"== {tutoriaali}: rakennetaan kuva {kuva}", flush=True)
    if subprocess.run(komento, stdout=subprocess.DEVNULL).returncode != 0:
        print(f"{tutoriaali}: kuvan rakentaminen epäonnistui")
        return False

    print(f"== {tutoriaali}: make testaa kontissa", flush=True)
    tulos = subprocess.run(
        ["docker", "run", "--rm", "-v", f"{JUURI}:/w", "-w", "/w", kuva,
         "make", "-C", tutoriaali, "testaa"])
    return tulos.returncode == 0


def main() -> int:
    argumentit = sys.argv[1:]
    if argumentit == ["--kaikki"]:
        argumentit = sorted(
            p.parent.name for p in
            (JUURI / ".devcontainer").glob("*/devcontainer.json")
            if p.parent.name != "kirjoittaminen"
            and (JUURI / p.parent.name / "Makefile").exists())
    if not argumentit:
        print(__doc__)
        return 2
    epaonnistuneet = [t for t in argumentit if not testaa(t)]
    if epaonnistuneet:
        print("EPÄONNISTUI:", ", ".join(epaonnistuneet))
        return 1
    print("OK:", ", ".join(argumentit))
    return 0


if __name__ == "__main__":
    sys.exit(main())
