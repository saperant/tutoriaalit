"""Tulostaa ostoskuitin. Ongelma on pilkottu pieniin funktioihin."""

ALV_PROSENTTI = 13.5   # esimerkkiarvo: tarkista voimassa oleva verokanta


def rivin_hinta(maara: int, a_hinta_snt: int) -> int:
    """Palauttaa tuoterivin hinnan sentteinä."""
    return maara * a_hinta_snt


def alv_osuus(brutto_snt: int, prosentti: float) -> int:
    """Palauttaa verollisesta hinnasta veron osuuden sentteinä."""
    return round(brutto_snt * prosentti / (100 + prosentti))


def euroina(sentit: int) -> str:
    """Muotoilee senttimäärän muotoon '12,34 €'."""
    return f"{sentit // 100},{sentit % 100:02d} €"


def tulosta_rivi(nimi: str, maara: int, a_hinta_snt: int) -> int:
    """Tulostaa tuoterivin ja palauttaa sen hinnan."""
    hinta = rivin_hinta(maara, a_hinta_snt)
    print(f"{nimi:<12}{maara:>3} x {euroina(a_hinta_snt):>8}"
          f"{euroina(hinta):>10}")
    return hinta


yhteensa = 0
yhteensa += tulosta_rivi("Kaurahiutale", 2, 189)
yhteensa += tulosta_rivi("Maito", 3, 115)
yhteensa += tulosta_rivi("Omena", 6, 45)
print("-" * 35)
print(f"{'Yhteensä':<25}{euroina(yhteensa):>10}")
vero_otsikko = f"josta ALV {ALV_PROSENTTI} %".replace(".", ",")
vero = alv_osuus(yhteensa, ALV_PROSENTTI)
print(f"{vero_otsikko:<25}{euroina(vero):>10}")
