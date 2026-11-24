"""Oppiva kytkin: MAC-osoitetaulu, tulvitus ja vanheneminen."""

from dataclasses import dataclass, field

LAAJALAHETYS = "ff:ff:ff:ff:ff:ff"


# @alku kytkin
@dataclass
class Kytkin:
    portteja: int
    vanhenemisaika: float = 300.0
    # MAC-osoite -> (portti, viimeksi nähty)
    taulu: dict[str, tuple[int, float]] = field(default_factory=dict)

    def vastaanota(self, portti: int, lahde: str, kohde: str,
                   aika: float) -> list[int]:
        """Palauttaa portit, joihin kehys lähetetään eteenpäin."""
        # 1. Oppiminen: lähettäjä on tämän portin takana.
        self.taulu[lahde] = (portti, aika)
        # 2. Välitys: tunnettu kohde yhteen porttiin, muuten tulvitus.
        tieto = self.taulu.get(kohde)
        if kohde != LAAJALAHETYS and tieto is not None:
            kohdeportti, nahty = tieto
            if aika - nahty <= self.vanhenemisaika:
                # Samaan porttiin ei lähetetä takaisin.
                return [] if kohdeportti == portti else [kohdeportti]
            del self.taulu[kohde]
        return [p for p in range(1, self.portteja + 1) if p != portti]
# @loppu kytkin


def main() -> None:
    # @alku kaytto
    k = Kytkin(portteja=4)
    a, b, c = "02:00:00:00:00:0a", "02:00:00:00:00:0b", "02:00:00:00:00:0c"
    tapahtumat = [
        (0.0, 1, a, LAAJALAHETYS, "A kysyy ARP:lla B:n osoitetta"),
        (0.1, 2, b, a, "B vastaa A:lle"),
        (0.2, 1, a, b, "A lähettää B:lle"),
        (0.3, 1, a, c, "A lähettää C:lle, jota ei vielä tunneta"),
        (400.0, 1, a, b, "A lähettää B:lle pitkän tauon jälkeen"),
    ]
    for aika, portti, lahde, kohde, selitys in tapahtumat:
        ulos = k.vastaanota(portti, lahde, kohde, aika)
        print(f"{selitys:40} -> portit {ulos}")
    for osoite, (portti, _) in sorted(k.taulu.items()):
        print(f"{osoite}  portti {portti}")
    # @loppu kaytto


if __name__ == "__main__":
    main()
