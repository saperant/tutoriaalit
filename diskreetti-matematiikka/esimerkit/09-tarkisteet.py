"""Tarkisteet modulaariaritmetiikalla: viitenumero, IBAN ja henkilötunnus."""


# @alku viite
def viitteen_tarkiste(perusosa: str) -> int:
    """Suomalainen viitenumero: painot 7, 3, 1 oikealta, täydennys
    seuraavaan kymmeneen."""
    painot = (7, 3, 1)
    summa = sum(int(n) * painot[i % 3]
                for i, n in enumerate(reversed(perusosa)))
    return -summa % 10


perus = "1234561"
print(f"viitenumero: {perus}{viitteen_tarkiste(perus)}")
# @loppu viite


# @alku iban
def iban_kelpaa(iban: str) -> bool:
    """IBAN: siirrä neljä ensimmäistä merkkiä loppuun, muuta kirjaimet
    luvuiksi (A = 10 … Z = 35); kelvollinen luku ≡ 1 (mod 97)."""
    s = iban.replace(" ", "")
    s = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in s)) % 97 == 1


for iban in ("FI21 1234 5600 0007 85", "FI21 1234 5600 0007 58"):
    print(iban, "kelpaa" if iban_kelpaa(iban) else "VIRHE")
# @loppu iban


# @alku hetu
def hetun_tarkiste(paivays: str, yksilo: str) -> str:
    """Henkilötunnuksen tarkistusmerkki: 9-numeroinen luku mod 31."""
    merkit = "0123456789ABCDEFHJKLMNPRSTUVWXY"
    return merkit[int(paivays + yksilo) % 31]


print("131052-308 ->", hetun_tarkiste("131052", "308"))
# Yksittäinen numerovirhe muuttaa aina jäännöksen, koska 31 on
# alkuluku ja muutos on muotoa d·10^k, jolla ei ole tekijää 31.
alkuperainen = "131052308"
huomattu = 0
for i in range(9):
    for d in "0123456789":
        if d != alkuperainen[i]:
            vaara = alkuperainen[:i] + d + alkuperainen[i + 1:]
            huomattu += (int(vaara) % 31 != int(alkuperainen) % 31)
print(f"yksittäisiä numerovirheitä huomattu: {huomattu}/81")
# @loppu hetu
