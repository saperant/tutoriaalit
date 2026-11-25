#!/usr/bin/env python3
"""Tuottaa kirjan sekvenssikaaviot, pääosin testatuista tulosteista.

Käyttö:  python3 kaaviot/tee.py            kirjoittaa kaaviot/*.dot
         python3 kaaviot/tee.py --tarkista  vertaa tallennettuihin

Kaavio piirretään samasta tulosteesta, jonka esimerkin testi vertaa,
joten kaavion viestit ovat ne, jotka verkossa oikeasti kulkivat.
TLS-kättelyn kaavio (10-tls.dot) on poikkeus: sen viestit on lueteltu
tässä tiedostossa, koska salatusta kättelystä ei saa vastaavaa tulostetta.
"""

import sys
from pathlib import Path

JUURI = Path(__file__).resolve().parent.parent


Viesti = tuple[str, str, str] | tuple[str, str, str, str]


def sekvenssi(toimijat: list[str], viestit: list[Viesti]) -> str:
    """Graphviz-sekvenssikaavio: elämänviivat ja vinot viestit.
    Viestin neljäs alkio on valinnainen Graphviz-attribuuttien lisäys."""
    n = len(viestit) + 1
    r = ["digraph {", "  nodesep=1.6; ranksep=0.32;",
         '  node [shape=point, width=0.04, color="#5B6B70"];',
         '  edge [arrowhead=none, style=dashed, color="#B8C4C8"];']
    for k, t in enumerate(toimijat):
        r.append(f'  t{k} [shape=box, width=1, label="{t}"];')
        r.append(f"  t{k} -> " + " -> ".join(f"t{k}_{i}" for i in range(n))
                 + ";")
    for i in range(n):
        r.append("  {rank=same; "
                 + " ".join(f"t{k}_{i};" for k in range(len(toimijat))) + "}")
    r.append('  edge [style=solid, arrowhead=normal, color="#1F2A2E",')
    r.append("        constraint=false];")
    nro = {t: k for k, t in enumerate(toimijat)}
    for i, (a, b, nimi, *lisa) in enumerate(viestit):
        attribuutit = f'label="{nimi}"' + "".join(f", {x}" for x in lisa)
        r.append(f"  t{nro[a]}_{i} -> t{nro[b]}_{i + 1} [{attribuutit}];")
    r.append("}")
    return "\n".join(r) + "\n"


KATOAA = 'color="#B04848", fontcolor="#B04848", style=dashed, arrowhead=tee'


def tcp(tiedosto: str = "07-kattely.odotettu") -> str:
    """Rivit 'asiakas > palvelin [S.] seq 0 ...'. Jos rivi on merkitty
    uudelleenlähetykseksi, sitä edeltävä sama segmentti on kadonnut."""
    viestit: list[Viesti] = []
    tuloste = (JUURI / "esimerkit" / tiedosto).read_text("utf-8")
    for rivi in tuloste.splitlines():
        if " > " not in rivi:
            continue
        osat = rivi.split()
        lahettaja, vastaanottaja, liput = osat[0], osat[2], osat[3]
        nimet = {"S": "SYN", "F": "FIN", "P": "PSH", ".": "ACK"}
        nimi = " ".join(nimet[m] for m in liput.strip("[]"))
        data = int(osat[osat.index("data") + 1])
        if data:
            nimi += f" + {data} B"
        if rivi.endswith("uudelleenlähetys"):
            a, b, edellinen = viestit[-1][:3]
            viestit[-1] = (a, b, edellinen + " (katoaa)", KATOAA)
            nimi += " (uudelleen)"
        viestit.append((lahettaja, vastaanottaja, nimi))
    return sekvenssi(["asiakas", "palvelin"], viestit)


def haviot() -> str:
    return tcp("07-haviot.odotettu")


def tls() -> str:
    """TCP- ja TLS 1.3 -kättely ennen ensimmäistä HTTP-pyyntöä."""
    tcp_vari = 'color="#5B6B70", fontcolor="#5B6B70"'
    return sekvenssi(["asiakas", "palvelin"], [
        ("asiakas", "palvelin", "TCP: SYN", tcp_vari),
        ("palvelin", "asiakas", "TCP: SYN ACK", tcp_vari),
        ("asiakas", "palvelin", "TCP: ACK", tcp_vari),
        ("asiakas", "palvelin", "ClientHello (SNI)"),
        ("palvelin", "asiakas", "ServerHello, varmenne, Finished"),
        ("asiakas", "palvelin", "Finished + HTTP-pyyntö"),
        ("palvelin", "asiakas", "HTTP-vastaus"),
    ])


KAAVIOT = {"07-kattely.dot": tcp, "07-haviot.dot": haviot,
           "10-tls.dot": tls}


def main() -> None:
    tarkista = "--tarkista" in sys.argv
    virheita = 0
    for nimi, tee in KAAVIOT.items():
        polku = JUURI / "kaaviot" / nimi
        uusi = tee()
        if not tarkista:
            polku.write_text(uusi, "utf-8")
        elif not polku.exists() or polku.read_text("utf-8") != uusi:
            print(f"VIRHE: kaaviot/{nimi} ei vastaa tulostetta "
                  "(aja python3 kaaviot/tee.py)")
            virheita += 1
    if tarkista and not virheita:
        print(f"OK: {len(KAAVIOT)} kaaviota vastaa tulosteita")
    sys.exit(1 if virheita else 0)


if __name__ == "__main__":
    main()
