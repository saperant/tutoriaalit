"""Täyttääkö varmuuskopiointi palvelun RPO- ja RTO-tavoitteet?

RPO (recovery point objective) kertoo, kuinka paljon dataa saa
menettää: kopiointiväli ei saa olla sitä pidempi. RTO (recovery time
objective) kertoo, kuinka nopeasti palvelun on palattava: palautuksen
siirto, purku ja tarkistus on mahduttava siihen.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Palvelu:
    nimi: str
    data_gt: float
    rpo_h: float
    rto_h: float


@dataclass(frozen=True)
class Kopiointi:
    nimi: str
    vali_h: float          # kopiointiväli
    palautus_mt_s: float   # palautusnopeus kohteeseen
    kaynnistys_h: float    # laitteiden ja palveluiden käynnistys


# @alku arvio
def arvioi(p: Palvelu, k: Kopiointi) -> str:
    palautus_h = p.data_gt * 1000 / k.palautus_mt_s / 3600 + k.kaynnistys_h
    puutteet = []
    if k.vali_h > p.rpo_h:
        puutteet.append(f"väli {k.vali_h:g} h > RPO {p.rpo_h:g} h")
    if palautus_h > p.rto_h:
        puutteet.append(f"palautus {palautus_h:.0f} h > RTO {p.rto_h:g} h")
    return "ok" if not puutteet else "EI: " + "; ".join(puutteet)
# @loppu arvio


def main() -> None:
    palvelut = [Palvelu("verkkokauppa", 800, rpo_h=0.25, rto_h=4),
                Palvelu("intranet", 200, rpo_h=24, rto_h=24),
                Palvelu("arkisto", 40_000, rpo_h=24, rto_h=72)]
    tavat = [Kopiointi("yökopio pilveen", 24, 120, 1),
             Kopiointi("15 min välein + lokit", 0.25, 400, 0.5)]
    for p in palvelut:
        for k in tavat:
            print(f"{p.nimi:12} | {k.nimi:21} | {arvioi(p, k)}")


if __name__ == "__main__":
    main()
