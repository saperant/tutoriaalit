"""Tilitapahtuman tietomalli ja jäsennys tekstiriviltä."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Tapahtuma:
    paiva: date
    luokka: str
    summa_snt: int          # tulot positiivisia, menot negatiivisia


def jasenna_summa(teksti: str) -> int:
    """'-62,40' -> -6240. Nostaa ValueErrorin virheellisestä tekstistä."""
    teksti = teksti.strip()
    etumerkki = -1 if teksti.startswith("-") else 1
    eurot, _, sentit = teksti.removeprefix("-").partition(",")
    if not eurot.isdigit() or not (sentit.isdigit() and len(sentit) == 2):
        raise ValueError(f"virheellinen summa: '{teksti}'")
    return etumerkki * (int(eurot) * 100 + int(sentit))


def jasenna_rivi(rivi: str) -> Tapahtuma:
    """Jäsentää rivin 'vvvv-kk-pp;luokka;summa'."""
    kentat = rivi.strip().split(";")
    if len(kentat) != 3:
        raise ValueError(f"odotettiin 3 kenttää, saatiin {len(kentat)}")
    paiva, luokka, summa = kentat
    if not luokka:
        raise ValueError("luokka puuttuu")
    try:
        pvm = date.fromisoformat(paiva)
    except ValueError:
        raise ValueError(f"virheellinen päivämäärä: '{paiva}'") from None
    return Tapahtuma(pvm, luokka.lower(), jasenna_summa(summa))
