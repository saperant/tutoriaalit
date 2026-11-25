# Kansivetoinen onkalo

Virtausratkaisija on nyt koottu ja tarkistettu tehtävällä, jonka tarkka
ratkaisu tunnetaan. Seuraava askel on tehtävä, jolla tarkkaa ratkaisua
ei ole. **Kansivetoinen onkalo** (*lid-driven cavity*) on alan
vakiotehtävä: neliön muotoinen, nesteellä täytetty onkalo, jonka kansi
liukuu vakionopeudella ja vetää nesteen kiertoliikkeeseen. Geometria on
yksinkertaisin mahdollinen, reunaehdot ovat pelkkiä seiniä, ja silti
virtauksessa on rajakerroksia, pääpyörre ja kulmien toisiopyörteitä.
Tässä luvussa tehtävä ratkaistaan ja tulokselle lasketaan virhearvio
ilman tarkkaa ratkaisua.

## Tehtävä

Onkalon sivu ja kannen nopeus ovat ykkösiä, joten Reynoldsin luku on
viskositeetin käänteisluku. Tasapainotila haetaan marssimalla ajassa
levosta, kunnes nopeus ei enää muutu.

```{.python tiedosto="esimerkit/09-onkalo.py" osa="onkalo"}
```

Koska vain lopputila kiinnostaa, aika-askeleen tarkkuudella ei ole
väliä, ainoastaan sen pituudella. Reynoldsin luvulla 100 viskositeetti
on niin suuri, että Eulerin menetelmä sallii pidemmän askeleen kuin
AB2: diffuusion raja on sille kaksinkertainen, eikä advektion raja
$2\nu/U^2$ vielä pure.

Tulosta ei voi verrata kokonaisena kenttänä, joten siitä poimitaan
tunnuslukuja: pääpyörteen voimakkuus eli virtafunktion minimi, pyörteen
keskipiste sekä nopeuden ääriarvot onkalon keskilinjoilla. Samoja
suureita on taulukoitu kirjallisuudessa vuosikymmenten ajan, ja niillä
virtauslaskentaohjelmia verrataan toisiinsa.

![Virtaviivat kahdella Reynoldsin luvulla. Risti on pääpyörteen
keskipiste. Alakulmissa on heikot vastakkaiseen suuntaan pyörivät
toisiopyörteet.](kuvat/onkalo.png){width=90%}

Kansi vetää nestettä oikealle, oikea seinä kääntää sen alas, ja koko
onkalo täyttyy yhdestä pyörteestä. Alakulmiin neste ei jaksa kiertää,
ja niihin jää hitaita toisiopyörteitä.

Yläkulmissa tehtävä on **singulaarinen**: kannen nopeus on yksi ja
seinän nolla samassa pisteessä. Paine ja pyörteisyys kasvavat kulmaa
lähestyttäessä rajatta, eivätkä niiden arvot kulmissa suppene hilaa
tihentämällä. Tilanne on sama kuin sisäänpäin kääntyvän kulman
jännitys taidossa *Fysikaalinen mallinnus ja simulointi*: singulaarista
suuretta ei raportoida, ja tarkistukseen valitaan suureet, jotka ovat
kaukana kulmista.

## Kolme hilaa ja virhearvio

Kun tarkkaa ratkaisua ei ole, virhe arvioidaan laskemalla sama tehtävä
kolmella hilalla, joista jokainen on edellistä kaksi kertaa tiheämpi.
Peräkkäisten tulosten erotuksista saadaan **havaittu kertaluku**,
**Richardsonin ekstrapoloinnilla** arvio hilasta riippumattomalle
tulokselle ja **verkkosuppenemisindeksi** (GCI) tiheimmän hilan
virheelle. Menetelmä on esitiedoista tuttu.

```{.python tiedosto="esimerkit/09-onkalo.py" osa="hilat"}
```

```{.tuloste tiedosto="esimerkit/09-onkalo.odotettu" rivit="1-10"}
```

![Vasemmalla vaakanopeus onkalon pystysuoralla keskilinjalla kolmella
hilalla. Oikealla profiilin minimi ruudun koon funktiona ja siitä
ekstrapoloitu arvo.](kuvat/onkalo-hilat.png){width=95%}

Taulukosta luetaan neljä asiaa.

- Tulokset muuttuvat hilan mukana samaan suuntaan ja pienenevin
  askelin. Tämä on edellytys koko menettelylle: jos tulokset
  heilahtelisivat, hilat eivät olisi vielä suppenemisalueella.
- Havaittu kertaluku on 1,4–2,0 eli lähellä menetelmän toista
  kertalukua, muttei tasan. Tunnusluvut poimitaan hilapisteistä, ja
  ääriarvon paikka osuu eri hiloilla eri kohtaan ruudun sisällä.
