# Suunnitteluharjoitus: lyhytosoitepalvelu

Lyhytosoitepalvelu muuttaa pitkän osoitteen lyhyeksi koodiksi
(`https://lyh.yt/3kT9xQa`) ja ohjaa koodin käyttäjän alkuperäiseen
osoitteeseen. Toiminto on pieni, mutta palvelussa tulevat vastaan lähes
kaikki edellisten lukujen kysymykset: suuri luku:kirjoitus-suhde,
yksikäsitteiset tunnukset ilman koordinointia, välimuisti, kuumat
avaimet, saatavuus ja kuormantasaus. Luku käy läpi suunnittelun luvun 1
vaiheiden mukaan ja päättyy pieneen toteutukseen, joka ajetaan oikeilla
palveluilla.

## Vaatimukset

Toiminnalliset vaatimukset:

- Linkin luonti: `POST /linkit` osoitteella, vastauksena koodi.
- Uudelleenohjaus: `GET /<koodi>` vastaa `302` ja `Location`-otsakkeen.
- Tuntematon koodi: `404`.

Rajaukset: ei omia koodeja, ei vanhenemista eikä tilastoja; ne olisivat
seuraavia laajennuksia. Laadulliset vaatimukset:

| Vaatimus | Tavoite |
|----------|---------|
| kuorma | 100 miljoonaa uutta linkkiä kuukaudessa, 100 ohjausta linkkiä kohden |
| latenssi | ohjauksista 99 % alle 50 ms palvelun reunalla |
| saatavuus | ohjauksista 99,9 % onnistuu kuukaudessa; luonti saa olla hetken poissa |
| pysyvyys | luotu linkki ei saa kadota |
| konsistenssi | luotu linkki toimii heti luojalleen; muille hetken viive sallitaan |

Saatavuustavoite on tarkoituksella eri ohjaukselle ja luonnille.
Rikkinäinen linkki näkyy kaikille, jotka sitä klikkaavat; luonnin katko
näkyy vain luojalle, joka voi yrittää uudelleen.

## Arviot

```{.python tiedosto="esimerkit/luku12/lyhyt_arvio.py" osa="oletukset"}
```

```{.tuloste tiedosto="esimerkit/luku12/lyhyt_arvio.odotettu"}
```

Johtopäätökset:

- **Kirjoitukset mahtuvat yhteen tietokantaan.** 150 kirjoitusta
  sekunnissa huipussa on pieni kuorma.
- **Luvut eivät mahdu ilman välimuistia.** 15 000 lukua sekunnissa
  huipussa on yhden tietokannan rajoilla; välimuisti tai lukureplikat
  tarvitaan, ja Zipf-jakautunut suosio (luku 6) tekee välimuistista
  tehokkaan.
- **Data mahtuu yhdelle koneelle vielä viiden vuoden päästä.**
  3 teratavua on suuri mutta ei poikkeuksellinen PostgreSQL-tietokanta.
  Osiointi on tarpeen vasta myöhemmin, ja koodi pääavaimena on valmis
  osioavain (luku 5).
- **Tunnisteeseen riittää 40 bittiä**, ja seitsemän merkin base62-koodi
  kattaa sen.

## Tunnukset ja tietomalli

Koodin luontiin on kolme tavallista tapaa:

| Tapa | Hyvää | Huonoa |
|------|-------|--------|
| satunnainen koodi | ei koordinointia, ei arvattava | törmäykset tarkistettava, pitkä koodi |
| tiiviste osoitteesta | sama osoite, sama koodi | törmäykset, ei eri koodeja samalle osoitteelle |
| laskuri ja muunnos | lyhyt, ei törmäyksiä | laskuri on jaettu tila; peräkkäiset arvattavia |

Toteutus käyttää tietokannan sekvenssiä: se on jo kahdennettu kannan
mukana, eikä sovelluspalvelinten tarvitse sopia mitään. Sekvenssin numero
sekoitetaan kääntyvällä kuvauksella, jotta peräkkäiset koodit eivät
paljasta palvelun kokoa tai toistensa olemassaoloa:

```{.python tiedosto="esimerkit/jarjestelma/tunnus.py" osa="koodi"}
```

