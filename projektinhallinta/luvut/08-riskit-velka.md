# Riskit, tekninen velka ja laatu

Riski on epävarma tapahtuma, joka toteutuessaan haittaa projektia.
Tekninen velka on oikotie, joka nopeuttaa työtä nyt ja hidastaa sitä
myöhemmin. Laatu on se, mitä kummankin laiminlyönti lopulta maksaa.
Yhteistä kolmelle on, että kustannus tulee myöhemmin kuin päätös, ja
siksi ne jäävät helposti kiireen jalkoihin.

## Riskien tunnistaminen

Riskienhallinta alkaa listasta. Tom DeMarco ja Timothy Lister
kiteyttävät asian niin, että riskienhallinta on projektinhallintaa
aikuisille: tunnustetaan, että asiat voivat mennä vikaan, ja
varaudutaan siihen sen sijaan, että toivotaan parasta.

Ohjelmistoprojektin tavallisimmat riskit toistuvat hankkeesta toiseen:

- vaatimukset muuttuvat tai ne on ymmärretty väärin,
- arvio on liian optimistinen,
- avainhenkilö lähtee tai sairastuu,
- ulkoinen riippuvuus (toimittaja, rajapinta, laite, viranomainen)
  myöhästyy,
- tekniikka ei toimi oletetulla tavalla tai ei skaalaudu,
- integraatio muihin järjestelmiin on oletettua vaikeampi,
- tuotantodata on erilaista kuin testidata.

Tunnistamisen hyvä väline on **ennakoiva ruumiinavaus** (*pre-mortem*),
jonka Gary Klein on kuvannut. Tiimi kuvittelee, että projekti on
päättynyt ja epäonnistunut pahasti, ja jokainen kirjoittaa itsekseen,
miksi niin kävi. Asetelma antaa luvan sanoa ääneen epäilyt, joita
suunnitteluvaiheen toiveikkuudessa ei muuten sanota.

## Riskirekisteri

Tunnistetut riskit kirjataan **rekisteriin**, jossa jokaisella on
todennäköisyys, vaikutus, omistaja ja suunnitelma. Todennäköisyyden ja
vaikutuksen tulo on **altistus**, jolla riskit pannaan järjestykseen.

```{.python tiedosto="esimerkit/08-riskit.py" osa="rekisteri"}
```

Jokaiselle riskille valitaan toimintatapa:

| Tapa | Merkitys | Esimerkki |
|------------|--------------------------------------|----------------------------------------|
| vältä | muutetaan suunnitelmaa niin, ettei riski voi toteutua | jätetään riskialtis integraatio pois ensimmäisestä julkaisusta |
| pienennä | lasketaan todennäköisyyttä tai vaikutusta | kuormitustesti heti, tiedon jakaminen tiimissä |
| siirrä | toinen osapuoli kantaa seuraukset | sopimussakko toimittajalle, vakuutus |
| hyväksy | ei tehdä mitään etukäteen, varataan puskuri | pieni riski, jonka torjunta maksaisi enemmän |

Altistusten summa on odotusarvo. Se ei ole varaus, koska riskit joko
toteutuvat tai eivät. Varauksen suuruus saadaan simuloimalla, mitkä
riskit toteutuvat:

```{.python tiedosto="esimerkit/08-riskit.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/08-riskit.odotettu"}
```

Rekisteristä voi lukea kolme asiaa.

**Varaus mitoitetaan jakaumasta.** Altistusten summa on 25 päivää,
mutta 85 %:n varmuuteen tarvitaan 46 päivää ja 95 %:n varmuuteen 64.
Pelkkä odotusarvo varauksena riittää vain runsaassa puolessa
tapauksista.

**Torjunta on sijoitus, jolla on tuotto.** Hyötysuhde vertaa
altistuksen laskua torjunnan hintaan. Toimittajariskin torjunta (kolme
päivää varhaiseen integraatiotestiin) laskee altistusta viisi päivää,
joten se kannattaa. Kannattavien torjuntojen jälkeen sekä keskiarvo
että 95 %:n varaus pienenevät.

**Kaikkea ei kannata torjua.** Avainhenkilöriskin torjunta maksaa kuusi
päivää ja laskee altistusta alle kolme. Kun se otetaan mukaan,
keskiarvo huononee. Päätös voi silti olla oikea, jos vaikutus olisi
kohtuuton, sillä odotusarvo ei kerro kaikkea: riskiä, joka kaataisi
koko hankkeen, torjutaan, vaikka laskelma ei sitä puoltaisi.

Luvut ovat arvauksia, ja se on sanottava ääneen. Todennäköisyys ”40 %”
tarkoittaa käytännössä ”melko todennäköinen”. Laskelman arvo on
järjestyksessä ja suuruusluokassa: se pakottaa vertaamaan riskejä
keskenään ja torjunnan hintaa sen hyötyyn. Monet tiimit käyttävät
kolmiportaista asteikkoa (pieni, keskisuuri, suuri) lukujen sijaan, ja
se riittää järjestämiseen.

