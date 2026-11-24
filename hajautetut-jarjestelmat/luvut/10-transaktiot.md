# Hajautetut transaktiot

Transaktio muuttaa useaa asiaa niin, että joko kaikki muutokset
tapahtuvat tai mikään ei tapahdu. Yhdessä tietokannassa atomisuuden
takaa loki (ks. *SQL*). Kun muutettavat tiedot ovat eri solmuilla, eri
tietokannoissa tai eri palveluissa, solmujen on sovittava
lopputuloksesta, ja sopiminen on taas konsensusongelma. Tämä luku
toteuttaa kaksivaiheisen sitoutumisen, näyttää sen tunnetun estotilan
ja käsittelee idempotenssin, joka tekee uudelleenyrityksistä
turvallisia.

## Kaksivaiheinen sitoutuminen

Kaksivaiheisessa sitoutumisessa (*two-phase commit*, 2PC) yksi solmu on
*koordinaattori* ja muut *osallistujia*:

1. **Valmistelu.** Koordinaattori kirjaa transaktion alun ja pyytää
   osallistujia valmistautumaan. Osallistuja, joka voi sitoutua, kirjaa
   valmistelun levylle, lukitsee muutettavat tiedot ja äänestää kyllä.
   Muuten se äänestää ei ja voi perua heti.
2. **Päätös.** Jos kaikki äänestivät kyllä, koordinaattori kirjaa
   päätöksen *sitouta* lokiinsa, muuten *peru*. Kirjaus on
   sitoutumishetki. Sitten se lähettää päätöksen osallistujille, jotka
   soveltavat sen ja vapauttavat lukot.

Kyllä-ääni on lupaus: osallistuja ei saa enää perua omin päin, koska
koordinaattori on ehkä jo päättänyt sitoutua. Siksi valmistelu on
kirjattava pysyvästi ennen ääntä, ja siksi osallistuja on äänen jälkeen
koordinaattorin armoilla.

```{.cpp tiedosto="esimerkit/10-2pc.cpp" osa="levy"}
```

Koordinaattorin päätöksen kirjaaminen ja lähettäminen ovat omia
tapahtumiaan, jotta testi voi kaataa koordinaattorin kummasta tahansa
kohdasta. Palautuessaan koordinaattori lukee lokinsa: jos päätös on
siellä, se lähetetään uudelleen; jos transaktio alkoi mutta päätöstä
ei ole, transaktio perutaan (*presumed abort*):

```{.cpp tiedosto="esimerkit/10-2pc.cpp" osa="koordinaattori"}
```

Epätietoinen osallistuja kysyy päätöstä 100 ms välein:

```{.cpp tiedosto="esimerkit/10-2pc.cpp" osa="osallistuja"}
```

Koe kaataa koordinaattorin sekunniksi joko kaikkien äänten jälkeen
ennen päätöksen kirjaamista tai kirjaamisen jälkeen ennen lähettämistä.
Sarake *lukko* kertoo, kauanko osallistujat pitivät lukkoja, ja
*kyselyjä*, montako kertaa ne kysyivät päätöstä:

```{.tuloste tiedosto="esimerkit/10-2pc.odotettu"}
```

Ilman vikoja transaktio sitoutui (S) tai peruttiin (P) kaikilla
osallistujilla, ja lukkoja pidettiin noin 15 ms. Kun koordinaattori
kaatui viimeisen äänen jälkeen, osallistujat olivat *epätietoisia*
(*in doubt*): kaikki olivat äänestäneet kyllä, joten kukaan ei voinut
perua, eikä kukaan voinut sitouttaa, koska päätöstä ei ehkä ollut
tehty. Lukot pysyivät koko sekunnin, jonka koordinaattori oli
poissa, ja osallistujat kysyivät päätöstä 30 kertaa. Kumpikin
lopputulos on oikea: ennen päätöstä kaatunut koordinaattori perui,
päätöksen jälkeen kaatunut lähetti sitoutumisen uudelleen.

Tämä on 2PC:n *estotila* (*blocking*). Turvallisuus säilyy, mutta
eteneminen riippuu yhdestä solmusta. Kolmivaiheinen sitoutuminen (3PC)
lisää välivaiheen, jonka avulla osallistujat voivat päättää ilman
koordinaattoria, mutta se olettaa synkronisen verkon eikä kestä
verkon jakautumista. Käytännön ratkaisu on replikoida koordinaattorin
päätös konsensuksella: Spanner ja CockroachDB tekevät 2PC:n Raft- tai
Paxos-ryhmien välillä, jolloin koordinaattorin "kaatuminen" tarkoittaa
johtajan vaihtoa ryhmän sisällä, ei päätöksen katoamista.

XA-standardi toteuttaa 2PC:n tietokantojen ja viestijonojen välillä.
Sitä käytetään vähän, koska yksi hidas osallistuja pitää kaikkien lukkoja
ja koordinaattorin vika pysäyttää kaikki.

## Kun 2PC ei sovi

