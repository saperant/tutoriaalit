"""Pistetulo: kulma, kohtisuoruus ja projektio."""

import math

Vektori = list[float]


def piste(a: Vektori, b: Vektori) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


def pituus(v: Vektori) -> float:
    return math.sqrt(piste(v, v))


# @alku kulma
def kulma_asteina(a: Vektori, b: Vektori) -> float:
    """Kulma kaavasta a·b = |a||b| cos θ."""
    c = piste(a, b) / (pituus(a) * pituus(b))
    # Pyöristysvirhe voi viedä arvon hieman yli välin [-1, 1].
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


kulku = [1.0, 0.0]                    # vene kulkee itään
for nimi, tuuli in [("myötätuuli", [5.0, 0.0]),
                    ("sivutuuli", [0.0, 5.0]),
                    ("viisto vastatuuli", [-3.0, 4.0])]:
    print(f"{nimi:<18} a·b = {piste(kulku, tuuli):5.1f}  "
          f"kulma {kulma_asteina(kulku, tuuli):6.1f}°")
# @loppu kulma

# @alku projektio
def projektio(v: Vektori, suunta: Vektori) -> Vektori:
    """v:n komponentti suunnan suuntaan: (v·u / u·u) u."""
    k = piste(v, suunta) / piste(suunta, suunta)
    return [k * x for x in suunta]


# Rinne nousee 30°. Painovoiman komponentti rinteen suuntaan vetää
# kärryä alas, kohtisuora komponentti painaa sitä rinnettä vasten.
paino = [0.0, -9.81 * 100.0]          # 100 kg, newtoneina
rinne = [math.cos(math.radians(30)), math.sin(math.radians(30))]
alas = projektio(paino, rinne)
kohti = [p - a for p, a in zip(paino, alas, strict=True)]
print(f"rinteen suuntaan: {pituus(alas):6.1f} N")
print(f"rinnettä vasten:  {pituus(kohti):6.1f} N")
print(f"komponentit kohtisuorassa: {abs(piste(alas, kohti)) < 1e-9}")
# @loppu projektio
