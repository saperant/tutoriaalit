"""Lukitustiedoston tiivisteiden tarkistus ennen asennusta.

Lukitustiedosto kiinnittää jokaisen riippuvuuden version ja paketin
tiivisteen. Asennus hylkää paketin, jonka sisältö ei täsmää, vaikka
nimi ja versio olisivat oikeat: peukaloitu peili, välimuisti tai
uudelleen julkaistu versio jää kiinni.
"""

import hashlib
from pathlib import Path

# @alku tarkistus
def lue_lukitus(teksti: str) -> dict[str, str]:
    """Rivit muotoa 'paketti-1.0.tar.gz sha256:...'."""
    tulos = {}
    for rivi in teksti.splitlines():
        if rivi.strip() and not rivi.startswith("#"):
            nimi, tiiviste = rivi.split()
            tulos[nimi] = tiiviste.removeprefix("sha256:")
    return tulos


def tarkista(hakemisto: Path, lukitus: dict[str, str]) -> list[str]:
    virheet = []
    for tiedosto in sorted(hakemisto.iterdir()):
        odotettu = lukitus.get(tiedosto.name)
        if odotettu is None:
            virheet.append(f"{tiedosto.name}: ei lukitustiedostossa")
            continue
        saatu = hashlib.sha256(tiedosto.read_bytes()).hexdigest()
        if saatu != odotettu:
            virheet.append(f"{tiedosto.name}: tiiviste ei täsmää")
    return virheet
# @loppu tarkistus


def main() -> None:
    paketit = Path("paketit")
    paketit.mkdir()
    sisalto = {"pyynto-2.32.tar.gz": b"pyynto 2.32 lahdekoodi",
               "jasennin-1.4.tar.gz": b"jasennin 1.4 lahdekoodi"}
    for nimi, data in sisalto.items():
        (paketit / nimi).write_bytes(data)
    lukitus = "".join(
        f"{n} sha256:{hashlib.sha256(d).hexdigest()}\n"
        for n, d in sisalto.items())
    print("lukitus luettu:", len(lue_lukitus(lukitus)), "pakettia")
    print("puhdas asennus:", tarkista(paketit, lue_lukitus(lukitus))
          or "kaikki kunnossa")

    # @alku peukalointi
    (paketit / "jasennin-1.4.tar.gz").write_bytes(
        b"jasennin 1.4 lahdekoodi + takaovi")
    (paketit / "apu-0.1.tar.gz").write_bytes(b"ylimaarainen paketti")
    for virhe in tarkista(paketit, lue_lukitus(lukitus)):
        print("hylätty:", virhe)
    # @loppu peukalointi


if __name__ == "__main__":
    main()
