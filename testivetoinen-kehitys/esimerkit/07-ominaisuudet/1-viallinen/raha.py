"""Rahasummien käsittely sentteinä: kolme tavallista virhettä."""


# @alku viat
def muotoile(sentit: int) -> str:
    eurot, loput = divmod(sentit, 100)
    return f"{eurot},{loput}"            # vika: 1205 -> '12,5'


def jasenna(teksti: str) -> int:
    eurot, _, loput = teksti.partition(",")
    return int(eurot) * 100 + int(loput.ljust(2, "0"))


def jaa_tasan(summa: int, osia: int) -> list[int]:
    return [summa // osia] * osia        # vika: jakojäännös katoaa


def prosentti(sentit: int, prosentit: int) -> int:
    return round(sentit * prosentit / 100)   # vika: round(0.5) == 0
# @loppu viat
