"""STRIDE elementeittäin: uhkat johdetaan tietovuokaaviosta."""

from dataclasses import dataclass

# Microsoftin STRIDE-per-element-taulukko: mitkä uhkaluokat koskevat
# kutakin tietovuokaavion elementtityyppiä.
# @alku taulukko
STRIDE = {
    "S": "väärä henkilöllisyys (spoofing)",
    "T": "peukalointi (tampering)",
    "R": "kiistäminen (repudiation)",
    "I": "tietovuoto (information disclosure)",
    "D": "palvelunesto (denial of service)",
    "E": "oikeuksien korotus (elevation of privilege)",
}
KOSKEE = {
    "toimija": "SR",
    "prosessi": "STRIDE",
    "varasto": "TRID",
    "virta": "TID",
}
# @loppu taulukko


# @alku malli
@dataclass(frozen=True)
class Elementti:
    nimi: str
    tyyppi: str              # toimija, prosessi tai varasto
    vyohyke: str             # luottamusvyöhyke, jossa elementti on


@dataclass(frozen=True)
class Virta:
    mista: Elementti
    mihin: Elementti
    sisalto: str
    tyyppi: str = "virta"

    @property
    def nimi(self) -> str:
        return f"{self.mista.nimi} → {self.mihin.nimi}: {self.sisalto}"

    @property
    def ylittaa_rajan(self) -> bool:
        return self.mista.vyohyke != self.mihin.vyohyke


selain = Elementti("Selain", "toimija", "internet")
api = Elementti("Verkkokauppa-API", "prosessi", "oma palvelinympäristö")
kanta = Elementti("Tilaustietokanta", "varasto", "oma palvelinympäristö")
maksu = Elementti("Maksupalvelu", "toimija", "kumppanin järjestelmä")

ELEMENTIT = [selain, api, kanta, maksu]
VIRRAT = [
    Virta(selain, api, "tilaus"),
    Virta(api, kanta, "kyselyt"),
    Virta(api, maksu, "maksupyyntö"),
    Virta(maksu, api, "maksuilmoitus"),
]
# @loppu malli


def uhat(osa: Elementti | Virta) -> list[str]:
    return [STRIDE[k] for k in KOSKEE[osa.tyyppi]]


def tulosta() -> None:
    # Luottamusrajan ylittävät virrat käsitellään ensin: niissä
    # hyökkääjä pääsee käsiksi dataan.
    rajalla = [v for v in VIRRAT if v.ylittaa_rajan]
    sisalla = [v for v in VIRRAT if not v.ylittaa_rajan]
    osat: list[Elementti | Virta] = [*rajalla, *ELEMENTIT, *sisalla]
    for osa in osat:
        raja = " [luottamusraja]" if osa in rajalla else ""
        print(f"{osa.nimi}{raja}")
        for uhka in uhat(osa):
            print(f"  - {uhka}")
    print(f"Uhkia yhteensä: {sum(len(uhat(osa)) for osa in osat)}")


if __name__ == "__main__":
    tulosta()
