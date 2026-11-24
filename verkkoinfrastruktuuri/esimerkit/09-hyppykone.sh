#!/usr/bin/env bash
# Etäkäyttö hyppykoneen (bastion) kautta. Sisäverkon palvelimeen ei ole
# suoraa pääsyä; ylläpitäjä yhdistää SSH:n ProxyJumpilla hyppykoneen läpi.
# Kirjautuminen vain avaimella, ja palvelinavaimet tarkistetaan.
# shellcheck source-path=SCRIPTDIR source=labra.sh
source "$(dirname "$0")/labra.sh"

for s in yllapitaja hyppy palvelin; do solmu "$s"; done
linkki yllapitaja eth0 hyppy ulko
linkki hyppy sisa palvelin eth0
ns yllapitaja ip addr add 192.0.2.50/24 dev eth0
ns hyppy ip addr add 192.0.2.10/24 dev ulko
ns hyppy ip addr add 10.80.0.1/24 dev sisa
ns palvelin ip addr add 10.80.0.20/24 dev eth0
# Hyppykone ei reititä: sisäverkkoon pääsee vain sen SSH-palvelun kautta.
ns hyppy sysctl -qw net.ipv4.ip_forward=0

S=$LABRA_HAK
# @alku palvelimet
juuri mkdir -p /run/sshd
ssh-keygen -q -t ed25519 -N '' -f "$S/yllapitaja"
for p in hyppy palvelin; do
    ssh-keygen -q -t ed25519 -N '' -f "$S/$p-isantaavain"
    cat > "$S/$p.sshd" <<KONF
HostKey $S/$p-isantaavain
AuthorizedKeysFile $S/yllapitaja.pub
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
StrictModes no
PidFile $S/$p-sshd.pid
KONF
    # sshd käynnistetään absoluuttisella polulla (se käynnistää itsensä
    # uudelleen jokaiselle yhteydelle).
    ns "$p" "$(juuri sh -c 'command -v sshd')" -D -f "$S/$p.sshd" \
        > /dev/null 2>&1 &
done
# @loppu palvelimet
kuuntelee() { ns "$1" ss -ltn | grep -q ':22 '; }
odota 10 kuuntelee hyppy
odota 10 kuuntelee palvelin

# @alku asiakas
# Tunnetut palvelinavaimet: ensimmäisellä kerralla avain varmistetaan
# muuta kautta (tässä suoraan avaintiedostosta), ei sokeasti hyväksytä.
{
    echo "192.0.2.10 $(cut -d' ' -f1,2 "$S/hyppy-isantaavain.pub")"
    echo "10.80.0.20 $(cut -d' ' -f1,2 "$S/palvelin-isantaavain.pub")"
} > "$S/known_hosts"
cat > "$S/ssh_config" <<KONF
Host hyppy
    HostName 192.0.2.10
Host sisapalvelin
    HostName 10.80.0.20
    ProxyJump hyppy
Host *
    User root
    IdentityFile $S/yllapitaja
    IdentitiesOnly yes
    UserKnownHostsFile $S/known_hosts
    StrictHostKeyChecking yes
    BatchMode yes
KONF
# @loppu asiakas

# @alku kokeilu
ssh_() { ns yllapitaja ssh -F "$S/ssh_config" "$@"; }
echo "suoraan: $(ns yllapitaja ping -c 1 -W 1 10.80.0.20 > /dev/null 2>&1 \
    && echo ok || echo ei reittiä)"
echo "hypyn kautta: $(ssh_ sisapalvelin \
    "ip -4 -o addr show eth0 | awk '{print \$4}'")"
# @loppu kokeilu
