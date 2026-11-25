"""Malliratkaisu 03-1: Lämpötilan luokitus."""

HELLERAJA = 25

lampotila = int(input())
if lampotila < 0:
    print("pakkasta")
elif lampotila == 0:
    print("nollassa")
elif lampotila < HELLERAJA:
    print("lämmintä")
else:
    print("hellettä")
