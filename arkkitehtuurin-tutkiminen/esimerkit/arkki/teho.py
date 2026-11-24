"""Teho-, energia- ja pinta-alamallit suunnittelutilan tutkimiseen.

Kertoimet ovat havainnollisia, eivät minkään valmistusprosessin
arvoja. Oikeat arviot tulevat synteesistä, piirikirjastoista ja
työkaluista kuten CACTI (välimuistit) ja McPAT (koko suoritin).
"""

import math
from dataclasses import dataclass


# @alku piiri
@dataclass(frozen=True)
class Piiri:
    """Logiikkalohkon sähköiset parametrit nimellisjännitteellä."""
    kapasitanssi_nf: float  # kytkeytyvä kapasitanssi jaksossa, nF
    aktiivisuus: float = 0.15  # kytkeytyvä osuus jaksossa (alfa)
    vuoto_a: float = 2.0  # vuotovirta nimellisjännitteellä, A
    v_nimellinen: float = 1.0
    f_nimellinen: float = 3.0  # GHz
    v_kynnys: float = 0.35
    alfa_potenssi: float = 1.3  # Sakuraien ja Newtonin alfa-potenssilaki
    vuoto_kerroin: float = 3.0  # vuodon kasvu jännitteen mukana (1/V)

    def taajuus(self, v: float) -> float:
        """Suurin taajuus (GHz) jännitteellä v: f ~ (V - Vt)^a / V."""
        def f(x: float) -> float:
            return float((x - self.v_kynnys) ** self.alfa_potenssi) / x
        return self.f_nimellinen * f(v) / f(self.v_nimellinen)

    def dynaaminen(self, v: float, f: float) -> float:
        """Dynaaminen teho P = alfa C V^2 f (W), f gigahertseinä."""
        return self.aktiivisuus * self.kapasitanssi_nf * v * v * f

    def vuoto(self, v: float) -> float:
        """Vuototeho P = V I(V); vuotovirta kasvaa eksponentiaalisesti
        jännitteen mukana (DIBL)."""
        i = self.vuoto_a * math.exp(self.vuoto_kerroin
                                    * (v - self.v_nimellinen))
        return v * i
# @loppu piiri


# @alku energia
# Energia operaatiota kohden 45 nm:n prosessissa (Horowitz 2014).
# Muistiviittaukset 64 bittiä.
ENERGIA_PJ = {
    "kokonaisluku 32 b yhteenlasku": 0.1,
    "kokonaisluku 32 b kertolasku": 3.1,
    "liukuluku 32 b yhteenlasku": 0.9,
    "liukuluku 32 b kertolasku": 3.7,
    "SRAM 8 KiB": 10.0,
    "SRAM 32 KiB": 20.0,
    "SRAM 1 MiB": 100.0,
    "DRAM": 2000.0,  # 1,3-2,6 nJ
}


def sram_energia(koko_kib: float) -> float:
    """SRAM-luvun energia (pJ, 64 b) neliöjuurisäännöllä: johtimien
    pituus ja siten kapasitanssi kasvaa kuten sivun pituus.
    Sovitettu arvoon 10 pJ / 8 KiB."""
    return 10.0 * math.sqrt(koko_kib / 8)
# @loppu energia


# @alku pinta-ala
def sram_ala(koko_kib: float, solu_um2: float = 0.03,
             tehokkuus: float = 0.5) -> float:
    """SRAM-makron pinta-ala (mm2): bittisolut jaettuna
    pinta-alatehokkuudella (solujen osuus makrosta; loput ovat
    dekoodereita, lukuvahvistimia ja johdotusta)."""
    bitit = koko_kib * 1024 * 8
    return bitit * solu_um2 / tehokkuus / 1e6
# @loppu pinta-ala


# @alku mittarit
def edp(energia: float, viive: float) -> float:
    """Energia-viivetulo. ED^2P (viive toiseen) painottaa nopeutta."""
    return energia * viive
# @loppu mittarit
