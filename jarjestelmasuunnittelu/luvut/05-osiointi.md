# Konsistentti hajautus ja osiointi

Kun data ei mahdu yhdelle koneelle tai kirjoituksia on enemmän kuin yksi
kone ehtii, data jaetaan osiin (*partitioning*, *sharding*), ja jokainen
osa on omalla solmullaan. Samaa jakoa tarvitaan välimuistiklusterissa,
viestijonon osioissa ja avaimen mukaan tasaavassa kuormantasaajassa.
Kaksi kysymystä ratkaisee: miten avain kuvataan solmulle niin, että jako
on tasainen, ja kuinka paljon dataa joutuu liikkumaan, kun solmuja
lisätään tai poistetaan.

## Modulo ja sen ongelma

Suoraviivaisin jako on tiiviste modulo solmujen määrä:

```{.python tiedosto="esimerkit/jarjestelma/hajautus.py" osa="modulo"}
```

Jako on tasainen, mutta solmujen määrän muuttuessa lähes jokainen avain
vaihtaa solmua. Välimuistiklusterissa se tarkoittaa, että lähes koko
välimuisti tyhjenee kerralla ja kuorma vyöryy tietokantaan; osioidussa
tietokannassa lähes kaikki data siirtyy. Tiiviste ei saa myöskään olla
Pythonin `hash()`, joka vaihtuu prosessista toiseen: kaikkien
palvelinten on laskettava sama jako.

## Konsistentti hajautus

Konsistentissa hajautuksessa (*consistent hashing*) sekä solmut että
avaimet kuvataan samalle kehälle, ja avain kuuluu ensimmäiselle
solmulle myötäpäivään. Kun solmu lisätään, se ottaa avaimet vain
naapuriltaan; kun solmu poistuu, sen avaimet siirtyvät seuraavalle.
Yksi solmu kehällä jakaa kehän epätasaisesti, joten jokainen solmu
sijoitetaan kehälle monta kertaa *virtuaalisolmuina*:

```{.python tiedosto="esimerkit/jarjestelma/hajautus.py" osa="rengas"}
```

![Saman luokan kehä neljällä virtuaalisolmulla solmua kohden. Piste on
virtuaalisolmu, ja sitä edeltävä kaari on sen avainalue. Kun s5
lisätään, omistaja vaihtuu vain kaarilla, jotka s5 leikkaa
naapureiltaan; muu kehä pysyy ennallaan.](kuvat/rengas.png){width=80%}

*Rendezvous*-hajautus (*highest random weight*) saavuttaa saman ilman
kehää: avain kuuluu solmulle, jonka yhdistetty tiiviste on suurin.

```{.python tiedosto="esimerkit/jarjestelma/hajautus.py" osa="rendezvous"}
```

Kokeessa 100 000 avainta jaetaan neljälle solmulle, ja sitten viides
lisätään:

```{.python tiedosto="esimerkit/luku05/siirrot.py" osa="siirto"}
```

```{.tuloste tiedosto="esimerkit/luku05/siirrot.odotettu"}
```

Modulossa 80 % avaimista siirtyy, ja kolme neljäsosaa siirroista on
turhia: avain siirtyy vanhalta solmulta toiselle vanhalle. Rengas ja
rendezvous siirtävät vain viidenneksen, eli juuri sen osuuden, jonka
uuden solmun kuuluukin saada. Virtuaalisolmujen määrä ratkaisee
tasaisuuden: yhdellä virtuaalisolmulla kuormin solmu saa 2,7-kertaisen
osuuden, sadalla 1,1-kertaisen. Rendezvous on tasainen ilman
virtuaalisolmuja, mutta haku käy läpi kaikki solmut; sitä käytetään,
kun solmuja on kymmeniä, ja rengasta, kun niitä on tuhansia.

Konsistenttia hajautusta käyttävät esimerkiksi Cassandra, DynamoDB:n
edeltäjä Dynamo, Memcached-asiakkaat ja Envoy (`ring_hash`, `maglev`).
Redis Cluster käyttää yksinkertaisempaa muotoa: avainavaruus on
16 384 kiinteää lohkoa (*hash slot*), ja lohkot jaetaan solmuille.
Solmua lisättäessä siirretään kokonaisia lohkoja. Kiinteä lohkojako on
helppo hallita ja seurata, ja sitä käytetään myös monissa
tietokannoissa.

## Osiointi avainalueilla ja tiivisteellä

Tietokannan osiointi tehdään joko avainalueittain (*range
partitioning*) tai tiivisteellä (*hash partitioning*):

```{.python tiedosto="esimerkit/luku05/osiointi.py" osa="jaot"}
```

```{.tuloste tiedosto="esimerkit/luku05/osiointi.odotettu"}
```

