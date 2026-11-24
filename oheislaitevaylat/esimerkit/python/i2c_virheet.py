"""I2C:n monen isännän väylä: arbitraatio ja jumiutuneen väylän
vapautus."""

from mallit.i2c import Isanta, Rekisterilaite, dekoodaa, simuloi

# @alku arbitraatio
# Kaksi isäntää aloittaa samalla hetkellä. Väylä on johdotettu JA,
# joten ensimmäinen bitti, jossa toinen lähettää 1 ja toinen 0,
# ratkaisee: ykkösen lähettäjä näkee nollan ja luopuu.
for kohteet in ((0x48, 0x4A), (0x48, 0x48)):
    laitteet = [Rekisterilaite(o, bytearray(4)) for o in sorted(set(kohteet))]
    a = Isanta([(kohteet[0], bytes([0x00, 0x11]), 0)])
    b = Isanta([(kohteet[1], bytes([0x00, 0x22]), 0)])
    aalto = simuloi([a, b, *laitteet], 120)
    print(f"isannat kohteisiin {kohteet[0]:02x} ja {kohteet[1]:02x}:")
    print(f"  vaylalla: {dekoodaa(aalto)}")
    for nimi, isanta in (("A", a), ("B", b)):
        tila = isanta.loki[0] if isanta.loki else "siirto valmis"
        print(f"  isanta {nimi}: {tila}")
# @loppu arbitraatio

# @alku vapautus
print()
eeprom = Rekisterilaite(0x50, bytearray([0x00, 0x5A]))
kesken = Isanta([(0x50, bytes([0x00]), 2)], katkaise=135)
aalto = simuloi([kesken, eeprom], 150)
print(f"isanta nollautuu kesken luvun: {dekoodaa(aalto)}")
loppu = aalto.naytteet[-1]
print(f"vayla: SCL {loppu[0]}, SDA {loppu[1]} (laite lahettaa yha)")
uusi = Isanta([(0x50, bytes([0x01]), 1)], vapauta=True)
aalto = simuloi([uusi, eeprom], 240, aalto.osa(len(aalto.naytteet) - 1,
                                               len(aalto.naytteet)))
print(f"uusi isanta: {dekoodaa(aalto)}")
print("\n".join(uusi.loki))
# @loppu vapautus
