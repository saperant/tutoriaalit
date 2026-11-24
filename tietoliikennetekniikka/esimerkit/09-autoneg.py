"""Automaattinen neuvottelu: valitaan paras molempien tukema tila."""

# @alku neuvottelu
# Prioriteettijärjestys (IEEE 802.3, liite 28B): paras ensin.
PRIORITEETTI = ["10GBASE-T", "5GBASE-T", "2.5GBASE-T",
                "1000BASE-T FD", "1000BASE-T HD", "100BASE-T2 FD",
                "100BASE-TX FD", "100BASE-T2 HD", "100BASE-T4",
                "100BASE-TX HD", "10BASE-T FD", "10BASE-T HD"]


def neuvottele(oma: set[str], vasta: set[str]) -> str:
    yhteiset = oma & vasta
    for tila in PRIORITEETTI:
        if tila in yhteiset:
            return tila
    return "ei yhteyttä"
# @loppu neuvottelu


kannettava = {"1000BASE-T FD", "100BASE-TX FD", "100BASE-TX HD",
              "10BASE-T FD", "10BASE-T HD"}
kytkin = {"2.5GBASE-T", "1000BASE-T FD", "100BASE-TX FD"}
vanha_kytkin = {"100BASE-TX HD", "10BASE-T HD"}
print("kannettava + kytkin:      ", neuvottele(kannettava, kytkin))
print("kannettava + vanha kytkin:", neuvottele(kannettava, vanha_kytkin))
# @alku duplex
def rinnakkaistunnistus(nopeus_signaalista: str) -> str:
    """Vastapää ei neuvottele (asetettu kiinteästi). Nopeus päätellään
    linjasignaalista, mutta dupleksia ei voi päätellä, joten standardi
    olettaa puolidupleksin."""
    return f"{nopeus_signaalista} HD"


kiintea = "100BASE-TX FD"
tulos = rinnakkaistunnistus("100BASE-TX")
print(f"kiinteä {kiintea} + neuvotteleva -> {tulos}:"
      f" dupleksiristiriita = {tulos.split()[1] != kiintea.split()[1]}")
# @loppu duplex
