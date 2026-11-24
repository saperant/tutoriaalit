"""Parametroidut ajot omissa ajohakemistoissaan, kukin manifestin kanssa."""

from __future__ import annotations

import json
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from vuo.kulku import projektin_vuo, versio
from vuo.raportit import lue_sta, lue_yosys_stat

JUURI = Path(__file__).resolve().parent


# @alku ajo
def aja_leveys(ajot: Path, leveys: int) -> Path:
    """Yksi ajo: hakemisto parametrin mukaan ja manifesti, josta ajon
    voi toistaa ja jonka perusteella tuloksia voi vertailla."""
    hak = ajot / f"leveys-{leveys}"
    vuo = projektin_vuo(JUURI, hak, leveys=leveys)
    tilat = vuo.aja("sta")
    manifesti = {
        "parametrit": {"LEVEYS": leveys, "jakso_ns": 10.0},
        "vaiheet": tilat,
        "komennot": {n: list(vuo.vaiheet[n].komento) for n in tilat},
        "tyokalut": {t: versio(t) for t in ("verilator", "yosys")},
    }
    (hak / "ajo.json").write_text(json.dumps(manifesti, indent=2,
                                             ensure_ascii=False))
    return hak
# @loppu ajo


# @alku kooste
def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ajot = Path(tmp)
        leveydet = [4, 8, 16]
        with ThreadPoolExecutor(3) as pooli:
            hakemistot = list(pooli.map(lambda w: aja_leveys(ajot, w),
                                        leveydet))
        print(" ".join(sorted(p.name for p in ajot.iterdir())))
        for leveys, hak in zip(leveydet, hakemistot, strict=True):
            manifesti = json.loads((hak / "ajo.json").read_text())
            res = lue_yosys_stat(hak / "synteesi" / f"stat_{leveys}.json")
            ajoitus = lue_sta((hak / "sta.txt").read_text())
            print(f"{hak.name}: kiikkuja {res.kiikut}, ajoitus "
                  f"{'MET' if ajoitus.kunnossa else 'VIOLATED'}, "
                  f"vaiheita {len(manifesti['vaiheet'])}")
        print("ajo.json:", ", ".join(sorted(manifesti)))
# @loppu kooste


if __name__ == "__main__":
    main()
