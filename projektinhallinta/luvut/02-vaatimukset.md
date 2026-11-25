# Vaatimukset

Vaatimus kertoo, mitä järjestelmän pitää tehdä tai millainen sen pitää
olla, jotta joku saa siitä hyötyä. Väärin ymmärretty vaatimus on
projektin kallein virhe, koska kaikki sen päälle tehty työ on tehty
väärään suuntaan. Tässä luvussa käydään läpi, keneltä vaatimukset
tulevat, missä muodossa ne kirjataan, miten ne priorisoidaan ja miten
laajuus pidetään hallinnassa.

## Sidosryhmät ja vaatimusten lajit

**Sidosryhmä** on kuka tahansa, johon järjestelmä vaikuttaa tai joka
vaikuttaa siihen: käyttäjät, tilaaja ja maksaja, ylläpito ja tuki,
tietoturvasta ja tietosuojasta vastaavat, viranomainen ja kehitystiimi
itse. Sidosryhmillä on eri tavoitteet. Maksaja haluaa säästöä, käyttäjä
sujuvan työpäivän ja ylläpitäjä järjestelmän, joka ei herätä öisin.
Vaatimusmäärittelyn ensimmäinen tehtävä on selvittää, keitä sidosryhmät
ovat, ja toinen sovittaa ristiriitaiset toiveet yhteen.

Vaatimukset jaetaan kahteen lajiin:

- **Toiminnallinen vaatimus** kertoo, mitä järjestelmä tekee: asiakas
  voi maksaa tilauksen verkkopankissa.
- **Laatuvaatimus** (ei-toiminnallinen vaatimus) kertoo, kuinka hyvin:
  maksusivu latautuu alle sekunnissa, palvelu on käytettävissä 99,9 %
  ajasta, ruudunlukija osaa lukea lomakkeen.

Laatuvaatimukset unohtuvat helposti, koska kukaan ei pyydä niitä ennen
kuin ne puuttuvat. Standardi ISO/IEC 25010 luettelee laatuominaisuudet
muistilistaksi: toiminnallinen sopivuus, suorituskyky, yhteensopivuus,
käytettävyys, luotettavuus, tietoturva, ylläpidettävyys ja
siirrettävyys. Laatuvaatimus on hyödyllinen vasta mitattavana: ”nopea”
ei ole vaatimus, ”95 % hauista palautuu alle 500 millisekunnissa
tuotantodatan kokoisella aineistolla” on.

Lisäksi on **rajoitteita**, joista ei neuvotella: lait ja standardit,
olemassa olevat järjestelmät, joihin on liityttävä, sekä sovittu
teknologia.

## Tasot: tavoitteesta hyväksymiskriteeriin

Vaatimukset muodostavat hierarkian. Ylimpänä on **tavoite**, joka
kertoo, miksi koko hanke tehdään (”tilausten käsittelyaika puolittuu”).
Tavoitteesta johdetaan **ominaisuuksia** (verkkomaksu), ominaisuuksista
pieniä toteutettavia paloja ja niistä tarkat ehdot, joilla pala on
valmis. Kun jokainen pala voidaan jäljittää tavoitteeseen, turha työ
erottuu: jos tarina ei palvele mitään tavoitetta, sitä ei tarvita.

Perinteinen vaatimusmäärittely kirjoittaa vaatimukset numeroituna
dokumenttina (”järjestelmän tulee…”), ja standardi ISO/IEC/IEEE 29148
kuvaa hyvän vaatimuksen ominaisuudet: yksiselitteinen, todennettava,
toteutettavissa ja jäljitettävä. Tapa on edelleen käytössä siellä,
missä vaatimukset ovat sopimuksen tai viranomaishyväksynnän perusta.
Ketterissä menetelmissä vaatimukset kirjataan useimmiten
käyttäjätarinoina.

## Käyttäjätarinat

**Käyttäjätarina** on lyhyt kuvaus tarpeesta käyttäjän näkökulmasta.
Vakiintunut muoto on

```text
Asiakkaana haluan tallentaa ostoskorin,
jotta voin jatkaa ostoksia toisella laitteella.
```

