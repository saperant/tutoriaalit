"""Kellon siirtymä NTP:n neljästä aikaleimasta ja ajautuvan kellon virhe."""

from dataclasses import dataclass


# @alku ntp
@dataclass(frozen=True)
class Vaihto:
    """Yksi kysely: t1 ja t4 asiakkaan, t2 ja t3 palvelimen kellosta."""

    t1: float   # asiakas lähettää
    t2: float   # palvelin vastaanottaa
    t3: float   # palvelin vastaa
    t4: float   # asiakas vastaanottaa

    def siirtyma(self) -> float:
        """Paljonko palvelimen kello on asiakkaan kelloa edellä."""
        return ((self.t2 - self.t1) + (self.t3 - self.t4)) / 2

    def kiertoviive(self) -> float:
        """Verkossa kulunut aika; palvelimen käsittelyaika ei kuulu siihen."""
        return (self.t4 - self.t1) - (self.t3 - self.t2)
# @loppu ntp


def kysely(todellinen_s: float, meno_ms: float, paluu_ms: float) -> Vaihto:
    """Simuloi kyselyn: palvelimen kello on todellinen_s edellä."""
    t1 = 100.0
    t2 = t1 + meno_ms / 1000 + todellinen_s
    t3 = t2 + 0.0005                     # palvelin käsittelee 0,5 ms
    t4 = t3 - todellinen_s + paluu_ms / 1000
    return Vaihto(t1, t2, t3, t4)


# @alku koe
def main() -> None:
    print("todellinen siirtymä 250,0 ms")
    print("meno  paluu  arvio     virhe   kiertoviive/2")
    for meno, paluu in ((12.0, 12.0), (20.0, 4.0), (4.0, 20.0), (80.0, 8.0)):
        v = kysely(0.250, meno, paluu)
        virhe = (v.siirtyma() - 0.250) * 1000
        print(f"{meno:4.0f}  {paluu:5.0f}  {v.siirtyma() * 1000:6.1f} ms"
              f"  {virhe:+5.1f} ms  {v.kiertoviive() * 1000 / 2:5.1f} ms")
# @loppu koe

# @alku ajautuma
    print()
    print("ajautuma  virhe/vrk  5 min:n raja täyttyy")
    for ppm in (1, 20, 50, 200):
        vrk = ppm * 1e-6 * 86400
        print(f"{ppm:4d} ppm  {vrk:6.2f} s   {300 / vrk:7.0f} vrk")
# @loppu ajautuma


if __name__ == "__main__":
    main()
