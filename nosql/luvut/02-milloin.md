# Milloin relaatiomalli ei riitä

Relaatiomalli tallentaa jokaisen tiedon kerran ja kokoaa näkymät
kyselyhetkellä liitoksilla. Malli ei tiedä, miten dataa luetaan, joten
se palvelee kaikkia kyselyjä kohtuullisesti. NoSQL-tietokannat tekevät
päinvastoin: ne tallentavat datan siinä muodossa, jossa se luetaan,
ja palvelevat suunniteltuja kyselyjä erinomaisesti ja muita huonosti
tai ei ollenkaan.

## Sama tilaus kahdella tavalla

Normalisoidussa mallissa tilaus on kolmessa taulussa:

```{.python tiedosto="esimerkit/luku02/mallit.py" osa="normalisoitu"}
```

```{.dot otsikko="Tilaus normalisoituna ja dokumenttina."}
digraph {
  rankdir=LR;
  subgraph cluster_r { label="relaatiomalli"; style=dashed;
    tilaus [label="tilaus\nid, asiakas, kaupunki"];
    rivi [label="rivi\ntilaus, tuote, kpl, hinta"];
    tuote [label="tuote\nid, nimi, hinta"];
    rivi -> tilaus; rivi -> tuote; }
  subgraph cluster_d { label="dokumenttimalli"; style=dashed;
    dok [label="tilaus T1\nasiakas: aino\nrivit: [keitin x1,\n lamppu x2]"]; }
}
```

Tilauksen näyttäminen vaatii liitoksen. Dokumenttina sama tieto tulee
yhdellä haulla yhdestä paikasta:

```{.python tiedosto="esimerkit/luku02/mallit.py" osa="nakyma"}
```

Toisinpäin kysymys "montako lamppua on myyty" on relaatiomallissa
suora koostekysely, dokumenttimallissa pitää purkaa jokaisen tilauksen
rivit. PostgreSQL osaa molemmat:

```{.python tiedosto="esimerkit/luku02/mallit.py" osa="toisinpain"}
```

Ja kun tuotteen nimi muuttuu, normalisoidussa mallissa muutos tehdään
yhteen riviin. Dokumenttimallissa nimi on kopioitu jokaiseen
tilaukseen, jos se on kopioitu, ja kaikki kopiot pitää päivittää:

```{.python tiedosto="esimerkit/luku02/mallit.py" osa="muutos"}
```

```{.tuloste tiedosto="esimerkit/luku02/mallit.odotettu"}
```

Tässä on koko kysymyksen ydin. Normalisointi optimoi kirjoitukset ja
eheyden, denormalisointi luvut. Kumpikaan ei ole oikein yleisesti, vaan
kuorman perusteella.

## Kyselylähtöinen mallinnus

Relaatiomallinnus alkaa käsitteistä: mitä asioita on ja miten ne
liittyvät toisiinsa. NoSQL-mallinnus alkaa kyselyistä: mitä sovellus
kysyy, kuinka usein ja millä avaimella. Cassandrassa (luku 7) tämä on
pakko, koska kysely ilman partitioavainta hylätään. MongoDB:ssä se on
suositus: upotus vai viittaus ratkeaa sen mukaan, luetaanko tiedot
yhdessä.

Kyselylähtöinen malli on nopea niille kyselyille, joita varten se
tehtiin. Uusi kysymys, jota ei suunniteltu, voi vaatia koko datan
läpikäynnin tai uuden kopion datasta. Relaatiotietokannassa uusi
kysymys on yleensä uusi indeksi.

## Skeemattomuuden hinta

Dokumenttitietokantaa kutsutaan usein skeemattomaksi. Tarkemmin:
skeema ei ole tietokannassa vaan sovelluksessa. Jokainen koodi, joka
lukee dokumentteja, olettaa jonkin rakenteen, ja jos kenttä on
vanhemmissa dokumenteissa eri muodossa, virhe näkyy vasta lukiessa.
Skeeman muutos tehdään joko kaikkiin dokumentteihin kerralla tai
sovelluksen pitää osata lukea kaikki historian muodot.

