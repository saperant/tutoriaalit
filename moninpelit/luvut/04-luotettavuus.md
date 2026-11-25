# Luotettavuuskerros

UDP:n päälle rakennetaan kerros, joka tekee neljä asiaa: muodostaa
yhteyden, tunnistaa paketit sekvenssinumerolla, kertoo vastapuolelle
mitkä paketit saapuivat ja lähettää uudelleen vain sen, mikä ei saa
kadota. Tilapäivityksiä ei
lähetetä uudelleen, koska seuraava päivitys korvaa ne. Tapahtumat, kuten
esineen poimiminen tai chat-viesti, on saatava perille täsmälleen kerran.

## Yhteys UDP:n päällä

UDP:ssä ei ole yhteyksiä: jokainen datagrammi on erillinen, ja
lähettäjän osoitteen voi väärentää. Peli tarvitsee silti *yhteyden*:
palvelimen on tiedettävä, ketkä ovat mukana, ja huomattava, kun joku
katoaa. Yhteys rakennetaan kolmesta osasta: kättelystä, joka todistaa
osoitteen, aikakatkaisusta ja elossaoloviesteistä.

```{.cpp tiedosto="esimerkit/04-yhteys.cpp" osa="viestit"}
```

Palvelin ei varaa pelaajalle paikkaa ensimmäisestä viestistä. Se vastaa
*haasteella*: luvulla, jonka se laskee salaisuudestaan, lähettäjän
osoitteesta ja asiakkaan arpomasta luvusta. Vasta kun asiakas palauttaa
haasteen, palvelin tietää, että asiakas todella vastaanottaa viestit
ilmoittamassaan osoitteessa. Haastetta ei tallenneta, joten väärennetty
pyyntö ei kuluta palvelimen muistia.

```{.cpp tiedosto="esimerkit/04-yhteys.cpp" osa="haaste"}
```

Asiakas on pieni tilakone. Jokainen vaihe lähetetään uudelleen, kunnes
seuraava viesti saapuu, koska kättelyn viestit katoavat siinä missä
muutkin.

```{.cpp tiedosto="esimerkit/04-yhteys.cpp" osa="asiakas"}
```

```{.tuloste tiedosto="esimerkit/04-yhteys.odotettu"}
```

![Sama kättely aikajanana 20 %:n häviöllä. Ensimmäinen pyyntö, kaksi
vastausta ja yksi hyväksyntä katoavat (rastit); uudelleenlähetys 200 ms:n
välein vie kättelyn silti läpi. Palvelin varaa paikan hetkellä 541 ms,
kun ensimmäinen vastaus saapuu.](kuvat/kattely.png){width=95%}

Tuhat pyyntöä väärennetyistä osoitteista ei varaa yhtään paikkaa, eikä
sokkona arvattu vastaus kelpaa. Haasteviesti ei myöskään ole pyyntöä
suurempi; muuten palvelinta voisi käyttää liikenteen vahvistamiseen
kolmatta osapuolta vastaan. Kun asiakas hiljenee, palvelin purkaa
yhteyden viiden sekunnin aikakatkaisulla. Elossaoloviesti kerran
sekunnissa pitää yhteyden auki silloinkin, kun pelillä ei ole
lähetettävää. Oikea toteutus lisää salauksen ja todennuksen: haaste
todistaa osoitteen, ei pelaajan henkilöllisyyttä.

### Yhteys osoitteenmuunnoksen läpi

Kotireititin tekee osoitteenmuunnoksen (NAT): sisäverkon koneet näkyvät
ulos yhtenä julkisena osoitteena, ja sisään pääsee vain liikenne, joka
vastaa sisältä lähteneeseen. Asiakas–palvelin-mallissa tämä ei haittaa,
koska asiakas aloittaa aina. Kahden pelaajan suora yhteys ei sen sijaan
synny itsestään, koska kummankin reititin pudottaa toisen ensimmäisen
paketin.

```{.cpp tiedosto="esimerkit/04-nat.cpp" osa="nat"}
```

*Reiän avaamisessa* (hole punching) molemmat pelaajat kysyvät ensin
yhteiseltä palvelimelta toistensa julkiset osoitteet ja lähettävät
sitten toisilleen yhtä aikaa. Kummankin oma lähetys luo säännön, joka
päästää toisen paketit sisään.

```{.cpp tiedosto="esimerkit/04-nat.cpp" osa="reika"}
```

```{.tuloste tiedosto="esimerkit/04-nat.odotettu"}
```

Esimerkin NAT on pelkistys. Osa reitittimistä antaa jokaiselle
kohteelle eri julkisen portin (symmetrinen NAT), jolloin palvelimen
näkemä osoite ei kelpaa toiselle pelaajalle eikä reikä aukea. Siksi
vertaisyhteyksien rinnalle tarvitaan aina välityspalvelin, jonka kautta
liikenne kulkee, kun suora yhteys ei onnistu. Osoitteiden selvitys
(STUN), välitys (TURN) ja niiden yhdistelmä (ICE) ovat valmiita
protokollia, joita pelikirjastot käyttävät.

## Sekvenssinumerot

Kun yhteys on olemassa, jokainen paketti saa juoksevan numeron. 16-bittinen numero riittää, jos
vertailu sietää kierron: 60 paketin sekuntivauhdilla 65 536 kuluu
reilussa 18 minuutissa, ja sen jälkeen numerot alkavat alusta.

```{.cpp tiedosto="esimerkit/04-sekvenssit.cpp" osa="uudempi"}
```

```{.tuloste tiedosto="esimerkit/04-sekvenssit.odotettu"}
```

