"""Kaksi nimeä samalle listalle: yleinen yllätys."""

ostokset = ["maito", "leipä"]
toinen_nimi = ostokset           # EI kopioi, vaan viittaa samaan listaan
toinen_nimi.append("juusto")
print(ostokset)                  # muuttui myös

kopio = ostokset.copy()          # uusi lista samoilla alkioilla
kopio.append("omena")
print(ostokset, kopio)
