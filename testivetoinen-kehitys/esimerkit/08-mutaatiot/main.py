"""Vertaa kahta testisarjaa: kattavuus ja mutaatiopisteet."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from mutaattori import aja

TAMA = Path(__file__).resolve().parent
MODUULI = TAMA / "toimitus.py"


# @alku kattavuus
def kattavuus(testit: Path) -> str:
    """Rivi- ja haarakattavuus coverage.py:llä mitattuna."""
    with tempfile.TemporaryDirectory() as tmp:
        data = Path(tmp) / "data"
        raportti = Path(tmp) / "raportti.json"
        subprocess.run(
            [sys.executable, "-m", "coverage", "run", "--branch",
             f"--data-file={data}", f"--include={MODUULI}", "-m", "pytest",
             "-q", "-p", "no:cacheprovider", str(testit)],
            cwd=TAMA, capture_output=True, check=True)
        subprocess.run(
            [sys.executable, "-m", "coverage", "json", "-q",
             f"--data-file={data}", "-o", str(raportti)],
            cwd=TAMA, capture_output=True, check=True)
        yhteensa = json.loads(raportti.read_text("utf-8"))["totals"]
    return (f"rivit {yhteensa['covered_lines']}/{yhteensa['num_statements']}"
            f", haarat {yhteensa['covered_branches']}"
            f"/{yhteensa['num_branches']}")
# @loppu kattavuus


def main() -> None:
    for nimi in ("test_heikko.py", "test_vahva.py"):
        testit = TAMA / nimi
        tulokset = aja(MODUULI, testit)
        tapettu = sum(1 for _, hengissa in tulokset if not hengissa)
        print(f"{nimi}: {kattavuus(testit)}")
        print(f"  mutantteja {len(tulokset)}, tapettu {tapettu} "
              f"({100 * tapettu // len(tulokset)} %), hengissä:")
        for mutantti, hengissa in tulokset:
            if hengissa:
                print(f"    rivi {mutantti.rivi:>2}: {mutantti.kuvaus}")


if __name__ == "__main__":
    main()
