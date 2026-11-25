# Dev Containers -määrittely

*Development Containers* on avoin määrittely (containers.dev), jonka
Microsoft aloitti VS Codea varten ja jota nykyään tukevat myös GitHub
Codespaces, JetBrainsin kehitysympäristöt, DevPod ja määrittelyn oma
komentorivityökalu. Määrittelyn ydin on yksi tiedosto,
`devcontainer.json`. Se vastaa kolmeen kysymykseen: mistä kontti
tehdään, mitä sille tehdään käynnistyksen yhteydessä ja miten editori
siihen liittyy.

Työkalut etsivät tiedostoa projektin juuresta kolmesta paikasta:

- `.devcontainer/devcontainer.json` (tavallisin),
- `.devcontainer.json`,
- `.devcontainer/<nimi>/devcontainer.json`, kun konfiguraatioita on
  useita. Tämä tutoriaalikokoelma käyttää tätä: yksi alihakemisto
  tutoriaalia kohden.

Tiedosto on JSONia, jossa saa olla kommentteja (*JSON with Comments*).
Kommentit kannattaa käyttää: asetuksen syy on yhtä tärkeä kuin asetus.

## Pienin konfiguraatio: valmis kuva

```{.javascript tiedosto="esimerkit/muunnelmat/kuva.json"}
```

Kenttä `image` nimeää valmiin kuvan. Microsoft julkaisee yleisimmille
kielille kehityskäyttöön tehtyjä kuvia nimellä
`mcr.microsoft.com/devcontainers/<kieli>`; niissä on valmiina
tavallinen käyttäjä `vscode`, Git ja perustyökalut. Versio lukitaan
tunnisteella (`:3.12`), jotta ympäristö ei vaihdu itsestään.

Kontin lähteitä on kolme, ja niistä valitaan yksi:

| Kenttä | Lähde | Milloin |
|---------------------|--------------------------|--------------------------------|
| `image` | valmis kuva | kielen vakiotyökalut riittävät |
| `build.dockerfile` | oma Dockerfile | tarvitaan omia paketteja tai versioita |
| `dockerComposeFile` | Compose-tiedosto | kehitys tarvitsee rinnalle palveluita, esimerkiksi tietokannan |

Kohdassa `build` annetaan Dockerfilen polku (`dockerfile`),
rakennushakemisto (`context`) ja rakennusargumentit (`args`). Polut
ovat suhteessa `devcontainer.json`-tiedoston hakemistoon.

## Ominaisuudet (features)

*Ominaisuus* on valmis asennuspala, joka lisätään kuvan päälle:
kieli, komentorivityökalu tai vaikkapa Docker kontin sisään. Ominaisuudet
jaetaan konttirekistereissä samaan tapaan kuin kuvat, ja niille annetaan
valitsimia.

```{.javascript tiedosto="esimerkit/muunnelmat/ominaisuudet.json"}
```

Ominaisuuksilla saa työkalut ilman omaa Dockerfilea, ja sama pala toimii
eri peruskuvien päällä. Hinta on, että asennus tapahtuu työkalun
(VS Code, Codespaces, komentorivityökalu) rakentaessa kuvaa: pelkkä
`docker build` ei ominaisuuksia tunne. Lukitse ominaisuudenkin versio
(`:1` on pääversio), ja käytä vain luotettavien julkaisijoiden
ominaisuuksia, koska asennuskoodi ajetaan pääkäyttäjänä.

Sama tiedosto näyttää myös portit: `forwardPorts` tuo kontin portin
omalle koneelle, joten kontissa käynnistetty kehityspalvelin aukeaa
selaimessa osoitteessa `localhost:8000`.

## Elinkaarikomennot

Kontin luomisen ja käynnistämisen eri vaiheisiin voi liittää komentoja:

