"""devcontainer.json-tiedoston lukeminen ja tarkistaminen.

Käyttö:  python3 devkontti.py TIEDOSTO...

Tarkistin tuntee Dev Containers -määrittelyn yleisimmät kentät. Se ei
korvaa virallista JSON-skeemaa, mutta löytää tavallisimmat virheet:
kirjoitusvirheen kentän nimessä, väärän tyypin, puuttuvan tai
kaksinkertaisen kuvan lähteen ja tuntemattoman muuttujan.
"""

from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any

Asetukset = dict[str, Any]


# @alku jsonc
def lue_jsonc(teksti: str) -> Asetukset:
    """Jäsentää JSONin, jossa saa olla kommentteja ja ylimääräinen
    pilkku viimeisen alkion jälkeen (JSON with Comments)."""
    osat: list[str] = []
    i = 0
    while i < len(teksti):
        merkki = teksti[i]
        if merkki == '"':                      # merkkijono sellaisenaan
            loppu = i + 1
            while teksti[loppu] != '"':
                loppu += 2 if teksti[loppu] == "\\" else 1
            osat.append(teksti[i:loppu + 1])
            i = loppu + 1
        elif teksti.startswith("//", i):       # rivin loppuun
            rivinvaihto = teksti.find("\n", i)
            i = len(teksti) if rivinvaihto < 0 else rivinvaihto
        elif teksti.startswith("/*", i):       # lohkokommentti
            i = teksti.index("*/", i) + 2
        else:
            osat.append(merkki)
            i += 1
    siisti = re.sub(r",(\s*[}\]])", r"\1", "".join(osat))
    tulos = json.loads(siisti)
    if not isinstance(tulos, dict):
        raise ValueError("ylimmän tason on oltava olio")
    return tulos
# @loppu jsonc


# Kentän tyyppi: Pythonin tyyppi tai usean vaihtoehdon monikko.
KOMENTO = (str, list, dict)
KENTAT: dict[str, Any] = {
    "name": str,
    "image": str,
    "build": dict,
    "dockerComposeFile": (str, list),
    "service": str,
    "runServices": list,
    "features": dict,
    "overrideFeatureInstallOrder": list,
    "workspaceFolder": str,
    "workspaceMount": str,
    "mounts": list,
    "runArgs": list,
    "appPort": (int, str, list),
    "forwardPorts": list,
    "portsAttributes": dict,
    "otherPortsAttributes": dict,
    "containerEnv": dict,
    "remoteEnv": dict,
    "containerUser": str,
    "remoteUser": str,
    "updateRemoteUserUID": bool,
    "userEnvProbe": str,
    "overrideCommand": bool,
    "shutdownAction": str,
    "init": bool,
    "privileged": bool,
    "capAdd": list,
    "securityOpt": list,
    "initializeCommand": KOMENTO,
    "onCreateCommand": KOMENTO,
    "updateContentCommand": KOMENTO,
    "postCreateCommand": KOMENTO,
    "postStartCommand": KOMENTO,
    "postAttachCommand": KOMENTO,
    "waitFor": str,
    "hostRequirements": dict,
    "customizations": dict,
}
RAKENNUS: dict[str, Any] = {
    "dockerfile": str,
    "context": str,
    "args": dict,
    "target": str,
    "cacheFrom": (str, list),
    "options": list,
}
MUUTTUJAT = {
    "localWorkspaceFolder", "localWorkspaceFolderBasename",
    "containerWorkspaceFolder", "containerWorkspaceFolderBasename",
    "devcontainerId",
}
MUUTTUJA = re.compile(r"\$\{([^}]*)\}")


def _tyyppi(odotettu: Any) -> str:
    nimet = {str: "merkkijono", int: "luku", bool: "totuusarvo",
             list: "taulukko", dict: "olio"}
    tyypit = odotettu if isinstance(odotettu, tuple) else (odotettu,)
    return " tai ".join(nimet[t] for t in tyypit)


