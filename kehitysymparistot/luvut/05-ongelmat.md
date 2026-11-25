# Yleiset ongelmat

Kehityskontti poistaa ison joukon ympäristöongelmia mutta tuo muutaman
oman. Lähes kaikki niistä johtuvat siitä, että kontti ja isäntäkone
ovat kaksi eri järjestelmää, joiden välillä jaetaan tiedostoja, verkko
ja tunnuksia.

## Tiedostojen omistaja

Linuxissa tiedoston omistaja on numero (UID), ei nimi. Lähdekoodi
liitetään konttiin sellaisenaan, joten kontin käyttäjän `vscode`
(UID 1000) pitää vastata isäntäkoneen käyttäjää. Jos numerot eroavat,
kontti ei saa kirjoittaa lähdekoodiin, tai kontissa luodut tiedostot
ovat isäntäkoneella väärän käyttäjän omistamia.

VS Code ratkaisee tämän Linuxissa itse: se muuttaa kontin käyttäjän
UID:n vastaamaan isäntäkoneen käyttäjää (asetus `updateRemoteUserUID`,
oletuksena päällä). Ohjelma `aja_kontissa.py` tekee saman yksinkertaisemmin
ajamalla kontin isäntäkoneen käyttäjän numerolla (`--user`).

Pahin virhe on ajaa konttia pääkäyttäjänä (`"remoteUser": "root"`).
Silloin kaikki kontissa luodut tiedostot, kuten käännöstuotteet ja
Gitin objektit, ovat isäntäkoneella pääkäyttäjän omistamia, ja
seuraava `git pull` kontin ulkopuolella epäonnistuu.

## Hitaat tiedostoliitokset

Linuxissa liitos on suora ja nopea. Windowsissa ja macOS:ssä Docker
toimii virtuaalikoneessa, ja isäntäkoneen hakemiston liittäminen sen
läpi on hidasta: tuhansien pienten tiedostojen käännös tai
riippuvuuksien asennus voi kestää moninkertaisesti.

- **Windows:** pidä lähdekoodi WSL 2:n tiedostojärjestelmässä, älä
  `C:`-asemalla.
- **macOS ja Windows:** komento *Dev Containers: Clone Repository in
  Container Volume* kloonaa repositorion suoraan Dockerin taltioon,
  jolloin liitosta isäntäkoneelle ei ole lainkaan.
- **Kaikki:** siirrä raskaat hakemistot, kuten `node_modules` ja
  käännöstuotteet, taltioon tai kontin omaan tiedostojärjestelmään
  (luvun 3 esimerkissä `CARGO_TARGET_DIR`).

## Välimuistit ja uudelleenrakennus

Kontin uudelleenrakennus tyhjentää kaiken, mikä ei ole lähdekoodissa
tai taltiossa: ladatut riippuvuudet, kääntäjän välimuistit ja
komentohistorian. Nimetty taltio (`mounts`, `type=volume`) säilyttää ne.
Taltio on kuitenkin jaettua tilaa, jota mikään ei siivoa, joten nimeä
se projektin mukaan ja pidä siinä vain uudelleen ladattavissa olevaa
sisältöä.

Itse kuvan rakennusta nopeuttaa Dockerin kerrosvälimuisti: Dockerfilen
käskyt ajetaan uudelleen vain muuttuneesta käskystä eteenpäin. Laita
harvoin muuttuvat ja hitaat asennukset alkuun ja usein muuttuvat
loppuun.

## Salaisuudet

Kuvaan tai `devcontainer.json`-tiedostoon ei kirjoiteta salasanoja,
tunnuksia eikä avaimia. Kuva on tiedosto, jota jaetaan, ja sen jokainen
kerros säilyy, vaikka myöhempi käsky poistaisi tiedoston.

- **Git ja SSH:** VS Code välittää konttiin isäntäkoneen Git-tunnukset
  ja SSH-agentin, joten avaimia ei kopioida.
- **Ympäristömuuttujat:** `${localEnv:NIMI}` lukee arvon isäntäkoneelta
  kontin käynnistyessä (luvun 3 esimerkki `liitokset.json`).
