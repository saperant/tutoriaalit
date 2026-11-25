# Team Topologies

Matthew Skeltonin ja Manuel Pais'n kirja *Team Topologies* (2019) on
viime vuosien vaikutusvaltaisin kuvaus ohjelmisto-organisaation
rakenteesta. Se ei ole menetelmä vaan sanasto: neljä tiimityyppiä ja
kolme vuorovaikutustapaa, joilla tiimien suhteista voi puhua
täsmällisesti. Tämä luku käy sanaston läpi ja arvioi lopuksi, mitä
mallista tiedetään.

## Lähtökohdat

Malli rakentuu kolmen ajatuksen varaan.

- **Tiimi on perusyksikkö.** Työ annetaan pysyvälle tiimille, ei
  yksilöille, eikä tiimiä koota uudelleen jokaista projektia varten.
- **Conwayn laki otetaan vakavasti.** Tiimien rajat ja
  vuorovaikutus suunnitellaan sen mukaan, millainen järjestelmästä
  halutaan (luku 2).
- **Tiimin kognitiivinen kuorma on rajallinen.** Tiimille annetaan
  vain sen verran vastuuta kuin se pystyy hallitsemaan (luku 5).

Tavoite on **nopea virtaus**: muutos kulkee ideasta tuotantoon
odottamatta muita tiimejä.

## Neljä tiimityyppiä

| Tiimityyppi | Tehtävä | Esimerkki |
|-------------------|---------------------------|------------------------|
| virtaan linjattu (*stream-aligned*) | toimittaa arvoa yhdelle työvirralle alusta tuotantoon | tilaustiimi |
| alustatiimi (*platform*) | tarjoaa sisäisiä palveluja, jotka nopeuttavat virtatiimejä | toimitusputki, tietokannat palveluna |
| mahdollistava (*enabling*) | auttaa tiimejä hankkimaan puuttuvan osaamisen | testauksen tai tietoturvan tuki |
| monimutkaisen osajärjestelmän tiimi (*complicated subsystem*) | omistaa osan, joka vaatii syvää erikoisosaamista | hinnoittelun optimointimalli |

**Virtaan linjattu tiimi** on mallin perustyyppi, ja useimpien
tiimien pitäisi olla tällaisia. Virta voi olla tuote, palvelu,
käyttäjäpolku tai asiakasryhmä. Tiimi omistaa virtansa kokonaan:
se selvittää tarpeen, toteuttaa, julkaisee ja vastaa tuotannosta.
Muut kolme tyyppiä ovat olemassa keventääkseen virtatiimien kuormaa.

**Alustatiimi** tekee asioita, joita jokainen virtatiimi muuten tekisi
itse: ympäristöt, toimitusputken, valvonnan, tunnistautumisen. Alustaa
kohdellaan tuotteena, jonka asiakkaita ovat muut tiimit (luku 6).

**Mahdollistava tiimi** koostuu jonkin alan osaajista, jotka
työskentelevät virtatiimin rinnalla rajatun ajan. Sen tavoite on tehdä
itsensä tarpeettomaksi: kun tiimi osaa asian, mahdollistajat siirtyvät
seuraavaan. Se ei tee työtä tiimin puolesta, sillä silloin siitä tulisi
pullonkaula.

**Monimutkaisen osajärjestelmän tiimi** perustetaan vain, kun osa vaatii
osaamista, jota ei ole järkevää odottaa jokaiselta tiimiltä:
matemaattinen malli, videokoodekki, reaaliaikainen kaupankäyntialgoritmi.
Peruste on kognitiivinen kuorma, ei koodin uudelleenkäyttö.

## Kolme vuorovaikutustapaa

Tiimityyppiä tärkeämpää on, miten tiimit ovat tekemisissä keskenään.

| Tapa | Mitä tapahtuu | Hinta | Sopii |
|---------------|---------------------------|----------------|-------------------|
| yhteistyö (*collaboration*) | kaksi tiimiä tekee tiiviisti yhdessä | korkea, rajat hämärtyvät | uuden asian selvittämiseen, rajatuksi ajaksi |
| palveluna (*X-as-a-Service*) | tiimi käyttää toisen tarjoamaa palvelua | matala, vaatii hyvän rajapinnan | vakiintuneeseen tarpeeseen |
| fasilitointi (*facilitating*) | tiimi auttaa toista oppimaan tai poistamaan esteen | kohtalainen | osaamisen siirtoon |

