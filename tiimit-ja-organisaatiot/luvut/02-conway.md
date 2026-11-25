# Conwayn laki

Johdannon esimerkissä tiimijako päätti, mitkä muutokset ovat halpoja.
Sama pätee toiseen suuntaan: tiimijako päättää myös, millainen
järjestelmästä tulee. Tämä luku käy läpi väitteen, sen näytön ja
tavat mitata sitä omasta koodista.

## Alkuperäinen väite

Melvin Conway esitti vuonna 1968 artikkelissaan *How Do Committees
Invent?*, että järjestelmiä suunnitteleva organisaatio tuottaa
väistämättä suunnitelmia, joiden rakenne jäljittelee organisaation
viestintärakennetta. Fred Brooks antoi havainnolle nimen Conwayn laki
kirjassaan *The Mythical Man-Month*.

Perustelu on yksinkertainen. Kaksi osaa voi toimia yhdessä vain, jos
niiden tekijät sopivat rajapinnasta, ja sopiminen vaatii viestintää.
Missä viestintää on paljon, rajapinnat ovat rikkaita ja osat kietoutuvat
toisiinsa. Missä viestintää on vähän, syntyy kapea ja muodollinen
rajapinta tai ei rajapintaa lainkaan. Conwayn oma esimerkki on
kääntäjä: jos kääntäjää tekee neljä ryhmää, siitä tulee nelivaiheinen.

Laki ei väitä, että rakenne olisi hyvä tai huono. Se sanoo, että
organisaatio rajaa suunnitelmat, jotka ylipäätään voivat syntyä. Conway
päätteli tästä, että organisaation pitää voida muuttua suunnittelun
edetessä, koska ensimmäinen käsitys rakenteesta on harvoin paras.

## Sosiotekninen järjestelmä

Ajatus on vanhempi kuin ohjelmistoala. Eric Trist ja Ken Bamforth
tutkivat 1950-luvun alussa brittiläisiä hiilikaivoksia ja havaitsivat,
ettei uusi louhintatekniikka parantanut tuottavuutta, kun se rikkoi
työryhmien totutun tavan jakaa vastuuta. Tästä syntyi käsite
**sosiotekninen järjestelmä**: tekninen järjestelmä ja sitä käyttävä
ihmisten järjestelmä on suunniteltava yhdessä, koska kumpikaan ei toimi
ilman toista.

Ohjelmistossa tekninen puoli on koodi, rajapinnat ja tuotantoympäristö,
sosiaalinen puoli tiimit, vastuut ja viestintäkanavat. Arkkitehtuurin
muutos, joka ei muuta vastuita, jää usein kuvaksi wikiin. Vastuiden
muutos, jota arkkitehtuuri ei tue, tuottaa tiimejä, jotka eivät voi
toimittaa mitään yksin.

## Mitä laista tiedetään

Conwayn artikkelissa ei ollut mittauksia. Myöhempi tutkimus on
testannut väitettä nimellä **peilaushypoteesi** (*mirroring
hypothesis*).

- MacCormack, Baldwin ja Rusnak (2012) vertasivat ohjelmistopareja,
  joilla oli sama tehtävä mutta eri tekijäorganisaatio: tiivis
  yrityksen tiimi tai löyhä avoimen lähdekoodin yhteisö. Löyhästi
  kytkeytyneiden yhteisöjen tuotteet olivat selvästi modulaarisempia.
- Colfer ja Baldwin (2016) kävivät läpi yli sata empiiristä tutkimusta
  eri aloilta. Selvä enemmistö tuki hypoteesia, mutta poikkeuksiakin
  löytyi: avoimen lähdekoodin yhteisöissä ja yritysten välisessä
  yhteistyössä rakenteet eivät aina peilaa toisiaan, kun yhteinen
  alusta ja avoin viestintä korvaavat organisaatiorajat.
- Nagappan, Murphy ja Basili (2008) ennustivat Windows Vistan
  binäärien vikaherkkyyttä. Organisaatiota kuvaavat mittarit, kuten
  koodia muokanneiden insinöörien ja organisaatioiden määrä, ennustivat
  vikoja paremmin kuin koodin omat mittarit.
- Cataldo ja Herbsleb kollegoineen mittasivat, kuinka hyvin tiimien
  todellinen koordinointi vastasi koodin riippuvuuksia. Kun vastaavuus
  oli hyvä, muutospyynnöt valmistuivat nopeammin.

Näyttö on siis vahvaa siinä, että organisaation ja järjestelmän
rakenteet korreloivat ja että niiden epäsuhta maksaa. Näyttö on
heikompaa siitä, mikä tietty organisaatiorakenne on paras. Laki on
taipumus, ei luonnonlaki.

## Käänteinen Conway-liike

Jos rakenne seuraa organisaatiota, organisaatio kannattaa suunnitella
halutun rakenteen mukaan. Tätä kutsutaan käänteiseksi Conway-liikkeeksi
(*inverse Conway maneuver*): ensin päätetään tavoitearkkitehtuuri,
sitten muodostetaan tiimit sen osien ympärille.

Liikkeellä on rajansa. Tiimien siirtely ei itsessään muuta koodia:
vanha rakenne on olemassa, ja uudet tiimit joutuvat aluksi muuttamaan
toistensa osia. Lisäksi tavoitearkkitehtuuri on arvaus. Jos arvaus on
väärä, organisaatio jähmettää väärän rakenteen. Siksi liike tehdään
pienin askelin ja mitataan, lähenivätkö rakenteet toisiaan (luku 10).

## Mittaaminen: riippuvuudet tiimirajojen yli

