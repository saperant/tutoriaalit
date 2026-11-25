"""Rahasummien käsittely sentteinä: korjattu versio."""

# @alku raha
def muotoile(sentit: int) -> str:
    """1205 -> '12,05'."""
    eurot, loput = divmod(sentit, 100)
    return f"{eurot},{loput:02d}"


def jasenna(teksti: str) -> int:
    """'12,05' -> 1205."""
    eurot, _, loput = teksti.partition(",")
    return int(eurot) * 100 + int(loput.ljust(2, "0"))


def jaa_tasan(summa: int, osia: int) -> list[int]:
    """Jakaa summan osiin, jotka eroavat toisistaan enintään sentin."""
    perus, yli = divmod(summa, osia)
    return [perus + 1] * yli + [perus] * (osia - yli)


def prosentti(sentit: int, prosentit: int) -> int:
    """Prosenttiosuus pyöristettynä lähimpään senttiin, puolikas ylös."""
    return (sentit * prosentit + 50) // 100
# @loppu raha

