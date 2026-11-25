"""Rakentaa projektin kehityskontin ja ajaa siinä komennon.

Käyttö:  python3 aja_kontissa.py HAKEMISTO KOMENTO [ARGUMENTTI...]

Pieni versio siitä, mitä VS Code, Codespaces ja devcontainer-
komentorivityökalu tekevät tiedostolle .devcontainer/devcontainer.json:
kuva rakennetaan, lähdekoodi liitetään konttiin, postCreateCommand
ajetaan ja sen jälkeen annettu komento. Ominaisuuksia (features) ja
Composea tämä ei tue.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from devkontti import Asetukset, lue_jsonc, tarkista

VALITYS = ["http_proxy", "https_proxy", "no_proxy",
           "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY"]


def docker_toimii() -> bool:
    if shutil.which("docker") is None:
        return False
    return subprocess.run(["docker", "info"], capture_output=True,
                          check=False).returncode == 0


# @alku valitys
def valityspalvelin() -> tuple[list[str], list[str]]:
    """Välityspalvelimen asetukset rakennukselle ja ajolle. Paikallinen
    välityspalvelin näkyy kontille vain isännän verkossa."""
    asetetut = {n: os.environ[n] for n in VALITYS if n in os.environ}
    rakennus = [f"--build-arg={n}={a}" for n, a in asetetut.items()]
    ajo = [f"--env={n}={a}" for n, a in asetetut.items()]
    if any("127.0.0.1" in a or "localhost" in a for a in asetetut.values()):
        rakennus.append("--network=host")
        ajo.append("--network=host")
    return rakennus, ajo
# @loppu valitys


# @alku rakenna
def rakenna(hakemisto: Path, asetukset: Asetukset) -> str:
    """Palauttaa kuvan nimen: valmis kuva tai Dockerfilesta rakennettu."""
    if "image" in asetukset:
        return str(asetukset["image"])
    rakennus = asetukset["build"]
    # Polut ovat suhteessa devcontainer.json-tiedoston hakemistoon.
    kanta = hakemisto / ".devcontainer"
    kuva = f"devkontti-{hakemisto.name}"
    komento = ["docker", "build", "--quiet", f"--tag={kuva}",
               f"--file={kanta / rakennus['dockerfile']}"]
    for nimi, arvo in rakennus.get("args", {}).items():
        komento.append(f"--build-arg={nimi}={arvo}")
    komento += valityspalvelin()[0]
    komento.append(str(kanta / rakennus.get("context", ".")))
    subprocess.run(komento, check=True, stdout=subprocess.DEVNULL)
    return kuva
# @loppu rakenna


# @alku aja
def aja(hakemisto: Path, asetukset: Asetukset, kuva: str,
        komento: list[str]) -> int:
    oletus = f"/workspaces/{hakemisto.name}"
    tyohakemisto = str(asetukset.get("workspaceFolder", oletus)).replace(
        "${localWorkspaceFolderBasename}", hakemisto.name)
    ymparisto = asetukset.get("containerEnv", {})

    # Kontissa ajetaan ensin postCreateCommand ja sitten pyydetty komento.
    vaiheet = [shlex.join(komento)]
    if isinstance(asetukset.get("postCreateCommand"), str):
        vaiheet.insert(0, str(asetukset["postCreateCommand"]))
    return subprocess.run(
        ["docker", "run", "--rm",
         # Sama käyttäjä kuin isännällä, jotta liitetyn hakemiston
         # tiedostot ovat luettavissa (vrt. updateRemoteUserUID).
         f"--user={os.getuid()}:{os.getgid()}",
         f"--volume={hakemisto}:{tyohakemisto}",
         f"--workdir={tyohakemisto}",
         *[f"--env={n}={a}" for n, a in ymparisto.items()],
         *valityspalvelin()[1],
         kuva, "sh", "-c", " && ".join(vaiheet)],
        check=False).returncode
# @loppu aja


def main(argumentit: list[str]) -> int:
    if len(argumentit) < 2:
        print(__doc__)
        return 2
    hakemisto = Path(argumentit[0]).resolve()
    tiedosto = hakemisto / ".devcontainer" / "devcontainer.json"
    asetukset = lue_jsonc(tiedosto.read_text("utf-8"))
    virheet = tarkista(asetukset)
    if virheet or "dockerComposeFile" in asetukset:
        print("\n".join(virheet or ["Composea ei tueta"]))
        return 1
    if not docker_toimii():
        print("OHITETTU: Docker ei ole käytettävissä")
        return 0
    kuva = rakenna(hakemisto, asetukset)
    print(f"kuva rakennettu: {kuva}", flush=True)
    return aja(hakemisto, asetukset, kuva, argumentit[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
