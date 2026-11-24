# Konsistenssi ja replikointi käytännössä

Taito *Hajautetut järjestelmät* käsittelee replikoinnin teorian:
johtaja–seuraaja-mallin, kvoorumit, konsistenssimallit sekä CAP- ja
PACELC-lauseet. Tässä luvussa samat asiat näkyvät tietokantojen
asetuksina, joita sovelluskehittäjä joutuu valitsemaan: mitä
kirjoituksen kuittaus tarkoittaa, mistä luetaan ja mitä tapahtuu, kun
kopioita puuttuu.

## Redis: asynkroninen replika

Redisin replikointi on asynkronista: ensisijainen palvelin kuittaa
kirjoituksen heti ja lähettää sen replikoille perässä. Kaatuessa
viimeiset kirjoitukset voivat siis kadota, vaikka ne kuitattiin.
`WAIT` odottaa, että annettu määrä replikoita on vastaanottanut
aiemmat kirjoitukset:

```{.python tiedosto="esimerkit/luku10/replika.py" osa="wait"}
```

`WAIT` ei tee replikoinnista synkronista: jos se palauttaa liian pienen
luvun, kirjoitus on silti tehty ensisijaiseen. Se kertoo vain, kuinka
moni replika sen ehti saada. Replika on oletuksena vain luku -tilassa:

```{.python tiedosto="esimerkit/luku10/replika.py" osa="vain-luku"}
```

```{.tuloste tiedosto="esimerkit/luku10/replika.odotettu"}
```

Replikalta luettaessa arvo voi olla vanha. Jos käyttäjän pitää nähdä
oma kirjoituksensa, luetaan ensisijaiselta tai odotetaan `WAIT`illa.
Ensisijaisen kaatuessa Redis Sentinel tai Redis Cluster ylentää replikan;
tällöin kuittaamatta replikoitumattomat kirjoitukset katoavat.

## MongoDB: kirjoitus- ja lukutakuut

MongoDB:n replikajoukossa on yksi ensisijainen ja muut toissijaisia.
*Write concern* kertoo, milloin kirjoitus kuitataan:

- `w=1`: ensisijainen on kirjoittanut sen.
- `w="majority"`: enemmistö jäsenistä on kirjoittanut sen. Tällainen
  kirjoitus ei katoa, vaikka ensisijainen vaihtuisi.
- `w=2`, `w=3`: annettu määrä jäseniä.

```{.python tiedosto="esimerkit/luku10/kuittaus.py" osa="kuittaus"}
```

Kun vaaditaan enemmän kuin joukossa on jäseniä, kirjoitus tehdään
silti, mutta kuittaus epäonnistuu:

```{.python tiedosto="esimerkit/luku10/kuittaus.py" osa="liikaa"}
```

Tämä on tärkeä yksityiskohta virheenkäsittelylle: `WriteConcernError`
ei tarkoita, että kirjoitus peruttiin, vaan ettei takuuta saatu.
Uudelleenyritys voi tehdä saman kirjoituksen kahdesti, joten
kirjoitusten on oltava idempotentteja tai ehdollisia.

*Read concern* kertoo, mitä luku saa nähdä. `"majority"` näkee vain
enemmistön vahvistamat kirjoitukset, joten luettu arvo ei voi kadota
vikatilanteessa:

```{.python tiedosto="esimerkit/luku10/kuittaus.py" osa="luku"}
```

```{.tuloste tiedosto="esimerkit/luku10/kuittaus.odotettu"}
```

Lisäksi *read preference* päättää, luetaanko ensisijaiselta vai
toissijaisilta. Toissijaiselta luettu arvo voi olla vanha, ellei
käytetä kausaalista istuntoa (*causal consistency*), joka takaa, että
istunto näkee omat kirjoituksensa.

## Cassandra: säädettävä konsistenssi

Cassandran konsistenssitasot näytettiin luvussa 7: kirjoitus ja luku
tasolla `QUORUM` takaavat, että luku näkee viimeisimmän kuitatun
kirjoituksen, ja `ONE` vaihtaa takuun nopeuteen ja saatavuuteen.
Monen konesalin klusterissa `LOCAL_QUORUM` vaatii enemmistön vain
paikallisesta konesalista, jolloin kirjoitus ei odota mantereen
toiselle puolelle.

Cassandra korjaa kopioiden eroja kolmella tavalla: luettaessa
(*read repair*), vihjatuilla kirjoituksilla, jotka tallennetaan, kun
kopio on hetkellisesti poissa (*hinted handoff*), ja säännöllisellä
täydellä vertailulla (*repair*), joka on ajettava ennen kuin
hautakivien säilytysaika päättyy.

## Osiointi

Replikointi kopioi saman datan monelle palvelimelle; osiointi jakaa
eri datan eri palvelimille. Kaikki tämän tutoriaalin tietokannat
osioivat avaimen perusteella, mutta eri tavoin:

| Tietokanta | Osiointi | Avaimen valinta |
|-----------|--------------------|-----------------------|
| Redis Cluster | 16 384 lokeroa avaimen tiivisteen mukaan | `{aaltosulkeissa}` oleva osa ryhmittelee avaimet samaan lokeroon |
| MongoDB | osioavaimen arvoväli tai tiiviste | osioavain on kyselyjen yhteinen ehto; huono valinta on vaikea muuttaa |
| Cassandra | partitioavaimen tiiviste renkaalla | partitioavain on pakollinen jokaisessa kyselyssä |
| Neo4j | ei osiointia yhteisöversiossa | graafin jakaminen on vaikeaa, koska polut ylittäisivät palvelimia |

Konsistentti hajautus, kuumat avaimet ja uudelleenosiointi
käsitellään taidossa *Skaalautuvien järjestelmien suunnittelu*.
Muistisääntö on sama kaikille: avaimen pitää jakaa kuorma tasaisesti,
ja tavallisimman kyselyn pitää osua yhteen osioon.

## Käytännössä

- Selvitä, mitä tietokantasi kuittaus tarkoittaa. "OK" voi tarkoittaa
  muistissa yhdellä palvelimella.
- Käytä MongoDB:ssä `w="majority"`-kirjoituksia datalle, jota ei saa
  menettää, ja `readConcern: "majority"`-lukuja, kun luettu ei saa
  kadota.
- Älä tulkitse kuittausvirhettä perutuksi kirjoitukseksi; tee
  kirjoituksista idempotentteja.
- Lue replikalta vain, kun vanha arvo kelpaa. Käyttäjän oma kirjoitus
  luetaan ensisijaiselta tai kausaalisessa istunnossa.
- Valitse osioavain kyselyjen ja kuorman jakautumisen mukaan; sitä on
  vaikea muuttaa myöhemmin.

## Itsearviointi

- Osaat kertoa, miten Redisin asynkroninen replikointi voi kadottaa
  kuitatun kirjoituksen ja mitä `WAIT` takaa.
- Osaat valita MongoDB:n write concern- ja read concern -tasot ja
  käsitellä kuittausvirheen oikein.
- Osaat selittää, miten Cassandra korjaa kopioiden erot.
- Osaat verrata, miten Redis, MongoDB ja Cassandra osioivat datan.
