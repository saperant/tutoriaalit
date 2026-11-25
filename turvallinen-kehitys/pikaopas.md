---
title: Tietoturva kehitystyössä
subtitle: Pikaopas · salaisuudet, toimitusketju ja turvallinen CI
---

# Kerrokset

| Missä | Tarkistus | Rooli |
|-------|-----------|-------|
| editori | linteri tietoturvasäännöin | välitön palaute |
| commit-koukku | salaisuudet, linteri | nopea palaute, ohitettavissa |
| CI | SAST, salaisuudet, riippuvuudet, työnkulut | portti, ei ohitettavissa |
| koodialusta | push protection, haarasuojaus, koodinomistajat | viimeinen varmistus |
| julkaisu | SBOM, allekirjoitus, alkuperätieto | todisteet käyttäjälle |
| tuotanto | haavoittuvuusvertailu jatkuvasti | uudet tiedotteet |

# Salaisuudet

- Ei koodiin, ei kuvaan (`COPY .env`, `ARG`), ei asiakkaalle.
- Säilytys: ympäristö < varasto (Vault, KMS) < dynaaminen tunnus.
- Kierto: uusi avain jakoon, allekirjoitus uudella, vanha pois.
- Vuoto: **kumoa** → selvitä käyttö → korvaa → siivoa historia → opi.
- Historiaan jää: `refs/original`, reflog, kloonit, forkit, välimuistit.

```{.bash tiedosto="esimerkit/03-koukku.sh" osa="koukku"}
```

# Kehitysympäristö

| Vältä | Tilalle |
|-------|---------|
| `image: x:latest` | `image: x@sha256:...` |
| `--privileged` | `--cap-add=` vain tarvittava |
| Dockerin soketti | rootless / DinD |
| salaisuus `containerEnv` | `${localEnv:NIMI}` |
| root | `remoteUser` |
| tuotantodata | synteettinen; HMAC-pseudonyymi, yleistys, k ≥ 2 |

# Riippuvuudet

| Uhka | Torjunta |
|------|----------|
| uusi kaapattu versio | lukitus, viive, katselmoitu päivitys |
| muokattu paketti | tiivisteet (`--require-hashes`, `npm ci`) |
| kirjoitusvirhe | nimen tarkistus, arvio ennen lisäystä |
| riippuvuussekaannus | yksi lähde, nimiavaruus, lähteen kiinnitys |
| asennusskripti | eristetty asennus, `--ignore-scripts` |

SBOM: CycloneDX / SPDX, pURL `pkg:pypi/nimi@versio`, toistettava.
Haavoittuvuudet: OSV, versiovertailu osina, VEX perusteluille.

# Allekirjoitukset

```{.bash tiedosto="esimerkit/07-allekirjoitus.sh" osa="asetukset"}
```

```{.bash tiedosto="esimerkit/07-julkaisu.sh" osa="allekirjoita"}
```

`git log --format='%G? %s'`: G hyvä, U ei luotettu, N ei
allekirjoitusta, B virheellinen.

Toistettava tar: `--sort=name --mtime=... --owner=0 --group=0
--numeric-owner` ja `gzip -n`; aika `SOURCE_DATE_EPOCH`.

SLSA Build L1 alkuperätieto · L2 isännöity, allekirjoitettu · L3
eristetty, väärentämätön.

# CI

| Virhe | Korjaus |
|-------|---------|
| `pull_request_target` + PR:n koodi | `pull_request`, ei salaisuuksia vieraalle koodille |
| `${{ github.event... }}` `run`-lohkossa | `env:`-muuttuja, `"$MUUTTUJA"` |
| `uses: x@v4` | `uses: x@<40 merkin tiiviste>` |
| ei `permissions` | `contents: read`, lisäykset työkohtaisesti |
| pysyvä pilviavain | OIDC: `iss`, `aud` ja tarkka `sub` |
| julkaisuavain kehittäjällä | julkaisu CI:stä, trusted publishing |

# Katselmointi

- Haarasuojaus: PR, hyväksyntä ei tekijältä, vanhenee uusista
  commiteista, pakolliset tarkistukset, ei ohituksia.
- `CODEOWNERS`: viimeinen osuma voittaa; yksi rivin omistajista riittää;
  suojaa myös työnkulut, riippuvuustiedostot ja `CODEOWNERS` itse.
- Katsoja: luottamusrajat, valtuutus, virhepolut, mitä puuttuu.
- Poikkeukset: `# noqa: SÄÄNTÖ  syy`, perustaso + vanhenemispäivä.

# Vastuulauseke

Aja skannereita ja tarkistimia vain omiin repositorioihin ja
järjestelmiin tai omistajan luvalla.
