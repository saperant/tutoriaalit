"""Polkujen ohitus (path traversal): käyttäjän antama tiedostonimi."""

import tempfile
from pathlib import Path


# @alku haavoittuva
def lue_haavoittuva(juuri: Path, nimi: str) -> str:
    return (juuri / nimi).read_text()   # VIRHE: "../" ja "/" pääsevät läpi
# @loppu haavoittuva


# @alku korjattu
def lue(juuri: Path, nimi: str) -> str:
    polku = (juuri / nimi).resolve()    # purkaa "..":t ja symboliset linkit
    if not polku.is_relative_to(juuri.resolve()):
        raise PermissionError(f"polku hakemiston ulkopuolella: {nimi}")
    return polku.read_text()
# @loppu korjattu


with tempfile.TemporaryDirectory() as hak:
    juuri = Path(hak) / "julkinen"
    juuri.mkdir()
    (juuri / "ohje.txt").write_text("käyttöohje\n")
    (Path(hak) / "salaisuudet.env").write_text("API_AVAIN=abc123\n")

    hyokkays = "../salaisuudet.env"
    print("haavoittuva:", lue_haavoittuva(juuri, hyokkays), end="")
    print("korjattu, sallittu:", lue(juuri, "ohje.txt"), end="")
    for nimi in [hyokkays, str(Path(hak) / "salaisuudet.env")]:
        try:
            lue(juuri, nimi)
        except PermissionError:
            print("korjattu: estetty", Path(nimi).name)
