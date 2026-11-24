"""Hinta-asiakas erilaisissa vikatilanteissa: hintapalvelu vikaproxyn
takana samassa Docker-verkossa."""

from __future__ import annotations

import urllib.request
from collections.abc import Callable

from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from testiapu import kontit
from varasto.hinnat import HintaAsiakas, HintaVirhe


def post(kontti: DockerContainer, portti: int, polku: str) -> None:
    pyynto = urllib.request.Request(
        kontit.osoite(kontti, portti) + polku, method="POST")
    with urllib.request.urlopen(pyynto, timeout=5):
        pass


# @alku matriisi
def main() -> None:
    kontit.apukuva().build()
    with (Network() as verkko,
          kontit.hintapalvelu().with_network(verkko)
          .with_network_aliases("hinnat") as palvelu,
          kontit.vikaproxy(verkko, "hinnat:8080") as proxy):
        asiakas = HintaAsiakas(kontit.osoite(proxy, 8666),
                               aikaraja=0.3, yritykset=3, tauko=0.05)
        tapaukset: list[tuple[str, Callable[[], None]]] = [
            ("normaali", lambda: None),
            ("2 x 503", lambda: post(palvelu, 8080,
                                     "/hallinta/virheet?n=2")),
            ("3 x 503", lambda: post(palvelu, 8080,
                                     "/hallinta/virheet?n=3")),
            ("viive 1000 ms", lambda: post(proxy, 8474,
                                           "/viive?ms=1000")),
            ("katko", lambda: post(proxy, 8474, "/katkaise")),
        ]
        for nimi, vika in tapaukset:
            vika()
            try:
                tulos = f"{asiakas.hae('ABC-1').hinta_snt} snt"
            except HintaVirhe as e:
                tulos = f"HintaVirhe: {e}"
            post(proxy, 8474, "/palauta")
            print(f"{nimi:<15}{tulos}")
# @loppu matriisi


if __name__ == "__main__":
    main()
