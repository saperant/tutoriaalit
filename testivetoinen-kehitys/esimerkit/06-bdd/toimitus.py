"""Toimitusmaksu painon ja tilauksen summan mukaan."""

ILMAISEN_RAJA = 5_000      # senttiä: vähintään 50 euron tilaus
PIENI_PAKETTI = 2_000      # grammaa
ISO_PAKETTI = 10_000
SUURIN_PAINO = 30_000


# @alku maksu
def toimitusmaksu(paino_g: int, summa_snt: int) -> int:
    """Palauttaa toimitusmaksun sentteinä.

    Enintään 2 kg maksaa 5,90 e, enintään 10 kg 9,90 e ja enintään
    30 kg 19,90 e. Vähintään 50 euron tilaus toimitetaan ilmaiseksi,
    jos se painaa enintään 10 kg. Yli 30 kg:n lähetyksiä ei toimiteta.
    """
    if paino_g <= 0:
        raise ValueError("painon on oltava positiivinen")
    if paino_g > SUURIN_PAINO:
        raise ValueError("yli 30 kg:n lähetyksiä ei toimiteta")
    if summa_snt >= ILMAISEN_RAJA and paino_g <= ISO_PAKETTI:
        return 0
    if paino_g <= PIENI_PAKETTI:
        return 590
    if paino_g <= ISO_PAKETTI:
        return 990
    return 1_990
# @loppu maksu