Joustavuudesta on hyötyä, kun rakenne todella vaihtelee – esimerkiksi
tuotteiden ominaisuudet, joita on keittimellä eri kuin teltalla – tai
kun sovellus kehittyy nopeasti. Silloinkin skeeman voi määritellä
tietokantaan (luku 6), ja PostgreSQLin JSONB-sarake antaa saman
joustavuuden relaatiotietokannan sisällä.

## Milloin harkita muuta kuin relaatiotietokantaa

| Tarve | Vaihtoehto | Miksi |
|------------------------------|----------------|--------------------|
| tuhansia–miljoonia yksinkertaisia hakuja sekunnissa avaimella, muistin nopeus | avain-arvo (Redis) | ei kyselysuunnittelijaa, data muistissa |
| vaihtelevan rakenteen kokonaisuudet, jotka luetaan yhdessä | dokumentti (MongoDB) | yksi haku, ei liitoksia |
| valtava kirjoitusmäärä, lineaarinen skaalautuminen monelle palvelimelle | leveäsarake (Cassandra) | LSM-puu, ei johtajaa |
| yhteyksien läpikäynti, polut, suositukset | graafi (Neo4j) | yhteydet tallennettu suoraan |
| mittaukset aikaleimoineen, aikaväliin perustuvat koosteet | aikasarja (luku 11) | pakkaus, aikaikkunat, säilytysajat |
| tekstihaku, sumea haku, relevanssi | hakukone (luku 11) | käänteinen indeksi |

Yhteistä kaikille on, että ne skaalautuvat vaakasuunnassa helpommin
kuin perinteinen relaatiotietokanta, koska ne luopuvat jostakin:
liitoksista, monen rivin transaktioista tai vahvasta
konsistenssista. Sitä ennen kannattaa varmistaa, että tarve on
todellinen. Yksi PostgreSQL-palvelin käsittelee kymmeniätuhansia
kyselyjä sekunnissa ja teratavuja dataa.

## Monta tietokantaa samassa järjestelmässä

Suurissa järjestelmissä eri tietokannat hoitavat eri tehtäviä: tilaukset
relaatiotietokannassa, istunnot ja välimuisti Redisissä, tuotehaku
hakukoneessa ja suositukset graafissa. Tätä kutsutaan nimellä
*polyglot persistence*. Hinta on, että data on kopioitu järjestelmiin,
joiden pitää pysyä samassa tahdissa, ja jokainen uusi tietokanta on
uusi asia ylläpitää, varmuuskopioida ja osata. Siksi uusi tietokanta
otetaan käyttöön vasta, kun nykyinen ei todistetusti riitä.

## Käytännössä

- Aloita relaatiotietokannasta. Valitse muu vasta, kun osaat nimetä
  kuorman, jota relaatiotietokanta ei palvele.
- Kirjoita kyselyt ja niiden määrät ylös ennen mallinnusta. NoSQL-malli
  suunnitellaan niiden mukaan, ja malli on hyvä vain niille.
- Älä luovu eheydestä huomaamattasi: jos valitset tietokannan ilman
  vierasavaimia tai transaktioita, päätä, missä eheys silloin
  varmistetaan.
- Skeemattomuus siirtää skeeman sovellukseen. Dokumentoi se ja
  validoi se, mieluiten tietokannassa.
- Kun tarvitset vain vähän joustavuutta, PostgreSQLin JSONB voi riittää.

## Itsearviointi

- Osaat kertoa, mitä normalisointi optimoi ja mitä denormalisointi.
- Osaat mallintaa saman tiedon relaatiotauluina ja dokumenttina ja
  kertoa, mitkä kyselyt kumpikin palvelee hyvin.
- Osaat perustella, milloin NoSQL-tietokanta on parempi valinta kuin
  relaatiotietokanta ja milloin ei.
- Osaat selittää, mitä skeemattomuus tarkoittaa ylläpidon kannalta.