| Kenttä | Ajetaan | Tyypillinen käyttö |
|------------------------|-------------------------------|---------------------------|
| `initializeCommand` | isäntäkoneella ennen rakennusta | harvoin tarpeen |
| `onCreateCommand` | kerran, kun kontti luodaan | hitaat kertatyöt |
| `updateContentCommand` | kun lähdekoodi päivittyy | riippuvuuksien asennus |
| `postCreateCommand` | kerran, kun käyttäjä on liitetty | projektin valmistelu |
| `postStartCommand` | joka käynnistyksellä | taustapalvelun käynnistys |
| `postAttachCommand` | aina, kun editori liittyy | tilan näyttäminen |

Komento on merkkijono (ajetaan kuoressa), taulukko (ohjelma
argumentteineen ilman kuorta) tai olio, jonka komennot ajetaan
rinnakkain. Dockerfileen kuuluu se, mikä on sama kaikille ja muuttuu
harvoin (työkalut); elinkaarikomentoihin se, mikä riippuu lähdekoodista
(riippuvuuksien asennus projektin tiedostojen mukaan).

## Liitokset, ympäristö ja käyttäjä

```{.javascript tiedosto="esimerkit/muunnelmat/liitokset.json"}
```

- **Lähdekoodi** liitetään konttiin automaattisesti hakemistoon
  `/workspaces/<kansion nimi>`. Jos projekti on Git-repositorion
  alihakemistossa, työkalut liittävät koko repositorion ja avaavat
  alihakemiston. Kenttä `workspaceFolder` vaihtaa avattavan hakemiston;
  tämän kokoelman konfiguraatiot avaavat sillä tutoriaalin
  esimerkkihakemiston.
- **`mounts`** liittää muita hakemistoja tai nimettyjä taltioita.
  Taltio säilyy, vaikka kontti rakennetaan uudelleen, joten se sopii
  välimuisteille.
- **`containerEnv`** asettaa ympäristömuuttujat koko kontille,
  **`remoteEnv`** vain editorin käynnistämille prosesseille.
- **`remoteUser`** on käyttäjä, jona editori ja päätteet toimivat.
  Kehityskuvissa se on tavallinen käyttäjä `vscode`, jolla on `sudo`.
- **`runArgs`** välittää valitsimia suoraan `docker run` -komennolle.
  Se on varaventtiili: mitä enemmän valitsimia, sitä vähemmän
  konfiguraatio toimii muualla kuin paikallisessa Dockerissa.
- **`hostRequirements`** kertoo Codespacesille, kuinka iso kone
  tarvitaan.

Merkkijonoissa voi käyttää muuttujia:

| Muuttuja | Arvo |
|--------------------------------------|--------------------------------|
| `${localWorkspaceFolder}` | projektin polku omalla koneella |
| `${localWorkspaceFolderBasename}` | projektikansion nimi |
| `${containerWorkspaceFolder}` | projektin polku kontissa |
| `${localEnv:NIMI}` | ympäristömuuttuja omalta koneelta |
| `${containerEnv:NIMI}` | ympäristömuuttuja kontista |

## Editorin asetukset

Kohta `customizations` on työkalukohtainen. VS Codelle siinä luetellaan
laajennukset, jotka asennetaan konttiin, ja asetukset, jotka ovat
voimassa vain tässä projektissa. Näin kielituki, muotoilija ja testien
ajo toimivat kaikilla samoin ilman, että kukaan säätää editoriaan käsin.
Luvun 4 projektin konfiguraatiossa on esimerkki.

## Työkalut: sama tiedosto, kolme käyttötapaa

**VS Code** lukee tiedoston, rakentaa kuvan paikallisella Dockerilla,
käynnistää kontin ja asentaa sen sisään palvelinosansa. Editorin
käyttöliittymä pyörii omalla koneella, mutta tiedostot, pääte ja
laajennukset toimivat kontissa. Komento *Dev Containers: Rebuild
Container* rakentaa kontin uudelleen, kun konfiguraatio muuttuu, ja
*Add Dev Container Configuration Files* luo aloituspohjan valmiista
malleista.