Yhteistyö on tavoista kallein, koska molemmat tiimit kantavat toisen
asiat mielessään. Siksi se on tarkoitettu väliaikaiseksi: kun yhdessä
on selvitetty, missä raja kulkee ja millainen rajapinta toimii,
siirrytään palvelusuhteeseen. Pysyvä tiivis yhteistyö kahden tiimin
välillä kertoo, että raja on väärässä paikassa. Tämä on sama havainto
kuin luvun 2 sykli: tilaus- ja maksutiimi, jotka muuttavat toistensa
rajapintoja joka viikko, ovat jatkuvassa yhteistyötilassa, halusivat
tai eivät.

```{.dot otsikko="Esimerkkiyrityksen topologia: virtatiimit käyttävät alustaa palveluna, ja muut tiimityypit tukevat niitä"}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.45;
  { rank=same; haku [label="hakutiimi"]; osto [label="ostotiimi"];
    tilaus [label="tilaustiimi"]; maksu [label="maksutiimi"]; }
  { rank=same; tuki [label="testaustuki\n(mahdollistava)", shape=ellipse];
    hinta [label="hinnoittelulaskenta\n(osajärjestelmä)", shape=octagon]; }
  alusta [label="alustatiimi", width=4.2];
  tuki -> haku [label="fasilitointi", style=dotted];
  hinta -> osto [label="palveluna", dir=back];
  tilaus -> maksu [label="yhteistyö", dir=both, style=bold];
  haku -> alusta [label="palveluna"]; osto -> alusta;
  tilaus -> alusta; maksu -> alusta;
}
```

## Tiimin rajapinta

Jotta palvelusuhde toimii, tiimin on oltava muille yhtä selkeä kuin
hyvän kirjaston. Kirja kutsuu tätä tiimin rajapinnaksi (*team API*).
Siihen kuuluvat tiimin omistama koodi ja palvelut, niiden versiointi
ja dokumentaatio, tiimin työtavat, viestintäkanavat ja vasteajat sekä
tieto siitä, mitä tiimi parhaillaan tekee ja mitä se aikoo tehdä.
Käytännössä se on yksi sivu, josta toinen tiimi näkee, miten palvelua
käytetään ilman palaveria ja mistä apua saa, kun se ei riitä.

## Mistä raja vedetään

Järjestelmän jakamiseen kirja tarjoaa murtumatasot (*fracture
planes*): luontevat saumat, joista kokonaisuus halkeaa siististi.

- **liiketoiminta-alue:** rajattu konteksti (ks.
  *Palveluarkkitehtuurit*) on useimmiten paras raja
- **sääntely:** esimerkiksi maksukorttitietoja käsittelevä osa
  erotetaan, jotta vaatimukset eivät koske koko järjestelmää
- **muutostahti:** viikoittain muuttuva osa erilleen vuosittain
  muuttuvasta
- **sijainti:** eri toimipaikkojen tai aikavyöhykkeiden tiimit
  (luku 10)
- **riski:** osa, jossa virhe on kallis, erilleen kokeiluista
- **suorituskyky:** osa, jolla on poikkeavat kuormavaatimukset
- **tekniikka:** vain jos tekniikka todella vaatii eri osaamista
- **käyttäjäryhmä:** esimerkiksi kuluttajat ja yritysasiakkaat

Tekniikka on listalla tarkoituksella loppupäässä. Jako
käyttöliittymään, taustaan ja tietokantaan on helpoin tehdä ja
tuottaa luvun 3 luovutusketjun.

## Topologia muuttuu

Topologia ei ole lopputila. Tyypillinen kaari: virtatiimi ja
alustatiimi tekevät uutta palvelua yhteistyössä muutaman viikon, sitten
alusta tarjoaa sen palveluna ja yhteistyö päättyy. Kirja kehottaa
tarkkailemaan merkkejä, jotka kertovat muutostarpeesta: ohjelmisto on
kasvanut liian suureksi yhdelle tiimille, toimitustahti hidastuu tai
tiimi odottaa jatkuvasti toista.

