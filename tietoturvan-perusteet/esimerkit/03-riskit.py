"""Riskirekisteri ja 5 × 5 -riskimatriisi."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Riski:
    kuvaus: str
    todennakoisyys: int   # 1 = harvinainen ... 5 = lähes varma
    vaikutus: int         # 1 = vähäinen ... 5 = kriittinen
    hallinta: str = ""

    @property
    def taso(self) -> int:
        return self.todennakoisyys * self.vaikutus

    @property
    def luokka(self) -> str:
        if self.taso >= 15:
            return "korkea"
        return "keskitaso" if self.taso >= 6 else "matala"


# @alku rekisteri
REKISTERI = [
    Riski("Varmuuskopiot julkisessa säilössä", 4, 5,
          "säilö yksityiseksi, salaus, valvonta"),
    Riski("Ylläpitäjän tunnusten kalastelu", 3, 5,
          "phishing-kestävä MFA (FIDO2)"),
    Riski("Palvelunestohyökkäys kampanjan aikana", 3, 3,
          "CDN ja nopeusrajoitus"),
    Riski("Vanhentunut kirjasto, julkinen haavoittuvuus", 4, 4,
          "riippuvuuksien automaattinen päivitys"),
    Riski("Työntekijän kadonnut kannettava", 2, 2,
          "levyn salaus, etätyhjennys"),
]
# @loppu rekisteri

for r in sorted(REKISTERI, key=lambda r: -r.taso):
    print(f"{r.taso:>2} {r.luokka:<9} {r.kuvaus}")
    print(f"{'':>13}→ {r.hallinta}")

# Matriisi: rivit vaikutus 5 → 1, sarakkeet todennäköisyys 1 → 5.
print("\nvaikutus \\ todennäköisyys")
for v in range(5, 0, -1):
    solut = [sum(1 for r in REKISTERI
                 if r.vaikutus == v and r.todennakoisyys == t)
             for t in range(1, 6)]
    print(f"{v}  " + " ".join(str(n) if n else "." for n in solut))
print("   1 2 3 4 5")
