"""Tunnistaa laiteohjelmistotiedoston muodon sen alusta.

Käyttö: python3 tunnista.py TIEDOSTO...

Kuten file(1), mutta vain sulautettujen tavallisimmille muodoille, ja
raa'an binäärin kohdalla tarkistetaan, näyttääkö alku Cortex-M:n
vektoritaululta.
"""
import struct
import sys

ELF_KONEET = {0x28: "ARM", 0x3E: "x86-64", 0xF3: "RISC-V"}


# @alku tunnista
def tunnista(data: bytes) -> str:
    if data[:4] == b"\x7fELF":
        luokka = {1: "32", 2: "64"}.get(data[4], "?")
        kone, = struct.unpack_from("<H", data, 18)
        tulo, = struct.unpack_from("<I", data, 24)
        return (f"ELF{luokka}, {ELF_KONEET.get(kone, hex(kone))}, "
                f"tulokohta {tulo:#x}")
    if data[:1] == b":" and all(r.startswith(b":")
                                for r in data.split()[:8]):
        return "Intel HEX (tekstiä, tietueet :LLAAAATT...CC)"
    if data[:2] == b"S0":
        return "Motorola S-record (tekstiä, tietueet S0..S9)"
    if data[:2] in (b"\x78\x9c", b"\x78\xda", b"\x78\x01"):
        return "zlib-pakattu data"
    if len(data) >= 8:
        pino, reset = struct.unpack_from("<II", data, 0)
        if 0x20000000 <= pino <= 0x20100000 and reset & 1:
            return (f"raaka Cortex-M-kuva: pino {pino:#010x}, "
                    f"Reset {reset:#010x}")
    alku = data[:4]
    if all(0x20 <= t < 0x7F for t in alku):
        return f"tuntematon muoto, taikaluku {alku.decode()!r}"
    return "tuntematon muoto"
# @loppu tunnista


def main() -> None:
    for polku in sys.argv[1:]:
        with open(polku, "rb") as f:
            data = f.read()
        nimi = polku.rsplit("/", 1)[-1]
        print(f"{nimi}: {tunnista(data)}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
