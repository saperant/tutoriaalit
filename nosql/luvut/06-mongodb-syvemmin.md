# MongoDB: aggregaatio, skeema ja transaktiot

Tämä luku käsittelee MongoDB:n ominaisuuksia, jotka tuovat sen
lähemmäs relaatiotietokantaa: koosteet, tietokannassa valvottu skeema
ja monen dokumentin transaktiot. Lopuksi sama tehtävä tehdään
PostgreSQLin JSONB-sarakkeella, jotta valinnan voi tehdä tiedon pohjalta.

## Aggregaatioputki

Aggregaatioputki on vaiheiden luettelo, jossa kukin vaihe muuntaa
edellisen tuottamat dokumentit. `$match` suodattaa, `$unwind` purkaa
taulukon riveiksi, `$group` kokoaa, `$sort` järjestää ja `$project`
muotoilee tuloksen. Myynti kaupungeittain ja tuotteittain:

```{.python tiedosto="esimerkit/luku06/aggregaatio.py" osa="putki"}
```

Vaiheiden vastineet SQL:ssä ovat `WHERE`, liitos taulukon riveihin,
`GROUP BY`, `ORDER BY` ja `SELECT`-lista. Ryhmittelyn tulosta voi
suodattaa uudella `$match`-vaiheella kuten SQL:n `HAVING`-ehdolla:

```{.python tiedosto="esimerkit/luku06/aggregaatio.py" osa="asiakkaat"}
```

```{.tuloste tiedosto="esimerkit/luku06/aggregaatio.odotettu"}
```

Järjestyksellä on väliä: `$match` alussa voi käyttää indeksiä ja
karsii dokumentit ennen raskaita vaiheita. Suunnittelija siirtää
joitain ehtoja itse aikaisemmaksi, mutta putki kannattaa kirjoittaa
suodatus ensin.

## Skeemavalidointi

Kokoelmalle voi määrätä JSON Schema -muotoisen validaattorin, jonka
tietokanta tarkistaa jokaisessa lisäyksessä ja päivityksessä:

```{.python tiedosto="esimerkit/luku06/validointi.py" osa="skeema"}
```

```{.python tiedosto="esimerkit/luku06/validointi.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/luku06/validointi.odotettu"}
```

Tyhjä rivitaulukko, merkkijonona annettu kappalemäärä ja puuttuva
asiakas hylättiin virhekoodilla 121 (*DocumentValidationFailure*).
Kolmas tapaus on yleinen virhe: sovellus lähettää lukeman lomakkeelta
merkkijonona, ja ilman validointia se tallentuisi sellaisenaan.

Validaattorin voi ottaa käyttöön olemassa olevaan kokoelmaan
tasolla `validationLevel: "moderate"`, jolloin vanhoja virheellisiä
dokumentteja saa päivittää, mutta uudet tarkistetaan. Näin skeeman
voi tiukentaa vähitellen.

## Transaktiot

Yhden dokumentin päivitys on aina atominen. Siksi hyvä dokumenttimalli
pitää yhteen kuuluvat muutokset samassa dokumentissa, ja moni
sovellus ei koskaan tarvitse muuta. Kun muutos koskee useaa dokumenttia
tai kokoelmaa, MongoDB tukee transaktioita replikajoukossa ja
osioidussa klusterissa (siksi esimerkkien MongoDB on yhden jäsenen
replikajoukko).

Viimeisen teltan varaus ja tilauksen lisäys tehdään yhdessä; jos
varastossa ei ole, myös tilaus perutaan:

```{.python tiedosto="esimerkit/luku06/transaktio.py" osa="transaktio"}
```

```{.tuloste tiedosto="esimerkit/luku06/transaktio.odotettu"}
```

`with_transaction` yrittää transaktiota uudelleen, jos se kohtaa
ohimenevän virheen kuten ristiriidan toisen transaktion kanssa, ja
peruu sen, kun funktio heittää muun poikkeuksen. Toisen tilauksen
lisäys ehdittiin tehdä ennen virhettä, mutta peruutus poisti sen.

Transaktiot maksavat: ne pitävät lukkoja, rajoittuvat oletuksena
60 sekuntiin ja ovat osioidussa klusterissa hajautettuja. Jos
sovellus tarvitsee niitä jatkuvasti, dokumenttimalli on luultavasti
väärin rajattu – tai relaatiotietokanta olisi parempi valinta.

## Sama tehtävä PostgreSQLilla

PostgreSQLin `jsonb`-tyyppi tallentaa JSON-dokumentin binäärimuodossa,
ja sille on operaattorit (`->`, `->>`, `@>`) ja GIN-indeksi. Tilaukset
dokumentteina, kuitenkin relaatiotaulussa, jossa on pääavain ja
tarkistusrajoite:

```{.python tiedosto="esimerkit/luku06/jsonb.py" osa="taulu"}
```

Sama myyntikooste kuin aggregaatioputkella. `jsonb_array_elements`
purkaa rivit kuten `$unwind`:

```{.python tiedosto="esimerkit/luku06/jsonb.py" osa="kysely"}
```

Sisältää-ehto `@>` käyttää GIN-indeksiä:

```{.python tiedosto="esimerkit/luku06/jsonb.py" osa="sisaltaa"}
```

```{.tuloste tiedosto="esimerkit/luku06/jsonb.odotettu"}
```

Tulos on sama. Ero on muualla:

| Ominaisuus | MongoDB | PostgreSQL JSONB |
|--------------------|-------------------|--------------------|
| liitokset muihin tauluihin | `$lookup`, rajoitettu | täydet SQL-liitokset |
| transaktiot | replikajoukossa, maksavat | aina, halpoja |
| skeema | valinnainen JSON Schema | sarakkeet ja rajoitteet + vapaa JSON |
| vaakaskaalaus | sisäänrakennettu osiointi | laajennuksilla (esim. Citus) |
| päivitys osaan dokumenttia | operaattoreilla paikallaan | koko arvo kirjoitetaan uudelleen |

Jos data on enimmäkseen relaatiomuotoista ja vain osa vaihtelevaa,
JSONB-sarake relaatiotaulussa on yleensä parempi kuin kokonaan uusi
tietokanta. MongoDB on vahvoilla, kun lähes kaikki data on
dokumentteja ja kuorma kasvaa yhden palvelimen yli.

## Käytännössä

- Kirjoita aggregaatioputket suodatus ensin, jotta `$match` voi käyttää
  indeksiä ja vähentää käsiteltävää dataa.
- Ota skeemavalidointi käyttöön ainakin pakollisille kentille ja
  tyypeille; skeemattomuus on valinta, ei pakko.
- Suunnittele dokumentit niin, että tavallinen muutos koskee yhtä
  dokumenttia. Transaktiot ovat poikkeusta varten.
- Käytä `with_transaction`-apua tai vastaavaa, joka yrittää ohimenevien
  virheiden jälkeen uudelleen.
- Harkitse PostgreSQLin JSONB:tä, ennen kuin otat käyttöön erillisen
  dokumenttitietokannan.

## Itsearviointi

- Osaat kirjoittaa aggregaatioputken, joka purkaa taulukon, ryhmittelee
  ja järjestää.
- Osaat määritellä kokoelmalle skeemavalidoinnin ja tunnistaa
  validointivirheen.
- Osaat tehdä monen dokumentin transaktion ja kertoa, milloin sitä
  tarvitaan.
- Osaat tehdä saman dokumenttikyselyn PostgreSQLin JSONB:llä ja vertailla
  vaihtoehtoja.
