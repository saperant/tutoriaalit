"""I2C-siirrot bittitasolla: rekisterin luku, NACK ja kellonvenytys."""

from mallit.i2c import Isanta, Rekisterilaite, dekoodaa, simuloi

# @alku luku
# Anturi osoitteessa 0x48; rekisteri 1 = asetus, 2..3 = raja.
anturi = Rekisterilaite(0x48, bytearray([0x00, 0x60, 0x4B, 0x00]))
isanta = Isanta([
    (0x48, bytes([0x01]), 1),     # osoitin := 1, toistettu START, luku
    (0x48, bytes([0x02]), 2),     # kahden tavun rekisteri
    (0x49, b"", 1),               # väärä osoite
    (0x48, bytes([0x01, 0x40]), 0),  # kirjoitus rekisteriin 1
])
aalto = simuloi([isanta, anturi], 560)
for siirto in dekoodaa(aalto).split(" P"):
    if siirto.strip():
        print(siirto.strip() + " P")
print("\n".join(isanta.loki))
print(f"asetusrekisteri nyt {anturi.rekisterit[1]:#04x}")
print()
print("ensimmainen siirto alusta, osoitetavu 0x90 (48W) ja ACK:")
print(aalto.osa(0, 44).piirra(askel=1))
# @loppu luku

# @alku venytys
print()
hidas = Rekisterilaite(0x48, bytearray([0x00, 0x60]), venytys=10)
isanta = Isanta([(0x48, bytes([0x01]), 1)])
aalto = simuloi([isanta, hidas], 200)
print("laite venyttaa kelloa kuittauksen jalkeen:")
print(dekoodaa(aalto))
print(aalto.osa(26, 90).piirra(askel=1))
# @loppu venytys
