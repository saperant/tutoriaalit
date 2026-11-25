"""Malliratkaisu 08-1: Laskuri."""


class Laskuri:
    """Laskuri, jota kasvatetaan yksi kerrallaan."""

    def __init__(self) -> None:
        self.arvo = 0

    def kasvata(self) -> None:
        self.arvo += 1

    def nollaa(self) -> None:
        self.arvo = 0
