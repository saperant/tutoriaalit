"""Ajoitusvuoto: tavallinen vertailu lopettaa ensimmäiseen eroon."""

import hmac

OIKEA = "f3a91c07d2"


# @alku naiivi
def naiivi_vertailu(a: str, b: str, laskuri: list[int]) -> bool:
    """Kuten ==: palaa heti ensimmäisestä erosta. Laskuri mittaa työtä."""
    if len(a) != len(b):
        return False
    for x, y in zip(a, b, strict=True):
        laskuri[0] += 1
        if x != y:
            return False
    return True
# @loppu naiivi


def main() -> None:
    # @alku hyokkays
    # Hyökkääjä mittaa vastausajan; tässä aika on vertailtujen merkkien
    # määrä. Oikea ensimmäinen merkki näkyy pidempänä vastausaikana.
    tulokset = {}
    for merkki in "0123456789abcdef":
        laskuri = [0]
        naiivi_vertailu(OIKEA, merkki + "0" * 9, laskuri)
        tulokset[merkki] = laskuri[0]
    paras = max(tulokset, key=lambda m: tulokset[m])
    print("pisin vertailu merkillä:", paras)
    # @loppu hyokkays

    # @alku oikein
    print("vakioaikainen tulos:", hmac.compare_digest(OIKEA, "f" + "0" * 9))
    # @loppu oikein


if __name__ == "__main__":
    main()
