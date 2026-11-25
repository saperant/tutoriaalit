"""ISO-TP (ISO 15765-2): viesti, joka ei mahdu yhteen CAN-kehykseen."""

from mallit.can import Kehys, lahetettavat


# @alku pilko
def pilko(viesti: bytes) -> list[bytes]:
    """Jakaa viestin CAN-kehysten datakentiksi. Ensimmäinen tavu kertoo
    kehyksen lajin: 0x0N yksittäinen (N tavua), 0x1L LL ensimmäinen
    (pituus 12 bittiä), 0x2S jatkokehys (järjestysnumero S)."""
    if len(viesti) <= 7:
        return [bytes([len(viesti)]) + viesti]
    kehykset = [bytes([0x10 | len(viesti) >> 8, len(viesti) & 0xFF])
                + viesti[:6]]
    for numero, alku in enumerate(range(6, len(viesti), 7), start=1):
        kehykset.append(bytes([0x20 | numero & 0x0F])
                        + viesti[alku:alku + 7])
    return kehykset


def kokoa(kehykset: list[bytes]) -> bytes:
    """Kokoaa viestin; ValueError, jos jatkokehys puuttuu."""
    laji = kehykset[0][0] >> 4
    if laji == 0:
        return kehykset[0][1:1 + kehykset[0][0]]
    pituus = (kehykset[0][0] & 0x0F) << 8 | kehykset[0][1]
    viesti = kehykset[0][2:]
    for numero, kehys in enumerate(kehykset[1:], start=1):
        if kehys[0] != 0x20 | numero & 0x0F:
            raise ValueError(f"odotettiin jatkokehysta {numero & 0x0F}, "
                             f"tuli {kehys[0] & 0x0F}")
        viesti += kehys[1:]
    if len(viesti) < pituus:
        raise ValueError("viesti jai kesken")
    return viesti[:pituus]
# @loppu pilko


# @alku ajo
PYYNTO, VASTAUS = 0x7E0, 0x7E8  # lähettäjän ja vastaanottajan tunnisteet
viesti = bytes(range(0x41, 0x41 + 20))  # 20 tavua: ei mahdu 8 tavuun
kehykset = pilko(viesti)
# Vastaanottaja ohjaa vuota ensimmäisen kehyksen jälkeen: 0x30 = jatka,
# lohkon koko 0 = kaikki kerralla, kehysten väli vähintään 10 ms.
vuonohjaus = bytes([0x30, 0x00, 0x0A])

print(f"viesti {len(viesti)} tavua: {viesti.decode()}")
bitteja = 0
for i, data in enumerate(kehykset):
    laji = {0: "yksittainen", 1: "ensimmainen", 2: "jatko"}[data[0] >> 4]
    bitteja += len(lahetettavat(Kehys(PYYNTO, data)))
    print(f"  {PYYNTO:#05x} {laji:12} {data.hex(' ')}")
    if i == 0 and len(kehykset) > 1:
        bitteja += len(lahetettavat(Kehys(VASTAUS, vuonohjaus)))
        print(f"  {VASTAUS:#05x} {'vuonohjaus':12} {vuonohjaus.hex(' ')}")
print(f"koottu: {kokoa(kehykset).decode()}")
print(f"vaylalla {bitteja} bittia, hyotykuormaa {8 * len(viesti)}")

try:
    kokoa([kehykset[0], kehykset[2]])  # toinen kehys katosi
except ValueError as virhe:
    print(f"kehys katosi: {virhe}")
# @loppu ajo
