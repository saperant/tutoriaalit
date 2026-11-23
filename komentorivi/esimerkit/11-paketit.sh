#!/usr/bin/env bash
# Mistä paketista tiedosto tulee ja onko paketti asennettu?
# Toimii Debianissa ja Ubuntussa ilman verkkoyhteyttä.
set -euo pipefail
export LC_ALL=C

# @alku dpkg
dpkg -S "$(readlink -f "$(command -v sort)")"
dpkg-query -W -f='${Package} ${Status}\n' coreutils
dpkg-query -W -f='${Status}\n' olematon-paketti 2>&1 || true
# @loppu dpkg
