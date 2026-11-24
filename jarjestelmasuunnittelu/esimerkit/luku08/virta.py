"""Vähintään kerran -käsittely Redis Streamsilla.

Kuluttajaryhmä "laskutus" lukee tilaukset virrasta. Kuluttaja k1
kaatuu ennen kuin ehtii kuitata viimeisen viestinsä, joten k2 ottaa
sen haltuunsa (XAUTOCLAIM). Viesti käsitellään siis kahdesti, ja
kuluttajan on oltava idempotentti. Viesti, jota ei voi käsitellä,
siirretään kolmannen yrityksen jälkeen kuolleiden viestien virtaan.
"""

import time

from jarjestelma.resp import Redis, Vastaus, lista, luku, teksti
from jarjestelma.ymparisto import Ymparisto

VIRTA, RYHMA = "tilaukset", "laskutus"
ENINTAAN = 3          # toimitusyrityksiä ennen kuolleiden virtaa


def kentat(viesti: Vastaus) -> tuple[str, dict[str, str]]:
    tunnus, tiedot = lista(viesti)
    arvot = [teksti(a) for a in lista(tiedot)]
    return teksti(tunnus), dict(zip(arvot[::2], arvot[1::2], strict=True))


# @alku kasittely
def kasittele(r: Redis, tiedot: dict[str, str]) -> str:
    """Laskuttaa tilauksen kerran. SET NX on idempotenssiavain: jos
    tilaus on jo laskutettu, toista laskua ei tehdä."""
    summa = int(tiedot["summa"])          # ValueError: ei käsiteltävissä
    if r.komento("SET", f"laskutettu:{tiedot['tilaus']}", summa,
                 "NX") is None:
        return "jo laskutettu, kuitataan"
    return f"laskutettu {summa} e"


def kuluta(r: Redis, kuluttaja: str, viestit: list[Vastaus],
           kaatuu_ennen: str | None = None) -> None:
    for viesti in viestit:
        tunnus, tiedot = kentat(viesti)
        try:
            tulos = kasittele(r, tiedot)
        except ValueError:
            print(f"  {kuluttaja} {tiedot['tilaus']}: virhe, ei kuitata")
            continue
        if tiedot["tilaus"] == kaatuu_ennen:
            print(f"  {kuluttaja} {tiedot['tilaus']}: {tulos}"
                  " -- KAATUU ennen kuittausta")
            return
        r.komento("XACK", VIRTA, RYHMA, tunnus)
        print(f"  {kuluttaja} {tiedot['tilaus']}: {tulos}")
# @loppu kasittely


# @alku haltuunotto
def ota_haltuun(r: Redis, kuluttaja: str) -> None:
    """Ottaa haltuun viestit, joita ei ole kuitattu 100 ms:iin.
    Liian monesti toimitetut siirretään kuolleiden virtaan."""
    odottavat = lista(r.komento("XPENDING", VIRTA, RYHMA, "-", "+", 100))
    yrityksia = {teksti(lista(o)[0]): luku(lista(o)[3])
                 for o in odottavat}
    _, viestit, _ = lista(r.komento("XAUTOCLAIM", VIRTA, RYHMA,
                                    kuluttaja, 100, "0-0"))
    kasiteltavat = []
    for viesti in lista(viestit):
        tunnus, tiedot = kentat(viesti)
        if yrityksia[tunnus] >= ENINTAAN:
            r.putki([("XADD", f"{VIRTA}:kuolleet", "*", "tilaus",
                      tiedot["tilaus"], "syy", "summa ei ole luku"),
                     ("XACK", VIRTA, RYHMA, tunnus)])
            print(f"  {kuluttaja} {tiedot['tilaus']}: {ENINTAAN} yritystä,"
                  " kuolleiden virtaan")
        else:
            kasiteltavat.append(viesti)
    kuluta(r, kuluttaja, kasiteltavat)
# @loppu haltuunotto


def main() -> None:
    with Ymparisto() as ymp, Redis(ymp.redis()) as r:
        # @alku tuottaja
        r.komento("XGROUP", "CREATE", VIRTA, RYHMA, "$", "MKSTREAM")
        for tilaus, summa in [("t1", "30"), ("t2", "12"), ("t3", "99"),
                              ("t4", "kaksi"), ("t5", "40"), ("t6", "7")]:
            r.komento("XADD", VIRTA, "*", "tilaus", tilaus, "summa", summa)
        # @loppu tuottaja

        def lue(kuluttaja: str, maara: int) -> list[Vastaus]:
            vastaus = lista(r.komento("XREADGROUP", "GROUP", RYHMA,
                                      kuluttaja, "COUNT", maara,
                                      "STREAMS", VIRTA, ">"))
            return lista(lista(vastaus[0])[1]) if vastaus else []

        print("k1 lukee kolme:")
        kuluta(r, "k1", lue("k1", 3), kaatuu_ennen="t3")
        print("k2 lukee loput:")
        kuluta(r, "k2", lue("k2", 10))
        for kierros in range(1, 4):
            time.sleep(0.2)
            print(f"k2 ottaa haltuun kuittaamattomat ({kierros}):")
            ota_haltuun(r, "k2")
        odottaa = lista(r.komento("XPENDING", VIRTA, RYHMA))[0]
        print("kuittaamatta:", luku(odottaa))
        print("kuolleita:", luku(r.komento("XLEN", f"{VIRTA}:kuolleet")))
        laskut = sorted(teksti(a) for a in
                        lista(r.komento("KEYS", "laskutettu:*")))
        print("laskutetut:", " ".join(a.split(":")[1] for a in laskut))


if __name__ == "__main__":
    main()