Yksinkertaisin mittari lasketaan riippuvuusverkosta: kuinka moni
riippuvuus ylittää tiimirajan ja syntyykö tiimien välille syklejä.
Tiimiverkossa tiimi A riippuu tiimistä B, jos jokin A:n osa kutsuu B:n
osaa:

```{.python tiedosto="esimerkit/02-conway.py" osa="tiimiverkko"}
```

Sykli tiimien välillä tarkoittaa, ettei kumpikaan voi julkaista
muutostaan sopimatta toisen kanssa. Syklit löytyvät vahvoista
komponenteista (ks. *Algoritmit*); näin pienessä verkossa riittää
tarkistaa, ketkä tavoittavat toisensa:

```{.python tiedosto="esimerkit/02-conway.py" osa="syklit"}
```

```{.tuloste tiedosto="esimerkit/02-conway.odotettu"}
```

Kerrosjaossa kahdeksan kahdestatoista riippuvuudesta ylittää tiimirajan,
mutta ne kulkevat yhteen suuntaan. Ominaisuusjaossa ylittäviä on neljä,
ja kaksi niistä muodostaa syklin: tilaus aloittaa maksun, ja maksu
ilmoittaa tilansa tilaukselle. Vaihtoehtoja on kolme: yhdistää
tilaus ja maksu yhden tiimin vastuulle, katkaista sykli tapahtumilla
(maksu julkaisee tapahtuman eikä kutsu tilausta; ks.
*Palveluarkkitehtuurit*) tai hyväksyä tiivis yhteistyö tietoisesti.

## Mittaaminen: mitkä osat muuttuvat yhdessä

Staattinen riippuvuus kertoo, mikä voisi vaatia koordinointia.
Versionhallinnan historia kertoo, mikä on vaatinut. Jos kaksi
tiedostoa muuttuu usein samassa muutoksessa, ne ovat kytköksissä,
vaikkei koodissa näkyisi riippuvuutta (*co-change*, looginen kytkentä).
Esimerkkihistoriassa on 160 muutosta. Lokista luetaan jokaisen
muutoksen tekijä ja tiedostot:

```{.python tiedosto="esimerkit/historia.py" osa="loki"}
```

Jokaisesta muutoksesta lasketaan tiedostoparit ja kytkentäaste:

```{.python tiedosto="esimerkit/02-yhteismuutokset.py" osa="parit"}
```

Sama historia kertoo, montako tiimiä kukin muutos olisi vaatinut
kummallakin tiimijaolla:

```{.python tiedosto="esimerkit/02-yhteismuutokset.py" osa="tiimit"}
```

```{.tuloste tiedosto="esimerkit/02-yhteismuutokset.odotettu"}
```

Useimmin yhdessä muuttuvat saman ominaisuuden eri kerrokset. Kerrosjako
leikkaa juuri näiden parien välistä, joten kaksi muutosta kolmesta
vaatii usean tiimin työtä. Ominaisuusjaossa osuus on alle kolmannes.
Toiseksi yleisin pari on kuitenkin `maksu/api` ja `tilaus/api`: sama
kytkös, joka näkyi syklinä riippuvuusverkossa. Historia siis sekä
tukee ominaisuusjakoa että osoittaa sen heikon kohdan.

![Yhdessä muuttuneiden osien määrät esimerkkihistoriassa. Lävistäjän
lohkot ovat saman ominaisuuden kerroksia; niiden ulkopuolella erottuu
tilauksen ja maksun kytkös.](kuvat/yhteismuutokset.png){width=48%}

Oman repositorion analyysiin riittää `git log --name-only`. Tuloksilla
on kolme rajoitusta. Suuret siivousmuutokset (muotoilu,
uudelleennimeäminen) kytkevät kaiken kaikkeen ja kannattaa suodattaa
pois. Usean repositorion muutoksiksi jaetun työn kytkös ei näy. Ja
historia näyttää nykyisen organisaation tuottaman rakenteen, ei sitä,
mikä olisi mahdollista.

## Käytännössä

- **Piirrä molemmat kartat.** Tiimien viestintäsuhteet ja järjestelmän
  riippuvuudet rinnakkain paljastavat epäsuhdan: riippuvuus ilman
  viestintäkanavaa on tuleva integraatiovirhe, viestintäkanava ilman
  riippuvuutta turhaa palaverointia.
- **Mittaa muutoksista, älä kaaviosta.** Tiimijaon hyvyys näkyy siinä,
  kuinka suuri osa muutoksista pysyy yhden tiimin sisällä. Laske se
  historiasta ennen ja jälkeen uudelleenjärjestelyn ja toista mittaus,
  kun tuote muuttuu.
- **Sykli tiimien välillä on hälytys.** Kaksi tiimiä, jotka eivät voi
  julkaista erikseen, ovat käytännössä yksi tiimi kahdella työjonolla.
- **Älä suunnittele arkkitehtuuria, jota organisaatio ei voi
  ylläpitää.** Kaksikymmentä mikropalvelua viiden hengen tiimillä on
  epäsuhta, samoin jaettu monoliitti kymmenellä tiimillä.

## Itsearviointi

- Osaat selittää Conwayn lain ja perustella sen viestinnän tarpeella.
- Osaat kertoa, mitä peilaushypoteesin tutkimus tukee ja mihin se ei
  ota kantaa.
- Osaat laskea tiimirajan ylittävät riippuvuudet, tunnistaa tiimien
  välisen syklin ja arvioida tiimijakoa Git-historian yhdessä
  muuttuvista tiedostoista.
- Osaat kuvata käänteisen Conway-liikkeen ja sen kaksi riskiä.
