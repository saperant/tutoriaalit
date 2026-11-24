"""Varmuuskopioiden säilytys: isoisä–isä–poika (GFS).

Päivittäisiä kopioita säilytetään viikko, viikoittaisia kuukausi,
kuukausittaisia vuosi ja vuosittaisia kolme vuotta. Ryhmästä (viikko,
kuukausi, vuosi) säilytetään sen uusin kopio. Funktio päättää, mitkä
kopiot säilytetään; muut poistetaan. Sama logiikka on esimerkiksi
resticin forget-komennossa (--keep-daily 7 --keep-weekly 4
--keep-monthly 12 --keep-yearly 3).
"""

from collections.abc import Callable
from datetime import date, timedelta


# @alku gfs
def sailytettavat(kopiot: list[date], paivat: int = 7, viikot: int = 4,
                  kuukaudet: int = 12, vuodet: int = 3) -> set[date]:
    uusin_ensin = sorted(kopiot, reverse=True)
    sailyta: set[date] = set(uusin_ensin[:paivat])

    def ryhmittain(avain: Callable[[date], tuple[int, ...]],
                   maara: int) -> None:
        nahdyt: set[tuple[int, ...]] = set()
        for d in uusin_ensin:
            if avain(d) not in nahdyt and len(nahdyt) < maara:
                nahdyt.add(avain(d))
                sailyta.add(d)   # ryhmän uusin kopio

    ryhmittain(lambda d: tuple(d.isocalendar()[:2]), viikot)
    ryhmittain(lambda d: (d.year, d.month), kuukaudet)
    ryhmittain(lambda d: (d.year,), vuodet)
    return sailyta
# @loppu gfs


def main() -> None:
    tanaan = date(2026, 11, 24)
    kopiot = [tanaan - timedelta(days=n) for n in range(4 * 365)]
    jaa = sorted(sailytettavat(kopiot))
    print(f"kopioita {len(kopiot)}, säilytetään {len(jaa)}")
    print("vanhimmat:", ", ".join(d.isoformat() for d in jaa[:4]))
    print("uusimmat:", ", ".join(d.isoformat() for d in jaa[-3:]))


if __name__ == "__main__":
    main()