def _tarkista_kentat(arvot: Asetukset, sallitut: dict[str, Any],
                     paikka: str) -> list[str]:
    virheet = []
    for nimi, arvo in arvot.items():
        if nimi not in sallitut:
            lahin = difflib.get_close_matches(nimi, sallitut, n=1)
            vihje = f" (tarkoititko {lahin[0]}?)" if lahin else ""
            virheet.append(f"{paikka}{nimi}: tuntematon kenttä{vihje}")
            continue
        odotettu = sallitut[nimi]
        # bool on Pythonissa int:n alaluokka, joten se suljetaan pois.
        vaara_bool = isinstance(arvo, bool) and odotettu is not bool
        if vaara_bool or not isinstance(arvo, odotettu):
            virheet.append(f"{paikka}{nimi}: pitää olla "
                           f"{_tyyppi(odotettu)}")
    return virheet


def _merkkijonot(arvo: Any) -> list[str]:
    if isinstance(arvo, str):
        return [arvo]
    if isinstance(arvo, list):
        return [m for a in arvo for m in _merkkijonot(a)]
    if isinstance(arvo, dict):
        return [m for a in arvo.values() for m in _merkkijonot(a)]
    return []


# @alku tarkista
def tarkista(asetukset: Asetukset) -> list[str]:
    """Palauttaa virheet; tyhjä lista tarkoittaa kelvollista."""
    virheet = _tarkista_kentat(asetukset, KENTAT, "")
    rakennus = asetukset.get("build")
    if isinstance(rakennus, dict):
        virheet += _tarkista_kentat(rakennus, RAKENNUS, "build.")
        if "dockerfile" not in rakennus:
            virheet.append("build.dockerfile: puuttuu")

    # Kontin lähteitä on täsmälleen yksi: kuva, Dockerfile tai Compose.
    lahteet = [n for n in ("image", "build", "dockerComposeFile")
               if n in asetukset]
    if not lahteet:
        virheet.append("kontin lähde puuttuu: image, build tai "
                       "dockerComposeFile")
    elif len(lahteet) > 1:
        virheet.append("vain yksi lähde: " + ", ".join(lahteet))
    if "dockerComposeFile" in asetukset:
        for pakollinen in ("service", "workspaceFolder"):
            if pakollinen not in asetukset:
                virheet.append(f"{pakollinen}: pakollinen Composen kanssa")

    for teksti in _merkkijonot(asetukset):
        for nimi in MUUTTUJA.findall(teksti):
            if nimi.split(":")[0] in ("localEnv", "containerEnv"):
                continue
            if nimi not in MUUTTUJAT:
                virheet.append(f"tuntematon muuttuja ${{{nimi}}}")
    return virheet
# @loppu tarkista


# @alku huomiot
def huomiot(asetukset: Asetukset) -> list[str]:
    """Asetukset, jotka ovat sallittuja mutta ansaitsevat perustelun."""
    tulos = []
    argumentit = " ".join(_merkkijonot(asetukset.get("runArgs", []))
                          + _merkkijonot(asetukset.get("mounts", [])))
    if "docker.sock" in argumentit:
        tulos.append("jakaa isännän Docker-soketin: kontista voi "
                     "hallita koko isäntää")
    if asetukset.get("privileged") or "--privileged" in argumentit:
        tulos.append("ajetaan etuoikeutettuna")
    if "seccomp=unconfined" in argumentit:
        tulos.append("seccomp-suodatin on pois päältä")
    if asetukset.get("remoteUser") == "root":
        tulos.append("käyttäjänä root")
    kuva = asetukset.get("image", "")
    if kuva and (":" not in kuva or kuva.endswith(":latest")):
        tulos.append("kuvan versio on lukitsematta")
    return tulos
# @loppu huomiot


def main(argumentit: list[str]) -> int:
    if not argumentit:
        print(__doc__)
        return 2
    virheellisia = 0
    for nimi in argumentit:
        try:
            asetukset = lue_jsonc(Path(nimi).read_text("utf-8"))
        except (ValueError, IndexError) as virhe:
            print(f"{nimi}: ei ole kelvollista JSONia ({virhe})")
            virheellisia += 1
            continue
        virheet = tarkista(asetukset)
        print(f"{nimi}: {'VIRHE' if virheet else 'OK'}")
        for rivi in virheet:
            print(f"  virhe: {rivi}")
        for rivi in huomiot(asetukset):
            print(f"  huomio: {rivi}")
        virheellisia += bool(virheet)
    return 1 if virheellisia else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
