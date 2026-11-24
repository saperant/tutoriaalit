"""Verkon kuvaus koodina: lukee kuvauksen (TOML), tarkistaa sen ja
tulostaa laboratorion käyttöönottokomennot (labra.sh:n funktiot).

Käyttö: python3 main.py [kuvaus.toml]"""

import ipaddress
import sys
import tomllib
from pathlib import Path
from typing import Any

Kuvaus = dict[str, Any]


# @alku tarkistus
def tarkista(kuvaus: Kuvaus) -> list[str]:
    """Palauttaa kaikki virheet kerralla, jotta ne voi korjata yhdellä
    kierroksella."""
    virheet: list[str] = []
    verkot: dict[str, ipaddress.IPv4Network] = {}
    for s in kuvaus["segmentti"]:
        verkko = ipaddress.IPv4Network(s["verkko"])
        for nimi, muu in verkot.items():
            if verkko.overlaps(muu):
                virheet.append(f"{s['nimi']}: {verkko} menee päällekkäin "
                               f"segmentin {nimi} kanssa")
        if ipaddress.IPv4Address(s["yhdyskaytava"]) not in verkko:
            virheet.append(f"{s['nimi']}: yhdyskäytävä ei ole verkossa")
        verkot[s["nimi"]] = verkko
    kaytetyt: set[ipaddress.IPv4Address] = set()
    for laite in kuvaus["laite"]:
        osoite = ipaddress.IPv4Address(laite["osoite"])
        verkko_ = verkot.get(laite["segmentti"])
        if verkko_ is None:
            virheet.append(f"{laite['nimi']}: tuntematon segmentti "
                           f"{laite['segmentti']}")
        elif osoite not in verkko_ or osoite in (
                verkko_.network_address, verkko_.broadcast_address):
            virheet.append(f"{laite['nimi']}: {osoite} ei kelpaa "
                           f"verkossa {verkko_}")
        if osoite in kaytetyt:
            virheet.append(f"{laite['nimi']}: {osoite} on jo käytössä")
        kaytetyt.add(osoite)
    return virheet
# @loppu tarkistus


# @alku komennot
def komennot(kuvaus: Kuvaus) -> list[str]:
    r = kuvaus["reititin"]
    rivit = [f"solmu {r}", f"ns {r} sysctl -qw net.ipv4.ip_forward=1"]
    segmentit = {s["nimi"]: s for s in kuvaus["segmentti"]}
    for s in kuvaus["segmentti"]:
        kytkin = f"k-{s['nimi']}"
        pituus = ipaddress.IPv4Network(s["verkko"]).prefixlen
        rivit += [
            f"solmu {kytkin}",
            f"ns {kytkin} ip link add br0 type bridge",
            f"ns {kytkin} ip link set dev br0 up",
            f"linkki {r} {s['nimi']} {kytkin} {r}",
            f"ns {kytkin} ip link set dev {r} master br0",
            (f"ns {r} ip addr add {s['yhdyskaytava']}/{pituus}"
             f" dev {s['nimi']}"),
        ]
    for laite in kuvaus["laite"]:
        s = segmentit[laite["segmentti"]]
        kytkin = f"k-{s['nimi']}"
        pituus = ipaddress.IPv4Network(s["verkko"]).prefixlen
        rivit += [
            f"solmu {laite['nimi']}",
            f"linkki {laite['nimi']} eth0 {kytkin} {laite['nimi']}",
            f"ns {kytkin} ip link set dev {laite['nimi']} master br0",
            (f"ns {laite['nimi']} ip addr add {laite['osoite']}/{pituus}"
             " dev eth0"),
            (f"ns {laite['nimi']} ip route add default"
             f" via {s['yhdyskaytava']}"),
        ]
    return rivit
# @loppu komennot


def main() -> int:
    polku = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        Path(__file__).with_name("verkko.toml"))
    kuvaus = tomllib.loads(polku.read_text("utf-8"))
    virheet = tarkista(kuvaus)
    if virheet:
        for v in virheet:
            print(f"virhe: {v}", file=sys.stderr)
        return 1
    print("\n".join(komennot(kuvaus)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
