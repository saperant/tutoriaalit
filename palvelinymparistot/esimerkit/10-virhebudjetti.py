"""SLO, virhebudjetti ja palamisnopeuteen perustuva hälytys.

SLI (service level indicator) on mitattu suure, esim. onnistuneiden
pyyntöjen osuus. SLO (objective) on sille asetettu tavoite, esim.
99,9 % 30 päivän aikana. Virhebudjetti on sallittu epäonnistumisten
osuus (0,1 %). Hälytys perustuu siihen, kuinka nopeasti budjetti
palaa: nopea palaminen herättää päivystäjän, hidas tekee tiketin.
"""

SLO = 0.999
BUDJETTI = 1 - SLO


# @alku palaminen
def palamisnopeus(virheet: int, pyynnot: int) -> float:
    """1,0 = budjetti kuluu tasan SLO-jakson aikana."""
    return (virheet / pyynnot) / BUDJETTI if pyynnot else 0.0


def halytys(pitka: float, lyhyt: float, raja: float) -> bool:
    """Monen ikkunan sääntö: sekä pitkä että lyhyt ikkuna ylittävät
    rajan, joten hälytys ei laukea vanhasta piikistä eikä hetken
    värähdyksestä."""
    return pitka > raja and lyhyt > raja
# @loppu palaminen


def main() -> None:
    # @alku tilanteet
    # (nimi, virheet 1 h, pyynnöt 1 h, virheet 5 min, pyynnöt 5 min,
    #  virheet 6 h, pyynnöt 6 h)
    tilanteet = [
        ("normaali päivä", 30, 360_000, 2, 30_000, 180, 2_160_000),
        ("tietokanta kaatui", 9_000, 360_000, 1_500, 30_000,
         9_200, 2_160_000),
        ("hidas vuoto", 2_400, 360_000, 200, 30_000, 14_000, 2_160_000),
        ("ohimennyt piikki", 6_000, 360_000, 3, 30_000, 6_100, 2_160_000),
    ]
    for nimi, v1h, p1h, v5m, p5m, v6h, p6h in tilanteet:
        b1h = palamisnopeus(v1h, p1h)
        b5m = palamisnopeus(v5m, p5m)
        b6h = palamisnopeus(v6h, p6h)
        if halytys(b1h, b5m, 14.4):     # 2 % budjetista tunnissa
            toimi = "PÄIVYSTÄJÄ"
        elif halytys(b6h, b1h, 6):      # 5 % budjetista 6 tunnissa
            toimi = "tiketti"
        else:
            toimi = "ei toimia"
        print(f"{nimi:17} 1 h ×{b1h:5.1f}  5 min ×{b5m:5.1f}  "
              f"6 h ×{b6h:5.1f} → {toimi}")
    # @loppu tilanteet


if __name__ == "__main__":
    main()
