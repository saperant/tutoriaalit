#!/usr/bin/env bash
# Suunnitelma, toteutus, uusi suunnitelma ja käsin tehty muutos (drift).
set -euo pipefail
cd "$(dirname "$0")"
tila=$(mktemp)
trap 'rm -f "$tila"' EXIT
rm -f "$tila"

echo "== suunnitelma tyhjälle tilalle"
python3 tila.py suunnitelma haluttu.json "$tila"
echo "== toteutus"
python3 tila.py toteuta haluttu.json "$tila"
echo "== toinen ajo"
python3 tila.py suunnitelma haluttu.json "$tila"
echo "== joku kasvatti klusteria käsin konsolista"
python3 - "$tila" <<'PY'
import json, sys
p = sys.argv[1]
t = json.load(open(p))
t["kaynnit-tuotanto"]["solmuja"] = 5
json.dump(t, open(p, "w"))
PY
python3 tila.py suunnitelma haluttu.json "$tila"
