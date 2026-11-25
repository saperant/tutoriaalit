"""Toimitusmaksu, jossa on kaksi tyypillistä rajavirhettä."""

ILMAISEN_RAJA = 5_000
PIENI_PAKETTI = 2_000
ISO_PAKETTI = 10_000
SUURIN_PAINO = 30_000


# @alku viat
def toimitusmaksu(paino_g: int, summa_snt: int) -> int:
    if paino_g <= 0:
        raise ValueError("painon on oltava positiivinen")
    if paino_g > SUURIN_PAINO:
        raise ValueError("yli 30 kg:n lähetyksiä ei toimiteta")
    if summa_snt > ILMAISEN_RAJA and paino_g <= ISO_PAKETTI:   # vika: >
        return 0
    if paino_g < PIENI_PAKETTI:                                # vika: <
        return 590
    if paino_g <= ISO_PAKETTI:
        return 990
    return 1_990
# @loppu viat