Kasvava avain (aikaleima, sekvenssi) on avainalueittain jaettuna
pahin mahdollinen: kaikki uudet kirjoitukset osuvat viimeiseen osioon,
ja muut osiot ovat toimettomina. Tiivisteellä kirjoitukset tasaantuvat,
mutta avainalueen haku ("100 viimeisintä tilausta") joutuu kysymään
kaikkia osioita ja yhdistämään tulokset (*scatter-gather*), ja sen
latenssi on hitaimman osion latenssi (luku 3).

Valinta riippuu kyselyistä. Usein käytetään yhdistelmää: osioavain
tiivisteellä ja sen sisällä järjestysavain. Esimerkiksi viestipalvelussa
osioavain on keskustelun tunniste ja järjestysavain viestin aikaleima:
keskustelut jakautuvat tasaisesti, ja yhden keskustelun viestit ovat
yhdessä osiossa järjestyksessä. Cassandran *partition key* ja
*clustering key* sekä DynamoDB:n *partition key* ja *sort key*
toteuttavat tämän.

Osiointi rikkoo asioita, jotka yksi tietokanta antaa ilmaiseksi:

- **Toissijaiset indeksit.** Indeksi joko osioidaan datan mukana
  (paikallinen indeksi; haku kysyy kaikkia osioita) tai omalla
  avaimellaan (globaali indeksi; kirjoitus päivittää kahta osiota).
- **Liitokset ja koosteet osioiden yli** muuttuvat hajautetuiksi
  kyselyiksi tai ne tehdään sovelluksessa.
- **Transaktiot osioiden yli** vaativat hajautetun transaktion (taito
  *Hajautetut järjestelmät*). Hyvä osioavain pitää yhteen kuuluvan
  datan samassa osiossa.

## Kuumat avaimet

Tasainen jako ei auta, jos yksi avain saa suuren osan kuormasta:
julkkiksen tili, viraalivideo, kampanjatuote. Esimerkissä 30 %
pyynnöistä menee yhdelle tilille:

```{.python tiedosto="esimerkit/luku05/osiointi.py" osa="kuuma"}
```

Kuuman avaimen osio saa 48 % kuormasta, vaikka osioita on neljä.
*Suolaus* jakaa avaimen useaksi ala-avaimeksi (`julkkis#0` … `julkkis#7`),
jotka hajautuvat eri osioihin. Hinta on lukupuolella: luku kokoaa kaikki
ala-avaimet. Suolaus sopii laskureille ja syötteille, joissa kirjoitus
on kuuma; jos kuumaa on luku, ratkaisu on välimuisti (luku 6) tai
kopiot kuumasta avaimesta usealla solmulla.

## Uudelleenosiointi

Osioiden määrä kannattaa valita alussa selvästi solmujen määrää
suuremmaksi, esimerkiksi satoja tai tuhansia loogisia osioita
kymmenelle solmulle. Kun solmu lisätään, sille siirretään kokonaisia
osioita, eikä yksittäisiä avaimia tarvitse laskea uudelleen. Siirto on
silti raskas: data kopioidaan taustalla, muutokset siirron ajalta
toistetaan, ja lopuksi omistajuus vaihdetaan atomisesti. Siirtonopeutta
rajoitetaan, jotta se ei kilpaile tuotantokuorman kanssa.

## Käytännössä

- **Älä osioi, ennen kuin on pakko.** Yksi hyvin mitoitettu
  relaatiotietokanta lukureplikoineen kantaa yllättävän pitkälle (luku
  2). Osiointi tuo pysyvää monimutkaisuutta kyselyihin, transaktioihin
  ja ylläpitoon.
- **Valitse osioavain kyselyjen mukaan.** Yleisin kysely kohdistuu
  yhteen osioon, ja yhteen kuuluva data on samassa osiossa.
- **Vältä kasvavaa avainta avainalueosioinnissa.** Aikaleima
  osioavaimena kuormittaa vain uusinta osiota.
- **Käytä monta loogista osiota solmua kohden.** Uudelleenosiointi on
  silloin osioiden siirtoa, ei avainten uudelleenlaskentaa.
- **Seuraa osioiden kuormaa, ei vain keskiarvoa.** Kuuma osio näkyy
  vain osiokohtaisista metriikoista.

## Itsearviointi

- Osaat selittää, miksi modulojako siirtää lähes kaikki avaimet
  solmujen määrän muuttuessa ja miten konsistentti hajautus välttää sen.
- Osaat toteuttaa konsistentin hajautuksen virtuaalisolmuineen ja
  rendezvous-hajautuksen sekä mitata niiden tasaisuuden.
- Osaat verrata avainalue- ja tiivisteosiointia kirjoitusten ja
  hakujen kannalta ja valita osio- ja järjestysavaimen.
- Osaat tunnistaa kuuman avaimen ja jakaa sen suolauksella tai
  välimuistilla.
