"""Baudinopeuden virhe: jakajien pyöristys ja vastaanottimen sieto."""

from mallit.uart import Kehysmuoto, linja, vastaanota

# @alku jakajat
NOPEUDET = (9600, 115200, 921600)


def virhe(kello: float, jakaja: int, ylinaytteistys: int,
          haluttu: int) -> float:
    toteutunut = kello / (jakaja * ylinaytteistys)
    return (toteutunut - haluttu) / haluttu * 100


print("kello         nopeus  jakaja  virhe")
for kello, ylinaytteistys, nimi in (
        (25e6, 1, "25 MHz CMSDK"),  # BAUDDIV = kello / nopeus
        (16e6, 16, "16 MHz x16"),
        (1.8432e6, 16, "1.8432 MHz x16")):
    for nopeus in NOPEUDET:
        jakaja = round(kello / (ylinaytteistys * nopeus))
        if jakaja == 0:
            print(f"{nimi:14} {nopeus:6}      -  liian nopea")
            continue
        v = virhe(kello, jakaja, ylinaytteistys, nopeus)
        print(f"{nimi:14} {nopeus:6} {jakaja:6} {v:+7.2f} %")
# @loppu jakajat

# @alku sieto
# Lähettimen bitti on promille-luvun verran pidempi (hitaampi
# lähetin) tai lyhyempi kuin vastaanottimen 16 näytettä.
muoto = Kehysmuoto()
data = bytes([0x00, 0x55, 0xFF, 0x0F, 0x80])
otsake, tulos, rajat = [], [], []
for promille in range(-70, 71, 10):
    pituus = 16 * (1 + promille / 1000)
    saadut = vastaanota(linja(data, muoto, pituus), muoto)
    oikein = (len(saadut) == len(data) and
              all(s.tavu == d and s.virhe is None
                  for s, d in zip(saadut, data, strict=True)))
    otsake.append(f"{promille // 10:+3d}")
    tulos.append("  ." if oikein else "  x")
    if oikein:
        rajat.append(promille)
print()
print("virhe % " + "".join(otsake))
print("tulos   " + "".join(tulos))
print("(. = kaikki tavut oikein, x = virheita)")
print(f"toimii {min(rajat) / 10:+.0f} % ... {max(rajat) / 10:+.0f} %")
teoria = (0.5 - 1 / 16) / 9.5 * 100
print(f"teoreettinen raja 8N1, 16x: +-{teoria:.1f} %")
# @loppu sieto