Rekisteri on hyödyllinen vain elävänä. Se käydään läpi säännöllisesti,
toteutuneet ja vanhentuneet riskit poistetaan ja uudet lisätään.
Riskistä, joka on toteutunut, tulee **ongelma**, ja se siirtyy
tavalliseen työjonoon.

## Riskivetoinen suunnittelu

Riskejä ei vain kirjata, vaan ne ohjaavat työn järjestystä. Boehmin
spiraalimallin ydin (luku 3) on tehdä riskialtein asia ensin, kun
suunnan muuttaminen on vielä halpaa.

- **Tekninen kokeilu** (*spike*) on lyhyt, aikarajattu selvitys, jonka
  tulos on tieto eikä tuotantokoodi: toimiiko kirjasto, riittääkö
  suorituskyky.
- **Prototyyppi** vastaa kysymykseen, ymmärrettiinkö tarve oikein.
- **Kävelevä luuranko** (luku 2) paljastaa integraatioriskit, koska
  kaikki osat kytketään yhteen heti.

Luvun 5 epävarmuuskartio kapenee juuri näillä keinoilla. Aika ei
vähennä epävarmuutta, vaan kokeilujen tulokset.

## Tekninen velka

Ward Cunningham otti vertauksen käyttöön vuonna 1992. Kun koodi
julkaistaan vajavaisin tiedoin tai kiireessä, otetaan velkaa. Pieni
velka nopeuttaa kehitystä, kunhan se maksetaan pian takaisin
kirjoittamalla koodi uudelleen. Vaara syntyy, kun velkaa ei makseta:
jokainen sen päälle tehty työ maksaa korkoa.

Martin Fowler jakaa velan kahdella akselilla nelikenttään:

| Laji | Tietoinen | Tahaton |
|----------------|------------------------------------|------------------------------------|
| **harkittu** | ”julkaistaan nyt ja siivotaan heti perään” | ”nyt tiedämme, miten tämä olisi pitänyt tehdä” |
| **harkitsematon** | ”ei meillä ole aikaa suunnitella” | ”mikä kerrosarkkitehtuuri?” |

Harkittu ja tietoinen velka on liiketoimintapäätös. Tahaton velka
syntyy oppimisesta eikä ole kenenkään vika: projektin lopussa tiedetään
aina enemmän kuin alussa. Harkitsematon velka on yksinkertaisesti
huonoa työtä, ja sen kutsuminen velaksi kaunistelee asiaa.

Velka näkyy käytännössä hitautena: muutos, joka ennen vei päivän, vie
viikon; jokainen korjaus rikkoo jotain muuta; uusi tekijä tarvitsee
kuukausia päästäkseen sisään. Tyypillisiä muotoja ovat puuttuvat
testit, päällekkäinen koodi, vanhentuneet riippuvuudet, käsin tehtävät
julkaisuvaiheet ja dokumentoimattomat erikoistapaukset.

### Korkomalli

Vertausta voi viedä pidemmälle laskemalla. Mallissa oikotie tuottaa
ominaisuuksia 30 % nopeammin mutta kasvattaa velkaa, velasta maksetaan
korkoa jokaisessa sprintissä ja maksamaton velka kasvaa, koska sen
päälle rakennetaan.

```{.python tiedosto="esimerkit/08-velka.py" osa="malli"}
```

Verrataan neljää strategiaa 40 sprintin ajan:

```{.python tiedosto="esimerkit/08-velka.py" osa="strategiat"}
```

```{.tuloste tiedosto="esimerkit/08-velka.odotettu"}
```

![Kertyneet ominaisuudet neljällä strategialla. Pystyviiva on
kahdeksannen sprintin määräaika.](kuvat/velka.png){width=66%}

Tulkinta:

- **Oikotie toimii lyhyellä matkalla.** Kahdeksannen sprintin kohdalla
  oikotietä käyttänyt tiimi on 19 % edellä. Jos määräaika on oikea ja
  ratkaiseva (messut, lain voimaantulo), velan ottaminen on perusteltua.
- **Laina on kallis.** Jatkuva oikominen jää velattomasta jälkeen
  sprintissä 20, ja lopussa tiimi saa aikaan enää murto-osan
  alkuperäisestä tahdistaan, koska kapasiteetti kuluu korkoon.
- **Velka kannattaa maksaa pois, mutta se sattuu.** Lyhennyksen aikana
  ominaisuuksia syntyy vähän, ja tiimi näyttää hitaalta. Neljänkymmenen
  sprintin kohdalla velkansa maksanut on kuitenkin selvästi edellä
  sitä, joka jätti velan paikalleen, ja ero kasvaa.
- **Halvinta on olla ottamatta velkaa, jos kiirettä ei ole.** Velaton
  tiimi on lopussa kaikkia edellä.

