"""Miksi rahaa ei lasketa liukuluvuilla."""

hinta = 0.10
print(hinta + 0.20)               # ei tasan 0.3
print(hinta + 0.20 == 0.30)
print(round(hinta + 0.20, 2) == 0.30)

# Rahat kokonaisina sentteinä: laskut ovat tarkkoja.
hinta_snt = 10
yhteensa_snt = hinta_snt + 20
print(yhteensa_snt == 30)
print(f"{yhteensa_snt // 100},{yhteensa_snt % 100:02d} €")
