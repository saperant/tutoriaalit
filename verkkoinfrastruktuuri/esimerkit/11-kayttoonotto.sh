#!/usr/bin/env bash
# Verkko rakennetaan kuvauksesta: generaattori tarkistaa kuvauksen ja
# tuottaa komennot, jotka ajetaan sellaisenaan. Lopuksi kuvaus
# varmennetaan testeillä.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"
KUVAUS=$(dirname "$0")/11-verkko

# @alku kayttoonotto
python3 "$KUVAUS/main.py" > "$LABRA_HAK/suunnitelma.sh"
echo "suunnitelmassa $(wc -l < "$LABRA_HAK/suunnitelma.sh") komentoa"
# shellcheck source=/dev/null # generoitu tiedosto
source "$LABRA_HAK/suunnitelma.sh"
# @loppu kayttoonotto

# @alku varmennus
# Hyväksymistestit: kuvauksen lupaamat yhteydet toimivat.
tavoittaa tyoasema 10.30.20.10
tavoittaa tiedosto 10.30.10.20
# @loppu varmennus

# @alku virheellinen
# Virheellinen muutos jää kiinni ennen käyttöönottoa.
sed -e 's/"10.30.20.0\/24"/"10.30.0.0\/16"/' \
    -e 's/"10.30.10.20"/"10.30.10.10"/' \
    "$KUVAUS/verkko.toml" > "$LABRA_HAK/muutos.toml"
# Virheet tulevat virhetulosteeseen; ohjataan ne näkyviin.
{ python3 "$KUVAUS/main.py" "$LABRA_HAK/muutos.toml" > /dev/null; } 2>&1 ||
    echo "muutos hylättiin"
# @loppu virheellinen
