# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Automatisoi muistettava.** Koukku, CI-tarkistus ja haarasuojaus
   eivät unohda eivätkä väsy.
2. **Koukku auttaa, CI päättää.** Kehittäjän koneen tarkistukset ovat
   nopeaa palautetta; ohittamaton portti on CI:ssä ja koodialustalla.
3. **Salaisuus ei kuulu koodiin, kuvaan eikä asiakkaalle.** Ja kun se
   vuotaa: kumoa ensin, siivoa sitten.
4. **Lyhytikäinen tunnus on paras tunnus.** OIDC ja dynaamiset tunnukset
   pysyvien avainten tilalle.
5. **Lukitse, tarkista, päivitä hallitusti.** Lukitustiedosto
   tiivisteineen, asennus sen mukaan, päivitykset pull requesteina.
6. **Tiedä, mitä toimitat.** SBOM jokaisesta julkaisusta ja jatkuva
   vertailu haavoittuvuustietoon.
7. **Allekirjoita ja tarkista.** Allekirjoitus, jota kukaan ei tarkista,
   ei suojaa mitään. Luotettu avain eri reittiä kuin julkaisu.
8. **CI on etuoikeutettu järjestelmä.** Vähimmät oikeudet, kiinnitetyt
   toiminnot, ei vierasta koodia salaisuuksien kanssa.
9. **Kaksi henkilöä kriittisiin muutoksiin.** Myös ylläpitäjille, myös
   kiireessä.
10. **Turvallisen tavan on oltava helppo.** Muuten kiireessä valitaan
    helppo tapa.

## Työkalut tehtävittäin

| Tehtävä | Työkaluja |
|---------|-----------|
| salaisuusskannaus | gitleaks, trufflehog, detect-secrets, koodialustan push protection |
| salaisuusvarasto | HashiCorp Vault, OpenBao, pilvien KMS ja Secrets Manager, SOPS |
| koukkujen jakelu | pre-commit, lefthook |
| riippuvuuspäivitykset | Dependabot, Renovate |
| SBOM | Syft, cdxgen, CycloneDX-liitännäiset |
| haavoittuvuusskannaus | osv-scanner, pip-audit, npm audit, Grype, Trivy |
| SAST | ruff/Bandit, Semgrep, CodeQL, SpotBugs + FindSecBugs, gosec |
| DAST | OWASP ZAP |
| työnkulkujen tarkistus | actionlint, zizmor |
| allekirjoitukset | ssh-keygen -Y, Sigstore (cosign, gitsign), in-toto |
| projektin arvio | OpenSSF Scorecard |

## Jatkotaidot taitopuussa

- **Web-sovellusten tietoturva**: sovelluksen hyökkäykset ja
  torjunnat, joita DAST etsii ja katselmoija arvioi.
- **Palveluarkkitehtuurin tietoturva**: salaisuuksien hallinta
  tuotannossa, työkuormien identiteetit ja nollaluottamus.
- **Kontit ja pilvi**: kuvien rakentaminen, CI/CD-putket ja
  infrastruktuuri koodina, joihin tämän tutoriaalin käytännöt
  sovelletaan.
- **Haavoittuvuudet**: fuzzaus ja muistivirheiden analyysi.

## Lähteet

### Viitekehykset ja ohjeet

- OWASP SAMM (Software Assurance Maturity Model), versio 2:
  <https://owaspsamm.org/>.
- NIST SP 800-218, *Secure Software Development Framework (SSDF)*,
  versio 1.1 (2022).
- OWASP ASVS (Application Security Verification Standard), versio 5.0
  (2025): <https://owasp.org/www-project-application-security-verification-standard/>.
- OWASP Cheat Sheet Series (CC BY-SA 4.0), erityisesti *Secrets
  Management*, *CI/CD Security* ja *Software Supply Chain Security*:
  <https://cheatsheetseries.owasp.org/>.
- OWASP Top 10 CI/CD Security Risks:
  <https://owasp.org/www-project-top-10-ci-cd-security-risks/>.
- SLSA (Supply-chain Levels for Software Artifacts), versio 1.0:
  <https://slsa.dev/>.
- CycloneDX (ECMA-424): <https://cyclonedx.org/>; SPDX (ISO/IEC
  5962): <https://spdx.dev/>; Package URL:
  <https://github.com/package-url/purl-spec>.
- OSV-skeema ja -tietokanta: <https://osv.dev/>.
- Reproducible Builds: <https://reproducible-builds.org/>.
- Sigstore: <https://www.sigstore.dev/>.

### Alustojen dokumentaatio

- GitHub Docs: *Security hardening for GitHub Actions*,
  *About security hardening with OpenID Connect*, *About protected
  branches*, *About code owners*.
- Git: `git help config` (kohdat `gpg.format` ja
  `gpg.ssh.allowedSignersFile`) ja `ssh-keygen(1)` (kohta
  `-Y sign`).
- PyPI: *Trusted Publishers*; pip: *Secure installs*
  (`--require-hashes`).
- Python: PEP 503 (nimien normalisointi) ja PEP 706
  (tar-arkistojen purkusuodattimet).

### Säädökset

- Kyberkestävyyssäädös (EU) 2024/2847, liite I (haavoittuvuuksien
  käsittely ja SBOM): <https://eur-lex.europa.eu/>.
- Tietosuoja-asetus (EU) 2016/679, artiklat 4(5) (pseudonymisointi) ja
  25 (sisäänrakennettu tietosuoja).

### Tapaukset

- Alex Birsan: *Dependency Confusion: How I Hacked Into Apple,
  Microsoft and Dozens of Other Companies* (2021).
- CVE-2024-3094 (xz-utils) ja CVE-2025-30066 (tj-actions/changed-files).

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkiohjelmat saa
vapaasti käyttää omissa ohjelmissa.
