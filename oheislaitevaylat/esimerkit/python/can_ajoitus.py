"""CAN-bitin ajoitus: esijakaja, aikakvantit ja näytepiste."""

# @alku ajoitus
# Bitti jaetaan aikakvantteihin (TQ): SYNC (1) + TSEG1 (PROP +
# PHASE1) + TSEG2 (PHASE2). Näyte otetaan TSEG1:n lopussa. CiA
# suosittelee näytepisteeksi noin 87,5 %.
TAVOITE = 0.875


def ajoitukset(kello: int, nopeus: int) -> list[tuple[int, int, int, int]]:
    """Kaikki (esijakaja, TQ/bitti, TSEG1, TSEG2), joilla nopeus
    toteutuu tarkasti; TQ:ta 8..25 bittiä kohti."""
    tulos = []
    for esijakaja in range(1, 65):
        kvantteja, jaannos = divmod(kello, esijakaja * nopeus)
        if jaannos or not 8 <= kvantteja <= 25:
            continue
        tseg2 = max(2, round(kvantteja * (1 - TAVOITE)))
        tulos.append((esijakaja, kvantteja, kvantteja - 1 - tseg2, tseg2))
    return tulos


print("kello   nopeus   BRP  TQ  TSEG1 TSEG2 SJW  naytepiste")
for kello, nopeus in ((8_000_000, 1_000_000), (16_000_000, 500_000),
                      (40_000_000, 500_000), (40_000_000, 125_000)):
    vaihtoehdot = ajoitukset(kello, nopeus)
    paras = min(vaihtoehdot,
                key=lambda v: abs((1 + v[2]) / v[1] - TAVOITE))
    brp, tq, tseg1, tseg2 = paras
    sjw = min(4, tseg2)  # tahdistuksen hyppy, enintään TSEG2
    piste = (1 + tseg1) / tq * 100
    print(f"{kello // 10**6:3} MHz {nopeus // 1000:5}k {brp:5} {tq:3} "
          f"{tseg1:5} {tseg2:5} {sjw:3} {piste:8.1f} %  "
          f"({len(vaihtoehdot)} vaihtoehtoa)")
# @loppu ajoitus
