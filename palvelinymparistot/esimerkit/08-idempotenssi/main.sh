#!/usr/bin/env bash
# Komento (shell) ei tiedä lopputilasta mitään: se lisää rivin joka
# ajolla. Moduuli (lineinfile) kuvaa halutun tilan ja muuttaa vain, jos
# tila poikkeaa siitä.
set -euo pipefail
export LC_ALL=C.UTF-8
cd "$(dirname "$0")"
tyo=$(mktemp -d)
trap 'rm -rf "$tyo"' EXIT
export KOHDE=$tyo/hosts ANSIBLE_HOME=$tyo/ansible ANSIBLE_NOCOLOR=1
export ANSIBLE_LOCAL_TEMP=$tyo/ansible/tmp ANSIBLE_LOCALHOST_WARNING=0
export ANSIBLE_INVENTORY_UNPARSED_WARNING=0

ansible-playbook --syntax-check kirjaus.yml > /dev/null && echo "syntaksi ok"
for ajo in 1 2 3; do
    ansible-playbook kirjaus.yml \
        -e ansible_python_interpreter="$(command -v python3)" > /dev/null
    echo "ajon $ajo jälkeen: huono $(wc -l < "$KOHDE.huono") riviä," \
        "hyvä $(wc -l < "$KOHDE.hyva") rivi"
done
