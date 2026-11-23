#!/usr/bin/env bash
# Tiedoston generointi here-dokumentilla: muuttujat laajennetaan, mutta
# lainatussa versiossa teksti säilyy sellaisenaan.
set -euo pipefail

palvelu='laskutus'
portti=8443
tyontekijat=4

# @alku laajentuva
cat > "$palvelu.conf" <<EOF_CONF
# Generoitu: älä muokkaa käsin
[palvelu]
nimi = $palvelu
portti = $portti
tyontekijat = $(( tyontekijat * 2 ))
EOF_CONF
cat "$palvelu.conf"
# @loppu laajentuva

# @alku kirjaimellinen
cat > tarkistus.sh <<'EOF_SKRIPTI'
#!/usr/bin/env bash
echo "kotihakemisto on $HOME"
EOF_SKRIPTI
grep -c 'HOME' tarkistus.sh
# @loppu kirjaimellinen

# @alku merkkijono
tr '[:lower:]' '[:upper:]' <<< "here-merkkijono: $palvelu"
# @loppu merkkijono
