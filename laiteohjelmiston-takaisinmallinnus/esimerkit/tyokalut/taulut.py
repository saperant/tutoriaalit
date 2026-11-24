"""Tietuetaulukoiden etsintä datasta.

Käyttö: python3 taulut.py KUVA KANTA ALKU LOPPU

Jokainen sana luokitellaan: S = osoitin merkkijonoon, F = osoitin
Thumb-funktioon (pariton), 0 = nolla, N = pieni luku (alle 0x10000),
muut = ?. Taulukoksi tulkitaan vähintään kolme peräkkäistä samanlaista
tietuetta (2-4 sanaa), joissa on ainakin yksi S tai F. Nolla käy
merkkijono-osoittimen paikalle (valinnainen kenttä).
"""
import sys

from kuva import Kuva


def luokka(kuva: Kuva, arvo: int) -> str:
    if arvo == 0:
        return "0"
    if arvo & 1 and kuva.sisaltaa(arvo - 1) and kuva.merkkijono(arvo) is None:
        return "F"
    teksti = kuva.merkkijono(arvo)
    if teksti is not None and len(teksti) >= 2:
        return "S"
    return "N" if arvo < 0x10000 else "?"


# @alku sopii
def sopii(malli: str, tietue: str) -> bool:
    """Tietue sopii malliin, jos kentät ovat samat; S-kentässä saa olla
    myös nolla."""
    return all(m == t or (m == "S" and t == "0")
               for m, t in zip(malli, tietue))
# @loppu sopii


def etsi(kuva: Kuva, alku: int, loppu: int
         ) -> list[tuple[int, int, str, int]]:
    """Palauttaa (osoite, sanoja tietueessa, malli, tietueita)."""
    sanat = [kuva.u32(o) for o in range(alku, loppu - 3, 4)]
    luokat = "".join(luokka(kuva, s) for s in sanat)
    loydetyt = []
    i = 0
    while i < len(luokat):
        paras = None
        for leveys in (2, 3, 4):
            malli = luokat[i:i + leveys]
            if len(malli) < leveys or "?" in malli or not (
                    "S" in malli or "F" in malli) or malli[0] == "0":
                continue
            n = 1
            while sopii(malli, luokat[i + n * leveys:i + (n + 1) * leveys]):
                n += 1
            if n >= 3 and (paras is None or n * leveys > paras[0] * paras[1]):
                paras = (n, leveys, malli)
        if paras:
            n, leveys, malli = paras
            loydetyt.append((alku + 4 * i, leveys, malli, n))
            i += n * leveys
        else:
            i += 1
    return loydetyt


def kentta(kuva: Kuva, arvo: int) -> str:
    teksti = kuva.merkkijono(arvo) if arvo else None
    if teksti is not None and len(teksti) >= 2:
        return f'"{teksti[:28]}"'
    if arvo & 1 and arvo > 0xFFFF:
        return f"fn {arvo - 1:#x}"
    return str(arvo)


def main() -> None:
    kuva = Kuva.lue(sys.argv[1], int(sys.argv[2], 0))
    alku, loppu = int(sys.argv[3], 0), int(sys.argv[4], 0)
    for osoite, leveys, malli, n in etsi(kuva, alku, loppu):
        print(f"{osoite:#x}: {n} tietuetta, {leveys} sanaa, malli {malli}")
        for j in range(n):
            arvot = [kuva.u32(osoite + 4 * (j * leveys + k))
                     for k in range(leveys)]
            print("   ", ", ".join(kentta(kuva, a) for a in arvot))


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
