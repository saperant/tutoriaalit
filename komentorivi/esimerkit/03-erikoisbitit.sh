#!/usr/bin/env bash
# setgid-bitti jaetulle hakemistolle ja sticky-bitti.
set -euo pipefail
export LC_ALL=C
umask 002

# @alku bitit
mkdir projektit yhteinen
chmod 2775 projektit           # setgid: uudet tiedostot saavat ryhmän
chmod 1777 yhteinen            # sticky: vain omistaja voi poistaa
stat -c '%a %A %n' projektit yhteinen
mkdir projektit/uusi
stat -c '%a %A %n' projektit/uusi
# @loppu bitit
