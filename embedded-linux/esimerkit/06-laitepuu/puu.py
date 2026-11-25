"""Piirtää käännetyn laitepuun ylimmän tason Graphviz-kaavioksi.

Solmut ja ominaisuudet luetaan fdtget-komennolla. Samannimiset solmut
(virt-koneen 32 virtio-paikkaa) yhdistetään yhdeksi laatikoksi, ja
yhden solmun phandle-viittaukset piirretään katkoviivoin.

Käyttö: python3 puu.py LAITEPUU.dtb SOLMU   (esim. pl011@9000000)
"""

import subprocess
import sys


def fdtget(dtb: str, solmu: str, ominaisuus: str = "",
           valinnat: tuple[str, ...] = ()) -> list[str]:
    """Palauttaa ominaisuuden arvot tai tyhjän listan, jos sitä ei ole."""
    kohde = [solmu, ominaisuus] if ominaisuus else [solmu]
    tulos = subprocess.run(["fdtget", *valinnat, dtb, *kohde],
                           capture_output=True, text=True, check=False)
    return tulos.stdout.split() if tulos.returncode == 0 else []


def tunnus(nimi: str) -> str:
    return "n_" + "".join(c if c.isalnum() else "_" for c in nimi)


# @alku puu
def piirra(dtb: str, tutkittava: str) -> str:
    heksa = ("-t", "x")
    ryhmat: dict[str, list[str]] = {}
    for solmu in fdtget(dtb, "/", valinnat=("-l",)):
        ryhmat.setdefault(solmu.split("@")[0], []).append(solmu)
    phandlet = {}
    malli = fdtget(dtb, "/", "model")[0]
    rivit = ["digraph {", "  rankdir=LR; node [shape=box];",
             f'  juuri [label="/\\n{malli}"];']
    for kanta, solmut in ryhmat.items():
        nimi = solmut[0]
        if len(solmut) > 1:
            nimi = f"{kanta}@… ({len(solmut)} kpl)"
        sopivuus = fdtget(dtb, "/" + solmut[0], "compatible")
        teksti = nimi + (f"\\n{sopivuus[0]}" if sopivuus else "")
        rivit.append(f'  {tunnus(kanta)} [label="{teksti}"];')
        rivit.append(f"  juuri -> {tunnus(kanta)};")
        for arvo in fdtget(dtb, "/" + solmut[0], "phandle", heksa):
            phandlet[arvo] = kanta
    # Keskeytysohjain periytyy juuresta, ellei solmulla ole omaa.
    polku = "/" + tutkittava
    ohjain = (fdtget(dtb, polku, "interrupt-parent", heksa)
              or fdtget(dtb, "/", "interrupt-parent", heksa))
    viittaukset = [("interrupt-parent", ohjain[0])]
    viittaukset += [("clocks", arvo) for arvo in dict.fromkeys(
        fdtget(dtb, polku, "clocks", heksa))]
    lahde = tunnus(tutkittava.split("@")[0])
    for ominaisuus, arvo in viittaukset:
        rivit.append(f"  {lahde} -> {tunnus(phandlet[arvo])} [style=dashed,")
        rivit.append('    constraint=false, '
                     f'label="{ominaisuus} = <0x{arvo}>"];')
    return "\n".join(rivit + ["}"])
# @loppu puu


if __name__ == "__main__":
    print(piirra(sys.argv[1], sys.argv[2]))
