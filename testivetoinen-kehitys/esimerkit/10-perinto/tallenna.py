"""Tallentaa vanhan toteutuksen tulosteet vertailuaineistoksi.

Ajetaan kerran ennen refaktorointia: python3 tallenna.py
"""

import lasku_vanha
from tapaukset import KULTAINEN, TAPAUKSET, tulosta


def main() -> None:
    osat = [
        f"== {nimi}\n" + tulosta(lasku_vanha.lasku, tyyppi, koodi, kori)
        for nimi, tyyppi, koodi, kori in TAPAUKSET
    ]
    KULTAINEN.write_text("".join(osat), "utf-8")
    print(f"{len(osat)} tapausta tallennettu")


if __name__ == "__main__":
    main()
