"""Sisäkkäiset rakenteet: sanakirja, jonka arvot ovat listoja."""

arvosanat: dict[str, list[int]] = {
    "Aino": [5, 4, 5],
    "Ville": [3, 4],
}

print(arvosanat["Aino"][0])              # ensin avain, sitten indeksi
arvosanat["Ville"].append(5)             # muutetaan sisempää listaa
arvosanat.setdefault("Li", []).append(4)     # uusi avain tarvittaessa

for nimi, lista in sorted(arvosanat.items()):
    keskiarvo = sum(lista) / len(lista)
    print(f"{nimi:<6}{lista}  keskiarvo {keskiarvo:.2f}")

# Lista monikoita: taulukon rivit.
tuotteet = [("kahvi", 699), ("tee", 320), ("pulla", 150)]
halvin = min(tuotteet, key=lambda tuote: tuote[1])
print(f"Halvin: {halvin[0]} ({halvin[1]} snt)")
