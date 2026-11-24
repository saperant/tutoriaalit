"""SBOM CycloneDX-muodossa lukitustiedostosta ja kahden SBOM:n vertailu.

SBOM (software bill of materials) luettelee, mistä osista ohjelmisto
koostuu. Kun uusi haavoittuvuus julkaistaan, SBOM vastaa minuuteissa
kysymykseen "onko meillä tätä ja missä versiossa".
"""

import hashlib
import json
from typing import Any

Paketti = tuple[str, str]          # nimi, versio


# @alku sbom
def sbom(tuote: str, versio: str, paketit: list[Paketti]) -> dict[str, Any]:
    komponentit = [
        {"type": "library", "name": nimi, "version": ver,
         "purl": f"pkg:pypi/{nimi}@{ver}"}
        for nimi, ver in sorted(paketit)]
    # Sarjanumero sisällöstä: sama syöte -> sama SBOM (toistettavuus).
    sisalto = json.dumps(komponentit, sort_keys=True).encode()
    uuid = hashlib.sha256(sisalto).hexdigest()
    return {
        "bomFormat": "CycloneDX", "specVersion": "1.6",
        "serialNumber": f"urn:uuid:{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}"
                        f"-{uuid[16:20]}-{uuid[20:32]}",
        "metadata": {"component": {"type": "application",
                                   "name": tuote, "version": versio}},
        "components": komponentit,
    }
# @loppu sbom


# @alku vertailu
def vertaa(vanha: dict[str, Any], uusi: dict[str, Any]) -> list[str]:
    def versiot(s: dict[str, Any]) -> dict[str, str]:
        return {k["name"]: k["version"] for k in s["components"]}
    a, b = versiot(vanha), versiot(uusi)
    muutokset = [f"+ {n} {b[n]}" for n in sorted(b.keys() - a.keys())]
    muutokset += [f"- {n} {a[n]}" for n in sorted(a.keys() - b.keys())]
    muutokset += [f"~ {n} {a[n]} -> {b[n]}" for n in sorted(a.keys() & b)
                  if a[n] != b[n]]
    return muutokset
# @loppu vertailu


def main() -> None:
    v1 = sbom("tilauspalvelu", "1.4.0", [
        ("requests", "2.31.0"), ("urllib3", "2.0.7"),
        ("jinja2", "3.1.2")])
    v2 = sbom("tilauspalvelu", "1.5.0", [
        ("requests", "2.32.3"), ("urllib3", "2.2.3"),
        ("pyyaml", "6.0.2")])
    print("ensimmäinen komponentti:", v1["components"][0]["purl"])
    print("komponentteja:", len(v1["components"]))
    print("sama syöte, sama SBOM:",
          v1 == sbom("tilauspalvelu", "1.4.0", [
              ("jinja2", "3.1.2"), ("requests", "2.31.0"),
              ("urllib3", "2.0.7")]))
    for muutos in vertaa(v1, v2):
        print(muutos)


if __name__ == "__main__":
    main()
