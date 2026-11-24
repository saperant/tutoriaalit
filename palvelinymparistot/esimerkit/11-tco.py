"""Kokonaiskustannukset (TCO): oma konesali vai pilvi viidessä vuodessa.

Laitteen hankintahinta on vain osa kustannuksista. Mukaan lasketaan
sähkö (myös jäähdytys: PUE), konesalitila, tuki ja lisenssit sekä
ylläpitotyö. Pilvessä maksetaan käytöstä, mutta jatkuvasti päällä
olevat koneet maksavat koko ajan. Luvut ovat suuntaa-antavia
esimerkkiarvoja; oikeassa laskelmassa käytetään omia hintoja.
"""

from dataclasses import dataclass

VUODET = 5
TUNTEJA_V = 8760


@dataclass(frozen=True)
class OmaKonesali:
    palvelimia: int
    hinta_per_palvelin: float     # €
    teho_kw: float                # keskimääräinen kulutus / palvelin
    pue: float                    # kokonaisenergia / IT-energia
    sahko_eur_kwh: float
    tila_eur_v: float             # räkkitila ja verkko / vuosi
    tuki_eur_v: float             # huoltosopimus, lisenssit / palvelin
    yllapito_h_v: float           # ylläpitotunnit / vuosi
    tuntihinta: float


# @alku tco
def oma_tco(k: OmaKonesali) -> dict[str, float]:
    sahko_kwh = k.palvelimia * k.teho_kw * k.pue * TUNTEJA_V * VUODET
    return {
        "laitteet": k.palvelimia * k.hinta_per_palvelin,
        "sähkö ja jäähdytys": sahko_kwh * k.sahko_eur_kwh,
        "tila ja verkko": k.tila_eur_v * VUODET,
        "tuki ja lisenssit": k.tuki_eur_v * k.palvelimia * VUODET,
        "ylläpitotyö": k.yllapito_h_v * k.tuntihinta * VUODET,
    }


def pilvi_tco(instansseja: int, eur_h: float, kaytto: float,
              alennus: float, yllapito_h_v: float, tuntihinta: float
              ) -> dict[str, float]:
    tunnit = instansseja * TUNTEJA_V * VUODET * kaytto
    return {
        "laskenta": tunnit * eur_h * (1 - alennus),
        "ylläpitotyö": yllapito_h_v * tuntihinta * VUODET,
    }
# @loppu tco


def teur(eur: float) -> str:
    return f"{eur / 1000:,.0f} t€".replace(",", " ")


def tulosta(nimi: str, erat: dict[str, float]) -> None:
    print(f"{nimi}: {teur(sum(erat.values()))}")
    for era, eur in erat.items():
        print(f"  {era:20} {teur(eur):>8}")


def main() -> None:
    oma = OmaKonesali(palvelimia=10, hinta_per_palvelin=14_000,
                      teho_kw=0.45, pue=1.5, sahko_eur_kwh=0.12,
                      tila_eur_v=12_000, tuki_eur_v=1_500,
                      yllapito_h_v=400, tuntihinta=80)
    tulosta("oma konesali", oma_tco(oma))
    # @alku kaytto
    for kaytto, alennus, nimi in ((1.0, 0.0, "pilvi, aina päällä"),
                                  (1.0, 0.4, "pilvi, 3 v sitoumus"),
                                  (0.35, 0.0, "pilvi, skaalautuva")):
        tulosta(nimi, pilvi_tco(10, 1.10, kaytto, alennus, 150, 80))
    # @loppu kaytto


if __name__ == "__main__":
    main()
