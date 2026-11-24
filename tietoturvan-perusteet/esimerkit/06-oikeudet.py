"""Tiedosto-oikeudet (DAC) ja niiden tarkastus Unixissa."""

import os
import stat
import tempfile
from pathlib import Path


# @alku tarkastus
def ongelmat(juuri: Path) -> list[str]:
    loydot = []
    for polku in sorted(juuri.rglob("*")):
        tila = polku.stat().st_mode
        nimi = polku.relative_to(juuri)
        if tila & stat.S_IWOTH:
            loydot.append(f"{nimi}: kaikki voivat kirjoittaa")
        if polku.suffix in {".key", ".env"} and tila & (stat.S_IRWXG
                                                        | stat.S_IRWXO):
            loydot.append(f"{nimi}: salaisuus muidenkin luettavissa")
    return loydot
# @loppu tarkastus


with tempfile.TemporaryDirectory() as hak:
    juuri = Path(hak)
    (juuri / "palvelin.key").write_text("-----BEGIN PRIVATE KEY-----\n")
    (juuri / "asetukset.env").write_text("TIETOKANTA_SALASANA=...\n")
    (juuri / "loki.txt").write_text("")
    os.chmod(juuri / "palvelin.key", 0o644)
    os.chmod(juuri / "asetukset.env", 0o600)
    os.chmod(juuri / "loki.txt", 0o666)  # noqa: S103 – tarkoituksella

    for rivi in ongelmat(juuri):
        print(rivi)
    # @alku korjaus
    os.chmod(juuri / "palvelin.key", 0o600)   # vain omistaja
    os.chmod(juuri / "loki.txt", 0o640)       # omistaja ja ryhmä
    # @loppu korjaus
    print("korjauksen jälkeen:", ongelmat(juuri))
