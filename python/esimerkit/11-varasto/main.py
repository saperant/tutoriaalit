"""Sovelluksen käynnistys: kokoaa osat yhteen (composition root)."""

import sys

from malli import Tuote, VarastoVirhe
from muisti import Muistivarasto
from palvelu import Varastopalvelu


def main() -> int:
    varasto = Muistivarasto([Tuote("R-10", "ruuvi", 50),
                             Tuote("M-10", "mutteri", 5)])
    palvelu = Varastopalvelu(varasto)
    for koodi, maara in [("R-10", 20), ("M-10", 8), ("X-99", 1)]:
        try:
            tuote = palvelu.ota(koodi, maara)
            print(f"otettu {maara} {tuote.nimi}, jäljellä {tuote.saldo}")
        except VarastoVirhe as virhe:
            print(f"virhe: {virhe}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
