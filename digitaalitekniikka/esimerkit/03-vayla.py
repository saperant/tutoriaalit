"""Kolmitilalähtö ja avoin nielu: monta ajuria samalla johtimella.

Johtimen arvo ratkaistaan kaikkien ajurien lähdöistä. Kolmitilalähtö
voi irrottautua johtimesta (Z), jolloin toinen ajuri määrää arvon.
Avoin nielu osaa vetää vain alas; ykkönen tulee ylösvetovastuksesta.
"""

# @alku ratkaisu
def ratkaise(ajurit: list[str]) -> str:
    """Johtimen arvo, kun ajurien lähdöt ovat 0, 1 tai Z (irti)."""
    aktiiviset = {a for a in ajurit if a != "Z"}
    if not aktiiviset:
        return "Z"                   # kukaan ei aja: johdin kelluu
    if len(aktiiviset) == 2:
        return "X"                   # 0 ja 1 yhtä aikaa: väyläriita
    return aktiiviset.pop()


def kolmitila(data: int, sallinta: int) -> str:
    return str(data) if sallinta else "Z"
# @loppu ratkaisu


# @alku avoin
def avoin_nielu(data: int) -> str:
    """Avoin nielu vetää alas, kun data on 0, ja on muuten irti."""
    return "0" if data == 0 else "Z"


def ylosveto(arvo: str) -> str:
    """Ylösvetovastus tekee kelluvasta johtimesta ykkösen."""
    return "1" if arvo == "Z" else arvo
# @loppu avoin


def main() -> None:
    # @alku koe
    print("Kolmitilaväylä, ajurit A ja B (data, sallinta):")
    for a, b in [((1, 1), (0, 0)), ((1, 0), (0, 1)),
                 ((1, 0), (0, 0)), ((1, 1), (0, 1))]:
        arvo = ratkaise([kolmitila(*a), kolmitila(*b)])
        print(f"  A={kolmitila(*a)} B={kolmitila(*b)}  ->  väylä {arvo}")

    print("Avoin nielu ja ylösveto (I2C:n SDA):")
    for da, db in [(1, 1), (0, 1), (1, 0), (0, 0)]:
        arvo = ylosveto(ratkaise([avoin_nielu(da), avoin_nielu(db)]))
        print(f"  A={da} B={db}  ->  johdin {arvo}")
    # @loppu koe


if __name__ == "__main__":
    main()
