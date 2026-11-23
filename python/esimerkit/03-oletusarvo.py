"""Muuttuva oletusarvo luodaan vain kerran."""


# @alku ansa
def lisaa_vaarin(tuote: str, kori: list[str] = []) -> list[str]:  # noqa: B006
    kori.append(tuote)
    return kori


print(lisaa_vaarin("omena"))
print(lisaa_vaarin("päärynä"))   # sama lista kuin edellisellä kerralla!
# @loppu ansa


# @alku oikein
def lisaa(tuote: str, kori: list[str] | None = None) -> list[str]:
    if kori is None:
        kori = []
    kori.append(tuote)
    return kori


print(lisaa("omena"))
print(lisaa("päärynä"))
# @loppu oikein