- Ekstrapoloidut arvot ovat tehtävän vastaus: pääpyörteen voimakkuus
  $-0{,}1036$ ja keskilinjan pienin vaakanopeus $-0{,}214$.
- Tiheimmän hilan virhearvio on prosentin luokkaa. Tulos ilmoitetaan
  sen kanssa: $u_\text{min} = -0{,}213 \pm 0{,}002$ hilalla 64 × 64.

Ilman kolmea hilaa olisi vain yksi luku eikä mitään tietoa siitä,
montako sen numeroista on oikein. Karkeimman hilan tulos $-0{,}196$ on
yhdeksän prosenttia pielessä, eikä mikään siinä ajossa itsessään kerro
sitä.

## Vertailu kirjallisuuteen

Onkalovirtauksen tunnusluvut on julkaistu taulukkoina, joista
tunnetuin on Ghian, Ghian ja Shinin artikkeli vuodelta 1982. Uutta
ohjelmaa kokeiltaessa oma tulos asetetaan näiden taulukoiden rinnalle,
ja ero julkaistuihin arvoihin kertoo virheistä, joita hilan
tihentäminen ei paljasta: väärästä reunaehdosta, väärästä Reynoldsin
luvun määritelmästä tai puuttuvasta termistä. Sellainen virhe suppenee
siististi väärään arvoon.

Tässä tutoriaalissa vertailukohtana on oma ekstrapoloitu ratkaisu, ei
julkaistu taulukko. Se riittää osoittamaan, että ohjelma ratkaisee
kirjoitetut yhtälöt johdonmukaisesti, ja yhdessä luvun 7 tarkan
ratkaisun kanssa se on vahva tarkistus. Riippumatonta vertailua se ei
korvaa, ja lukijan kannattaa tehdä se lähteen taulukoita vasten.

## Reynoldsin luvun vaikutus

```{.python tiedosto="esimerkit/09-onkalo.py" osa="reynolds"}
```

```{.tuloste tiedosto="esimerkit/09-onkalo.odotettu" alkaen="Re = 400"}
```

Reynoldsin luvulla 400 pyörre on voimakkaampi ja sen keskipiste on
siirtynyt alemmas ja lähemmäs onkalon keskustaa. Seinien rajakerrokset
ovat ohuempia ja toisiopyörteet suurempia. Sama suunta jatkuu:
Reynoldsin luvun kasvaessa pyörre asettuu keskelle, rajakerrokset
ohenevat ja hilaa on tihennettävä seinien lähellä. Tasapainotilan
saavuttaminen kestää myös pidempään, koska viskositeetti vaimentaa
alkutilan häiriöitä hitaammin.

Riittävän suurella Reynoldsin luvulla tasapainotilaa ei enää ole, vaan
virtaus jää värähtelemään. Aikamarssi löytää tämän itsestään:
jäännös lakkaa pienenemästä. Menetelmä, joka ratkaisee suoraan
tasapainoyhtälöt, voi sen sijaan tuottaa ratkaisun, joka toteuttaa
yhtälöt mutta on epästabiili eikä esiinny luonnossa.

## Käytännössä

- **Aloita tunnetulla tehtävällä.** Ennen omaa geometriaa lasketaan
  onkalo tai muu vakiotapaus samalla ohjelmalla ja samoilla asetuksilla.
  Se paljastaa väärinkäsitykset asetuksista halvalla.
- **Kolme hilaa, ei yksi.** Hilariippuvuus tutkitaan niille suureille,
  jotka raportoidaan. Kaunis kenttäkuva suppenee paljon ennen
  seinäkitkaa tai pyörteen pituutta.
- **Ilmoita virhearvio.** Tulos ilman virhearviota on yksi luku
  tuntemattomalla tarkkuudella. GCI on alan vakiintunut tapa.
- **Varo singulaarisia pisteitä.** Kulmat, joissa reunaehto hyppää,
  tuottavat arvoja, jotka kasvavat hilan mukana. Älä raportoi niitä
  äläkä anna värikartan asteikon määräytyä niistä.
- **Valitse suppenemisen raja suureen mukaan.** Tasapainotilaa
  haettaessa lasku lopetetaan, kun seurattava suure ei enää muutu, ei
  kun jäännös alittaa jonkin totutun luvun (luku 12).

## Itsearviointi

- Osaat asettaa kansivetoisen onkalon tehtävän ja kertoa, miksi sitä
  käytetään ohjelmien tarkistamiseen.
- Osaat kuvata onkalovirtauksen rakenteen ja selittää, miksi yläkulmien
  arvot eivät suppene.
- Osaat laskea kolmen hilan tuloksista havaitun kertaluvun,
  ekstrapoloidun arvon ja virhearvion.
- Osaat kertoa, mitä hilasuppenemiskoe todistaa ja mitä se ei todista.
- Osaat ennustaa, miten virtaus ja laskennan vaatimukset muuttuvat,
  kun Reynoldsin luku kasvaa.