Jos sekvenssistä tulee pullonkaula, jokainen palvelin voi varata
kerralla tuhannen numeron lohkon (`nextval` väliajoin, Hi/Lo-malli), tai
tunnus voi koostua ajasta, solmun numerosta ja laskurista
(Snowflake-tyyppinen tunnus). Tietomalli on yksi taulu:

```{.sql tiedosto="esimerkit/luku12/skeema.sql"}
```

## Arkkitehtuuri

```{.dot otsikko="Lyhytosoitepalvelun tavoitearkkitehtuuri"}
digraph {
  nodesep=0.5; ranksep=0.45;
  asiakas [shape=plaintext];
  tasaaja [label="HAProxy (2 kpl)"];
  subgraph cluster_sovellus {
    label="tilattomat sovelluspalvelimet"; fontsize=9; color="#B8C4C8";
    a [label="sovellus a"]; b [label="sovellus b"];
  }
  redis [label="Redis"];
  subgraph cluster_kanta {
    label="PostgreSQL"; fontsize=9; color="#B8C4C8";
    kanta [label="ensisijainen"]; replika;
    {rank=same; kanta; replika;}
  }
  asiakas -> tasaaja;
  tasaaja -> a [label="  kierto,\l  terveystarkistus\l"];
  tasaaja -> b [label="  uudelleenyritys\l  yhteysvirheessä\l"];
  a -> redis [label="  cache-aside\l"];
  b -> redis;
  a -> kanta; b -> kanta [label="  huti, luonti\l"];
  kanta -> replika [style=dashed, label="replikointi"];
}
```

Kaavio on tavoitearkkitehtuuri; koeajossa on yksi tasaaja ja kanta
ilman replikaa. Välimuistin TTL on tunti ja negatiivisen välimuistin
60 sekuntia. Ohjaus lukee välimuistista ja hutilla kannasta;
olematonkin koodi tallennetaan hetkeksi välimuistiin, jotta
virheelliset tai haitalliset pyynnöt eivät kuormita kantaa. Jos Redis
ei vastaa, ohjaus jatkaa kannan varassa:

```{.python tiedosto="esimerkit/jarjestelma/lyhyt.py" osa="haku"}
```

Luonti tarkistaa osoitteen ja tallentaa sen. Luonnin jälkeen
luojalle palautetaan koodi, ja koska luonti ja ensimmäinen ohjaus
kulkevat ensisijaisen kannan kautta, linkki toimii heti; lukureplikoita
käytettäessä tarvittaisiin luvun 7 lue omat kirjoituksesi -takuu.

```{.python tiedosto="esimerkit/jarjestelma/lyhyt.py" osa="luonti"}
```

## Toteutus ja koeajo

Koeajo käynnistää PostgreSQLin, Redisin, kaksi sovelluspalvelinta ja
HAProxyn:

```{.python tiedosto="esimerkit/luku12/lyhyt_ajo.py" osa="kaynnistys"}
```

Sitten luodaan 200 linkkiä ja tehdään 3 000 ohjausta Zipf-jakautuneella
suosiolla; kolme prosenttia pyynnöistä on tuntemattomia koodeja:

```{.python tiedosto="esimerkit/luku12/lyhyt_ajo.py" osa="kuorma"}
```

Lopuksi Redis pysäytetään, ja ohjauksia jatketaan:

```{.python tiedosto="esimerkit/luku12/lyhyt_ajo.py" osa="heikentyminen"}
```

```{.tuloste tiedosto="esimerkit/luku12/lyhyt_ajo.odotettu"}
```

Tuloksista näkyy:

- **Molemmat palvelimet palvelivat**, ja koska palvelimet ovat tilattomia,
  linkki toimii riippumatta siitä, kumpi sen loi.
- **Välimuisti osui 2 716 ohjauksessa 2 908:sta**, ja jokainen huti
  vastasi yhden linkin ensimmäistä ohjausta. Kanta sai vain 7 % lukuja.
- **Negatiivinen välimuisti** vastasi 72 tuntemattomaan koodiin 92:sta
  kantaan menemättä.
- **Redisin pysähtyminen ei kaatanut palvelua.** Kaikki 100 ohjausta
  onnistuivat suoraan kannasta (`ohitettu`). Kuorma kannassa kasvoi,
  mikä on mitoitettava tai rajattava (luku 9).

