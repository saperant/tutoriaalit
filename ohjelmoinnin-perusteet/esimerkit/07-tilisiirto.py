"""Virheellinen pyyntö hylätään poikkeuksella heti, kun se havaitaan."""


def jasenna_summa(teksti: str) -> int:
    """Muuntaa tekstin '12,50' sentiksi (1250). Nostaa ValueErrorin, jos
    teksti ei ole kelvollinen positiivinen euromäärä."""
    eurot, _, sentit = teksti.strip().replace(".", ",").partition(",")
    if not eurot.isdigit():
        raise ValueError(f"virheellinen summa: '{teksti}'")
    if sentit and not (sentit.isdigit() and len(sentit) <= 2):
        raise ValueError(f"virheelliset sentit: '{teksti}'")
    summa = int(eurot) * 100 + int(sentit.ljust(2, "0"))
    if summa == 0:
        raise ValueError("summan on oltava suurempi kuin nolla")
    return summa


def euroina(sentit: int) -> str:
    return f"{sentit // 100},{sentit % 100:02d} €"


saldo = 10_000                       # sentteinä
for pyynto in ["25,50", "abc", "0", "12.345", "200"]:
    try:
        summa = jasenna_summa(pyynto)
    except ValueError as virhe:
        print(f"Hylätty: {virhe}")
        continue
    if summa > saldo:
        print(f"Hylätty: kate ei riitä ({euroina(summa)})")
        continue
    saldo -= summa
    print(f"Siirretty {euroina(summa)}, saldo {euroina(saldo)}")
