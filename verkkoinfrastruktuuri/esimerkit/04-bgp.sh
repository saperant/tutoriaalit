#!/usr/bin/env bash
# eBGP kahden autonomisen järjestelmän välillä. Asiakas (AS 65001)
# ilmoittaa verkkonsa operaattorille (AS 65002). Operaattori hyväksyy
# vain sovitut etuliitteet: suodatus estää virheellisen oletusreitin.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

solmu asiakas
solmu operaattori
linkki asiakas op operaattori as
ns asiakas ip addr add 198.51.100.1/30 dev op
ns operaattori ip addr add 198.51.100.2/30 dev as

# @alku asiakas
cat > "$LABRA_HAK/asiakas.conf" <<'KONF'
router id 198.51.100.1;
protocol device {}
# Ilmoitettavat verkot. Oletusreitti on tässä virheellisesti mukana.
protocol static ilmoitukset {
    ipv4;
    route 203.0.113.0/24 blackhole;
    route 0.0.0.0/0 blackhole;
}
protocol bgp operaattori {
    local 198.51.100.1 as 65001;
    neighbor 198.51.100.2 as 65002;
    ipv4 { import none; export where proto = "ilmoitukset"; };
}
KONF
# @loppu asiakas

# @alku operaattori
cat > "$LABRA_HAK/operaattori.conf" <<'KONF'
router id 198.51.100.2;
protocol device {}
protocol kernel { ipv4 { export all; }; }
# Asiakkaalta hyväksytään vain sille osoitettu lohko.
define ASIAKKAAN_VERKOT = [ 203.0.113.0/24 ];
protocol bgp asiakas {
    local 198.51.100.2 as 65002;
    neighbor 198.51.100.1 as 65001;
    ipv4 {
        import keep filtered on;    # hylätyt näkyvät vianetsinnässä
        import where net ~ ASIAKKAAN_VERKOT;
        export none;
    };
}
KONF
# @loppu operaattori

for s in asiakas operaattori; do
    ns "$s" bird -c "$LABRA_HAK/$s.conf" -s "$LABRA_HAK/$s.ctl" \
        -P "$LABRA_HAK/$s.pid"
done
opittu() {
    [[ -n $(ns operaattori ip route show 203.0.113.0/24 proto bird) ]]
}
odota 60 opittu
# @alku tulos
echo "Operaattorin BGP:stä oppimat reitit:"
ns operaattori ip route show proto bird | awk '{print $1, "via", $3}'
echo "Hylätyt (suodatetut) reitit:"
ns operaattori birdc -s "$LABRA_HAK/operaattori.ctl" \
    show route filtered protocol asiakas | awk '$1 ~ /\// {print $1}'
# @loppu tulos
