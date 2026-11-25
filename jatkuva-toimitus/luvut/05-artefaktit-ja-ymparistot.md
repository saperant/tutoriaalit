# Artefaktit, versiointi ja ympäristöt

Putken commit-vaihe tuottaa artefaktin: paketin, joka sisältää kaiken
ohjelman ajamiseen tarvittavan. Se voi olla konttikuva, asennuspaketti,
JAR-tiedosto, staattisesti linkitetty binääri tai, kuten tämän
tutoriaalin esimerkissä, tar-paketti. Tämä luku käsittelee artefaktin
elinkaarta: miten se rakennetaan, tunnistetaan, viedään ympäristöstä
toiseen ja miten ympäristöjen erot pidetään sen ulkopuolella.

## Rakenna kerran

Toimitusputken keskeinen sääntö on, että **artefakti rakennetaan kerran
ja sama artefakti viedään jokaiseen ympäristöön**. Tutoriaali *Kontit
ja pilvi-infrastruktuuri* esittää säännön konttikuville. Peruste on
yleinen.

Jos testiympäristöön ja tuotantoon rakennetaan erikseen, niissä ajetaan
kahta eri pakettia, vaikka lähdekoodi olisi sama. Rakennusten välillä
voi muuttua kääntäjän versio, riippuvuuden uusin sallittu versio,
peruskuva tai rakennuskoneen asetus. Testit ajettiin silloin jollekin
muulle kuin sille, mikä julkaistaan.

Säännöstä seuraa kolme asiaa.

- **Artefakti on muuttumaton.** Kun se on rakennettu, sitä ei muokata.
  Korjaus on uusi artefakti uudella tunnisteella.
- **Artefakti tunnistetaan sisällöstä.** Tiiviste kertoo
  yksiselitteisesti, mistä tavuista on kyse. Nimi tai versio voi
  osoittaa väärään pakettiin, tiiviste ei.
- **Artefakti ei sisällä ympäristön tietoja.** Sama paketti toimii
  testissä ja tuotannossa, joten osoitteet, tunnukset ja muut erot
  annetaan sille ulkoa.

## Toistettava rakennus

Voiko rakennuksen tulokseen luottaa? Vahvin vastaus on toistettava
rakennus (*reproducible build*): sama lähdekoodi tuottaa tavu tavulta
saman artefaktin, rakennettiinpa se millä koneella ja milloin tahansa.
Silloin kuka tahansa voi tarkistaa, että julkaistu paketti vastaa
lähdekoodia.

Tavallinen rakennus ei ole toistettava, koska pakettiin päätyy
huomaamatta ympäristön tietoja. Esimerkki kopioi lähdekoodin kahteen
hakemistoon eri aikaleimoin, kuten kävisi kahdella rakennuskoneella, ja
rakentaa paketin kummassakin kahdella tavalla.

```{.python tiedosto="esimerkit/luku05/toistettava.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/luku05/toistettava.odotettu"}
```

Tavallinen `tar` tallentaa jokaisen tiedoston muutosajan ja omistajan,
ja `gzip` kirjoittaa otsakkeeseensa pakkaushetken. Toistettava versio
asettaa ne vakioiksi ja käy tiedostot läpi aina samassa järjestyksessä.

```{.python tiedosto="esimerkit/toimitus/artefakti.py" osa="toistettava"}
```

Yleisimmät epädeterminismin lähteet ovat samat kielestä riippumatta:
aikaleimat, tiedostojen järjestys, rakennushakemiston polku,
käyttäjätunnus ja koneen nimi sekä kiinnittämättömät riippuvuudet.
Reproducible Builds -hankkeen sopima ympäristömuuttuja
`SOURCE_DATE_EPOCH` on vakiintunut tapa kertoa työkaluille, mitä
aikaleimaa käyttää. C-projektin toistettavaa käännöstä käsittelee
*Käännösjärjestelmät, testaus ja CI* ja toistettavuuden merkitystä
toimitusketjun turvallisuudelle *Tietoturva kehitystyössä*.

Täysi toistettavuus ei ole aina saavutettavissa kohtuullisella
vaivalla. Vähimmäisvaatimus on jäljitettävyys: jokaisesta artefaktista
tiedetään, mistä commitista, millä työkaluilla ja missä putken ajossa
se syntyi.

## Versiointi

Versiolla on kaksi eri tehtävää, jotka sekoitetaan usein.

**Viesti käyttäjälle.** Kirjaston tai asennettavan ohjelman versio
kertoo, mitä päivitys muuttaa. Semanttinen versiointi (ks.
*Versionhallinta (Git)*) on tätä varten: numerot ovat lupaus
yhteensopivuudesta.

**Tunniste.** Jatkuvasti toimitettavalla palvelulla ei ole
käyttäjälle näkyvää versiota, ja julkaisuja voi olla kymmeniä päivässä.
Silloin versio on pelkkä yksikäsitteinen tunniste, ja luontevin
tunniste on commitin tiiviste tai putken ajon järjestysnumero.

