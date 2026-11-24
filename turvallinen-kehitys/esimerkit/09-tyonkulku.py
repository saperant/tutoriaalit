"""GitHub Actions -työnkulkujen tarkistin: tunnetut vaaralliset mallit.

Rivipohjainen tarkistin ei ymmärrä YAMLia kokonaan, mutta se löytää
yleisimmät virheet. Oikeissa projekteissa sama tehdään työkaluilla,
kuten actionlint ja zizmor, jotka ajetaan CI:ssä.
"""

import re
from pathlib import Path

LAUSEKE = re.compile(
    r"\$\{\{\s*github\.(event\.(issue|comment|pull_request|review|"
    r"head_commit|commits|pages)|head_ref)[^}]*\}\}")
KIINNITETTY = re.compile(r"@[0-9a-f]{40}$")


# @alku tarkista
def tarkista(teksti: str) -> list[str]:
    havainnot = []
    rivit = teksti.splitlines()
    if not any(r.startswith("permissions:") for r in rivit):
        havainnot.append("ei permissions-osiota: oletusoikeudet voivat "
                         "olla kirjoitusoikeudet")
    run_lohko = False
    for nro, rivi in enumerate(rivit, 1):
        sisalto = rivi.strip()
        if sisalto.startswith("pull_request_target"):
            havainnot.append(f"{nro}: pull_request_target ajaa vieraan "
                             "koodin pääsyllä salaisuuksiin")
        if sisalto.startswith("run:"):
            run_lohko = True
        elif sisalto.startswith(("- ", "with:", "env:")):
            run_lohko = False
        if run_lohko and LAUSEKE.search(rivi):
            havainnot.append(f"{nro}: käyttäjän syöte suoraan "
                             "komentoon (skriptin injektio)")
        if sisalto.startswith("- uses:") or sisalto.startswith("uses:"):
            viite = sisalto.split("uses:", 1)[1].strip()
            if not viite.startswith(("./", "docker://")) \
                    and not KIINNITETTY.search(viite):
                havainnot.append(f"{nro}: toimintoa ei kiinnitetty "
                                 f"tiivisteeseen: {viite}")
    return havainnot
# @loppu tarkista


def main() -> None:
    hakemisto = Path(__file__).parent
    for nimi in ("09-vaarallinen.yml", "09-korjattu.yml"):
        havainnot = tarkista((hakemisto / nimi).read_text("utf-8"))
        print(f"{nimi}: {len(havainnot)} havaintoa")
        for h in havainnot:
            print(f"  {h}")


if __name__ == "__main__":
    main()
