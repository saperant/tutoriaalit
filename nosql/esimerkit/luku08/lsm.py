"""Oma LSM-puu: kirjoitukset, luvut, poistot ja kompaktointi."""

import tempfile
from pathlib import Path

from nosql.lsm import LSM


def ajo(_ymp: object) -> None:
    with tempfile.TemporaryDirectory() as hakemisto:
        puu = LSM(Path(hakemisto), memtable_koko=4)
        # @alku kaytto
        for i in range(20):
            puu.aseta(f"tuote:{i:02d}", f"hinta={i * 10}")
        for i in range(0, 20, 2):
            puu.aseta(f"tuote:{i:02d}", f"hinta={i * 11}")  # päivitys
        puu.poista("tuote:07")
        print("tiedostoja:", len(puu.taulut),
              "memtable:", len(puu.memtable))
        print("tuote:04 =", puu.hae("tuote:04"))
        print("tuote:07 =", puu.hae("tuote:07"))
        # @loppu kaytto

        # @alku vahvistus
        print("luettuja tiedostoja:", puu.tilasto.tiedostoja_luettu,
              "bloom ohitti:", puu.tilasto.bloom_ohitti)
        puu.tyhjenna()
        ennen = puu.tilasto.tavuja_kirjoitettu
        puu.kompaktoi()
        print("kompaktoinnin jalkeen tiedostoja:", len(puu.taulut),
              "avaimia:", len(puu.taulut[0].avaimet))
        kayttaja = puu.tilasto.tavuja_kayttajalta
        print(f"kirjoitusvahvistus ennen kompaktointia: "
              f"{ennen / kayttaja:.1f}, jalkeen: "
              f"{puu.tilasto.tavuja_kirjoitettu / kayttaja:.1f}")
        # @loppu vahvistus


if __name__ == "__main__":
    ajo(None)
