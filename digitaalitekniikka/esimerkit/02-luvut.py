"""Lukujen esitykset bitteinä: binääri, heksa, kahden komplementti,
Gray-koodi ja BCD."""


# @alku bitit
def bitit(arvo: int, leveys: int) -> str:
    """Arvon `leveys` alinta bittiä merkkijonona (MSB vasemmalla)."""
    return format(arvo & ((1 << leveys) - 1), f"0{leveys}b")


def etumerkillinen(koodi: int, leveys: int) -> int:
    """Tulkitsee bittikuvion kahden komplementin lukuna."""
    if koodi & (1 << (leveys - 1)):      # MSB:n paino on -2^(n-1)
        return koodi - (1 << leveys)
    return koodi
# @loppu bitit


# @alku vastaluku
def vastaluku(koodi: int, leveys: int) -> int:
    """Kahden komplementin vastaluku: käännä bitit ja lisää yksi."""
    maski = (1 << leveys) - 1
    return ((koodi ^ maski) + 1) & maski
# @loppu vastaluku


# @alku gray
def gray(n: int) -> int:
    return n ^ (n >> 1)


def bcd(n: int) -> str:
    """Kymmenjärjestelmän numerot neljän bitin ryhminä."""
    return " ".join(bitit(int(d), 4) for d in str(n))
# @loppu gray


def main() -> None:
    # @alku taulukko
    print("koodi  etumerkitön  kahden komplementti")
    for koodi in (0b0000, 0b0011, 0b0111, 0b1000, 0b1101, 0b1111):
        print(f" {bitit(koodi, 4)}  {koodi:11}  "
              f"{etumerkillinen(koodi, 4):19}")
    # @loppu taulukko

    print()
    for arvo in (5, 1, -8):
        k = arvo & 0b1111
        v = vastaluku(k, 4)
        print(f"-({arvo:2}): {bitit(k, 4)} -> käännä {bitit(~k, 4)}"
              f" -> +1 {bitit(v, 4)} = {etumerkillinen(v, 4)}")

    print()
    # @alku laajennus
    for arvo in (5, -3):
        k4 = arvo & 0xF
        laajennettu = k4 | (0xF0 if k4 & 0x8 else 0x00)
        print(f"{arvo:2}: 4 bittiä {bitit(k4, 4)}"
              f" -> 8 bittiä {bitit(laajennettu, 8)}")
    # @loppu laajennus

    print()
    print("n  binääri  Gray  muuttuvat bitit")
    for n in range(8):
        ero = bitit(gray(n) ^ gray((n + 1) % 8), 3)
        print(f"{n}  {bitit(n, 3)}      {bitit(gray(n), 3)}   {ero}")
    print(f"\n1984 BCD:na: {bcd(1984)} ({len(str(1984)) * 4} bittiä)")
    print(f"1984 binäärinä: {bitit(1984, 11)} (11 bittiä)")


if __name__ == "__main__":
    main()
