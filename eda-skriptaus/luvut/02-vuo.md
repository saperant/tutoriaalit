# Suunnitteluvuon rakenne

Suunnitteluvuo on joukko vaiheita, joista kukin lukee tiedostoja,
ajaa työkalun ja kirjoittaa uusia tiedostoja. Lint lukee RTL:n.
Synteesi lukee RTL:n ja synteesiskriptin ja kirjoittaa netlistan.
Ajoitusanalyysi lukee netlistan ja kirjoittaa raportin. Kun vaiheet,
niiden syötteet, tulosteet ja riippuvuudet on kuvattu, vuo osaa itse
päättää, mitä ajetaan ja missä järjestyksessä. Se tietää myös, mitä ei
tarvitse ajaa, koska mikään sen tulokseen vaikuttava ei ole muuttunut.

## Vaihe

Vaihe on tietue, jossa on komento, syötteet ja tulosteet sekä niiden
vaiheiden nimet, joiden tuloksia se tarvitsee:

```{.python tiedosto="esimerkit/vuo/vaiheet.py" osa="vaihe"}
```

Komento on lista eikä merkkijono. Työkalu käynnistetään suoraan ilman
kuorta, joten välilyönnit ja erikoismerkit poluissa eivät riko mitään
eikä komentoon voi ujuttaa toista komentoa. Ympäristömuuttujat ovat
osa vaihetta, koska Yosysin Tcl-skripti lukee niistä parametrinsa
(luku 4).

Tämän projektin vuossa on viisi vaihetta. Kaksi ensimmäistä,
lint ja synteesi:

```{.python tiedosto="esimerkit/vuo/kulku.py" osa="kulku"}
```

Muut vaiheet ovat samanlaisia: ajoitusanalyysi lukee synteesin
netlistan, käännös testipenkin ja RTL:n, ja simulointi ajaa käännöksen
tuottaman ohjelman. Kaksi asiaa kannattaa huomata. Ensinnäkin jokainen tuloste menee
ajohakemistoon, ei lähdekoodin viereen. Saman vuon voi siksi ajaa
rinnakkain eri parametreilla, ja ajohakemiston poistaminen palauttaa
projektin puhtaaseen tilaan. Toiseksi simuloinnin syöte on käännöksen
tuloste, simulaattoriohjelma `obj/sim`. Riippuvuus kulkee tiedostojen
kautta, joten muutos etenee vuossa eteenpäin ilman erillistä
kirjanpitoa.

## Järjestys ja rinnakkaisuus

Riippuvuudet muodostavat suunnatun syklittömän verkon. Pythonin
`graphlib` järjestää sen topologisesti. Vuo käyttää järjestäjää
tasoittain: `get_ready()` antaa vaiheet, joiden kaikki riippuvuudet on
käsitelty, ja ne ovat keskenään riippumattomia.

```{.python tiedosto="esimerkit/vuo/vaiheet.py" osa="jarjestys"}
```

Kohteen kanssa verkosta otetaan vain kohde ja sen riippuvuudet
rekursiivisesti, kuten Make tekee: `aja("sta")` ajaa lintin, synteesin
ja ajoitusanalyysin mutta ei simulointia. Kehä riippuvuuksissa
(`a` tarvitsee `b`:tä, joka tarvitsee `a`:ta) on vuon määrittelyvirhe,
ja `prepare()` ilmoittaa siitä poikkeuksella ennen kuin mitään on
ajettu. Tasot lajitellaan nimen mukaan, jotta tulostus ja lokit ovat
samassa järjestyksessä joka ajolla.

## Tila ja inkrementaalisuus

Make päättelee vanhentuneisuuden tiedostojen muutosajoista. Tämä vuo
laskee jokaiselle vaiheelle *leiman*: tiivisteen kaikesta, mikä
vaikuttaa vaiheen tulokseen. Siihen kuuluvat komento, ympäristö,
työkalun versio ja syötetiedostojen sisältö.

```{.python tiedosto="esimerkit/vuo/vaiheet.py" osa="leima"}
```

