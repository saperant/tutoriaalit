"""Päivitysmanifesti SUIT-mallin (RFC 9019, RFC 9124) periaatteella.

Manifesti kertoo, mille laitteelle päivitys on, mikä sen järjestysnumero
on ja mikä hyötykuorman tiiviste on. Laite tarkistaa manifestin
allekirjoituksen ja ehdot ennen kuin lataa mitään, ja hyötykuorman
tiivisteen ladattuaan. Oikea SUIT käyttää CBOR- ja COSE-muotoja; tässä
JSON ja Ed25519 pitävät esimerkin lyhyenä.
"""

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def kanoninen(data: dict[str, Any]) -> bytes:
    """Allekirjoitettava muoto: sama data tuottaa aina samat tavut."""
    return json.dumps(data, sort_keys=True,
                      separators=(",", ":")).encode()


# @alku tee
def tee_manifesti(avain: Ed25519PrivateKey, jarjestys: int,
                  luokka: str, kuorma: bytes, osoite: str) -> dict[str, Any]:
    sisalto = {
        "valmistaja": "Esimerkki Oy",
        "luokka": luokka,              # laitemalli, jolle kuva sopii
        "jarjestys": jarjestys,        # kasvaa joka julkaisussa
        "koko": len(kuorma),
        "tiiviste": hashlib.sha256(kuorma).hexdigest(),
        "osoite": osoite,
    }
    return {"sisalto": sisalto,
            "allekirjoitus": avain.sign(kanoninen(sisalto)).hex()}
# @loppu tee


@dataclass
class Laite:
    julkinen: Ed25519PublicKey
    luokka: str
    jarjestys: int
    tila: int

    # @alku tarkista
    def kasittele(self, manifesti: dict[str, Any], kuorma: bytes) -> str:
        sisalto = manifesti["sisalto"]
        try:
            self.julkinen.verify(bytes.fromhex(manifesti["allekirjoitus"]),
                                 kanoninen(sisalto))
        except InvalidSignature:
            return "hylätty: allekirjoitus"
        if sisalto["luokka"] != self.luokka:
            return "hylätty: eri laitemalli"
        if sisalto["jarjestys"] <= self.jarjestys:
            return "hylätty: ei uudempi kuin asennettu"
        if sisalto["koko"] > self.tila:
            return "hylätty: ei mahdu"
        # Vasta nyt ladataan hyötykuorma osoitteesta.
        if hashlib.sha256(kuorma).hexdigest() != sisalto["tiiviste"]:
            return "hylätty: hyötykuorman tiiviste"
        self.jarjestys = sisalto["jarjestys"]
        return f"asennetaan, järjestys nyt {self.jarjestys}"
    # @loppu tarkista


def main() -> None:
    avain = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    kuorma = b"laiteohjelmisto 2.0" * 100
    osoite = "https://paivitys.example/anturi-v2.bin"
    oikea = tee_manifesti(avain, 7, "anturi-r2", kuorma, osoite)

    def koe(nimi: str, manifesti: dict[str, Any], data: bytes) -> None:
        laite = Laite(avain.public_key(), "anturi-r2", 6, 64 * 1024)
        print(f"{nimi:30} {laite.kasittele(manifesti, data)}")

    koe("Oikea päivitys", oikea, kuorma)
    koe("Toisen laitemallin päivitys",
        tee_manifesti(avain, 7, "ohjain-r1", kuorma, osoite), kuorma)
    koe("Vanha päivitys toistettuna",
        tee_manifesti(avain, 5, "anturi-r2", kuorma, osoite), kuorma)
    muutettu = json.loads(json.dumps(oikea))
    muutettu["sisalto"]["osoite"] = "https://hyokkaaja.example/x.bin"
    koe("Osoitetta muutettu", muutettu, kuorma)
    koe("Hyötykuorma vioittunut", oikea, kuorma[:-1] + b"!")


if __name__ == "__main__":
    main()
