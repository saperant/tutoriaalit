"""Linjakoodit: NRZ, NRZI, Manchester ja 4B5B.

Linjakoodi muuttaa bitit signaalitasoiksi. Hyvä koodi pitää
tasajännitekomponentin pienenä ja tuottaa tarpeeksi tasonvaihtoja,
jotta vastaanotin pysyy lähettäjän kellossa.
"""

# @alku koodit
def nrz(bitit: str) -> list[int]:
    return [1 if b == "1" else -1 for b in bitit]


def nrzi(bitit: str) -> list[int]:
    """Ykkönen vaihtaa tasoa, nolla pitää sen."""
    taso, tulos = -1, []
    for b in bitit:
        if b == "1":
            taso = -taso
        tulos.append(taso)
    return tulos


def manchester(bitit: str) -> list[int]:
    """IEEE 802.3: 0 = korkea→matala, 1 = matala→korkea."""
    tulos: list[int] = []
    for b in bitit:
        tulos += [-1, 1] if b == "1" else [1, -1]
    return tulos


NELJA_VIISI = {  # 4B5B (100BASE-X): ei koskaan yli kolmea nollaa
    "0000": "11110", "0001": "01001", "0010": "10100", "0011": "10101",
    "0100": "01010", "0101": "01011", "0110": "01110", "0111": "01111",
    "1000": "10010", "1001": "10011", "1010": "10110", "1011": "10111",
    "1100": "11010", "1101": "11011", "1110": "11100", "1111": "11101",
}


def koodaa_4b5b(bitit: str) -> str:
    return "".join(NELJA_VIISI[bitit[i:i + 4]]
                   for i in range(0, len(bitit), 4))
# @loppu koodit


def pisin_tasainen(tasot: list[int]) -> int:
    pisin = nykyinen = 1
    for a, b in zip(tasot, tasot[1:], strict=False):
        nykyinen = nykyinen + 1 if a == b else 1
        pisin = max(pisin, nykyinen)
    return pisin


def kuvaa(nimi: str, tasot: list[int], bitteja: int) -> None:
    vaihdot = sum(a != b for a, b in zip(tasot, tasot[1:], strict=False))
    dc = sum(tasot) / len(tasot)
    print(f"{nimi:<12} {len(tasot) / bitteja:>10.2f} {dc:>+6.2f}"
          f" {vaihdot:>8} {pisin_tasainen(tasot):>7}")


# @alku vertailu
data = "0000" * 8 + "1111" * 4          # pitkiä nolla- ja ykkösjaksoja
print(f"{'koodi':<12} {'tasoa/bitti':>10} {'DC':>6} {'vaihtoja':>8}"
      f" {'pisin':>7}")
kuvaa("NRZ", nrz(data), len(data))
kuvaa("NRZI", nrzi(data), len(data))
kuvaa("Manchester", manchester(data), len(data))
kuvaa("4B5B + NRZI", nrzi(koodaa_4b5b(data)), len(data))
# @loppu vertailu