Muodossa on kolme osaa: kuka, mitä ja miksi. Viimeinen on tärkein,
koska se antaa toteuttajalle luvan ehdottaa parempaa ratkaisua samaan
tarpeeseen.

Tarina ei ole määrittely vaan muistutus keskustelusta. Ron Jeffries
tiivisti tämän kolmeen osaan: **kortti** (lyhyt teksti), **keskustelu**
(tekijät ja tilaaja käyvät asian läpi) ja **vahvistus** (ehdot, joilla
tarina hyväksytään). Jos keskustelu jää pois, tarina on vain huonosti
kirjoitettu vaatimus.

Bill Waken muistisääntö **INVEST** kuvaa hyvän tarinan:

| Kirjain | Ominaisuus | Merkitys |
|---------|---------------------|--------------------------------------------------|
| I | itsenäinen (*independent*) | voidaan tehdä ja julkaista muista riippumatta |
| N | neuvoteltava (*negotiable*) | toteutustapa on auki, tarve ei |
| V | arvokas (*valuable*) | tuottaa hyötyä käyttäjälle tai tilaajalle |
| E | arvioitava (*estimable*) | tiimi ymmärtää sen riittävästi arvioidakseen |
| S | pieni (*small*) | valmistuu muutamassa päivässä |
| T | testattava (*testable*) | on selvää, milloin se on valmis |

Tarinamuotoon ei pidä pakottaa kaikkea. Tekninen työ (”päivitä
tietokantaversio”) on rehellisempää kirjata tehtävänä kuin keksiä sille
käyttäjä.

## Hyväksymiskriteerit

**Hyväksymiskriteeri** on ehto, jonka täyttyminen voidaan todeta
kyllä tai ei. Kriteerit kirjoitetaan ennen toteutusta, ja ne tekevät
tarinasta testattavan:

```text
Oletetaan, että korissa on kaksi tuotetta ja asiakas on kirjautunut.
Kun asiakas kirjautuu toisella laitteella,
niin korissa on samat kaksi tuotetta.
```

Rakenne *oletetaan – kun – niin* (*given – when – then*) on sama, jota
käytetään suoritettavissa määrittelyissä. Kriteereistä voi tehdä
automaattisia hyväksymistestejä; se on taidon *Testivetoinen kehitys ja
testisuunnittelu* aihe. Hyvät kriteerit kattavat myös virhetilanteet:
mitä tapahtuu, kun maksu epäonnistuu tai syöte on tyhjä.

## Vaatimukset datana

Tuotejono on tietorakenne, ja sen puutteita voi etsiä koneellisesti
samaan tapaan kuin kääntäjä etsii virheitä koodista. Seuraavassa
esimerkissä tarina on tietue, jossa on INVEST-ominaisuuksia vastaavat
kentät:

```{.python tiedosto="esimerkit/02-tarinat.py" osa="tarina"}
```

Tarkistin etsii puuttuvan hyödyn, puuttuvat hyväksymiskriteerit, liian
suuret tarinat ja riippuvuuksien kehät:

```{.python tiedosto="esimerkit/02-tarinat.py" osa="tarkistus"}
```

Seitsemän tarinan esimerkkijonosta löytyy kuusi huomautusta. Tulosteen
jälkimmäinen osa on tarinakartta, johon palataan alla.

```{.tuloste tiedosto="esimerkit/02-tarinat.odotettu"}
```

Tarkistin ei tiedä, onko tarina oikea tai arvokas. Se varmistaa vain
muodon, ja siinä se on hyödyllinen: tarina ilman hyväksymiskriteerejä
ei pääse työn alle huomaamatta. Sama ajatus toimii
tehtävienhallintajärjestelmän kyselynä tai vientitiedoston tarkistuksena.

## Tarinakartta

Pitkä tuotejono on litteä lista, josta kokonaisuus katoaa. Jeff
Pattonin **tarinakartta** järjestää tarinat kahteen suuntaan.
Vaakasuunnassa ovat käyttäjän toiminnot siinä järjestyksessä, jossa hän
ne tekee (etsi, kerää, maksa). Pystysuunnassa ovat tarinat
tärkeysjärjestyksessä, ja vaakaviivat jakavat ne julkaisuihin.

