"""LT-100:n päivityspaketti (.lt1): rakenne sellaisena kuin se
analyysissa selvisi (luku 3).

  otsake, 32 tavua (little endian):
    0x00 4s  taikaluku "LT1P"
    0x04 u16 muodon versio (1)
    0x06 u16 otsakkeen pituus (32)
    0x08 u32 laitetunnus 0x4C540064 ("LT", malli 100)
    0x0C u32 ohjelmistoversio 0x00MMmmpp
    0x10 u16 osioiden määrä
    0x12 u16 liput (0)
    0x14 u32 allekirjoituksen pituus (0: ei allekirjoitusta)
    0x18 u32 CRC-32 koko paketista tämä kenttä nollattuna
    0x1C u32 paketin pituus
  osioluettelo, 16 tavua osiota kohden:
    u8 tyyppi, u8 liput (bitti 0: zlib), u16 varattu,
    u32 latausosoite (0xFFFFFFFF: ei ladata flashiin),
    u32 tallennettu pituus, u32 CRC-32 puretusta datasta
  osioiden data peräkkäin, kukin täytetty nollilla 4:n monikertaan

Käyttö: python3 lt1.py nayta PAKETTI
        python3 lt1.py pura PAKETTI HAKEMISTO
        python3 lt1.py kokoa HAKEMISTO PAKETTI
"""
import json
import os
import struct
import sys
import zlib
from dataclasses import asdict, dataclass

OTSAKE = struct.Struct("<4sHHIIHHIII")
OSIO = struct.Struct("<BBHIII")
TYYPIT = {1: "sovellus", 2: "asetukset", 3: "resurssit"}


@dataclass
class Osio:
    tyyppi: int
    liput: int
    osoite: int
    crc32: int
    data: bytes          # tallennettu muoto (mahdollisesti pakattu)

    @property
    def purettu(self) -> bytes:
        return zlib.decompress(self.data) if self.liput & 1 else self.data


@dataclass
class Paketti:
    laite: int
    versio: int
    allekirjoitus: bytes
    osiot: list[Osio]


# @alku jasenna
def jasenna(data: bytes) -> Paketti:
    (taika, muoto, otsakkeen_pituus, laite, versio, maara, _, allek,
     crc, pituus) = OTSAKE.unpack_from(data)
    if taika != b"LT1P" or muoto != 1 or pituus != len(data):
        raise ValueError("ei LT1P-paketti tai väärä pituus")
    nollattu = data[:0x18] + bytes(4) + data[0x1C:]
    if zlib.crc32(nollattu) != crc:
        raise ValueError("paketin tarkiste ei täsmää")
    osiot, sijainti = [], otsakkeen_pituus + maara * OSIO.size
    for i in range(maara):
        tyyppi, liput, _, osoite, koko, osio_crc = OSIO.unpack_from(
            data, otsakkeen_pituus + i * OSIO.size)
        osio = Osio(tyyppi, liput, osoite, osio_crc,
                    data[sijainti:sijainti + koko])
        if zlib.crc32(osio.purettu) != osio_crc:
            raise ValueError(f"osion {i} tarkiste ei täsmää")
        osiot.append(osio)
        sijainti += koko + (-koko % 4)
    loppu = data[sijainti:sijainti + allek]
    return Paketti(laite, versio, loppu, osiot)
# @loppu jasenna


# @alku kokoa
def kokoa(paketti: Paketti) -> bytes:
    runko = b"".join(OSIO.pack(o.tyyppi, o.liput, 0, o.osoite,
                               len(o.data), o.crc32)
                     for o in paketti.osiot)
    runko += b"".join(o.data + bytes(-len(o.data) % 4)
                      for o in paketti.osiot)
    runko += paketti.allekirjoitus
    pituus = OTSAKE.size + len(runko)

    def otsake(crc: int) -> bytes:
        return OTSAKE.pack(b"LT1P", 1, OTSAKE.size, paketti.laite,
                           paketti.versio, len(paketti.osiot), 0,
                           len(paketti.allekirjoitus), crc, pituus)

    return otsake(zlib.crc32(otsake(0) + runko)) + runko
# @loppu kokoa


def versio(arvo: int) -> str:
    return f"{arvo >> 16 & 0xFF}.{arvo >> 8 & 0xFF}.{arvo & 0xFF}"


def nayta(paketti: Paketti) -> None:
    print(f"laite {paketti.laite:#010x}, versio {versio(paketti.versio)},"
          f" allekirjoitus {len(paketti.allekirjoitus)} tavua")
    for o in paketti.osiot:
        osoite = "-" if o.osoite == 0xFFFFFFFF else f"{o.osoite:#07x}"
        pakattu = "zlib" if o.liput & 1 else "raaka"
        print(f"  {TYYPIT.get(o.tyyppi, '?'):<10} {osoite:>8} "
              f"{len(o.data):5} tavua {pakattu:<5} -> "
              f"{len(o.purettu):5} tavua, CRC {o.crc32:08x}")


def main() -> None:
    komento, lahde = sys.argv[1], sys.argv[2]
    if komento == "kokoa":
        with open(os.path.join(lahde, "paketti.json")) as f:
            tiedot = json.load(f)
        osiot = []
        for i, o in enumerate(tiedot.pop("osiot")):
            with open(os.path.join(lahde, f"osio{i}.bin"), "rb") as g:
                osiot.append(Osio(data=g.read(), **o))
        paketti = Paketti(osiot=osiot, allekirjoitus=b"", **tiedot)
        with open(sys.argv[3], "wb") as f2:
            f2.write(kokoa(paketti))
        return
    with open(lahde, "rb") as f3:
        paketti = jasenna(f3.read())
    if komento == "nayta":
        nayta(paketti)
    elif komento == "pura":
        kohde = sys.argv[3]
        os.makedirs(kohde, exist_ok=True)
        osiot_json = []
        for i, o in enumerate(paketti.osiot):
            with open(os.path.join(kohde, f"osio{i}.bin"), "wb") as g2:
                g2.write(o.data)
            with open(os.path.join(kohde, f"osio{i}.purettu"), "wb") as g3:
                g3.write(o.purettu)
            tieto = asdict(o)
            del tieto["data"]
            osiot_json.append(tieto)
        with open(os.path.join(kohde, "paketti.json"), "w") as f4:
            json.dump({"laite": paketti.laite, "versio": paketti.versio,
                       "osiot": osiot_json}, f4, indent=1)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
