# Hajautetut tiimit ja organisaation muuttaminen

Kaksi asiaa on vielä käsittelemättä: mitä etäisyys tekee tiimien
väliselle työlle ja miten organisaation rakennetta muutetaan
rikkomatta sitä, mikä toimii.

## Etäisyys on rajapinta

Thomas Allen mittasi 1970-luvulla insinöörien viestintää ja havaitsi,
että sen tiheys putoaa jyrkästi etäisyyden kasvaessa: jo muutaman
kymmenen metrin päässä istuvien kanssa puhuttiin yhtä harvoin kuin
toisessa rakennuksessa olevien. Herbsleb ja Mockus (2003) vertasivat
ohjelmistoyrityksessä muutoksia, jotka tehtiin yhdellä paikkakunnalla,
niihin, joihin osallistui usea toimipaikka. Hajautetut muutokset
kestivät noin kaksi ja puoli kertaa niin kauan, ja ero selittyi
pääosin sillä, että niihin tarvittiin enemmän ihmisiä.

Etäisyys toimii siis kuin tiimiraja: se vähentää satunnaista
viestintää ja tekee koordinoinnista kalliimpaa. Conwayn lain mukaan
se myös muovaa järjestelmää. Siksi sijainti on yksi luvun 4
murtumatasoista: jos organisaatio on kahdella paikkakunnalla,
järjestelmän raja kannattaa vetää samaan kohtaan, jotta tiivis
yhteistyö tapahtuu paikan sisällä ja paikkojen välillä riittää
rajapinta.

Etätyö muuttaa asetelmaa. Kun koko tiimi työskentelee etänä, kukaan
ei ole käytäväkeskustelujen ulkopuolella, ja tiimi joutuu
kirjoittamaan asiat näkyviin. Hankalin muoto on sekamalli, jossa osa
tiimistä on samassa huoneessa ja osa ei: päätökset syntyvät huoneessa,
ja etäjäsenet kuulevat niistä jälkikäteen.

## Aikavyöhykkeet

Aikaero on etäisyyden kovin muoto, koska se poistaa yhteisen työajan.
Lasketaan viiden toimipaikan yhteinen työaika, kun työpäivä on
kaikkialla yhdeksästä viiteen:

```{.python tiedosto="esimerkit/10-aikavyohykkeet.py" osa="yhteinen"}
```

Yhteistä aikaa tärkeämpi luku on usein kysymyksen kiertoaika:
kuinka kauan kestää, että kysyjä saa vastauksen luettavakseen.

```{.python tiedosto="esimerkit/10-aikavyohykkeet.py" osa="kierto"}
```

```{.tuloste tiedosto="esimerkit/10-aikavyohykkeet.odotettu"}
```

Helsingillä ja Lontoolla on kuusi yhteistä tuntia, ja aamulla kysytty
kysymys palaa kolmessa tunnissa. Helsingillä ja New Yorkilla yhteistä
aikaa on tunti, ja aamun kysymykseen saa vastauksen seuraavana aamuna.
San Franciscon kanssa yhteistä työaikaa ei ole lainkaan. Jos asian
selvittäminen vaatii kolme kysymystä ja vastausta, se vie Lontoon
kanssa työpäivän ja San Franciscon kanssa kolme.

Tästä seuraa kaksi sääntöä. Tiimin jäsenillä pitää olla riittävästi
yhteistä työaikaa, käytännössä vähintään puoli päivää. Ja tiimien,
joilla yhteistä aikaa ei ole, välisen suhteen on oltava palvelusuhde
(luku 4): rajapinta ja dokumentaatio ovat niin hyvät, ettei kysymyksiä
juuri tarvita.

## Asynkroninen viestintä

Kun yhteistä aikaa on vähän, työ nojaa viestintään, joka ei vaadi
samanaikaisuutta.

- **Kirjoita ensin.** Ehdotus, perustelu ja päätös ovat dokumentissa,
  ei kokouksen muistissa (luku 8). Kokous on poikkeus, johon tullaan
  luettuaan.
- **Kysy niin, ettei tarvita vastakysymystä.** Mitä yritit, mitä
  tapahtui, mitä odotit ja mihin mennessä tarvitset vastauksen.
  Jokainen säästetty kierros on aikaeron verran.
- **Tee tila näkyväksi.** Tehtävätaulu, päivän päätteeksi kirjattu
  tilanne ja selkeät vastuut korvaavat sen, mitä samassa huoneessa
  näkisi vilkaisemalla.
