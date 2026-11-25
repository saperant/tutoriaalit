"""Käytännöt koodina: tarkistaa Kubernetes-manifestit ennen käyttöönottoa.

Käyttö:  python3 politiikka.py <tiedosto.yaml> ...

Samaa ajatusta toteuttavat tuotannossa esimerkiksi Kyverno, OPA
Gatekeeper ja Conftest: säännöt ovat koodia, ja putki pysähtyy, jos
manifesti rikkoo niitä.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

TYOKUORMAT = {"Deployment", "StatefulSet", "DaemonSet", "Job"}


def poddit(dokumentti: dict[str, Any]) -> Iterator[dict[str, Any]]:
    if dokumentti.get("kind") in TYOKUORMAT:
        yield dokumentti["spec"]["template"]["spec"]


# @alku saannot
def tarkista_kontti(pod: dict[str, Any], s: dict[str, Any]) -> list[str]:
    virheet = []
    kuva = s.get("image", "")
    if ":" not in kuva.rsplit("/", 1)[-1] or kuva.endswith(":latest"):
        virheet.append(f"kuva '{kuva}' ilman kiinteää versiota")
    resurssit = s.get("resources", {})
    if "memory" not in resurssit.get("limits", {}):
        virheet.append("muistiraja puuttuu")
    if "requests" not in resurssit:
        virheet.append("resurssipyynnöt puuttuvat")
    for koetin in ("readinessProbe", "livenessProbe"):
        if koetin not in s:
            virheet.append(f"{koetin} puuttuu")
    turva = {**pod.get("securityContext", {}),
             **s.get("securityContext", {})}
    if not turva.get("runAsNonRoot"):
        virheet.append("runAsNonRoot ei ole päällä")
    if turva.get("allowPrivilegeEscalation", True):
        virheet.append("allowPrivilegeEscalation sallittu")
    if not turva.get("readOnlyRootFilesystem"):
        virheet.append("juuritiedostojärjestelmä kirjoitettavissa")
    return virheet
# @loppu saannot


def main(tiedostot: list[str]) -> int:
    loydetyt = 0
    for nimi in tiedostot:
        for dok in yaml.safe_load_all(Path(nimi).read_text("utf-8")):
            if not dok:
                continue
            for pod in poddit(dok):
                for s in pod.get("containers", []):
                    virheet = tarkista_kontti(pod, s)
                    if virheet:
                        tunnus = f"{dok['kind']}/{dok['metadata']['name']}"
                        print(f"{nimi}: {tunnus}, kontti {s['name']}:")
                    for virhe in virheet:
                        print(f"  - {virhe}")
                    loydetyt += len(virheet)
    if loydetyt:
        print(f"{loydetyt} rikkomusta")
        return 1
    print("OK: ei rikkomuksia")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
