"""Reititystaulu ja pisimmän etuliitteen haku (longest prefix match)."""

import ipaddress
from dataclasses import dataclass


@dataclass(frozen=True)
class Reitti:
    kohde: ipaddress.IPv4Network
    seuraava: str | None      # None: verkko on suoraan liitännässä
    liitanta: str
    metriikka: int = 0


# @alku haku
class Reititystaulu:
    def __init__(self, reitit: list[Reitti]) -> None:
        # Pisimmät etuliitteet ensin; tasatilanteessa pienin metriikka.
        self.reitit = sorted(
            reitit, key=lambda r: (-r.kohde.prefixlen, r.metriikka))

    def hae(self, osoite: str) -> Reitti | None:
        a = ipaddress.IPv4Address(osoite)
        for reitti in self.reitit:
            if a in reitti.kohde:
                return reitti
        return None
# @loppu haku


def main() -> None:
    # @alku taulu
    taulu = Reititystaulu([
        Reitti(ipaddress.IPv4Network("0.0.0.0/0"), "198.51.100.1", "wan"),
        Reitti(ipaddress.IPv4Network("10.20.0.0/16"), "10.0.0.2", "eth1"),
        Reitti(ipaddress.IPv4Network("10.20.2.0/24"), "10.0.0.3", "eth1"),
        Reitti(ipaddress.IPv4Network("10.0.0.0/24"), None, "eth1"),
        Reitti(ipaddress.IPv4Network("198.51.100.0/24"), None, "wan"),
        Reitti(ipaddress.IPv4Network("10.20.0.0/16"), "10.0.0.4", "eth1",
               metriikka=100),
    ])
    for kohde in ["10.20.2.9", "10.20.7.1", "10.0.0.3", "93.184.216.34"]:
        r = taulu.hae(kohde)
        assert r is not None
        reitti = f"via {r.seuraava}" if r.seuraava else "suoraan"
        print(f"{kohde:15} {str(r.kohde):16} {reitti:16} dev {r.liitanta}")
    # @loppu taulu


if __name__ == "__main__":
    main()