- **Sovi vasteajat.** Tiimin rajapintaan kuuluu, kuinka nopeasti
  mihinkin kanavaan vastataan.
- **Varaa yhteinen aika siihen, mihin teksti ei riitä.** Suunnittelu,
  erimielisyydet, tutustuminen ja retrospektiivit hyötyvät
  samanaikaisuudesta.

Asynkroninen työ ei ole vain hajautettujen tiimien asia. Sama
kirjoittamisen kuri auttaa jokaista tiimiä, jonka jäsenet haluavat
keskittyä ilman keskeytyksiä.

## Organisaation muuttaminen pienin askelin

Organisaatiomuutos on kallis. Kun tiimit kootaan uudelleen, jokainen
palaa muodostumisvaiheeseen (luku 5), omistajuudet katkeavat ja
toimitus hidastuu kuukausiksi. Suuri kertamuutos lyö lisäksi vetoa
yhden arvauksen puolesta: jos uusi rakenne on väärä, se selviää
vasta, kun kaikki on jo siirretty. Siksi rakennetta kannattaa muuttaa
kuten koodia, pienin ja peruttavin askelin.

1. **Mittaa nykytila.** Kuinka suuri osa muutoksista vaatii usean
   tiimin (luku 2)? Missä työ odottaa (luku 3)? Missä tiimit kokevat
   ylikuormaa (luku 5)? Ilman lähtötasoa muutoksen vaikutusta ei voi
   arvioida.
2. **Valitse yksi kipein raja.** Esimerkiksi tilaus- ja maksutiimin
   sykli tai luovutus, jossa työ odottaa viikon.
3. **Kokeile pienintä muutosta.** Usein se ei ole tiimien siirto vaan
   vuorovaikutustavan muutos: sovittu rajapinta, lyhyempi ottoväli,
   itsepalvelu tiketin tilalle tai yhden ihmisen lainaaminen toiseen
   tiimiin määräajaksi.
4. **Siirrä rajaa vasta sitten.** Jos raja on väärässä paikassa,
   siirrä vastuu tai jaa tiimi murtumatasoa pitkin. Yksi tiimi
   kerrallaan, ja tiimi itse mukana suunnittelussa.
5. **Mittaa uudelleen** ja päätä seuraava askel.

Tapa on sama kuin Kanban-menetelmän periaate aloittaa siitä, mitä
nyt tehdään, ja parantaa asteittain. Se on myös rehellinen sille,
mitä luvuissa 4 ja 9 todettiin näytöstä: koska mikään malli ei ole
todistetusti paras, oman organisaation mittaukset ovat parasta
saatavilla olevaa tietoa.

Muutos ei ole pelkkää rakennetta. Jos tavoitteet, mittarit ja
palkitseminen pysyvät ennallaan, ihmiset toimivat kuten ennenkin
uusilla nimikkeillä (luku 3). Ja koska muutos koskee ihmisten työtä
ja asemaa, se onnistuu parhaiten, kun ne, joita se koskee, ovat
mukana päättämässä siitä.

## Käytännössä

- **Vedä järjestelmän raja toimipaikkojen väliin.** Älä jaa yhtä
  tiivistä tiimiä kahdelle mantereelle.
- **Laske kiertoaika ennen kuin sovit yhteistyöstä.** Jos vastaus
  tulee seuraavana päivänä, yhteinen suunnittelu on hidasta, ja suhteen
  on oltava palvelusuhde.
- **Kohtele kaikkia etäjäseninä, jos yksikin on.** Kokous, jossa
  jokainen on omalla koneellaan, on tasapuolisempi kuin huone ja kaksi
  ruutua.
- **Muuta yksi asia kerrallaan.** Uusi tiimijako, uusi prosessi ja
  uusi työkalu samalla kertaa tekevät mahdottomaksi tietää, mikä
  vaikutti.
- **Anna muutokselle aikaa.** Tiimin suorituskyky notkahtaa aina
  muutoksen jälkeen. Arvioi tulosta kuukausien, ei viikkojen kuluttua.

## Itsearviointi

- Osaat selittää, miksi etäisyys toimii kuin tiimiraja, ja mitä siitä
  seuraa järjestelmän rajoille.
- Osaat laskea toimipaikkojen yhteisen työajan ja kysymyksen
  kiertoajan.
- Osaat nimetä asynkronisen viestinnän käytännöt ja kertoa, mihin
  yhteinen aika kannattaa käyttää.
- Osaat suunnitella organisaatiomuutoksen pieninä, mitattavina
  askelina ja perustella, miksi suuri kertamuutos on riski.
