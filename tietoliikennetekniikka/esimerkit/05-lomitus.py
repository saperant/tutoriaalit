"""Lomitus: purskevirhe hajotetaan yksittäisiksi virheiksi."""

# @alku lomitus
RIVEJA, SARAKKEITA = 4, 7      # neljä 7-bittistä Hamming-sanaa


def lomita(bitit: list[int]) -> list[int]:
    """Kirjoitetaan riveittäin, luetaan sarakkeittain."""
    return [bitit[r * SARAKKEITA + s]
            for s in range(SARAKKEITA) for r in range(RIVEJA)]


def pura(bitit: list[int]) -> list[int]:
    tulos = [0] * len(bitit)
    for i, b in enumerate(bitit):
        s, r = divmod(i, RIVEJA)
        tulos[r * SARAKKEITA + s] = b
    return tulos
# @loppu lomitus


def virheita_per_sana(virheet: list[int]) -> list[int]:
    return [sum(virheet[r * SARAKKEITA:(r + 1) * SARAKKEITA])
            for r in range(RIVEJA)]


# Neljän bitin purske keskellä lähetystä.
purske = [1 if 10 <= i < 14 else 0 for i in range(RIVEJA * SARAKKEITA)]
print("ilman lomitusta, virheitä sanoissa:", virheita_per_sana(purske))
print("lomitettuna, virheitä sanoissa:   ",
      virheita_per_sana(pura(purske)))
assert pura(lomita(list(range(28)))) == list(range(28))