**Codespaces** tekee saman GitHubin virtuaalikoneessa ja avaa editorin
selaimeen tai paikalliseen VS Codeen. Ympäristön koko valitaan
luotaessa, ja organisaatio voi rakentaa kuvat etukäteen (*prebuild*),
jolloin ympäristö aukeaa sekunneissa.

**Komentorivityökalu** `devcontainer` (npm-paketti `@devcontainers/cli`)
on määrittelyn viitetoteutus. Sillä sama ympäristö saadaan käyttöön
ilman editoria, tärkeimpänä CI:ssä:

```text
devcontainer up --workspace-folder .            # rakentaa ja käynnistää
devcontainer exec --workspace-folder . make testaa
devcontainer read-configuration --workspace-folder .
devcontainer build --workspace-folder . --image-name kesto-kehitys
```

Valitsin `--config` valitsee konfiguraation, kun niitä on useita.
Komennot on kokeiltu luvun 4 projektilla työkalun versiolla 0.91.0.
GitHub Actionsiin on valmis toiminto `devcontainers/ci`, joka ajaa
CI-työn kehityskontissa.

## Tarkistin

Tiedostossa on helppo tehdä virhe, joka ei näy heti: väärin kirjoitettu
kenttä jää huomaamatta, ja kontti käynnistyy ilman sitä. Editori
varoittaa osasta virheistä JSON-skeeman avulla. Tämän tutoriaalin
esimerkeissä on oma pieni tarkistin, joka tuntee yleisimmät kentät:

```{.python tiedosto="esimerkit/devkontti.py" osa="tarkista"}
```

Kolme virheellistä tiedostoa näyttävät tavallisimmat virheet:

```{.javascript tiedosto="esimerkit/muunnelmat/virhe-nimi.json"}
```

```{.javascript tiedosto="esimerkit/muunnelmat/virhe-tyypit.json"}
```

Tarkistin ajetaan kaikille esimerkkitiedostoille. Kelvolliseen
tiedostoon se voi lisätä huomion asetuksesta, joka vaatii perustelun;
niihin palataan luvussa 5.

```{.tuloste tiedosto="esimerkit/devkontti.odotettu"}
```

## Käytännössä

- **Aloita valmiista kuvasta.** Oma Dockerfile tarvitaan vasta, kun
  valmis kuva ja ominaisuudet eivät riitä. Vähemmän omaa koodia on
  vähemmän ylläpidettävää.
- **Lukitse versiot.** Kuvan tunniste, ominaisuuden versio ja
  työkalujen versiot Dockerfilessa. Lukitsematon ympäristö on eri
  ensi kuussa kuin tänään, ja juuri sen estämiseksi ympäristö kuvattiin.
- **Pidä konfiguraatio siirrettävänä.** `runArgs`, isäntäkoneen polut
  ja `initializeCommand` sitovat konfiguraation yhteen koneeseen.
  Codespaces ja CI eivät välttämättä tue niitä.
- **Kommentoi syyt.** ”Miksi tämä portti?” ja ”miksi tämä oikeus?”
  kuuluvat tiedostoon, eivät kenenkään muistiin.
- **Tiedosto versionhallintaan.** Ympäristön muutos katselmoidaan kuten
  koodin muutos, ja vanha haara saa vanhan ympäristönsä.

## Itsearviointi

- Osaat kertoa, mistä kolmesta lähteestä kehityskontti voidaan tehdä
  ja milloin kutakin käytetään.
- Osaat lukea `devcontainer.json`-tiedoston ja selittää sen kentät:
  kuva, ominaisuudet, elinkaarikomennot, liitokset, portit ja käyttäjä.
- Osaat valita, kuuluuko asennus Dockerfileen vai
  elinkaarikomentoon.
- Osaat kertoa, miten VS Code, Codespaces ja komentorivityökalu
  käyttävät samaa tiedostoa.
