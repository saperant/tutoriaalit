"""Malliratkaisu 08-3: Varasto ja invariantti."""


class VarastoVirhe(Exception):
    """Varaston kapasiteetti ylittyisi tai tavaraa ei ole tarpeeksi."""


class Varasto:
    """Varasto, jonka määrä pysyy välillä 0–kapasiteetti."""

    def __init__(self, kapasiteetti: int) -> None:
        self.kapasiteetti = kapasiteetti
        self._maara = 0

    @property
    def maara(self) -> int:
        return self._maara

    def lisaa(self, maara: int) -> None:
        if maara <= 0:
            raise ValueError(f"määrän on oltava positiivinen: {maara}")
        if self._maara + maara > self.kapasiteetti:
            raise VarastoVirhe(f"varastoon ei mahdu {maara}")
        self._maara += maara

    def ota(self, maara: int) -> None:
        if maara <= 0:
            raise ValueError(f"määrän on oltava positiivinen: {maara}")
        if maara > self._maara:
            raise VarastoVirhe(f"varastossa on vain {self._maara}")
        self._maara -= maara
