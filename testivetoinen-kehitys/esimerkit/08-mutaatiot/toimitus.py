"""Toimitusmaksu ja hyvityksen vähentäminen: mutaatiotestauksen kohde."""

ILMAISEN_RAJA = 5_000      # senttiä
PIENI_PAKETTI = 2_000      # grammaa
ISO_PAKETTI = 10_000
SUURIN_PAINO = 30_000


def toimitusmaksu(paino_g: int, summa_snt: int) -> int:
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


# @alku veloitus
def veloitettava(maksu: int, hyvitys: int) -> int:
    """Toimitusmaksusta jää maksettavaa hyvityksen jälkeen."""
    if hyvitys >= maksu:
        return 0
    return maksu - hyvitys
# @loppu veloitus
