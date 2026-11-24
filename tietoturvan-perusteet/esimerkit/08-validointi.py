"""Syötteen jäsentäminen reunalla: sallittujen arvojen lista ja rajat."""

import json
import re
from dataclasses import dataclass

ENINTAAN_TAVUA = 4096
TUOTEKOODI = re.compile(r"[A-Z]{3}-\d{4}")


@dataclass(frozen=True)
class Tilausrivi:
    tuote: str
    maara: int


class Hylatty(ValueError):
    pass


# @alku jasennys
def jasenna(raaka: bytes) -> list[Tilausrivi]:
    """Joko kelvollinen tilaus tai Hylatty; välimuotoja ei ole."""
    if len(raaka) > ENINTAAN_TAVUA:              # resurssien rajat ensin
        raise Hylatty("liian suuri pyyntö")
    try:
        data = json.loads(raaka)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Hylatty("ei JSONia") from e
    if not isinstance(data, list) or not 1 <= len(data) <= 50:
        raise Hylatty("odotettiin 1–50 riviä")
    rivit = []
    for r in data:
        if not isinstance(r, dict) or set(r) != {"tuote", "maara"}:
            raise Hylatty("rivin kentät: tuote, maara")
        tuote, maara = r["tuote"], r["maara"]
        if not isinstance(tuote, str) or not TUOTEKOODI.fullmatch(tuote):
            raise Hylatty(f"tuntematon tuotekoodin muoto: {tuote!r:.20}")
        # bool on Pythonissa int:n alityyppi, joten se suljetaan pois.
        if (isinstance(maara, bool) or not isinstance(maara, int)
                or not 1 <= maara <= 100):
            raise Hylatty("määrä 1–100")
        rivit.append(Tilausrivi(tuote, maara))
    return rivit
# @loppu jasennys


for syote in [b'[{"tuote": "KAH-0001", "maara": 2}]',
              b'[{"tuote": "KAH-0001", "maara": -5}]',
              b'[{"tuote": "KAH-0001", "maara": true}]',
              b'[{"tuote": "<script>", "maara": 1}]',
              b'[{"tuote": "KAH-0001", "maara": 1, "hinta": 0}]',
              b"[" * 5000]:
    try:
        print("hyväksytty:", jasenna(syote))
    except Hylatty as e:
        print("hylätty:", e)
