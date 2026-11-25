#!/usr/bin/env bash
# Työnkulkujen tarkistus ennen pushia: YAML jäsennetään ja verrataan
# GitHub Actionsin skeemaan. Työnkulkuja ei ajeta.
set -euo pipefail

# @alku validointi
tarkista() {
    check-jsonschema --builtin-schema vendor.github-workflows "$@" 2>&1
}
tarkista .github/workflows/ci.yml
if ! tarkista rikki.yml > virheet.txt; then
    echo "rikki.yml hylättiin:"
    sed -nE 's/^    (\$\.[^:]*): (.*)/\1\n    \2/p' virheet.txt
fi
# @loppu validointi

# @alku jasennys
python3 - <<'PY'
import yaml
ci = yaml.safe_load(open(".github/workflows/ci.yml"))
m = ci["jobs"]["rakenna"]["strategy"]["matrix"]
yhd = [(c, p) for c in m["cc"] for p in m["preset"]
       if {"cc": c, "preset": p} not in m.get("exclude", [])]
print("matriisin työt:", ", ".join(f"{c}/{p}" for c, p in yhd))
for nimi, tyo in ci["jobs"].items():
    print(f"työ {nimi}: tarvitsee {tyo.get('needs', '-')}")
PY
# @loppu jasennys

# @alku verkko
# Töiden verkko DOT-muodossa: matriisin yhdistelmät omina solminaan ja
# needs-riippuvuudet kaarina. Kirjan kuva on tiedosto tyot.dot.
python3 - > uusi.dot <<'PY'
import yaml
ci = yaml.safe_load(open(".github/workflows/ci.yml"))
solmut = {}
for nimi, tyo in ci["jobs"].items():
    m = tyo.get("strategy", {}).get("matrix")
    if m:
        solmut[nimi] = [f"{nimi}\\n{c} / {p}" for c in m["cc"]
                        for p in m["preset"]
                        if {"cc": c, "preset": p} not in m["exclude"]]
    else:
        solmut[nimi] = [nimi]
print("digraph {\n  rankdir=LR; nodesep=0.2; ranksep=0.7;")
print('  alku [label="push tai\\npull request", style="rounded,dashed"];')
for nimi, tyo in ci["jobs"].items():
    tarpeet = tyo.get("needs", [])
    tarpeet = [tarpeet] if isinstance(tarpeet, str) else tarpeet
    lahteet = [s for t in tarpeet for s in solmut[t]] or ["alku"]
    for kohde in solmut[nimi]:
        for lahde in lahteet:
            a = lahde if lahde == "alku" else f'"{lahde}"'
            print(f'  {a} -> "{kohde}";')
print("}")
PY
diff -u tyot.dot uusi.dot && echo "tyot.dot vastaa työnkulkua"
# @loppu verkko
