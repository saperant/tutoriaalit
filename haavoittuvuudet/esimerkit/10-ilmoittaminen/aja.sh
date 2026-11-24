#!/usr/bin/env bash
# Vakavuuden arviointi CVSS:llä ja security.txt-tiedoston tarkistus.
source ./yhteinen.sh

otsikko "CVSS 3.1 -peruspisteet"
# @alku cvss
python3 cvss.py < vektorit.txt
# @loppu cvss
otsikko "security.txt"
# @alku security
python3 tarkista_security.py 2026-11-24 security.txt vanhentunut.txt ||
    tila $?
# @loppu security