Esimerkin tuloste on tällainen kartta. Ensimmäinen julkaisu kulkee koko
polun päästä päähän: asiakas voi etsiä, kerätä ja maksaa, vaikka
jokainen vaihe on vielä karu. Tätä kutsutaan **käveleväksi
luurangoksi**. Vaihtoehto, jossa haku hiotaan täydelliseksi ennen kuin
maksaminen on olemassa, tuottaa ensimmäisen käyttökelpoisen version
vasta lopussa.

## Priorisointi

Kaikkea ei ehditä tehdä, joten järjestys ratkaisee. Yksinkertaisin
luokittelu on **MoSCoW**, joka on peräisin DSDM-menetelmästä:

| Luokka | Merkitys |
|---------------------|------------------------------------------------------|
| *must* (pakko) | ilman tätä julkaisu on hyödytön tai laiton |
| *should* (pitäisi) | tärkeä, mutta julkaisu toimii ilman |
| *could* (voisi) | tehdään, jos aikaa jää |
| *won't* (ei nyt) | sovitusti ei tässä julkaisussa |

Luokittelun heikkous on, että kaikki pyrkii pakolliseksi. Jos
pakollisia on yli puolet työmäärästä, joustovaraa ei ole.

Taloudellisempi tapa on kysyä, mitä odottaminen maksaa.
**Viivästymisen hinta** (*cost of delay*) on raha tai muu hyöty, joka
menetetään jokaiselta viikolta, jonka ominaisuus on tekemättä. Kun
yksi tiimi tekee työt peräkkäin, kokonaishinta on pienin, kun työt
tehdään järjestyksessä, jossa viivästymisen hinta jaettuna kestolla on
suurin. Donald Reinertsen kutsuu tätä nimellä CD3, ja skaalatuissa
ketterissä malleissa se tunnetaan lyhenteellä **WSJF** (*weighted
shortest job first*).

```{.python tiedosto="esimerkit/02-priorisointi.py" osa="hinta"}
```

```{.tuloste tiedosto="esimerkit/02-priorisointi.odotettu"}
```

Kuudella työllä arvokkain ensin -sääntö on huonompi kuin
saapumisjärjestys, koska arvokkain työ on myös pisin ja kaikki muut
odottavat sitä. WSJF tuottaa saman tuloksen kuin kaikkien 720
järjestyksen läpikäynti.

Tulos pätee, kun hinta ja kesto tiedetään. Niitä ei tiedetä, vaan ne
arvioidaan. Tulosteen jälkimmäinen taulukko näyttää, mitä tapahtuu, kun
kumpaankin lukuun lisätään satunnainen virhe ja järjestys lasketaan
virheellisistä arvioista:

```{.python tiedosto="esimerkit/02-priorisointi.py" osa="herkkyys"}
```

Kun arviot voivat olla kaksinkertaisia tai puolikkaita, kärkeen päätyy
oikea työ vain noin joka toisella kerralla, mutta kokonaishinta kasvaa
alle kymmenen prosenttia. Menetelmä kestää siis karkeat arviot, kunhan
suuruusluokat ovat oikein. Johtopäätös on käytännöllinen: tarkkoja
lukuja ei kannata hioa, eikä kahden lähekkäisen työn järjestyksestä
kannata kiistellä. Hyöty tulee siitä, että pitkät ja vähäarvoiset työt
eivät pääse jonon kärkeen. WSJF:n varjopuoli on, että se suosii pieniä
töitä: suuri ja tärkeä työ ei koskaan nouse kärkeen, ellei sitä pilkota.

## Laajuuden hallinta

**Laajuuden hiipiminen** (*scope creep*) tarkoittaa, että projektiin
lisätään työtä ilman, että aikataulu tai budjetti muuttuu. Yksittäinen
lisäys on aina pieni ja perusteltu. Ongelma on summa.

Keinot ovat yksinkertaisia mutta vaativat kurinalaisuutta:

- Jokainen lisäys kirjataan tuotejonoon ja priorisoidaan muiden
  joukossa. Kun jotain tulee sisään, jotain muuta siirtyy myöhemmäksi,
  ja tämä vaihtokauppa tehdään näkyvästi.
