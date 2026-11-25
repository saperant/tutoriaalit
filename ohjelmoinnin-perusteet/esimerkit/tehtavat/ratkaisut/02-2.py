"""Malliratkaisu 02-2: Matka-aika."""

MINUUTTEJA_TUNNISSA = 60

matka_km = float(input().replace(",", "."))
nopeus_kmh = int(input())
kesto_min = round(matka_km / nopeus_kmh * MINUUTTEJA_TUNNISSA)
tunnit = kesto_min // MINUUTTEJA_TUNNISSA
minuutit = kesto_min % MINUUTTEJA_TUNNISSA
print(f"Matka-aika: {tunnit} h {minuutit:02d} min")
