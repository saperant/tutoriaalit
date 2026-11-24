#!/usr/bin/env python3
"""Testaa tutoriaalin esimerkit sen omassa kehityskontissa.

Käyttö:  python3 yhteiset/testaa_kontti.py <tutoriaali> [<tutoriaali> ...]
         python3 yhteiset/testaa_kontti.py --kaikki
         python3 yhteiset/testaa_kontti.py --lista   (JSON-lista CI:lle)

Lukee tiedoston .devcontainer/<tutoriaali>/devcontainer.json, rakentaa
sen kuvaamasta Dockerfilesta kuvan samoilla rakennusargumenteilla ja
ajaa kontissa `make -C <tutoriaali> testaa`. Näin varmistetaan, että
lukijalle tarjottu kehityskontti todella riittää esimerkkien
kääntämiseen ja ajamiseen.

Jos ympäristömuuttuja SSL_CERT_FILE osoittaa järjestelmän oletuksesta
poikkeavaan varmennetiedostoon (esim. yrityksen tai muun välityspalvelimen
CA), varmenne lisätään testikuvaan, jotta paketinhallinta (apt, pip)
toimii välityspalvelimen takana. Lukijoille jaettava Dockerfile ei muutu.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent
VALITYS = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
           "no_proxy", "NO_PROXY"]
OLETUSVARMENNE = "/etc/ssl/certs/ca-certificates.crt"


def ymparistön_varmenne() -> Path | None:
    polku = os.environ.get("SSL_CERT_FILE")
    if polku and Path(polku).is_file() and polku != OLETUSVARMENNE:
        return Path(polku)
    return None


def luottava_konteksti(dockerfile: Path, konteksti: Path, varmenne: Path,
                       tmp: Path) -> tuple[Path, Path]:
    """Kopio rakennuskontekstista, jonka Dockerfile luottaa varmenteeseen."""
    uusi = tmp / "konteksti"
    shutil.copytree(konteksti, uusi)
    # Yksi varmenne tiedostoa kohden: JDK:n varmennevaraston päivitys
    # tuo tiedostosta vain ensimmäisen varmenteen.
    hak = uusi / "ymparisto-ca"
    hak.mkdir()
    teksti = varmenne.read_text("utf-8")
    loppu = "-----END CERTIFICATE-----"
    for i, osa in enumerate(teksti.split(loppu)[:-1]):
        alku = osa.find("-----BEGIN CERTIFICATE-----")
        (hak / f"ymparisto-{i:03}.crt").write_text(
            osa[alku:] + loppu + "\n", "utf-8")
    rivit = dockerfile.read_text("utf-8").splitlines(keepends=True)
    lisays = (
        "COPY ymparisto-ca/ /usr/local/share/ca-certificates/ymparisto/\n"
        "RUN update-ca-certificates\n"
        f"ENV PIP_CERT={OLETUSVARMENNE} "
        f"REQUESTS_CA_BUNDLE={OLETUSVARMENNE} "
        f"NODE_EXTRA_CA_CERTS={OLETUSVARMENNE}\n")
    for i, rivi in enumerate(rivit):
        if rivi.startswith("FROM "):
            rivit.insert(i + 1, lisays)
            break
    # JDK:n varmennevarasto syntyy vasta paketteja asennettaessa, joten
    # varmenteet päivitetään vielä lopuksi (esim. Mavenia varten).
    rivit.append("\nRUN update-ca-certificates -f > /dev/null\n")
    uusi_dockerfile = uusi / "Dockerfile.testi"
    uusi_dockerfile.write_text("".join(rivit), "utf-8")
    return uusi_dockerfile, uusi


def testaa(tutoriaali: str) -> bool:
    konfiguraatio = JUURI / ".devcontainer" / tutoriaali / "devcontainer.json"
    asetukset = json.loads(konfiguraatio.read_text("utf-8"))
    rakennus = asetukset["build"]
    dockerfile = (konfiguraatio.parent / rakennus["dockerfile"]).resolve()
    konteksti = (konfiguraatio.parent / rakennus.get("context", ".")).resolve()
    kuva = f"tutoriaalit-{tutoriaali}"

    # Välityspalvelin annetaan sekä rakennukselle että testiajolle, jossa
    # paketinhallinta (npm, Maven, Gradle) lataa projektien riippuvuudet.
    # Java-työkalut lukevat välityspalvelimen JAVA_TOOL_OPTIONS-muuttujasta.
    valitys = [a for a in VALITYS if a in os.environ]
    isantaverkko = []
    if any("127.0.0.1" in os.environ[a] or "localhost" in os.environ[a]
           for a in valitys):
        # Paikallinen välityspalvelin näkyy vain isäntäkoneen verkossa.
        isantaverkko = ["--network=host"]
    ajoymparisto = []
    for avain in [*valitys, "JAVA_TOOL_OPTIONS"]:
        if avain in os.environ:
            ajoymparisto += ["-e", f"{avain}={os.environ[avain]}"]

    with tempfile.TemporaryDirectory() as tmp:
        varmenne = ymparistön_varmenne()
        if varmenne:
            dockerfile, konteksti = luottava_konteksti(
                dockerfile, konteksti, varmenne, Path(tmp))
        komento = ["docker", "build", "-q", "-t", kuva,
                   "-f", str(dockerfile)]
        for avain, arvo in rakennus.get("args", {}).items():
            komento += ["--build-arg", f"{avain}={arvo}"]
        for avain in valitys:
            komento += ["--build-arg", f"{avain}={os.environ[avain]}"]
        komento += isantaverkko
        komento.append(str(konteksti))
        print(f"== {tutoriaali}: rakennetaan kuva {kuva}", flush=True)
        if subprocess.run(komento, stdout=subprocess.DEVNULL).returncode:
            print(f"{tutoriaali}: kuvan rakentaminen epäonnistui")
            return False

    print(f"== {tutoriaali}: make testaa kontissa", flush=True)
    tulos = subprocess.run(
        ["docker", "run", "--rm", *isantaverkko, *ajoymparisto,
         *asetukset.get("runArgs", []),
         "-v", f"{JUURI}:/w", "-w", "/w", kuva,
         "make", "-C", tutoriaali, "testaa"])
    return tulos.returncode == 0


def kaikki() -> list[str]:
    return sorted(
        p.parent.name for p in
        (JUURI / ".devcontainer").glob("*/devcontainer.json")
        if p.parent.name != "kirjoittaminen"
        and (JUURI / p.parent.name / "Makefile").exists())


def main() -> int:
    argumentit = sys.argv[1:]
    if argumentit == ["--lista"]:
        print(json.dumps(kaikki()))
        return 0
    if argumentit == ["--kaikki"]:
        argumentit = kaikki()
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
