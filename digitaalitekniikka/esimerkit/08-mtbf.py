"""Tahdistimen keskimääräinen vikaväli (MTBF).

Kiikku voi jäädä metastabiiliksi, jos sen syöte muuttuu aikaikkunan
T_w sisällä kellon reunan ympärillä. Tila ratkeaa eksponentiaalisesti
aikavakiolla tau. Jos ratkeamiseen on aikaa t_r, vikaväli on

    MTBF = exp(t_r / tau) / (T_w * f_kello * f_data).

Toinen kiikku antaa ensimmäiselle lähes kokonaisen kellojakson lisää
ratkeamisaikaa.
"""

import math

# @alku parametrit
TAU = 40e-12          # ratkeamisen aikavakio (s)
T_W = 30e-12          # metastabiilisuusikkuna (s)
F_KELLO = 1e9         # kellotaajuus (Hz)
F_DATA = 50e6         # asynkronisen syötteen muutostiheys (Hz)
T_CQ = 50e-12         # kiikun viive kellosta lähtöön (s)
T_SETUP = 40e-12      # seuraavan kiikun asetusaika (s)
LOGIIKKA = 0.7e-9     # logiikan viive ensimmäisen kiikun jälkeen (s)
# @loppu parametrit

SEKUNTIA_VUODESSA = 365.25 * 24 * 3600


# @alku mtbf
def mtbf(t_r: float) -> float:
    return math.exp(t_r / TAU) / (T_W * F_KELLO * F_DATA)


def ihmisittain(sekuntia: float) -> str:
    if sekuntia < 1:
        return f"{sekuntia * 1e6:.3g} µs"
    if sekuntia < 3600:
        return f"{sekuntia:.3g} s"
    if sekuntia < SEKUNTIA_VUODESSA:
        return f"{sekuntia / 3600:.3g} h"
    return f"{sekuntia / SEKUNTIA_VUODESSA:.3g} vuotta"
# @loppu mtbf


def main() -> None:
    jakso = 1 / F_KELLO
    # @alku vertailu
    tapaukset = {
        "1 kiikku, logiikkaa perässä": jakso - T_CQ - LOGIIKKA - T_SETUP,
        "1 kiikku, suoraan kiikkuun": jakso - T_CQ - T_SETUP,
        "2 kiikkua (tahdistin)": 2 * jakso - 2 * T_CQ - T_SETUP,
    }
    for nimi, t_r in tapaukset.items():
        print(f"{nimi:28} t_r = {t_r * 1e9:.2f} ns  "
              f"MTBF = {ihmisittain(mtbf(t_r))}")
    # @loppu vertailu


if __name__ == "__main__":
    main()
