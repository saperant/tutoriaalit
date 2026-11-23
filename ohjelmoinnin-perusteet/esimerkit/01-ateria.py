"""Laskee, paljonko kukin maksaa yhteisestä ravintolalaskusta."""

lasku = 86.40
tippi_prosentti = 10
henkiloita = 3

yhteensa = lasku * (1 + tippi_prosentti / 100)
osuus = yhteensa / henkiloita

print(f"Lasku tipin kanssa: {yhteensa:.2f} €")
print(f"Kukin maksaa: {osuus:.2f} €")
