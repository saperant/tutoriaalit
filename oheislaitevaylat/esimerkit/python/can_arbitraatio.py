"""CAN-arbitraatio: pienin tunniste voittaa tuhoamatta muita."""

from mallit.can import Kehys, arbitraatio, lahetettavat

# @alku arbitraatio
kehykset = [
    Kehys(0x65A, b"\x01"),  # esim. tilaviesti
    Kehys(0x123, b"\x02"),  # moottorin ohjaus
    Kehys(0x12F, b"\x03"),
]
tulos = arbitraatio(kehykset)
leveys = 16
print("bitti   " + "".join(f"{i % 10}" for i in range(leveys)))
for n, kehys in enumerate(kehykset):
    jono = lahetettavat(kehys)[:leveys]
    loppu = tulos.havisi.get(n, leveys)
    rivi = "".join(str(b) if i <= loppu else "." for i, b in
                   enumerate(jono))
    huom = (f"luopuu bitilla {loppu}" if n in tulos.havisi
            else "voittaa")
    print(f"{kehys.tunniste:#05x}   {rivi}  {huom}")
print("vayla   " + "".join(map(str, tulos.vayla[:leveys])))
voittaja = kehykset[tulos.voittaja]
print(f"vaylalle paasee {voittaja.tunniste:#05x}; muut yrittavat "
      "uudelleen kehyksen jalkeen")
# @loppu arbitraatio