Koko kokoonpanon mittaaminen paljastaa viiveitä, joita osien testit
eivät näytä. Tässä palvelussa sellainen on verkkopinossa: `http.server`
kirjoittaa otsakkeet ja rungon eri kirjoituksina, ja pysyvällä
yhteydellä Naglen algoritmi ja vastapuolen viivästetty kuittaus
pidättävät silloin jokaista vastausta noin 40 ms (taito
*Verkko-ohjelmointi*). Ilman asetusta `TCP_NODELAY` 3 000 pyynnön
koeajo kesti kehityskoneella yli minuutin, sen kanssa kolme sekuntia.
Siksi esimerkkien HTTP-palvelin kytkee Naglen algoritmin pois
(`disable_nagle_algorithm` tiedostossa `jarjestelma/http_apu.py`).

## Sama kontteina

Tuotannossa sama kokoonpano ajetaan kontteina. Compose-tiedosto kuvaa
sovelluspalvelimet ja niiden riippuvuudet terveystarkistuksineen, ja
salasana luetaan salaisuudesta eikä ympäristömuuttujasta (taito
*Kontit ja pilvi-infrastruktuuri*):

```{.yaml tiedosto="esimerkit/luku12/compose.yaml" osa="sovellus"}
```

Sama HAProxy-asetus kelpaa molempiin, koska osoitteet tulevat
ympäristömuuttujista: testissä `127.0.0.1` ja vapaat portit, Composessa
palvelujen nimet. Compose-tiedosto tarkistetaan Composen skeemaa vasten,
ja Dockerfile hadolintilla.

## Pullonkaulat ja seuraavat askeleet

Kun kuorma kasvaa kymmenkertaiseksi, ensimmäiset rajat ovat:

1. **Välimuistin muisti ja Redisin yksi säie.** Redis Cluster tai
   useampi instanssi konsistentilla hajautuksella (luku 5).
2. **Kannan luvut hudeilla ja Redisin katkossa.** Lukureplikat ja
   kuorman rajoitus, jotta välimuistin katko ei kaada kantaa (luvut 7 ja
   9).
3. **Kuumat linkit.** Viraali linkki voi saada kymmeniä tuhansia
   ohjauksia sekunnissa; paikallinen välimuisti sovelluspalvelimessa
   ja CDN ohjauksille (`Cache-Control` 302-vastauksessa) poistavat sen
   kuorman välimuistipalvelusta.
4. **Tallennus.** Viiden vuoden kuluttua osiointi koodin tiivisteellä.
5. **Alueet.** Ohjaukset voi palvella monesta alueesta, koska linkit
   eivät muutu: asynkroninen replikointi ja paikalliset välimuistit
   riittävät, ja luonti voi pysyä yhdessä alueessa.

## Käytännössä

- **Kulje vaiheet järjestyksessä.** Vaatimukset, arviot, rajapinta ja
  tietomalli, arkkitehtuuri, pullonkaulat. Arvio ratkaisee, mitä ei
  tarvitse rakentaa.
- **Erota saatavuustavoitteet toiminnoittain.** Kriittinen lukupolku ja
  harvinaisempi kirjoituspolku eivät tarvitse samaa tasoa.
- **Käytä valmista yksikäsitteisyyttä.** Tietokannan sekvenssi tai
  lohkovaraus on yksinkertaisempi kuin oma hajautettu laskuri.
- **Tee välimuistista ohitettava.** Palvelu hidastuu mutta ei kaadu, kun
  välimuisti on poissa.
- **Mittaa koko kokoonpano.** Komponenttien yksikkötestit eivät näytä
  verkkopinon, altaiden ja tasaajan yhteisvaikutusta.

## Itsearviointi

- Osaat kirjata lyhytosoitepalvelun toiminnalliset ja laadulliset
  vaatimukset ja johtaa niistä arviot.
- Osaat valita tunnusten luontitavan ja perustella valinnan.
- Osaat suunnitella arkkitehtuurin, jossa on tilattomat
  sovelluspalvelimet, välimuisti, negatiivinen välimuisti ja siisti
  heikentyminen.
- Osaat ajaa kokoonpanon oikeilla palveluilla ja lukea tuloksista
  osumasuhteen ja kannan kuorman.
- Osaat nimetä palvelun seuraavat pullonkaulat ja niiden ratkaisut.
