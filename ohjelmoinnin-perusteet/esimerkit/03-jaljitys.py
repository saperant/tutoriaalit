"""Laskee luvun numeroiden summan ja näyttää jokaisen kierroksen tilan."""

luku = 472
summa = 0
kierros = 0
while luku > 0:
    kierros = kierros + 1
    summa = summa + luku % 10      # lisätään viimeinen numero
    luku = luku // 10              # ja pudotetaan se pois
    print(f"kierros {kierros}: luku = {luku:>2}, summa = {summa:>2}")

print(f"Numeroiden summa on {summa}.")
