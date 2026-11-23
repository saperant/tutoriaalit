#!/usr/bin/env bash
# Sotkuisten oikeuksien korjaus: hakemistot 755, tiedostot 644,
# skriptit 755.
set -euo pipefail
export LC_ALL=C
umask 022

mkdir -p sivusto/kuvat sivusto/skriptit
touch sivusto/index.html sivusto/kuvat/logo.png
printf '#!/bin/sh\n' > sivusto/skriptit/paivita.sh
chmod 777 sivusto/index.html sivusto/kuvat
chmod 700 sivusto/skriptit
chmod 600 sivusto/kuvat/logo.png
chmod 755 sivusto/skriptit/paivita.sh

# @alku etsinta
echo "Kaikkien kirjoitettavissa:"
find sivusto -perm -o+w | sort
# @loppu etsinta

# @alku iso-x
chmod -R u=rwX,go=rX sivusto
find sivusto -printf '%m %p\n' | sort -k2
# @loppu iso-x

# @alku korjaus
find sivusto -type d -exec chmod 755 {} +
find sivusto -type f -exec chmod 644 {} +
find sivusto -type f -name '*.sh' -exec chmod 755 {} +
find sivusto -type f -printf '%m %p\n' | sort -k2
# @loppu korjaus
