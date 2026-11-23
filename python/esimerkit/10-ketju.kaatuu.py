"""Käsittelemätön ketjutettu poikkeus: traceback näyttää molemmat."""


class KonfiguraatioVirhe(Exception):
    pass


def lue_aikakatkaisu(arvo: str) -> float:
    try:
        return float(arvo)
    except ValueError as virhe:
        raise KonfiguraatioVirhe(f"aikakatkaisu: {arvo!r}") from virhe


lue_aikakatkaisu("viisi")
