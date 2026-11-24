"""CAN-datakehys: kentät, bittitäyttö, CRC ja virheiden havaitseminen."""

from mallit.can import (ACK_PAIKKA, DOMINANTTI, Kehys, Taytevirhe,
                        lahetettavat, tayta, vastaanota)

# @alku kentat
kehys = Kehys(0x123, bytes([0x00, 0xFF]))
print(f"kehys: tunniste {kehys.tunniste:#05x}, data "
      f"{kehys.data.hex(' ')}")
alue: list[int] = []
for nimi, bitit in kehys.kentat():
    print(f"  {nimi:5} {''.join(map(str, bitit))}")
    alue += bitit
taytetty, paikat = tayta(alue)
print(f"bitteja ennen taytetta {len(alue)}, taytteen jalkeen "
      f"{len(taytetty)} ({len(paikat)} taytebittia)")
rivi = "".join(map(str, taytetty))
merkit = "".join("^" if i in paikat else " " for i in range(len(rivi)))
for alku in range(0, len(rivi), 64):
    print(f"  {rivi[alku:alku + 64]}")
    print(f"  {merkit[alku:alku + 64].rstrip()}")
# @loppu kentat

# @alku virheet
print()
linja = lahetettavat(kehys)
linja[ACK_PAIKKA] = DOMINANTTI  # vastaanottaja kuittaa
def kuvaa(k: Kehys) -> str:
    return f"tunniste {k.tunniste:#05x}, data {k.data.hex(' ')}"


print(f"ehja: {kuvaa(vastaanota(linja))}")
for kohta in (8, 30, 40):
    vaurio = list(linja)
    vaurio[kohta] ^= 1  # yksi bitti kääntyy väylällä
    try:
        tulos = kuvaa(vastaanota(vaurio))
    except Taytevirhe as virhe:
        tulos = f"taytevirhe ({virhe})"
    except ValueError as virhe:
        tulos = str(virhe)
    print(f"bitti {kohta:2} kaantyi: {tulos}")
# @loppu virheet
