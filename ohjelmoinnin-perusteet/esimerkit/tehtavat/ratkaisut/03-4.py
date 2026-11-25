"""Malliratkaisu 03-4: Alkuluvut."""

n = int(input())
for ehdokas in range(2, n + 1):
    on_alkuluku = True
    for jakaja in range(2, ehdokas):
        if ehdokas % jakaja == 0:
            on_alkuluku = False
            break
    if on_alkuluku:
        print(ehdokas, end=" ")
print()
