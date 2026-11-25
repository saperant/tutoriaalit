# Monipalvelusovellus Composella

Docker Compose kuvaa usean kontin sovelluksen yhdessä YAML-tiedostossa:
palvelut, niiden kuvat, verkot, volyymit, ympäristömuuttujat ja
riippuvuudet. Yksi komento käynnistää koko sovelluksen. Compose sopii
kehitykseen, testeihin ja yhden koneen tuotantoon; usean koneen
klustereissa sen paikan ottaa Kubernetes.

## Käyntilaskuri Composella

Sovelluksen molemmat palvelut käyttävät samaa kuvaa. Yhteinen osa
kirjoitetaan kerran *laajennuskenttään* (`x-`-alkuiset avaimet Compose
ohittaa) ja liitetään palveluihin YAML-ankkurilla:

```{.yaml tiedosto="esimerkit/compose.yaml" osa="kuva"}
```

Palvelut:

```{.yaml tiedosto="esimerkit/compose.yaml" osa="palvelut"}
```

- **`build` ja `image`.** Compose rakentaa kuvan ja antaa sille nimen.
  Kun molemmilla palveluilla on sama nimi, kuva rakennetaan kerran.
- **Verkko ja nimet.** Compose luo sovellukselle oman verkon, jossa
  palvelut löytävät toisensa nimellä: api kutsuu osoitetta
  `http://laskuri:8080`. Laskurin porttia ei julkaista lainkaan, joten
  siihen ei pääse verkon ulkopuolelta. Verkko on isäntäkoneen
  Linux-silta, johon jokainen kontti liittyy virtuaalisella
  Ethernet-parilla; sillan toiminta on taidossa *Tietoverkot*.
- **Portin julkaisu vain paikallisesti.** `127.0.0.1:…:8080` avaa
  portin vain koneen omaan liitäntään. Pelkkä `8080:8080` avaisi sen
  kaikille verkoille, ja Docker ohittaa siinä isäntäkoneen palomuurin
  säännöt.
- **Ympäristömuuttujien interpolointi.** `${API_PORTTI:-8080}` tulee
  komennon ympäristöstä tai tiedostosta `.env`, oletuksena 8080. Näin
  testit voivat käyttää vapaata porttia.
- **`depends_on` ja terveys.** Api käynnistyy vasta, kun laskurin
  `HEALTHCHECK` (luku 3) raportoi terveen tilan. Pelkkä `depends_on`
  ilman ehtoa odottaisi vain käynnistymistä, ei valmiutta.
- **Volyymi.** Nimetty volyymi `laskuridata` säilyy, vaikka kontti
  poistetaan ja luodaan uudelleen. `docker compose down -v` poistaa sen.
- **`read_only`.** Kontin juuritiedostojärjestelmä on vain luku
  -tilassa; kirjoittaa voi vain volyymiin. Murtautuja ei voi muuttaa
  ohjelmaa, ja vahingossa kontin sisään kirjoitettu data huomataan heti.
- **`restart: unless-stopped`.** Kaatunut kontti käynnistetään
  uudelleen, mutta käsin pysäytetty ei.

Compose-tiedosto tarkistetaan Compose-määrittelyn skeemaa vasten ennen
ajoa (`check-jsonschema --builtin-schema vendor.compose-spec`) ja
Dockerin omalla tarkistuksella (`docker compose config`), joka myös
näyttää lopullisen, interpoloidun asetuksen.

## Sovellus ajossa

Esimerkkien testi käynnistää sovelluksen, kutsuu sitä, käynnistää
laskurin uudelleen ja pysäyttää apin:

```{.bash tiedosto="esimerkit/testit/docker.sh" osa="compose"}
```

Koko testin tuloste, myös luvun 3 ja 4 kuvat ja luvun 9 Helm-kaavio:

```{.tuloste tiedosto="esimerkit/testit/docker.odotettu"}
```

- `up -d --wait` palaa vasta, kun kaikki palvelut ovat terveitä. Ilman
  sitä ensimmäinen kutsu voisi osua palveluun, joka ei vielä kuuntele.
- Laskurin uudelleenkäynnistyksen jälkeen arvo on 3: tila oli
  volyymissa eikä kontissa.
- Apin pysäytys lähettää SIGTERMin, ja viimeinen lokirivi näyttää,
  että palvelu sammui hallitusti.

## Kehitys ja tuotanto

Composella voi kuvata eroja ympäristöjen välillä ilman, että
perustiedosto muuttuu:

```text
docker compose -f compose.yaml -f compose.kehitys.yaml up
```

Jälkimmäinen tiedosto ylikirjoittaa ja täydentää ensimmäistä,
esimerkiksi liittää lähdekoodin volyymiksi ja avaa debug-portin.
*Profiilit* (`profiles: [työkalut]`) käynnistävät valinnaiset palvelut,
kuten tietokannan hallintatyökalun, vain pyydettäessä. Compose Watch
(`docker compose watch`) synkronoi muuttuneet tiedostot konttiin ja
rakentaa kuvan uudelleen tarvittaessa.

## Käytännössä

- **Compose on sovelluksen paikallinen totuus.** Uusi kehittäjä saa
  koko sovelluksen ajoon yhdellä komennolla, ja integraatiotestit
  ajavat saman kokonaisuuden. Testikohtaiset, koodista käynnistettävät
  kontit ovat taidossa *Integraatiotestaus ja Testcontainers*.
- **Terveystarkistukset ja `--wait`.** Kilpailutilanteet käynnistyksessä
  ovat tavallisin syy epävakaisiin integraatiotesteihin.
- **Julkaise vain tarpeelliset portit ja vain paikallisesti.**
  Palvelujen välinen liikenne kulkee Composen verkossa.
- **Ei salaisuuksia Compose-tiedostoon.** Arvot `.env`-tiedostosta,
  joka ei ole versionhallinnassa, tai Composen `secrets`-määrittelyllä
  tiedostosta.
- **Projektin nimi erottaa rinnakkaiset ajot.** `-p` antaa verkoille,
  volyymeille ja konteille oman etuliitteen, joten CI voi ajaa useita
  testejä samalla koneella.

## Itsearviointi

- Osaat kuvata usean palvelun sovelluksen Compose-tiedostona: kuvat,
  verkko, volyymit, ympäristömuuttujat ja riippuvuudet.
- Osaat käyttää terveystarkistuksia niin, että palvelut käynnistyvät
  oikeassa järjestyksessä ja testit eivät kilpaile käynnistyksen
  kanssa.
- Osaat rajata portit ja kirjoitusoikeudet niin, että palvelu altistuu
  mahdollisimman vähän.
- Osaat erottaa kehitys- ja tuotantoasetukset ilman, että
  perustiedostoa kopioidaan.
