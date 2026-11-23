"""Nimet viittaavat olioihin: sijoitus ei kopioi."""

# @alku viittaus
ostokset = ["maito", "leipä"]
sama = ostokset            # uusi nimi samalle oliolle
sama.append("juusto")
print(ostokset)            # muutos näkyy molempien nimien kautta
print(sama is ostokset, id(sama) == id(ostokset))

kopio = list(ostokset)     # uusi lista, samat alkiot
kopio.append("kahvi")
print(len(ostokset), len(kopio))
# @loppu viittaus

# @alku muuttumaton
teksti = "kissa"
toinen = teksti
toinen += "t"              # str on muuttumaton: += luo uuden olion
print(teksti, toinen, teksti is toinen)
# @loppu muuttumaton

# @alku vertailu
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b, a is b)      # sama arvo, eri oliot
puuttuu = None
print(puuttuu is None)     # None verrataan aina is-operaattorilla
# @loppu vertailu
