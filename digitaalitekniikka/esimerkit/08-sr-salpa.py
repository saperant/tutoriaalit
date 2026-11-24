"""SR-salpa kahdesta ristiinkytketystä NOR-portista.

Salpa muistaa tilansa takaisinkytkennän ansiosta. Kielletty syöte
S = R = 1 pakottaa molemmat lähdöt nollaan, ja jos S ja R vapautuvat
samaan aikaan, salpa jää heilumaan: kumpikaan portti ei "voita".
Oikeassa piirissä epäsymmetria ratkaisee lopulta tilan satunnaisesti
(metastabiilisuus).
"""

from porttisim import Piiri


# @alku salpa
def sr_salpa() -> Piiri:
    p = Piiri()
    p.portti("NOR", ["R", "Qn"], "Q", viive=2)
    p.portti("NOR", ["S", "Q"], "Qn", viive=2)
    return p
# @loppu salpa


def main() -> None:
    # @alku koe
    p = sr_salpa()
    p.alusta("Qn", 1)                         # alkutila Q = 0
    p.asetu()
    for aika, s, r in [(2, 1, 0), (8, 0, 0),    # aseta, pidä
                       (12, 0, 1), (18, 0, 0),  # nollaa, pidä
                       (22, 1, 1), (28, 0, 0)]: # kielletty, vapauta
        p.aseta("S", s, aika)
        p.aseta("R", r, aika)
    p.aja(40)
    print("       0         1         2         3")
    print("       0123456789012345678901234567890123456789")
    print(p.aaltomuoto(["S", "R", "Q", "Qn"], 40))
    # @loppu koe


if __name__ == "__main__":
    main()
