---
title: Kehitysympäristöt ja Dev Containers
subtitle: Pikaopas · esimerkit käyttöön · devcontainer.json · ongelmat
---

# Tutoriaalien esimerkit käyttöön

| Tapa | Näin |
|--------------|-----------------------------------------------|
| Codespaces | *Code → Codespaces → New with options*, valitse tutoriaali |
| VS Code | *Dev Containers: Reopen in Container*, valitse tutoriaali |
| Zip | pura, avaa kansio, *Reopen in Container* |
| Ilman konttia | työkalut kohdasta `build.args` |

```text
make -C <paketti> testaa            # sama kuin CI
python3 03-nimi.py | diff - 03-nimi.odotettu
make aja-01-hei                     # C ja C++
```

| Tiedosto | Merkitys |
|---------------------|--------------------------------------|
| `.odotettu` | odotettu tuloste |
| `.syote`, `.argumentit` | syöte ja komentoriviargumentit |
| `.ei-kaanny.*` | ei käänny sellaisenaan, korjattuna kyllä |
| `.kaatuu.*`, `.virhe` | kaatuu tarkoituksella; virheen rivit |

# devcontainer.json

```{.javascript tiedosto="esimerkit/muunnelmat/kuva.json"}
```

| Kenttä | Tehtävä |
|----------------------|------------------------------------------|
| `image` | valmis kuva (lukitse versio) |
| `build` | `dockerfile`, `context`, `args` |
| `features` | valmiit asennuspalat kuvan päälle |
| `postCreateCommand` | kerran kontin luonnin jälkeen |
| `postStartCommand` | joka käynnistyksellä |
| `forwardPorts` | kontin portit omalle koneelle |
| `mounts` | taltiot ja muut liitokset |
| `containerEnv` | ympäristömuuttujat kontille |
| `remoteUser` | käyttäjä, jona editori toimii |
| `workspaceFolder` | avattava hakemisto |
| `customizations` | editorin laajennukset ja asetukset |
| `runArgs` | valitsimet `docker run` -komennolle |

Paikat: `.devcontainer/devcontainer.json`, `.devcontainer.json` tai
`.devcontainer/<nimi>/devcontainer.json`. Kommentit ovat sallittuja.

# Komentorivityökalu

```text
npm install -g @devcontainers/cli
devcontainer up --workspace-folder .
devcontainer exec --workspace-folder . make testaa
devcontainer read-configuration --workspace-folder .
```

# Valinta

| Tarve | Väline |
|--------------------------|---------------------------|
| yhden kielen paketit | venv, uv, lukitustiedosto |
| työkalujen versiot | mise, asdf |
| kielet ja järjestelmäpaketit | kehityskontti |
| tiukka toistettavuus | Nix |
| oma ydin | virtuaalikone |

# Ongelmat

- **Väärä omistaja:** käyttäjä `vscode`, ei root; työkalu sovittaa
  UID:n.
- **Hidas levy:** WSL 2 tai *Clone Repository in Container Volume*.
- **Asennus katosi:** kontti on kertakäyttöinen; lisää Dockerfileen.
- **Välimuisti katoaa:** nimetty taltio (`mounts`).
- **Salaisuus:** `${localEnv:NIMI}`, ei kuvaan eikä tiedostoon.
- **Välityspalvelin:** asetukset sekä rakennukseen että ajoon;
  varmenne kuvaan.
- **localhost:** kontissa kontti itse; isäntä on
  `host.docker.internal`.
- **Docker-soketti:** antaa kontille isännän pääkäyttäjän oikeudet.
- **Outo käytös:** *Rebuild Without Cache*.
- **Aina:** ympäristö versionhallintaan, versiot lukkoon, CI samaan
  ympäristöön.
