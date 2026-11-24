#!/usr/bin/env bash
# Tiedostokohtaiset säännöt: .gitattributes.
set -euo pipefail
# @alku vakiot
# Esimerkkien vakioympäristö: ei käyttäjän omia asetuksia, kiinteä
# tekijä ja kello, joten commit-tunnisteet ovat joka ajolla samat.
export LC_ALL=C.UTF-8 GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1
export GIT_AUTHOR_NAME="Aino Kehittäjä" GIT_AUTHOR_EMAIL=aino@example.fi
export GIT_COMMITTER_NAME=$GIT_AUTHOR_NAME
export GIT_COMMITTER_EMAIL=$GIT_AUTHOR_EMAIL
kello=1767261600              # 1.1.2026 klo 12.00 Suomen aikaa
aika() {                      # kello etenee minuutin
    kello=$((kello + 60))
    export GIT_AUTHOR_DATE="$kello +0200" GIT_COMMITTER_DATE="$kello +0200"
}
tallenna() { aika; git commit -q "$@"; }   # commit, kello etenee
aika
# @loppu vakiot

git init -q -b main laskuri
cd laskuri

# @alku attribuutit
cat > .gitattributes <<'ATTR'
# Rivinvaihdot normalisoidaan LF:ksi kaikilla alustoilla.
*           text=auto eol=lf
*.bat       text eol=crlf
*.png       binary
# Lukitustiedostoja ei yhdistetä rivi riviltä eikä näytetä diffissä.
package-lock.json  -diff merge=binary
# Ei mukaan julkaisuarkistoon (git archive).
/testit/    export-ignore
ATTR
git check-attr text eol diff -- kuva.png aja.bat main.py
# @loppu attribuutit
# @alku crlf
mkdir testit
printf 'print("hei")\r\n' > main.py      # Windows-rivinvaihto
printf 'assert True\n' > testit/testi.py
git add . 2> /dev/null && tallenna -m "Ohjelma ja testit"
git ls-files --eol main.py | awk '{ print $1, $2, $NF }'
git archive HEAD | tar -t
# @loppu crlf
