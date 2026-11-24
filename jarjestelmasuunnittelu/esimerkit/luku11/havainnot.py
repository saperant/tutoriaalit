"""Kaksi havaittavaa palvelua: kauppa kutsuu varastoa.

Lähetetään 20 tilausta. Varasto on hidas tilauksilla 7 ja 17 ja
epäonnistuu tilauksilla 9 ja 19. Lopuksi luetaan kummankin palvelun
/metrics ja kootaan hitaan tilauksen jälki lokiriveistä. Tunnukset
ovat satunnaisia, joten niitä ei tulosteta, vain niiden suhteet.
"""

import json
import urllib.error
import urllib.request
from pathlib import Path

from jarjestelma.ymparisto import Ymparisto


def hae(portti: int, polku: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{portti}{polku}",
                                    timeout=5) as v:
            return v.status, v.read().decode()
    except urllib.error.HTTPError as virhe:
        return virhe.code, virhe.read().decode()


def main() -> None:
    with Ymparisto() as ymp:
        lokit = {n: ymp.hakemisto / f"{n}.jsonl"
                 for n in ("kauppa", "varasto")}
        varasto = ymp.palvelu("jarjestelma.seurattu", "--nimi", "varasto",
                              "--loki", str(lokit["varasto"]))
        kauppa = ymp.palvelu("jarjestelma.seurattu", "--nimi", "kauppa",
                             "--alavirta", str(varasto.portti),
                             "--loki", str(lokit["kauppa"]))
        koodit = [hae(kauppa.portti, f"/tilaus/{n}")[0] for n in range(20)]
        virheet = [str(n) for n, k in enumerate(koodit) if k != 200]
        print(f"vastaukset: {koodit.count(200)} x 200, muut tilauksille"
              f" {' '.join(virheet)}: {sorted(set(koodit) - {200})}")

        # @alku mittarit
        for nimi, palvelu in (("kauppa", kauppa), ("varasto", varasto)):
            _, teksti = hae(palvelu.portti, "/metrics")
            print(f"{nimi} /metrics:")
            for rivi in teksti.splitlines():
                if rivi.startswith("http_pyynnot_yhteensa") or \
                        'le="0.25"' in rivi or 'le="+Inf"' in rivi:
                    print("  " + rivi.replace(f'palvelu="{nimi}",', ""))
        # @loppu mittarit

        # @alku kokoaminen
        rivit = [json.loads(r) for p in lokit.values()
                 for r in Path(p).read_text().splitlines()]
        juuri = next(r for r in rivit if r["palvelu"] == "kauppa"
                     and r["tunnus"] == "7")
        jalki = [r for r in rivit if r["jalki"] == juuri["jalki"]]
        print("tilauksen 7 jälki:")
        for r in sorted(jalki, key=lambda r: r["vanhempi"] is not None):
            sisennys = "    " if r["vanhempi"] else "  "
            nopeus = "hidas" if r["kesto_ms"] > 250 else "nopea"
            print(f"{sisennys}{r['palvelu']} {r['reitti']}/{r['tunnus']}"
                  f" {r['koodi']} {nopeus}")
        lapsi = next(r for r in jalki if r["vanhempi"])
        print("  varaston vanhempi on kaupan väli:",
              lapsi["vanhempi"] == juuri["vali"])
        print("  muissa jäljissä tilaus 7:",
              sum(r["tunnus"] == "7" for r in rivit) - len(jalki))
        # @loppu kokoaminen


if __name__ == "__main__":
    main()