Esimerkissä versio on `1.4.0+` ja kahdeksan merkkiä lähdepuun
tiivisteestä. Semanttisessa versioinnissa plusmerkin jälkeinen osa on
rakennuksen metatietoa, joka ei vaikuta versioiden järjestykseen.
Tiiviste lasketaan lähdepuun sisällöstä, joten sama lähde saa aina
saman version.

Kolme sääntöä pätee kumpaankin tapaan.

- **Versio annetaan rakennettaessa**, ei käyttöönotettaessa. Se on
  artefaktin sisällä.
- **Käynnissä oleva ohjelma osaa kertoa versionsa.** Esimerkin komento
  `viite versio` lukee sen paketin mukana tulleesta tiedostosta. Kun
  tuotannossa on vika, ensimmäinen kysymys on, mikä versio siellä on.
- **Julkaistua versiota ei käytetä uudelleen.** Liikkuva tunniste,
  kuten konttikuvien `latest`, osoittaa eri päivinä eri sisältöön,
  joten käyttöönotto ei ole toistettava eikä perumisen kohdetta
  tiedetä.

## Edistäminen ympäristöstä toiseen

Artefaktin vieminen ympäristöstä seuraavaan on edistämistä
(*promotion*). Mitään ei rakenneta uudelleen: sama tiedosto haetaan
artefaktivarastosta ja otetaan käyttöön seuraavassa ympäristössä.

```{.python tiedosto="esimerkit/luku05/edistaminen.py" osa="edistaminen"}
```

Käyttöönotto purkaa paketin omaan, tiivisteen mukaan nimettyyn
hakemistoonsa ja vaihtaa symbolisen linkin `nykyinen` osoittamaan
siihen. Vaihto on tiedostojärjestelmässä yksi atominen operaatio, joten
ohjelma ei ole missään vaiheessa puoliksi päivitetty. Edellinen versio
jää levylle, ja peruminen on saman linkin kääntäminen takaisin.

```{.python tiedosto="esimerkit/toimitus/artefakti.py" osa="kayttoonotto"}
```

```{.tuloste tiedosto="esimerkit/luku05/edistaminen.odotettu"}
```

Testissä ja tuotannossa on sama artefakti, ja ohjelma käyttäytyy
niissä eri tavoin vain siksi, että ympäristö antaa sille eri asetukset.
Viimeiset kaksi riviä näyttävät perumisen: viallinen versio vaihtui
takaisin edelliseen rakentamatta mitään.

Sama rakenne toistuu suuremmassa mittakaavassa. Konttialustalla
hakemistoa vastaa kuvan tiiviste ja linkkiä käyttöönoton kuvaus, joka
kertoo, mitä kuvaa ajetaan. Peruminen on paluu edelliseen kuvaukseen.
Olennaista on, että vanha versio on yhä saatavilla muuttumattomana.

## Konfiguraatio

Kaikki, mikä vaihtelee ympäristöjen välillä, on konfiguraatiota:
tietokannan osoite, ulkoisten palvelujen osoitteet, tunnukset,
lokitaso, ominaisuusliput. *The Twelve-Factor App* -ohjeiston tunnettu
sääntö on säilyttää konfiguraatio ympäristössä, erillään koodista.
Testi on yksinkertainen: voisiko koodin julkaista avoimena paljastamatta
yhtään tunnusta tai osoitetta?

Esimerkkisovellus lukee kaksi asetusta ympäristömuuttujista.

```{.python tiedosto="esimerkit/sovellus/viite/asetukset.py" osa="asetukset"}
```

Funktiossa on kolme käytäntöä, jotka pätevät yleisesti.

- **Asetukset luetaan yhdessä paikassa** ja välitetään eteenpäin
  tyypitettynä arvona. Ympäristömuuttujia ei lueta ympäri koodia.
- **Virheellinen arvo pysäyttää käynnistyksen.** Väärin kirjoitettu
  ympäristön nimi huomataan käyttöönotossa eikä ensimmäisen
  asiakkaan kohdalla.
- **Oletus on turvallisin vaihtoehto.** Ilman asetuksia ohjelma
  käynnistyy kehitystilaan, ei tuotantotilaan.

Ympäristömuuttujat ovat yksi tapa, eivät ainoa. Asetustiedosto, joka
liitetään käyttöönotossa, tai asetuspalvelu ajavat saman asian.
Olennaista on raja: artefakti on sama, asetukset tulevat ulkoa.

Konfiguraatio on silti koodia siinä mielessä, että sen muutos voi
kaataa tuotannon yhtä varmasti kuin ohjelmavirhe. Asetukset kuuluvat
versionhallintaan, niiden muutokset katselmoidaan ja ne kulkevat putken
läpi (luku 10). Poikkeus ovat salaisuudet, jotka eivät kuulu
versionhallintaan selväkielisinä. Niiden säilytystä käsittelee
*Tietoturva kehitystyössä*.