- Julkaisulle määritellään tavoite, ei ominaisuuslistaa. Tavoitteeseen
  (”asiakas voi tilata ja maksaa”) voi päästä monella laajuudella.
- Pienin julkaisukelpoinen kokonaisuus (*minimum viable product*)
  rajataan ensin, ja muu on lisää.
- Kiinteän laajuuden projekteissa muutokset kulkevat sovitun
  muutoksenhallinnan kautta: muutos arvioidaan, hinnoitellaan ja
  hyväksytään erikseen (luku 10).

## Valmiin määritelmä

Hyväksymiskriteerit ovat tarinakohtaisia. **Valmiin määritelmä**
(*definition of done*) on kaikille tarinoille yhteinen lista ehdoista,
joiden täytyttyä työ on oikeasti valmis: koodi on katselmoitu, testit
menevät läpi, dokumentaatio on päivitetty ja muutos on asennettu
testiympäristöön. Määritelmä estää ”valmis, paitsi” -tilat, jotka
tekevät edistymisen mittaamisesta mahdotonta ja kerryttävät
näkymätöntä työtä projektin loppuun.

Vastaavasti jotkin tiimit sopivat, milloin tarina on **valmis
aloitettavaksi** (*definition of ready*): hyväksymiskriteerit on
kirjattu, riippuvuudet tunnetaan ja koko on arvioitu. Tässä kannattaa
olla varovainen, sillä liian tiukka portti palauttaa vaiheittaisen
mallin, jossa mitään ei aloiteta ennen kuin kaikki on määritelty.

## Käytännössä

- **Kysy miksi, kunnes pääset tavoitteeseen.** Pyydetty ominaisuus on
  usein jonkun arvaus ratkaisusta. Kun tarve on selvillä, löytyy
  toisinaan halvempi keino.
- **Kirjaa laatuvaatimukset mitattavina ja testaa ne.** Suorituskyky-,
  tietoturva- ja saavutettavuusvaatimus, jota ei testata, ei toteudu.
- **Hyväksymiskriteerit ennen toteutusta.** Jos niitä ei osata
  kirjoittaa, tarinaa ei ymmärretä vielä riittävästi. Tämä on halvin
  hetki huomata väärinymmärrys.
- **Pidä jono lyhyenä kärjestä tarkkana.** Seuraavien viikkojen tarinat
  ovat pieniä ja tarkkoja, kauempana olevat suuria ja karkeita.
  Kaukaisten tarinoiden hiominen on hukkaa, koska osa niistä jää
  tekemättä.
- **Priorisoi viivästymisen hinnan suuruusluokalla.** Karkea arvio
  riittää, kuten esimerkki näytti. Tärkeintä on, että joku ylipäätään
  kysyy, mitä odottaminen maksaa.
- **Sano ei näkyvästi.** *Won't*-lista ja julkaisun rajaus ovat
  viestintää: sidosryhmä, joka tietää toiveensa siirtyneen, voi
  suunnitella sen mukaan.
- **Säädellyillä aloilla jäljitettävyys on vaatimus.** Lääkintä-,
  auto- ja ilmailuohjelmistoissa jokaisesta vaatimuksesta on voitava
  osoittaa toteutus ja testi. Tarinat eivät poista tätä tarvetta, mutta
  jäljitettävyyden voi tuottaa työkaluilla tarinoista ja testeistä.

## Itsearviointi

- Osaat tunnistaa projektin sidosryhmät ja erottaa toiminnalliset
  vaatimukset, laatuvaatimukset ja rajoitteet.
- Osaat kirjoittaa käyttäjätarinan ja sille hyväksymiskriteerit sekä
  arvioida tarinaa INVEST-ominaisuuksilla.
- Osaat selittää, mikä tarinakartta on ja miksi ensimmäinen julkaisu
  kulkee koko käyttäjän polun läpi.
- Osaat priorisoida töitä viivästymisen hinnan ja keston avulla ja
  kertoa, miksi menetelmä sietää karkeat arviot.
- Osaat erottaa hyväksymiskriteerit ja valmiin määritelmän ja kertoa,
  miten laajuuden hiipimistä hallitaan.