Topologian voi kirjoittaa datana ja tarkistaa siitä muutaman
nyrkkisäännön:

```{.python tiedosto="esimerkit/04-topologia.py" osa="topologia"}
```

```{.python tiedosto="esimerkit/04-topologia.py" osa="saannot"}
```

```{.tuloste tiedosto="esimerkit/04-topologia.odotettu"}
```

Raja-arvot (yhteistyötä enintään 12 viikkoa, fasilitointia enintään
puoli vuotta) ovat tämän esimerkin valintoja, eivät kirjan lukuja.
Tarkistin ei kerro, mitä pitää tehdä, mutta se tekee keskustelun
näkyväksi: maksutiimi on kahdessa pitkässä yhteistyösuhteessa yhtä
aikaa, ja testaustuki on ollut ostotiimin apuna vuoden.

## Kritiikki ja rajat

Mallin suosio ei ole todiste sen toimivuudesta. Seuraavat varaukset
on hyvä pitää mielessä.

- **Näyttö on tapauskertomuksia.** Kirja nojaa Conwayn lain
  tutkimukseen, toimituskyvyn tutkimukseen (*Accelerate*) ja
  yritysesimerkkeihin. Itse mallia, siis juuri näitä neljää tyyppiä ja
  kolmea tapaa, ei ole testattu vertailevilla tutkimuksilla.
- **Tyypit ovat ihanteita.** Todellinen tiimi on usein sekoitus:
  alustatiimi, joka myös ylläpitää yhtä tuotetta, tai virtatiimi,
  jolla on monimutkainen osajärjestelmä sisällään. Sanasto auttaa
  silti näkemään, mitä tiimiltä odotetaan.
- **Malli olettaa tuoteorganisaation.** Pysyvät tiimit, jaettavissa
  oleva arkkitehtuuri ja oma tuotanto ovat lähtöoletuksia. Projekteja
  myyvässä konsulttitalossa tai tiukasti säädellyssä laitekehityksessä
  ne eivät aina päde.
- **Pieni organisaatio ei tarvitse kaikkia tyyppejä.** Kymmenen hengen
  yrityksessä alusta on wikisivu ja mahdollistava tiimi yksi kokenut
  kehittäjä.
- **Kirja vaikenee paljosta.** Esihenkilötyö, urapolut, budjetointi ja
  palkitseminen jäävät käsittelemättä, vaikka ne usein ratkaisevat,
  onnistuuko muutos.
- **Nimenvaihto ei ole muutos.** Ylläpito-osaston nimeäminen
  alustatiimiksi ei muuta mitään, jos se palvelee edelleen tikettijonon
  kautta.

## Käytännössä

- **Aloita vuorovaikutuksesta.** Kysy jokaisesta tiimiparista, onko
  suhde yhteistyötä, palvelua vai fasilitointia ja pitäisikö sen olla.
  Epäselvä suhde on tavallisin kitkan lähde.
- **Aikarajaa yhteistyö.** Sovi alussa, mitä yhdessä selvitetään ja
  milloin siirrytään palvelusuhteeseen.
- **Kirjoita tiimin rajapinta auki.** Mitä omistamme, miten meitä
  käytetään, mistä meidät tavoittaa ja kuinka nopeasti vastaamme.
- **Perusta osajärjestelmätiimi vain osaamisen vuoksi.** ”Tätä koodia
  käyttää moni” ei riitä perusteeksi; se on kirjasto, ei tiimi.
- **Käytä mallia sanastona, älä tavoitetilana.** Kysymys ei ole,
  onko organisaatio Team Topologies -mallin mukainen, vaan odottaako
  jokin tiimi jatkuvasti toista.

## Itsearviointi

- Osaat nimetä neljä tiimityyppiä ja kertoa, miksi virtaan linjattu
  tiimi on niistä ensisijainen.
- Osaat kuvata kolme vuorovaikutustapaa ja perustella, miksi
  yhteistyön pitää olla väliaikaista.
- Osaat luetella, mitä tiimin rajapintaan kuuluu.
- Osaat valita järjestelmälle jakoperusteen murtumatasojen avulla ja
  perustella, miksi tekniikka on usein huono peruste.
- Osaat esittää mallista vähintään kolme varausta.