Leima tallennetaan onnistuneen ajon jälkeen tiedostoon
`leimat/<vaihe>.sha256`. Seuraavalla kerralla vaihe ohitetaan, jos
leima on sama ja tulosteet ovat yhä olemassa. Epäonnistunut vaihe
poistaa leimansa, joten se ajetaan aina uudelleen. Vaihe, jonka
riippuvuus epäonnistui, merkitään ohitetuksi eikä sitä ajeta lainkaan:
synteesi viallisesta RTL:stä tuottaisi vain lisää virheilmoituksia.

```{.python tiedosto="esimerkit/vuo/vaiheet.py" osa="aja"}
```

Saman tason vaiheet ajetaan säiepoolissa. Säikeet riittävät, koska
Python vain odottaa työkalujen prosesseja: varsinainen laskenta
tapahtuu työkaluissa, eikä Pythonin globaali lukko rajoita niitä.

Kokeillaan. Projekti kopioidaan tilapäishakemistoon, jotta lähteitä voi
muuttaa:

```{.python tiedosto="esimerkit/02-vuo.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/02-vuo.odotettu"}
```

Taulukossa viiva tarkoittaa, että vaihe oli ajan tasalla, ja tyhjä
solu, ettei vaihe kuulunut kohteeseen. Ensimmäinen ajo ajaa kaiken ja
toinen ei mitään. Kohta 3 näyttää
sisältötiivisteen edun: `touch` muuttaa vain muutosajan, joten mikään
ei vanhene. Kohdassa 4 kommentti muuttaa tiedoston sisältöä, joten
käännös ajetaan. Verilatorin tuottama ohjelma on kuitenkin tavulleen
sama kuin ennen, joten simuloinnin syöte ei muuttunut eikä simulointia
ajeta. Tätä kutsutaan varhaiseksi katkaisuksi (*early cutoff*):
muutoksen eteneminen pysähtyy vaiheeseen, jonka tulos ei muuttunut.
Suurissa vuoissa se säästää tunteja, kun esimerkiksi RTL:n kommentin
korjaus ei käynnistä uutta synteesiä ja sijoittelua.

Kohdassa 6 lint epäonnistuu, ja sen jälkeiset vaiheet ohitetaan.
Simulointihaara ei riipu laskurista, joten se on yhä ajan tasalla.
Tiedon siitä, mitä lint löysi, antaa loki `lokit/lint.log`. Vaiheen
tila kertoo vain, että lokia pitää lukea.

## Make vai Python

Sama vuo Makella on lyhyt. Jokainen sääntö kirjoittaa kohteen
tiedostoksi, ja lint, jolla ei ole omaa tulostetta, koskettaa
merkkitiedostoa `lint.ok`:

```{.makefile tiedosto="esimerkit/vuo.mk" osa="saannot"}
```

Esimerkki ajaa Maken Pythonista ilman ulomman Maken `MAKEFLAGS`-
muuttujaa ja kysyy tilaa komennolla `make -q`, joka ei aja mitään vaan
palauttaa arvon 0, jos kaikki on ajan tasalla. Funktio `kysy` tulostaa
sen perusteella "ajan tasalla" tai "vanhentunut":

```{.python tiedosto="esimerkit/02-make.py" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/02-make.odotettu"}
```

Make ei huomaa parametrin muutosta. `LEVEYS=16` on komentorivin
muuttuja, ei tiedosto, joten 16-bittisen laskurin synteesiä ei ajeta
ja vanha 8-bittinen netlista jää voimaan. Tämä on Make-pohjaisten
vuoiden yleisin virhe. Korjauksena parametrit kirjoitetaan tiedostoon,
joka päivitetään vain sisällön muuttuessa, ja tiedosto lisätään
riippuvuuksiin. Toisaalta pelkkä `touch` ajaa koko vuon uudelleen,
mikä on hukkaa mutta ei väärin.

