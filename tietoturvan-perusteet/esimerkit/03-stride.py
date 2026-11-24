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


@dataclass(frozen=True)
class Elementti:
    nimi: str
    tyyppi: str              # toimija, prosessi, varasto tai virta
    ylittaa_rajan: bool = False


# @alku malli
MALLI = [
    Elementti("Asiakas (selain)", "toimija"),
    Elementti("Verkkokauppa-API", "prosessi"),
    Elementti("Tilaustietokanta", "varasto"),
    Elementti("Selain → API (HTTPS)", "virta", ylittaa_rajan=True),
    Elementti("API → tietokanta", "virta"),
    Elementti("API → maksupalvelu", "virta", ylittaa_rajan=True),
]
# @loppu malli


def uhat(elementti: Elementti) -> list[str]:
    return [STRIDE[k] for k in KOSKEE[elementti.tyyppi]]


# Luottamusrajan ylittävät virrat käsitellään ensin: niissä hyökkääjä
# pääsee käsiksi dataan.
for e in sorted(MALLI, key=lambda e: not e.ylittaa_rajan):
    raja = " [luottamusraja]" if e.ylittaa_rajan else ""
    print(f"{e.nimi}{raja}")
    for uhka in uhat(e):
        print(f"  - {uhka}")
print(f"Uhkia yhteensä: {sum(len(uhat(e)) for e in MALLI)}")
