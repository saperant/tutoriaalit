"""Rahasummien jäsennys ja muotoilu. Summat ovat sentteinä (int)."""


def jasenna_summa(teksti: str) -> int:
    """Muuntaa tekstin '12,50' sentiksi (1250). Nostaa ValueErrorin, jos
    teksti ei ole kelvollinen ei-negatiivinen euromäärä."""
    eurot, _, sentit = teksti.strip().replace(".", ",").partition(",")
    if not eurot.isdigit():
        raise ValueError(f"virheellinen summa: '{teksti}'")
    if sentit and not (sentit.isdigit() and len(sentit) <= 2):
        raise ValueError(f"virheelliset sentit: '{teksti}'")
    return int(eurot) * 100 + int(sentit.ljust(2, "0"))


def euroina(sentit: int) -> str:
    """Muotoilee senttimäärän muotoon '12,34 €'."""
    etumerkki = "-" if sentit < 0 else ""
    sentit = abs(sentit)
    return f"{etumerkki}{sentit // 100},{sentit % 100:02d} €"


if __name__ == "__main__":
    # Ajetaan vain, kun tiedosto käynnistetään suoraan, ei importissa.
    print(euroina(jasenna_summa("12,5")))
