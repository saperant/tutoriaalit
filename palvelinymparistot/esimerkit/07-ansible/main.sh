#!/usr/bin/env bash
# Konfiguraationhallinta Ansiblella: ensimmäinen ajo muuttaa, toinen ei
# muuta mitään (idempotenssi), käsin tehty muutos näkyy tarkistusajossa
# (--check --diff), ja seuraava ajo palauttaa halutun tilan.
set -euo pipefail
export LC_ALL=C.UTF-8
cd "$(dirname "$0")"
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
export JUURI=$tyo/kohde ANSIBLE_HOME=$tyo/ansible
export ANSIBLE_LOCAL_TEMP=$tyo/ansible/tmp ANSIBLE_NOCOLOR=1
export ANSIBLE_RETRY_FILES_ENABLED=0

# @alku ajo
aja() {  # aja [lisävalitsimet]: tulostaa yhteenvedon
    ansible-playbook -i inventaario.ini palvelin.yml "$@" > "$tyo/loki"
    awk '/^localhost/ { print "  " $3, $4 }' "$tyo/loki"
    if grep -q '^RUNNING HANDLER' "$tyo/loki"; then
        echo "  käsittelijä ajettiin"
    fi
}
echo "1. ajo:"; aja
echo "2. ajo:"; aja
# @loppu ajo

# @alku ajautuminen
sed -i 's/^PermitRootLogin no/PermitRootLogin yes/' \
    "$JUURI/etc/ssh/sshd_config"
echo "käsin muutettu; tarkistusajo:"
aja --check --diff
grep -E '^[-+][A-Za-z]' "$tyo/loki"
echo "korjaava ajo:"; aja
grep PermitRootLogin "$JUURI/etc/ssh/sshd_config"
# @loppu ajautuminen