- **Codespaces:** salaisuudet tallennetaan GitHubin asetuksiin, ja ne
  näkyvät kontissa ympäristömuuttujina.

Salaisuuksien hallintaa laajemmin käsittelee taito *Tietoturva
kehitystyössä*.

## Verkko ja välityspalvelin

Yritysverkossa liikenne kulkee usein välityspalvelimen kautta. Kontti ei
peri isäntäkoneen asetuksia: sekä kuvan rakennus että ajettava kontti
tarvitsevat ne erikseen. Ohjelma `aja_kontissa.py` välittää asetukset
näin:

```{.python tiedosto="esimerkit/aja_kontissa.py" osa="valitys"}
```

Jos välityspalvelin purkaa TLS-yhteydet, kontin on lisäksi luotettava
sen varmenteeseen. Varmenne lisätään kuvaan Dockerfilessa
(`update-ca-certificates`); TLS-tarkistuksen kytkeminen pois ei ole
ratkaisu. Tämän kokoelman konttitestaaja tekee juuri näin, kun se
ajetaan välityspalvelimen takana.

Toinen tavallinen yllätys on `localhost`: kontissa se tarkoittaa
konttia itseään. Kontin palveluun päästään isäntäkoneelta välitetyn
portin kautta (`forwardPorts`), ja isäntäkoneen palveluun kontista
nimellä `host.docker.internal`.

## Docker kontin sisällä

Joskus kehityskontissa pitää ajaa kontteja, esimerkiksi
integraatiotestejä varten. Helpoin tapa on liittää isäntäkoneen
Docker-soketti konttiin:

```{.javascript tiedosto="esimerkit/muunnelmat/soketti.json"}
```

Tarkistin huomauttaa tiedostosta kolmesti, ja syystä: soketin kautta
kontti voi käynnistää isäntäkoneelle uuden kontin, johon on liitetty
koko isäntäkoneen levy. Soketin jakaminen antaa siis kontille
pääkäyttäjän oikeudet isäntäkoneeseen.

```{.python tiedosto="esimerkit/devkontti.py" osa="huomiot"}
```

Käytä sokettia vain, kun luotat kaikkeen kontissa ajettavaan koodiin,
riippuvuudet mukaan lukien. Vaihtoehto on ominaisuus
`docker-in-docker`, joka käynnistää konttiin oman, erillisen Dockerin;
se vaatii etuoikeutetun kontin mutta ei paljasta isäntäkoneen kontteja.
Taito *Integraatiotestaus ja Testcontainers* käyttää sokettia ja käy
läpi sen seuraukset.

Sama varovaisuus koskee valitsimia `--privileged` ja
`seccomp=unconfined`. Tässä kokoelmassa niitä käyttää muutama
tutoriaali, jonka aihe vaatii sitä (verkkonimiavaruudet, GCL-pohjainen
Maxima), ja jokaisessa syy on kirjattu.

## Käytännössä

- **Tavallinen käyttäjä, ei root.** Käytä peruskuvien käyttäjää
  `vscode` ja anna työkalun sovittaa UID.
- **Lähdekoodi lähelle Dockeria.** Windowsissa WSL 2, macOS:ssä taltio,
  jos liitos on hidas.
- **Salaisuudet tulevat ajon aikana.** Ei kuvaan, ei tiedostoon, ei
  versionhallintaan.
- **Oikeudet vain tarpeeseen.** Jokainen `runArgs`-valitsin ja jaettu
  soketti saa kommentin, joka kertoo miksi.
- **Epäile välimuistia.** Kun kontti käyttäytyy oudosti, rakenna se
  uudelleen ilman välimuistia ennen kuin etsit vikaa koodista.

## Itsearviointi

- Osaat selittää, miksi kontissa luotu tiedosto voi olla isäntäkoneella
  väärän käyttäjän omistama ja miten se vältetään.
- Osaat nopeuttaa kehityskonttia Windowsissa ja macOS:ssä.
- Osaat tuoda salaisuuden konttiin kirjoittamatta sitä kuvaan tai
  konfiguraatioon.
- Osaat kertoa, mitä oikeuksia Docker-soketin jakaminen antaa kontille.
