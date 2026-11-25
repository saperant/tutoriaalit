"""Sadalla jaollinen vuosi ei ole koskaan karkausvuosi (ei 2000)."""


def on_karkausvuosi(vuosi: int) -> bool:
    return vuosi % 4 == 0 and vuosi % 100 != 0
