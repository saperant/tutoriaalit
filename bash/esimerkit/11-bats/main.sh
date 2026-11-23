#!/usr/bin/env bash
# Ajaa hinnoittelukirjaston bats-testit TAP-muodossa. Testien
# kesto jätetään pois, jotta tuloste on toistettava.
set -euo pipefail

HAKEMISTO=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
bats --formatter tap "$HAKEMISTO/hinta.bats"
