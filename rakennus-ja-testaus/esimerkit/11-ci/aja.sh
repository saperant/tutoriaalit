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
