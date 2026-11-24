#!/usr/bin/env bash
# Commit-koukku, joka estää salaisuuden päätymisen versionhallintaan.
# Ajetaan tilapäisessä repositoriossa.
set -euo pipefail
# Käyttäjän omat git-asetukset (esim. commit.gpgsign) eivät vaikuta.
export GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1

git init -q -b main repo
cd repo
git config user.name "Aino Kehittäjä"
git config user.email "aino@example.fi"

# @alku koukku
cat > .git/hooks/pre-commit <<'KOUKKU'
#!/usr/bin/env bash
# Tarkistaa vain commitoitavat muutokset (git diff --cached).
set -euo pipefail
mallit='(AKIA|ASIA)[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY'
mallit+='|(password|secret|token|api_?key)[[:space:]]*[:=][[:space:]]*'
mallit+="[\"'][^\"']{8,}"
if git diff --cached -U0 | grep '^+' | grep -v 'salaisuus-sallittu:' \
        | grep -Eiq "$mallit"; then
    echo "pre-commit: muutoksessa näyttää olevan salaisuus" >&2
    echo "pre-commit: siirrä se ympäristöön tai salaisuusvarastoon" >&2
    exit 1
fi
KOUKKU
chmod +x .git/hooks/pre-commit
# @loppu koukku

# @alku kokeilu
yrita() {
    git add -A
    if git commit -q -m "$1" 2>/dev/null; then
        echo "hyväksytty: $1"
    else
        echo "estetty:    $1"
        git reset -q
    fi
}

printf 'osoite = "https://api.example.fi"\n' > asetukset.py
yrita "Lisää API-osoite"

printf 'api_key = "sk-9f3b2c71e04d"\n' >> asetukset.py
yrita "Lisää API-avain"

git checkout -q -- asetukset.py
printf 'api_key = os.environ["API_KEY"]\n' >> asetukset.py
yrita "Lue API-avain ympäristöstä"

printf 'aws = "AKIAIOSFODNN7EXAMPLE"\n' > vuoto.py
git add vuoto.py
git commit -q --no-verify -m "Ohitettu koukku" \
    && echo "hyväksytty: Ohitettu koukku (--no-verify)"
# @loppu kokeilu
git log --format='%s' | sed 's/^/historia: /'
