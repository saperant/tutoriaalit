"""Salaisuuden kierto ilman katkoa: avaintunniste ja limittäiset avaimet.

Palvelu allekirjoittaa tunnisteet HMAC:lla. Avain vaihdetaan kolmessa
vaiheessa, jotta jo myönnetyt tunnisteet eivät lakkaa toimimasta
kesken kaiken ja vanhan avaimen voi silti poistaa hallitusti.
"""

import hashlib
import hmac
from dataclasses import dataclass, field


# @alku avaimet
@dataclass
class Avainrengas:
    avaimet: dict[str, bytes] = field(default_factory=dict)
    allekirjoittaja: str = ""

    def allekirjoita(self, viesti: str) -> str:
        avain = self.avaimet[self.allekirjoittaja]
        mac = hmac.new(avain, viesti.encode(), hashlib.sha256)
        return f"{self.allekirjoittaja}.{viesti}.{mac.hexdigest()[:16]}"

    def tarkista(self, tunniste: str) -> bool:
        kid, viesti, mac = tunniste.split(".")
        avain = self.avaimet.get(kid)
        if avain is None:
            return False            # tuntematon tai poistettu avain
        oikea = hmac.new(avain, viesti.encode(), hashlib.sha256)
        return hmac.compare_digest(mac, oikea.hexdigest()[:16])
# @loppu avaimet


def main() -> None:
    # Esimerkissä avaimet ovat vakioita; oikeasti ne tulevat
    # salaisuusvarastosta eivätkä koskaan ole koodissa.
    rengas = Avainrengas({"k1": b"vanha-avain-2025"}, "k1")
    vanha = rengas.allekirjoita("asiakas=42")

    # @alku kierto
    # 1. Uusi avain jakoon: kaikki instanssit hyväksyvät molemmat.
    rengas.avaimet["k2"] = b"uusi-avain-2026"
    print("vaihe 1, vanha kelpaa:", rengas.tarkista(vanha))
    # 2. Allekirjoitus uudella avaimella, vanha kelpaa yhä.
    rengas.allekirjoittaja = "k2"
    uusi = rengas.allekirjoita("asiakas=42")
    print("vaihe 2, uusi kelpaa:", rengas.tarkista(uusi),
          "vanha kelpaa:", rengas.tarkista(vanha))
    # 3. Kun vanhat tunnisteet ovat vanhentuneet, vanha avain pois.
    del rengas.avaimet["k1"]
    print("vaihe 3, uusi kelpaa:", rengas.tarkista(uusi),
          "vanha kelpaa:", rengas.tarkista(vanha))
    # @loppu kierto
    vaarennetty = uusi[:-1] + ("0" if uusi[-1] != "0" else "1")
    print("muokattu tunniste kelpaa:", rengas.tarkista(vaarennetty))


if __name__ == "__main__":
    main()
