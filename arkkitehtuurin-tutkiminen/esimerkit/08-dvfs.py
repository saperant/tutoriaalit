"""Jännitteen ja taajuuden skaalaus (DVFS): teho, energia ja EDP."""

from arkki.teho import Piiri, edp

YDIN = Piiri(kapasitanssi_nf=33.0)
JAKSOT = 3e9  # tehtävän pituus, jaksoa (1 s nimellistaajuudella)


def main() -> None:
    # @alku taulukko
    print(f"{'V':>5} {'GHz':>5} {'P_dyn W':>8} {'P_vuoto W':>10}"
          f" {'aika s':>7} {'E J':>6} {'EDP Js':>7}")
    for v in (0.6, 0.7, 0.8, 0.9, 1.0, 1.1):
        f = YDIN.taajuus(v)
        p_dyn, p_vuoto = YDIN.dynaaminen(v, f), YDIN.vuoto(v)
        aika = JAKSOT / (f * 1e9)
        energia = (p_dyn + p_vuoto) * aika
        print(f"{v:>5} {f:5.2f} {p_dyn:8.2f} {p_vuoto:10.2f} {aika:7.2f}"
              f" {energia:6.2f} {edp(energia, aika):7.2f}")
    # @loppu taulukko
    # @alku maaraaika
    # Puolet jaksoista, määräaika 1 s. Kilpajuoksu: täysi nopeus ja
    # sitten lepo, jossa virta katkaistaan; DVFS: hitain jännite, jolla
    # määräaika täyttyy. Alusta (muisti, väylät, oheislaitteet) kuluttaa
    # vakiotehoa aina, kun ydin on käynnissä.
    tyo = JAKSOT / 2
    print("\nmääräaika 1 s, työtä 1,5 Gjaksoa, lepo 0 W")
    print(f"{'V':>5} {'aika s':>7} {'E, alusta 0 W':>14}"
          f" {'E, alusta 20 W':>15}")
    for v in (1.1, 1.0, 0.9, 0.8, 0.7, 0.6):
        f = YDIN.taajuus(v)
        aika = tyo / (f * 1e9)
        if aika > 1.0:
            print(f"{v:>5} {aika:7.2f}  määräaika ylittyy")
            continue
        ydin = YDIN.dynaaminen(v, f) + YDIN.vuoto(v)
        print(f"{v:>5} {aika:7.2f} {ydin * aika:14.2f}"
              f" {(ydin + 20) * aika:15.2f}")
    # @loppu maaraaika


if __name__ == "__main__":
    main()
