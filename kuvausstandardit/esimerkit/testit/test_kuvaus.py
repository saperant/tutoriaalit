"""Apukirjaston yksikkötestit: pääsytavat, SVD-kuvaus, otteiden
rivitys ja laitepuusolmut."""

from __future__ import annotations

from pathlib import Path

import pytest

from kuvaus.kaanna import KaannosVirhe, kaanna
from kuvaus.malli import rekisterit
from kuvaus.svd import svd_paasy
from kuvaus.tuota import LEVEYS, rivita

KENTAT = """
addrmap testi {
    reg {
        field { sw = rw; hw = r; } A[0:0] = 0;
        field { sw = r; hw = w; } B[1:1];
        field { sw = w; hw = r; } C[2:2] = 0;
        field { sw = rw; hw = na; hwset; onwrite = woclr; } D[3:3] = 0;
        field { sw = rw; hw = na; hwset; onwrite = woset; } E[4:4] = 0;
        field { sw = r; hw = na; counter; onread = rclr; } F[7:5] = 0;
    } R @ 0x0;
};
"""


def kaanna_teksti(tmp: Path, teksti: str) -> list[tuple[str, str]]:
    (tmp / "testi.rdl").write_text(teksti)
    return [(k.nimi, k.paasy)
            for r in rekisterit(kaanna("testi.rdl", rdl=tmp))
            for k in r.kentat]


def test_paasytavat(tmp_path: Path) -> None:
    assert kaanna_teksti(tmp_path, KENTAT) == [
        ("A", "RW"), ("B", "RO"), ("C", "WO"), ("D", "W1C"),
        ("E", "W1S"), ("F", "RC")]


def test_virheet_kerataan(tmp_path: Path) -> None:
    rikki = KENTAT.replace("A[0:0] = 0", "A[0:0] = 2")
    with pytest.raises(KaannosVirhe) as virhe:
        kaanna_teksti(tmp_path, rikki)
    assert any("testi.rdl:4: error" in v for v in virhe.value.viestit)


@pytest.mark.parametrize(("paasy", "odotettu"), [
    ("RW", ("read-write", {})),
    ("RO", ("read-only", {})),
    ("W1C", ("read-write", {"modifiedWriteValues": "oneToClear"})),
    ("RC", ("read-only", {"readAction": "clear"})),
])
def test_svd_paasy(paasy: str, odotettu: tuple[str, dict[str, str]]) -> None:
    assert svd_paasy(paasy) == odotettu


def test_rivitys_sailyttaa_sanat() -> None:
    rivi = "    x = " + " | ".join(f"signaali_{i}" for i in range(12)) + ";"
    tulos = rivita(rivi)
    assert all(len(r) <= LEVEYS for r in tulos)
    assert " ".join(r.strip() for r in tulos) == rivi.strip()


def test_rivitys_siirtaa_kommentin() -> None:
    rivi = "    if (a && b) begin // " + "pitka selitys " * 6
    tulos = rivita(rivi)
    assert tulos[0].strip().startswith("//")
    assert "//" not in "".join(tulos[1:])
