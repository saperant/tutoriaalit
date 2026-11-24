"""UART-kehys bittitasolla: aaltomuoto, näytteistys ja virheet."""

from mallit.aalto import Aalto
from mallit.uart import Kehysmuoto, kehyksen_bitit, linja, vastaanota


# @alku aalto
def piirra(tavu: int, muoto: Kehysmuoto) -> None:
    """Yksi kehys bitti kerrallaan; merkinnät kertovat bitin roolin."""
    aalto = Aalto(["TX"])
    aalto.lisaa(1)
    nimet = (["S"] + [f"d{i}" for i in range(muoto.databitit)]
             + (["P"] if muoto.pariteetti != "N" else [])
             + ["E"] * muoto.stopbitit)
    for bitti, nimi in zip(kehyksen_bitit(tavu, muoto), nimet,
                           strict=True):
        aalto.lisaa(bitti, merkinta=nimi)
    aalto.lisaa(1)
    print(f"{tavu:#04x} = {tavu:08b}, muoto {muoto}:")
    print(aalto.piirra(askel=4))
    print()


piirra(0x4B, Kehysmuoto())
piirra(0x4B, Kehysmuoto(pariteetti="E"))
# @loppu aalto


# @alku virheet
def nayta(otsikko: str, naytteet: list[int], muoto: Kehysmuoto) -> None:
    saadut = vastaanota(naytteet, muoto)
    kuvaus = ", ".join(f"{v.tavu:#04x}" + (f" ({v.virhe})" if v.virhe
                                          else "") for v in saadut)
    print(f"{otsikko:30} {kuvaus or '-'}")


m8e1 = Kehysmuoto(pariteetti="E")
puhdas = linja(b"OK", m8e1)
nayta("ehja", puhdas, m8e1)

hairio = list(puhdas)
keski = 2 * 16 + 16 * 3 + 8  # ensimmäisen kehyksen d2:n keskikohta
hairio[keski - 3:keski + 3] = [1 - hairio[keski]] * 6
nayta("hairio d2:ssa", hairio, m8e1)

katko = [1] * 32 + [0] * 16 * 14 + [1] * 32  # break: linja alhaalla
nayta("katko (break)", katko, m8e1)

piikki = [1] * 32 + [0] * 4 + [1] * 200  # alle puolen bitin pulssi
nayta("lyhyt piikki lepotilassa", piikki, m8e1)
# @loppu virheet
