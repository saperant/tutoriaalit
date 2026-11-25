"""Malliratkaisu 03-2: Summa lopetusmerkkiin asti."""

lukuja = 0
summa = 0
while True:
    luku = int(input())
    if luku == 0:
        break
    lukuja += 1
    summa += luku
print(f"Lukuja: {lukuja}, summa: {summa}")
