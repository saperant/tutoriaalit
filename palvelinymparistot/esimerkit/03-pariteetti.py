"""RAID 5:n toimintaperiaate: raidoitus ja kiertävä XOR-pariteetti.

Data jaetaan lohkoihin, jotka kirjoitetaan raidoiksi (stripe) levyjen
yli. Jokaisessa raidassa yksi lohko on muiden XOR, ja pariteetin paikka
kiertää levyltä toiselle. Kun yksi levy hajoaa, sen lohkot lasketaan
muiden levyjen lohkoista.
"""

import hashlib
from functools import reduce

LOHKO = 4  # tavua; oikeasti tyypillisesti 64–512 KiB


def xor(lohkot: list[bytes]) -> bytes:
    return bytes(reduce(lambda a, b: a ^ b, tavut)
                 for tavut in zip(*lohkot, strict=True))


# @alku kirjoitus
def kirjoita(data: bytes, levyja: int) -> list[list[bytes]]:
    """Palauttaa levyt lohkolistoina (yksi lohko raitaa kohti)."""
    data += b"\0" * (-len(data) % (LOHKO * (levyja - 1)))
    levyt: list[list[bytes]] = [[] for _ in range(levyja)]
    for raita, alku in enumerate(range(0, len(data),
                                       LOHKO * (levyja - 1))):
        osat = [data[alku + i * LOHKO:alku + (i + 1) * LOHKO]
                for i in range(levyja - 1)]
        pariteetin_levy = (levyja - 1 - raita) % levyja  # kiertää
        osat.insert(pariteetin_levy, xor(osat))
        for levy, lohko in zip(levyt, osat, strict=True):
            levy.append(lohko)
    return levyt


def rakenna(levyt: list[list[bytes] | None]) -> list[list[bytes]]:
    """Laskee puuttuvan levyn lohkot muiden levyjen XOR:na."""
    ehjat = [lev for lev in levyt if lev is not None]
    korvaava = [xor(list(raita)) for raita in zip(*ehjat, strict=True)]
    return [lev if lev is not None else korvaava for lev in levyt]
# @loppu kirjoitus


def lue(levyt: list[list[bytes]]) -> bytes:
    n = len(levyt)
    data = b""
    for raita in range(len(levyt[0])):
        pariteetin_levy = (n - 1 - raita) % n
        data += b"".join(levyt[i][raita] for i in range(n)
                         if i != pariteetin_levy)
    return data.rstrip(b"\0")


def main() -> None:
    # @alku koe
    data = b"Varmuuskopio ei ole RAID, eika RAID varmuuskopio."
    levyt = kirjoita(data, levyja=4)
    for i, levy in enumerate(levyt):
        print(f"levy {i}: " + " ".join(lohko.hex() for lohko in levy[:3]))
    hajonnut: list[list[bytes] | None] = list(levyt)
    hajonnut[2] = None                      # levy 2 hajoaa
    palautettu = rakenna(hajonnut)
    print("levy 2 rakennettu uudelleen:", palautettu[2] == levyt[2])
    tiiviste = hashlib.sha256(lue(palautettu)).hexdigest()[:16]
    print("data ehjä:", lue(palautettu) == data, tiiviste)
    # @loppu koe


if __name__ == "__main__":
    main()