Parametrit ovat keksittyjä, joten risteyskohdat (sprintit 11, 15 ja 20)
eivät päde mihinkään oikeaan projektiin. Käyrien muoto on se, mikä
yleistyy: lineaarinen hyöty alussa, kasvava hinta myöhemmin. Mallin
hyödyllisin käyttö on keskustelu tilaajan kanssa. Velka on helpompi
perustella päätöksenä, jolla on hinta ja takaisinmaksusuunnitelma, kuin
kehittäjien toiveena ”siivota koodia”.

### Velan hallinta

- **Tee velka näkyväksi.** Tietoisesti otettu velka kirjataan
  tuotejonoon samalla hetkellä, kun se otetaan, ja siihen kirjataan
  korko: mikä hidastuu ja kuinka paljon.
- **Maksa korkeakorkoisin ensin.** Koodi, jota muutetaan viikoittain,
  maksaa korkoa viikoittain. Ruma moduuli, johon kukaan ei koske, ei
  maksa mitään.
- **Lyhennä jatkuvasti.** Refaktorointi osana jokaista muutosta
  (”jätä koodi siistimmäksi kuin se oli”) on halvempaa kuin erilliset
  siivousprojektit, joille ei koskaan löydy aikaa.
- **Varaa kapasiteettia.** Moni tiimi sopii, että kiinteä osuus
  jokaisesta sprintistä käytetään ylläpitoon ja velan lyhennykseen.

## Laadun hinta

Laadunhallinnan klassinen jako erottaa neljä kustannuslajia:

| Laji | Sisältö | Esimerkki |
|----------------------|------------------------------------|------------------------------------|
| ehkäisy | virheiden syntymisen estäminen | koulutus, suunnittelu, koodauskäytännöt |
| arviointi | virheiden etsiminen | katselmointi, testaus, staattinen analyysi |
| sisäiset virheet | ennen julkaisua löytyneiden korjaus | uudelleentyö, uusintatestaus |
| ulkoiset virheet | asiakkaalla ilmenneiden seuraukset | tuki, korjausjulkaisut, maineen menetys |

Philip Crosbyn väite, että laatu on ilmaista, tarkoittaa tätä: ehkäisyyn
ja arviointiin käytetty raha on pienempi kuin virheistä seuraava lasku.
Ohjelmistossa ero on erityisen suuri, koska virheen korjaaminen
kallistuu sitä mukaa, kun se etenee kohti tuotantoa. Luvun 3
palautesilmukkamalli laski saman asian.

Laatua ei testata tuotteeseen jälkikäteen. Testaus mittaa laatua, mutta
laatu syntyy siitä, miten työ tehdään: pienet muutokset, katselmointi,
automaattiset testit ja valmiin määritelmä (luku 2), josta ei tingitä
kiireessä. Testauksen tekniikat käsitellään taidoissa *Testivetoinen
kehitys ja testisuunnittelu* ja *Integraatiotestaus ja Testcontainers*,
katselmointi taidoissa *Versionhallinta (Git)* ja *Tietoturva
kehitystyössä*.

Kiireessä laatu on se neljäs muuttuja, joka joustaa näkymättömästi
(luku 1). Valmiin määritelmä on sopimus siitä, että se ei jousta: jos
aika loppuu, karsitaan laajuutta, ei testejä.

## Käytännössä

- **Pidä riskilista lyhyenä ja elävänä.** Kymmenen suurinta riskiä,
  jokaisella omistaja ja seuraava toimenpide, läpikäynti kahden viikon
  välein.
- **Tee pre-mortem ennen sitoutumista.** Tunti koko tiimin kanssa
  tuottaa riskilistan, jota projektipäällikkö ei yksin keksi.
- **Riskialtein työ ensin.** Jos jokin voi kaataa hankkeen, selvitä se
  ensimmäisellä viikolla.
- **Mitoita varaus jakaumasta ja näytä se.** Puskuri ei ole
  pehmustetta vaan laskettu varaus nimetyille riskeille.
- **Velka on päätös, joka kirjataan.** Kuka päätti, miksi, mitä se
  maksaa ja milloin se maksetaan. Kirjaamaton oikotie on
  harkitsematonta velkaa.
- **Mittaa velkaa sen vaikutuksesta.** Luotettavin merkki on, että
  samankokoisten muutosten läpimenoaika kasvaa.
- **Älä neuvottele valmiin määritelmästä.** Laajuudesta ja
  aikataulusta voi neuvotella. Testaamaton koodi ei ole nopeammin
  valmis vaan myöhemmin rikki.

## Itsearviointi

- Osaat laatia riskirekisterin ja valita riskille toimintatavan.
- Osaat selittää, miksi altistusten summa ei riitä varaukseksi, ja
  arvioida torjuntatoimen kannattavuutta.
- Osaat kuvata teknisen velan vertauksen ja Fowlerin nelikentän.
- Osaat selittää korkomallin avulla, milloin velan ottaminen on
  perusteltua ja miksi se kannattaa maksaa pois.
- Osaat luetella laadun neljä kustannuslajia ja perustella ehkäisyn
  edullisuuden.