## Ympäristöt

Tyypillisessä putkessa on kehittäjän kone, yksi tai useampi
testiympäristö, tuotantoa jäljittelevä esituotanto (*staging*) ja
tuotanto.

```{.dot otsikko="Sama artefakti jokaiseen ympäristöön; vain asetukset vaihtuvat"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.55;
  a [label="artefakti\n(tiiviste)", shape=cylinder, group=y];
  { node [group=y]; t [label="testi"]; e [label="esituotanto"];
    p [label="tuotanto"]; }
  node [shape=note];
  ct [label="asetukset:\ntesti"]; ce [label="asetukset:\nesituotanto"];
  cp [label="asetukset:\ntuotanto"];
  a -> t [label="ota käyttöön"]; t -> e [label="edistä"];
  e -> p [label="edistä"];
  { rank=same; t; ct; } { rank=same; e; ce; } { rank=same; p; cp; }
  ct -> t [style=dashed]; ce -> e [style=dashed]; cp -> p [style=dashed];
}
```

Ympäristöjen arvo riippuu siitä, kuinka paljon ne muistuttavat
tuotantoa. Jokainen ero on paikka, jossa testissä toiminut asia voi
hajota tuotannossa.

| Ero | Seuraus | Lääke |
|-------------------|--------------------------|--------------------------|
| eri käyttöönottotapa | käyttöönotto testataan ensimmäisen kerran tuotannossa | sama skripti ja sama artefakti kaikkialla |
| eri ohjelmistoversiot (tietokanta, käyttöjärjestelmä) | versiokohtainen vika jää löytymättä | ympäristöt kuvataan koodina samasta lähteestä |
| käsin tehdyt muutokset | ympäristö ajautuu tuntemattomaan tilaan | muutokset vain koodin kautta (luku 10) |
| pieni tai keinotekoinen data | hidas kysely tai erikoistapaus jää löytymättä | tuotannon kaltainen, anonymisoitu data |
| ei oikeaa liikennettä | kuormasta ja samanaikaisuudesta johtuvat viat jäävät löytymättä | asteittainen julkaisu tuotannossa (luku 8) |

Kaksi viimeistä riviä kertovat rajan. Esituotanto ei koskaan ole
tuotanto: siellä ei ole samaa dataa, samoja käyttäjiä eikä samaa
kuormaa, ja täydellisen kopion ylläpito on kallista. Siksi nykyinen
käytäntö on siirtynyt kahteen suuntaan. Putken alkupäässä käytetään
**lyhytikäisiä ympäristöjä**, jotka luodaan muutosta varten ja
hävitetään testien jälkeen, jolloin ne eivät ehdi ajautua. Loppupäässä
hyväksytään, että viimeinen testi tapahtuu tuotannossa, ja
rakennetaan julkaisu niin, että se on turvallista.

Jaettu, pitkäikäinen testiympäristö on usein putken pullonkaula. Kun
usea tiimi käyttää samaa ympäristöä, ne odottavat vuoroaan ja
rikkovat toistensa testejä. Jos ympäristö on kuvattu koodina, jokainen
putken ajo voi saada omansa.

## Käytännössä

- Rakenna artefakti kerran ja vie sama tiedosto jokaiseen
  ympäristöön. Tarkista tiivisteestä, että näin tapahtuu.
- Anna jokaiselle artefaktille yksikäsitteinen versio, josta pääsee
  commitiin, ja tee ohjelmasta sellainen, että se kertoo versionsa.
- Älä käytä liikkuvia tunnisteita käyttöönotossa.
- Pidä ympäristökohtaiset asetukset artefaktin ulkopuolella ja
  tarkista ne käynnistyksessä.
- Säilytä edellinen versio käyttöönotettavana ja harjoittele
  peruminen ennen kuin sitä tarvitaan.
- Karsi ympäristöjen eroja järjestyksessä: ensin käyttöönottotapa,
  sitten ohjelmistoversiot, sitten data.

## Itsearviointi

- Osaat perustella, miksi artefakti rakennetaan kerran, ja kertoa,
  mikä voi muuttua kahden rakennuksen välillä.
- Osaat nimetä tavallisimmat syyt siihen, että rakennus ei ole
  toistettava, ja kertoa, miten ne poistetaan.
- Osaat erottaa version kaksi tehtävää ja valita versiointitavan
  kirjastolle ja jatkuvasti toimitettavalle palvelulle.
- Osaat kuvata käyttöönoton, jossa vaihto on atominen ja peruminen ei
  vaadi rakentamista.
- Osaat erottaa konfiguraation artefaktista ja kertoa, miten asetukset
  tarkistetaan.
- Osaat arvioida, mitkä ympäristöjen erot ovat riskejä ja mitä
  esituotanto ei voi paljastaa.