Palveluiden välillä 2PC on harvoin hyvä valinta: palvelut eivät halua
pitää lukkoja toisen palvelun puolesta, ja ulkoiset rajapinnat
(maksupalvelu, sähköposti) eivät tue valmisteluvaihetta. Vaihtoehto on
SAGA (Garcia-Molina ja Salem 1987): transaktio jaetaan paikallisiin
askeliin, joista jokainen sitoutuu heti, ja epäonnistumisen jälkeen
tehdyt askeleet kumotaan *korvaavilla toimenpiteillä*. SAGA luopuu
eristyksestä, sillä muut näkevät välitilat. Sen arkkitehtuuri,
orkestrointi ja koreografia käsitellään taidossa *Palveluarkkitehtuurit*.
SAGA nojaa kuitenkin kokonaan siihen, että jokaisen askeleen voi toistaa
turvallisesti.

## Idempotenssi

Luvun *Vikamallit ja simulaattori* ensimmäinen esimerkki näytti, että
uudelleenlähetetty pyyntö voi tulla käsitellyksi useasti. Verkossa
on kolme toimitusmallia:

- **Enintään kerran**: lähetä kerran, älä yritä uudelleen. Viestejä
  katoaa.
- **Vähintään kerran**: yritä uudelleen, kunnes kuittaus tulee. Viesti
  voi tulla käsitellyksi useasti.
- **Täsmälleen kerran**: mahdotonta toimituksena, koska lähettäjä ei voi
  erottaa kadonnutta pyyntöä kadonneesta kuittauksesta. Mahdollista
  *vaikutuksena*: vähintään kerran -toimitus ja vastaanottaja, joka
  tunnistaa toiston.

Toiston tunnistaa *idempotenssiavaimella*: asiakas antaa jokaiselle
loogiselle operaatiolle yksilöllisen tunnisteen ja lähettää saman
tunnisteen jokaisessa yrityksessä. Palvelin kirjaa käsitellyt avaimet
ja vastaa toistoon tallennetulla tuloksella:

```{.cpp tiedosto="esimerkit/10-idempotenssi.cpp" osa="palvelin"}
```

```{.cpp tiedosto="esimerkit/10-idempotenssi.cpp" osa="asiakas"}
```

Kokeessa asiakas tekee 50 tilisiirtoa verkossa, joka kadottaa 15 % ja
monistaa 5 % viesteistä, ja pankki kaatuu kymmenen kertaa:

```{.tuloste tiedosto="esimerkit/10-idempotenssi.odotettu"}
```

Enintään kerran hukkasi 13 siirtoa, ja asiakas tiesi vain 33:sta
varmasti. Vähintään kerran teki 56 siirtoa 50:n sijaan. Muistissa
pidetty avain korjasi verkon monistukset mutta ei kaatumisia: kolme
siirtoa tehtiin uudelleen, koska palvelin unohti avaimen kaatuessaan.
Vain pysyvä avain, joka tallennetaan samassa transaktiossa kuin
siirto, antoi täsmälleen 50.

Ehto "samassa transaktiossa" on olennainen. Jos siirto kirjataan ja
palvelin kaatuu ennen avaimen kirjaamista, toisto tehdään uudelleen.
Jos avain kirjataan ensin, kaatuminen hukkaa siirron. Kafkan
transaktiot, Stripen idempotenssiavaimet ja tietokannan
yksilöllisyysrajoite (*unique constraint*) ovat saman ajatuksen
toteutuksia.

## Käytännössä

- **Vältä hajautettuja transaktioita, jos voit.** Sijoita yhdessä
  muuttuva tieto samaan osioon tai palveluun. Hajautettu transaktio on
  aina hitaampi ja hauraampi kuin paikallinen.
- **Replikoi koordinaattori.** Jos 2PC on välttämätön, koordinaattorin
  päätöksen on oltava vikasietoinen, käytännössä konsensusryhmässä.
- **Rajaa lukkojen kesto.** Epätietoinen osallistuja pitää lukkojaan,
  kunnes saa päätöksen. Valvo epätietoisia transaktioita ja varaudu
  käsin ratkaisuun.
- **Tee jokaisesta muuttavasta rajapinnasta idempotentti.** Asiakas
  luo avaimen ennen ensimmäistä yritystä, ja palvelin tallentaa sen
  samassa transaktiossa kuin muutoksen.
- **Täsmälleen kerran on vaikutus, ei toimitus.** Kun järjestelmä lupaa
  täsmälleen kerran, selvitä, missä toisto tunnistetaan ja mitä
  tapahtuu kaatumisen jälkeen.

## Itsearviointi

- Osaat kuvata kaksivaiheisen sitoutumisen vaiheet ja sen, mitä kukin
  osapuoli kirjaa pysyvästi ja milloin.
- Osaat selittää 2PC:n estotilan ja sen, miksi osallistuja ei voi
  päättää yksin kyllä-äänen jälkeen.
- Osaat kertoa, miten Spanner ja CockroachDB poistavat estotilan, ja
  milloin SAGA on parempi valinta.
- Osaat erottaa enintään kerran-, vähintään kerran- ja täsmälleen
  kerran -mallit ja perustella, miksi täsmälleen kerran on mahdollinen
  vain vaikutuksena.
- Osaat toteuttaa idempotenssiavaimen niin, että se kestää palvelimen
  kaatumisen.
