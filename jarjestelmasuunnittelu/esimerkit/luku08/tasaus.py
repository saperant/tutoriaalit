"""Jono kuorman tasaajana: kampanjan purske ja käsittelyn kapasiteetti.

Tilauksia tulee tavallisesti 50 sekunnissa, ja kampanjan aikana
15 minuutin ajan 200 sekunnissa. Käsittelijät ehtivät 80 tilausta
sekunnissa. Ilman jonoa ylimäärä hylätään; jonon kanssa se odottaa ja
käsitellään, kun purske on ohi. Malli on virtausmalli: saapumiset ja
käsittely ovat tasaisia minuutin sisällä.
"""

PERUS = 50          # tilausta/s
PURSKE = 200        # tilausta/s kampanjan aikana
KAPASITEETTI = 80   # tilausta/s
KAMPANJA = range(10, 25)   # minuutit


def main() -> None:
    # @alku virtaus
    jono = 0
    hylatty = 0
    pisin = (0, 0)
    tyhja = None
    print(f"{'min':>4}{'saapuu/s':>10}{'jonossa':>10}{'odotus':>9}")
    for minuutti in range(100):
        saapuu = (PURSKE if minuutti in KAMPANJA else PERUS) * 60
        hylatty += max(0, saapuu - KAPASITEETTI * 60)   # ilman jonoa
        jono = max(0, jono + saapuu - KAPASITEETTI * 60)
        pisin = max(pisin, (jono, minuutti))
        if jono == 0 and minuutti >= KAMPANJA.stop and tyhja is None:
            tyhja = minuutti + 1
        if minuutti % 10 == 9 or minuutti + 1 == KAMPANJA.stop:
            odotus = jono / KAPASITEETTI / 60           # Littlen laki
            print(f"{minuutti + 1:>4}{saapuu // 60:>10}{jono:>10}"
                  f"{odotus:>7.0f} m")
    # @loppu virtaus
    print(f"ilman jonoa hylättäisiin {hylatty} tilausta")
    print(f"jono pisimmillään {pisin[0]} tilausta minuutilla {pisin[1] + 1}")
    ylimaara = (PURSKE - KAPASITEETTI) * 60 * len(KAMPANJA)
    purku = ylimaara / ((KAPASITEETTI - PERUS) * 60)
    print(f"purkuaika: {ylimaara} / ({KAPASITEETTI - PERUS}/s * 60)"
          f" = {purku:.0f} min, jono tyhjä minuutilla {tyhja}")


if __name__ == "__main__":
    main()
