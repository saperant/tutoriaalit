"""Kaksi nimeä samalle listalle: yleinen yllätys."""

ostokset = ["maito", "leipä"]
toinen_nimi = ostokset           # EI kopioi, vaan viittaa samaan listaan
toinen_nimi.append("juusto")
print(ostokset)                  # muuttui myös

kopio = ostokset.copy()          # uusi lista samoilla alkioilla
kopio.append("omena")
print(ostokset, kopio)

# Monikko (tuple) on muuttumaton: sopii kiinteälle arvoryhmälle.
sijainti = (60.17, 24.94)        # leveys- ja pituuspiiri
leveys, pituus = sijainti        # purku
print(f"{leveys} N, {pituus} E")
