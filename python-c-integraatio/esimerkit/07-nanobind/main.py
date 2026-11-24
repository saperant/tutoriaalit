"""Sama luokka pybind11:llä ja nanobindilla: tulokset ja kutsun hinta."""

import time
from typing import Protocol

import mittari
import tilasto_nb


class Lisattava(Protocol):
    def lisaa(self, x: float) -> None: ...


# @alku vertailu
def kutsun_aika(t: Lisattava, kerrat: int = 200_000) -> float:
    """Nopein viidestä ajosta: kerrat × t.lisaa(1.0)."""
    paras = float("inf")
    for _ in range(5):
        alku = time.perf_counter()
        for _ in range(kerrat):
            t.lisaa(1.0)
        paras = min(paras, time.perf_counter() - alku)
    return paras


def main() -> None:
    arvot = [20.1, 20.4, 19.8, 20.3]
    pb = mittari.Tilasto()
    nb = tilasto_nb.Tilasto()
    pb.lisaa_kaikki(arvot)
    nb.lisaa_kaikki(arvot)
    print("pybind11:", pb, f"{pb.keskiarvo:.3f}")
    print("nanobind:", nb, f"{nb.keskiarvo:.3f}")
    try:
        _ = tilasto_nb.Tilasto().keskiarvo
    except tilasto_nb.TyhjaOtos as e:
        print("nanobind TyhjaOtos:", e)

    t_pb = kutsun_aika(mittari.Tilasto())
    t_nb = kutsun_aika(tilasto_nb.Tilasto())
    print("nanobind-kutsu yli 1,3 kertaa nopeampi:", t_pb > 1.3 * t_nb)
# @loppu vertailu


if __name__ == "__main__":
    main()
