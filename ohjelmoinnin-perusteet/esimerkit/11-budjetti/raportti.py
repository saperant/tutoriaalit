"""Tapahtumien koosteet. Funktiot eivät tulosta, vaan palauttavat
tuloksen, joten niitä on helppo testata."""

from tapahtuma import Tapahtuma


def kuukausittain(tapahtumat: list[Tapahtuma]) -> dict[str, list[int]]:
    """Palauttaa kuukaudelle 'vvvv-kk' listan [tulot, menot]."""
    tulos: dict[str, list[int]] = {}
    for t in tapahtumat:
        kuukausi = f"{t.paiva:%Y-%m}"
        summat = tulos.setdefault(kuukausi, [0, 0])
        if t.summa_snt >= 0:
            summat[0] += t.summa_snt
        else:
            summat[1] += t.summa_snt
    return tulos


def suurimmat_menot(tapahtumat: list[Tapahtuma],
                    maara: int) -> list[tuple[str, int]]:
    """Palauttaa luokat, joihin on kulunut eniten rahaa."""
    menot: dict[str, int] = {}
    for t in tapahtumat:
        if t.summa_snt < 0:
            menot[t.luokka] = menot.get(t.luokka, 0) - t.summa_snt
    return sorted(menot.items(), key=lambda pari: pari[1],
                  reverse=True)[:maara]


def euroina(sentit: int) -> str:
    etumerkki = "-" if sentit < 0 else ""
    sentit = abs(sentit)
    return f"{etumerkki}{sentit // 100},{sentit % 100:02d} €"
