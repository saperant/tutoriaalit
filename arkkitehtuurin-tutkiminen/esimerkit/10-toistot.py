"""Simulointitulosten epävarmuus: toistot eri siemenillä ja 95 %:n
luottamusväli. Lopuksi koetiedosto, josta tulos voidaan toistaa."""

import hashlib
import json
from dataclasses import asdict, dataclass

from arkki.jonot import eksponentiaalinen, mm1, simuloi
from arkki.tilasto import luottamusvali, toistoja_tarvitaan


# @alku koe
@dataclass(frozen=True)
class Koe:
    """Kaikki, mitä tuloksen toistaminen vaatii, yhdessä paikassa."""
    malli: str = "M/M/1"
    kayttoaste: float = 0.9
    palvelu_ns: float = 10.0
    asiakkaita: int = 20_000
    siemenet: tuple[int, ...] = tuple(range(1, 11))
# @loppu koe


def main() -> None:
    koe = Koe()
    lam = koe.kayttoaste / koe.palvelu_ns
    # @alku toistot
    viipymat = [simuloi(lam, eksponentiaalinen(koe.palvelu_ns), 1,
                        koe.asiakkaita, siemen).viipyma
                for siemen in koe.siemenet]
    ka, puoli = luottamusvali(viipymat)
    # @loppu toistot
    print("viipymä (ns) siemenittäin:",
          " ".join(f"{w:.0f}" for w in viipymat))
    print(f"keskiarvo {ka:.1f} +- {puoli:.1f} (95 %), analyyttinen"
          f" {mm1(lam, 1 / koe.palvelu_ns).viipyma:.1f}")
    print(f"+-2 %:n tarkkuuteen tarvitaan noin"
          f" {toistoja_tarvitaan(viipymat, 0.02)} toistoa")
    # @alku tiedosto
    # Pyöristys ennen tiivistettä: viimeisen bitin erot eri koneiden
    # matematiikkakirjastoissa eivät saa muuttaa tunnistetta.
    tulos = {"viipyma_ka": round(ka, 2), "puolileveys": round(puoli, 2)}
    teksti = json.dumps({"koe": asdict(koe), "tulos": tulos},
                        sort_keys=True)
    tiiviste = hashlib.sha256(teksti.encode()).hexdigest()[:16]
    print(f"koetiedosto {tiiviste}.json: {teksti[:36]}...")
    # @loppu tiedosto


if __name__ == "__main__":
    main()
