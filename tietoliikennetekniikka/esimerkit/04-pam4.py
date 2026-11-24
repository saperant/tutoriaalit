"""PAM4: kaksi bittiä symbolissa Gray-koodattuna."""

# @alku pam4
# Gray-koodi: viereiset tasot eroavat vain yhdessä bitissä, joten
# tavallisin virhe (naapuritaso) maksaa vain yhden bitin.
TASOT = {"00": -3, "01": -1, "11": 1, "10": 3}
BITIT = {v: k for k, v in TASOT.items()}


def laheta(bitit: str) -> list[int]:
    return [TASOT[bitit[i:i + 2]] for i in range(0, len(bitit), 2)]


def vastaanota(symbolit: list[int]) -> str:
    return "".join(BITIT[s] for s in symbolit)
# @loppu pam4


data = "0001111000110110"
symbolit = laheta(data)
print("bitit   ", data)
print("symbolit", symbolit)
print("baudit / bittinopeus =", len(symbolit) / len(data))
assert vastaanota(symbolit) == data

# @alku virhe
# Kohina siirtää yhden symbolin naapuritasolle.
virheellinen = symbolit.copy()
virheellinen[2] = 1 if virheellinen[2] == 3 else virheellinen[2] + 2
vastaanotettu = vastaanota(virheellinen)
erot = sum(a != b for a, b in zip(data, vastaanotettu, strict=True))
print(f"symbolivirhe {symbolit[2]} -> {virheellinen[2]}:"
      f" {erot} bittivirhe(ttä)")
# @loppu virhe