Etumerkillinen erotus tulkitsee luvun uudemmaksi, jos se on enintään
puoli kierrosta edellä. Naiivi `a > b` erehtyy heti kierron jälkeen, ja
virhe näkyy vasta pitkässä pelissä: vastaanottaja alkaa hylätä kaikki
uudet paketit "vanhoina". 40 000 on 100:aa yli puoli kierrosta edellä,
joten se tulkitaan vanhemmaksi; käytännössä niin vanha paketti on joka
tapauksessa hylättävä.

## Kuittauskenttä

TCP kuittaa jokaisen segmentin erikseen. Pelipaketissa kuittaukset
kulkevat vastakkaiseen suuntaan menevien pakettien mukana ilmaiseksi:
jokaisessa paketissa on uusin vastaanotettu numero ja 32 bitin kenttä,
jossa bitti *i* kertoo, saapuiko paketti *uusin − 1 − i*. Yksi paketti
kuittaa siis 33 viimeisintä, ja yksittäinen kadonnut kuittaus korvautuu
seuraavalla.

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="paketti"}
```

![Paketin rakenne ja kuittauskentän tulkinta. Kun uusin vastaanotettu
on 105, kentän bitti 0 kertoo paketista 104, bitti 1 paketista 103 ja
niin edelleen 32 paketin verran.](kuvat/paketti.png){width=90%}

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="vastaanotto"}
```

Lähettäjä muistaa, mitkä tapahtumat kukin paketti kuljetti. Kun paketti
kuitataan, sen tapahtumat poistuvat jonosta. Kuittaamaton tapahtuma
lisätään uudelleen pakettiin, kun edellisestä lähetyksestä on kulunut
yli kiertoviiveen verran:

```{.cpp tiedosto="esimerkit/04-kuittaukset.cpp" osa="lahetys"}
```

```{.tuloste tiedosto="esimerkit/04-kuittaukset.odotettu"}
```

![Ote samasta ajosta. Asiakkaan paketti 97 kuljettaa tapahtuman 16 ja
katoaa. Palvelimen paketit kuittaavat sen jälkeen numerot 96, 98, 99 ja
100, mutta eivät 97:ää, joten tapahtuma pysyy jonossa ja lähtee
uudelleen paketissa 102, kun 150 ms on
kulunut.](kuvat/kuittaukset.png){width=95%}

15 %:n häviöllä kaikki 50 tapahtumaa käsiteltiin, ja yhdeksän niistä
tarvitsi uudelleenlähetyksen. Uudelleenlähetys voi johtaa
kaksoiskappaleeseen, jos alkuperäinen paketti saapui mutta sen kuittaus
katosi. Vastaanottaja tunnistaa kaksoiskappaleen tapahtuman tunnisteesta
ja käsittelee sen vain kerran: lopputulos on *täsmälleen kerran*,
vaikka verkko toimittaa *vähintään kerran*.

## Järjestys ja kanavat

Kaikki luotettavat viestit eivät tarvitse järjestystä. Chat-viestien
järjestyksellä on väliä, mutta kahden pelaajan esinepoiminnat ovat
toisistaan riippumattomia. Kerroksessa on siksi usein useita
*kanavia*: epäluotettava (tila), luotettava järjestämätön (tapahtumat)
ja luotettava järjestetty (chat, kauppa). Järjestetty kanava pidättää
vain omat viestinsä, ei koko yhteyttä.

## Käytännössä

- **Haaste ennen tilaa.** Palvelin ei varaa mitään eikä lähetä pyyntöä
  suurempaa vastausta osoitteeseen, jota ei ole varmistettu.
- **Aikakatkaisu ja elossaolo** kumpaankin suuntaan: myös asiakkaan on
  huomattava, että palvelin on kadonnut, ja kerrottava se pelaajalle.
- **Kuittaukset kulkevat vastakkaisen liikenteen mukana.** Erillistä
  kuittauspakettia ei tarvita, koska peli lähettää kumpaankin suuntaan
  jatkuvasti.
- **Sekvenssinumeroiden vertailu aina kierron sietävällä funktiolla.**
  Testaa kierto erikseen: aloita testi numerosta 65 500.
- **Tunnisteet tapahtumille, ei paketeille.** Sama tapahtuma voi kulkea
  useassa paketissa; vastaanottaja tunnistaa sen tunnisteesta.
- **Kiertoviiveen arvio kuittauksista.** Lähetysajan ja kuittauksen
  välinen aika antaa RTT:n ilman erillisiä pingejä; tasoita se
  liukuvalla keskiarvolla.
- **Hinta:** luotettava viesti vie tilaa jokaisessa paketissa, kunnes se
  kuitataan. Suuret luotettavat viestit (kartan lataus) pilkotaan ja
  lähetetään omalla kanavallaan, jotta ne eivät syrjäytä tilapäivityksiä.

## Itsearviointi

- Osaat rakentaa UDP:n päälle yhteyden: kättelyn haasteella,
  aikakatkaisun ja elossaoloviestit, ja perustella haasteen tarpeen.
- Osaat selittää, miksi kaksi NATin takana olevaa pelaajaa ei saa
  suoraa yhteyttä ilman reiän avaamista tai välityspalvelinta.
- Osaat vertailla kiertäviä sekvenssinumeroita oikein ja selittää,
  miksi naiivi vertailu rikkoutuu.
- Osaat toteuttaa kuittauskentän, joka kuittaa 33 viimeisintä pakettia.
- Osaat toteuttaa valikoivan uudelleenlähetyksen ja kaksoiskappaleiden
  tunnistuksen.
- Osaat jakaa pelin viestit epäluotettaviin ja luotettaviin kanaviin.
