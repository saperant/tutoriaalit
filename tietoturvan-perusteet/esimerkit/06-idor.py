"""Objektitason tarkistus: tunnisteen arvaaminen ei saa riittää (IDOR)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Lasku:
    numero: int
    asiakas: str
    summa: int


LASKUT = {1001: Lasku(1001, "aino", 120), 1002: Lasku(1002, "pekka", 4500)}


class EiLoydy(Exception):
    pass


# @alku haavoittuva
def hae_lasku_haavoittuva(kirjautunut: str, numero: int) -> Lasku:
    """VIRHE: kirjautuminen tarkistetaan, omistajuutta ei."""
    lasku = LASKUT.get(numero)
    if lasku is None:
        raise EiLoydy(numero)
    return lasku
# @loppu haavoittuva


# @alku korjattu
def hae_lasku(kirjautunut: str, numero: int) -> Lasku:
    lasku = LASKUT.get(numero)
    # Sama vastaus, oli lasku olemassa tai ei: muuten hyökkääjä voi
    # luetella olemassa olevat numerot.
    if lasku is None or lasku.asiakas != kirjautunut:
        raise EiLoydy(numero)
    return lasku
# @loppu korjattu


# Aino kokeilee seuraavaa laskunumeroa osoiteriviltä: /laskut/1002
print("haavoittuva:", hae_lasku_haavoittuva("aino", 1002))
for numero in (1001, 1002, 9999):
    try:
        print("korjattu:", hae_lasku("aino", numero))
    except EiLoydy:
        print(f"korjattu: 404 ({numero})")
