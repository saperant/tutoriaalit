"""Kehityskontin asetusten tarkistus: oikeudet, kuvat ja salaisuudet.

Kehityskontti on toistettava ympäristö, mutta huolimattomat asetukset
antavat sille enemmän valtaa kuin kehittäjän koneella on tarpeen.
"""

import re
from collections.abc import Iterator
from typing import Any

TIIVISTE = re.compile(r"@sha256:[0-9a-f]{64}$")
SALAINEN = re.compile(r"(?i)(token|secret|password|salasana|key)")


# @alku tarkistus
def tarkista(asetukset: dict[str, Any]) -> Iterator[str]:
    kuva = asetukset.get("image", "")
    if kuva and not TIIVISTE.search(kuva):
        nimi = kuva.rsplit("/", 1)[-1]
        yield f"kuvaa ei ole kiinnitetty tiivisteeseen: {nimi}"
    ajo = asetukset.get("runArgs", [])
    if "--privileged" in ajo:
        yield "--privileged antaa kontille isäntäkoneen ytimen oikeudet"
    for liitos in asetukset.get("mounts", []):
        if "docker.sock" in liitos:
            yield "Dockerin soketti kontissa = root isäntäkoneella"
    for nimi, arvo in asetukset.get("containerEnv", {}).items():
        if SALAINEN.search(nimi) and not arvo.startswith("${localEnv:"):
            yield f"salaisuus asetustiedostossa: {nimi}"
    if asetukset.get("remoteUser", "root") == "root":
        yield "kehitys ajetaan root-käyttäjänä"
# @loppu tarkistus


# Samat asetukset kuin devcontainer.json-tiedostoissa (JSON-muodossa).
ASETUKSET: dict[str, dict[str, Any]] = {
    "huolimaton": {
        "image": "mcr.microsoft.com/devcontainers/python:latest",
        "runArgs": ["--privileged"],
        "mounts": ["source=/var/run/docker.sock,"
                   "target=/var/run/docker.sock,type=bind"],
        "containerEnv": {"API_TOKEN": "sk-9f3b2c71e04d"},
    },
    "kiinnitetty": {
        "image": "mcr.microsoft.com/devcontainers/python@sha256:"
                 + "a" * 64,
        "containerEnv": {"API_TOKEN": "${localEnv:API_TOKEN}"},
        "remoteUser": "vscode",
    },
}


def main() -> None:
    for nimi, asetukset in ASETUKSET.items():
        havainnot = list(tarkista(asetukset))
        print(f"{nimi}: {len(havainnot)} havaintoa")
        for h in havainnot:
            print(f"  - {h}")


if __name__ == "__main__":
    main()
