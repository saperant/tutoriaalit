"""Herkkyysanalyysi: kuinka paljon valittu suunnitelma riippuu
kuorman oletuksista, ja vaihtuuko optimi, jos oletukset ovat väärin."""

from arkki.siru import Kuorma, arvioi
from arkki.tutkimus import Piste, Tila, herkkyys, ruudukko

TILA: Tila = {"r": [1, 2, 4, 8, 16], "c": [2, 4, 8, 16, 32],
        "v": [0.6, 0.7, 0.8, 0.9, 1.0, 1.1]}
TEHORAJA = 80.0
VALITTU: Piste = {"r": 1, "c": 16, "v": 0.8}
OLETUS: Piste = {"sarja": 0.01, "mpki": 3.0, "viive_ns": 80.0,
                 "kaista": 25.0}


def kuorma(k: Piste) -> Kuorma:
    return Kuorma(1 - k["sarja"], k["mpki"], k["viive_ns"], k["kaista"])


def nopeutus(p: Piste, k: Piste) -> float:
    """Suorituskyky absoluuttisena (käskyä / ns): perusytimeen
    suhteutettu nopeutus muuttuisi myös perusytimen mukana."""
    t = arvioi(p["r"], p["c"], p["v"], kuorma(k))
    return t.kaskyja_ns if t.teho <= TEHORAJA else 0.0


def main() -> None:
    # @alku joustot
    joustot = herkkyys(lambda k: nopeutus(VALITTU, k), OLETUS)
    print("valitun suunnitelman joustot (suorituskyvyn muutos / oletuksen"
          " muutos)")
    for nimi, e in joustot.items():
        print(f"  {nimi:<9} {e:+.2f}")
    # @loppu joustot
    # @alku optimi
    print(f"\n{'oletus':<9} {'muutos':>7} {'uusi optimi':>13}"
          f" {'käsky/ns':>9} {'valittu':>8} {'katumus':>8}")
    for nimi in OLETUS:
        for kerroin in (0.5, 2.0):
            k = {**OLETUS, nimi: OLETUS[nimi] * kerroin}
            paras = max(ruudukko(TILA), key=lambda p: nopeutus(p, k))
            s, s0 = nopeutus(paras, k), nopeutus(VALITTU, k)
            uusi = f"{paras['r']:g}/{paras['c']:g}/{paras['v']:g}"
            print(f"{nimi:<9} {kerroin - 1:+7.0%} {uusi:>13} {s:9.2f}"
                  f" {s0:8.2f} {1 - s0 / s:8.1%}")
    # @loppu optimi


if __name__ == "__main__":
    main()
