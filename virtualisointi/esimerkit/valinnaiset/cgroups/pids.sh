#!/usr/bin/env bash
# cgroups: pids-ohjain rajoittaa ryhmän prosessien määrää. Sama raja
# estää kontissa haarukkapommin (fork bomb) kaatamasta koko isäntää.
# Toimii cgroups v2:lla (nykyiset jakelut) ja v1:llä. Jos cgroup-
# tiedostojärjestelmään ei voi kirjoittaa (esim. konttien sisällä),
# esimerkki ohitetaan paluuarvolla 77.
set -euo pipefail
if [[ $EUID -ne 0 ]]; then exec sudo -n -- bash "$0" "$@"; fi
export LC_ALL=C

# @alku ryhma
if [[ -f /sys/fs/cgroup/cgroup.controllers ]]; then      # v2
    vanhempi=/sys/fs/cgroup
    grep -qw pids "$vanhempi/cgroup.subtree_control" 2>/dev/null ||
        echo +pids > "$vanhempi/cgroup.subtree_control" 2>/dev/null ||
        exit 77
else                                                     # v1
    vanhempi=/sys/fs/cgroup/pids
fi
ryhma=$vanhempi/virt-esimerkki-$$
mkdir "$ryhma" 2>/dev/null || exit 77
trap 'rmdir "$ryhma" 2>/dev/null || true' EXIT
echo 5 > "$ryhma/pids.max"
# @loppu ryhma

# @alku kokeilu
# Python liittyy ryhmään ja yrittää käynnistää 10 lasta.
python3 - "$ryhma" <<'PY'
import os
import sys

ryhma = sys.argv[1]
with open(f"{ryhma}/cgroup.procs", "w") as f:
    f.write(str(os.getpid()))
luku, kirjoitus = os.pipe()
lapset, epaonnistui = [], 0
for _ in range(10):
    try:
        pid = os.fork()
    except BlockingIOError:          # EAGAIN: raja tuli vastaan
        epaonnistui += 1
        continue
    if pid == 0:                     # lapsi odottaa, kunnes putki suljetaan
        os.close(kirjoitus)
        os.read(luku, 1)
        os._exit(0)
    lapset.append(pid)
with open(f"{ryhma}/pids.current") as f:
    nyt = f.read().strip()
print(f"pids.max 5: lapsia käynnistyi {len(lapset)}, "
      f"{epaonnistui} haarukointia epäonnistui, pids.current {nyt}")
os.close(kirjoitus)                  # lapset heräävät ja päättyvät
for pid in lapset:
    os.waitpid(pid, 0)
PY
# @loppu kokeilu
# Python-prosessi on päättynyt, joten ryhmä on tyhjä ja voidaan poistaa.