| Ominaisuus | Make | Python-vuo |
|--------------------|--------------------|--------------------|
| vanhentuneisuus | muutosaika | sisällön tiiviste |
| parametrit ja työkaluversio | eivät näy ilman lisäkikkoja | osa leimaa |
| rinnakkaisuus | `-j`, valmiina | säiepooli, itse kirjoitettu |
| virheen käsittely | pysähtyy (tai `-k`) | ohitetut vaiheet, tilat |
| raportit ja koosteet | kutsuu skriptejä | samassa ohjelmassa |
| saatavuus | kaikkialla | Python ja oma koodi |

Kumpikin on hyvä valinta. Pieni projekti pärjää Makella, kunhan
parametrit viedään tiedostoihin. Kun vuohon tulee parametrisweeppejä,
monta kohdetta ja raporttien käsittelyä, Python-vuo maksaa itsensä
takaisin. Usein molempia käytetään yhdessä: Make on käyttäjän
käyttöliittymä (`make synteesi`), ja sen säännöt kutsuvat Python-vuota.
Tällöin Python-vuolta kannattaa poistaa ulomman Maken `MAKEFLAGS`
(luku 3).

## Ajohakemistot ja parametrit

Parametrisweeppi ajaa saman vuon usealla parametriarvolla. Jokainen
ajo saa oman hakemistonsa, jonka nimi kertoo parametrit. Hakemistoon
kirjoitetaan manifesti, josta ajon voi toistaa:

```{.python tiedosto="esimerkit/02-parametrit.py" osa="ajo"}
```

Esimerkki ajaa kolme leveyttä rinnakkain ja lukee kunkin ajon
tulokset sen hakemistosta:

```{.tuloste tiedosto="esimerkit/02-parametrit.odotettu"}
```

Manifestissa on kaikki, mitä tuloksen tulkitsija tarvitsee:
parametrit, ajetut komennot, vaiheiden tilat ja työkalujen versiot.
Kun kaksi ajoa antaa eri tuloksen, manifestien vertailu kertoo,
erosivatko parametrit, komennot vai työkalut. Oikeassa projektissa
manifestiin lisätään versionhallinnan commit ja tieto siitä, oliko
työhakemistossa commitoimattomia muutoksia.

## Käytännössä

- **Tulosteet ajohakemistoon.** Lähdepuu pysyy puhtaana, ajoja voi
  olla rinnakkain, ja siivous on yhden hakemiston poisto. Ajohakemisto
  ei kuulu versionhallintaan.
- **Kaikki tulokseen vaikuttava leimaan.** Komento, ympäristö,
  työkaluversio ja syötteiden sisältö. Unohdettu syöte, kuten Tcl-
  skriptin `source`-komennolla lukema tiedosto, on vuon tavallisin
  bugi: muutos ei käynnistä uutta ajoa.
- **Epäonnistunut vaihe ei jätä leimaa.** Muuten seuraava ajo pitäisi
  puolivalmista tulosta ajan tasalla olevana.
- **Riippuvuudet ovat tiedostoja.** Jos vaihe tarvitsee toisen
  tuloksen, se lukee sen tiedostosta, joka on sen syötteissä. Pelkkä
  järjestys ilman tiedostoriippuvuutta rikkoutuu inkrementaalisessa
  ajossa.
- **Manifesti jokaiseen ajoon.** Kolmen kuukauden kuluttua kukaan ei
  muista, millä asetuksilla tulos syntyi.

## Itsearviointi

- Osaat kuvata suunnitteluvuon vaiheina, joilla on syötteet,
  tulosteet ja riippuvuudet, ja järjestää ne rinnakkain ajettaviin
  tasoihin.
- Osaat selittää, miksi sisältötiiviste on muutosaikaa luotettavampi
  peruste uudelleenajolle ja mitä varhainen katkaisu tarkoittaa.
- Osaat kertoa, miksi Make-vuo ei huomaa parametrin muutosta, ja
  korjata sen.
- Osaat järjestää parametroidut ajot omiin hakemistoihinsa ja
  kirjoittaa manifestin, josta ajon voi toistaa.
