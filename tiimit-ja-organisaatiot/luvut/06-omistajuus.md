# Omistajuus, alustat ja sisäiset tuotteet

Tiimiraja on hyödyllinen vain, jos on selvää, kuka omistaa mitä. Tämä
luku käsittelee koodin ja palvelun omistajuutta, sen mittaamista
historiasta sekä alustaa, jonka tehtävä on keventää muiden tiimien
kuormaa.

## Mitä omistaminen tarkoittaa

Omistaja päättää osan suunnasta, hyväksyy siihen tulevat muutokset,
korjaa sen viat ja vastaa siitä tuotannossa. Omistajuus ilman
päätösvaltaa on pelkkää syyllisyyttä, ja päätösvalta ilman
tuotantovastuuta tuottaa ratkaisuja, joiden hinnan maksaa joku muu.

Koodin omistajuudelle on kolme perusmallia:

| Malli | Kuka saa muuttaa | Vahvuus | Riski |
|----------|-----------------------|-----------------|--------------------|
| vahva | vain omistaja | selkeä vastuu, yhtenäinen suunta | omistajasta tulee pullonkaula |
| heikko | kuka tahansa, omistaja hyväksyy | muutos ei jää jonoon | omistajan katselmointikuorma |
| yhteinen | kuka tahansa | ei odotusta | kukaan ei vastaa kokonaisuudesta |

Tutkimus antaa suuntaa. Bird kollegoineen (2011) havaitsi Windowsin
komponenteissa, että mitä useampi satunnainen tekijä komponenttiin oli
tehnyt pieniä muutoksia, sitä enemmän siinä oli vikoja. Tulos puoltaa
mallia, jossa osalla on selvä pääomistaja ja muiden muutokset kulkevat
tämän katselmoinnin kautta. Yhteinen omistajuus toimii parhaiten yhden
tiimin sisällä, missä kaikki tuntevat koodin.

## CODEOWNERS

GitHub ja GitLab lukevat repositorion `CODEOWNERS`-tiedostosta, kenen
hyväksyntä muutokseen vaaditaan. Tiedosto on omistajuus koneluettavassa
muodossa:

```{.python tiedosto="esimerkit/06-codeowners.py" osa="tiedosto"}
```

Säännöt luetaan ylhäältä alas, ja viimeinen osuva sääntö voittaa.
Seuraava jäsennin tukee muodon tavallisinta osajoukkoa:

```{.python tiedosto="esimerkit/06-codeowners.py" osa="jasennys"}
```

Tiedostosta kannattaa tarkistaa kolme asiaa: onko jokaisella
tiedostolla omistaja, onko omistaja tiimi eikä yksittäinen ihminen ja
osuvatko kaikki säännöt johonkin:

```{.python tiedosto="esimerkit/06-codeowners.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/06-codeowners.odotettu"}
```

Tarkistus löytää kolme tyypillistä ongelmaa. Infrastruktuurikoodilla
ei ole omistajaa, joten sen muutoksia ei katselmoi kukaan, jonka
tehtävä se olisi. Maksun rajapinta ja tietokanta ovat yhden ihmisen
varassa. Sääntö `/toimitus/` viittaa hakemistoon, jota ei enää ole.
Tarkistuksen voi ajaa toimitusputkessa.

## Kuka koodin oikeasti tuntee

`CODEOWNERS` kertoo, kenen pitäisi tuntea koodi. Historia kertoo, kuka
sen tuntee. Lasketaan jokaiselle osalle, kuinka suuren osan muutoksista
kukin tekijä on tehnyt:

```{.python tiedosto="esimerkit/06-omistajuus.py" osa="osuudet"}
```

**Bussikerroin** (*bus factor*, *truck factor*) on pienin määrä
ihmisiä, joiden poistuminen pysäyttäisi työn. Sille ei ole yhtä
määritelmää. Tässä osan tuntijaksi lasketaan jokainen, joka on tehnyt
vähintään neljänneksen sen muutoksista, ja kerroin arvioidaan ahneesti:

```{.python tiedosto="esimerkit/06-omistajuus.py" osa="bussikerroin"}
```

```{.tuloste tiedosto="esimerkit/06-omistajuus.odotettu"}
```

Kahdeksalla kahdestatoista osasta on vain yksi tuntija, ja kolmen
ihmisen lähtö jättäisi yli puolet järjestelmästä ilman ketään, joka
tuntee sen. Maksu on kokonaan Pekan varassa, mikä näkyi jo
`CODEOWNERS`-tiedostossa. Avelino kollegoineen (2016) arvioi samoin
suosittuja avoimen lähdekoodin projekteja: useimmissa bussikerroin oli
yksi tai kaksi.

Mittarilla on rajansa. Muutosten määrä ei ole sama asia kuin
ymmärrys: katselmoija voi tuntea koodin hyvin tekemättä siihen
muutoksia, ja vanha tekijä on voinut unohtaa. Mittari kertoo, mistä
kannattaa kysyä, ei vastausta. Kerrointa nostavat parityö,
katselmointien kierrättäminen ja tehtävien antaminen tietoisesti
toiselle.

## Tee se, aja se

Amazonin teknologiajohtaja Werner Vogels tiivisti vuonna 2006
periaatteen ”you build it, you run it”: palvelun rakentanut tiimi
myös ajaa sitä tuotannossa. Perustelu on palautesilmukka. Tiimi, joka
herää omiin hälytyksiinsä, korjaa niiden syyt, ja tiimi, joka näkee
käyttäjien ongelmat, tekee parempia päätöksiä.

Periaate toimii vain, jos tiimillä on myös keinot. Tuotantovastuu
ilman oikeutta priorisoida korjauksia ominaisuuksien edelle uuvuttaa.
Jokainen tiimi ei myöskään voi rakentaa omaa tuotantoympäristöään, ja
siksi tarvitaan alusta.

## Alusta sisäisenä tuotteena

**Alusta** on joukko itsepalveluna käytettäviä rajapintoja, työkaluja,
palveluja ja ohjeita, jotka sisäinen tiimi tarjoaa muille tiimeille.
Tyypillinen sisältö on toimitusputki, ajoympäristö, tietokannat,
valvonta ja tunnistautuminen. Alustan tarkoitus on poistaa virtatiimien
ulkoista kuormaa (luku 5): tiimin ei tarvitse tietää, miten klusteri
toimii, kunhan se saa palvelunsa ajoon. Sana *tuote* on olennainen.

- **Alustalla on käyttäjiä, ei alamaisia.** Jos tiimit käyttävät
  alustaa vain pakosta, se on epäonnistunut. Käyttöä ja tyytyväisyyttä
  mitataan kuten minkä tahansa tuotteen.
- **Itsepalvelu on vaatimus.** Jos uuden palvelun ympäristö vaatii
  tiketin ja kolmen päivän odotuksen, alusta on luvun 3 luovutusjono.
- **Tasoitettu tie, ei muuri.** Alusta tarjoaa tuetun oletuspolun
  (*golden path*, *paved road*), jota seuraamalla saa valvonnan,
  tietoturvan ja päivitykset valmiina. Polulta saa poiketa, mutta
  silloin tiimi kantaa itse sen, minkä alusta muuten hoitaisi.
- **Ohuin toimiva alusta.** Team Topologiesin *thinnest viable
  platform* on pienin alusta, joka nopeuttaa tiimejä. Pienessä
  organisaatiossa se voi olla wikisivu, joka kertoo, mitä
  pilvipalveluja käytetään ja miten.

Alustatiimin tavallisin virhe on rakentaa sitä, mikä on teknisesti
kiinnostavaa, eikä sitä, mitä tiimit tarvitsevat. Toinen on kasvaa
liian aikaisin: viiden tiimin organisaatiossa kymmenen hengen
alustatiimi maksaa enemmän kuin säästää.

## InnerSource

Entä kun tiimi tarvitsee muutoksen toisen tiimin omistamaan osaan eikä
omistaja ehdi? **InnerSource** tuo avoimen lähdekoodin käytännöt
organisaation sisälle: koodi on kaikkien luettavissa, kuka tahansa voi
ehdottaa muutosta, ja omistajatiimin nimetyt jäsenet katselmoivat ja
hyväksyvät sen. Malli on heikon omistajuuden muoto. Se poistaa
jonotuksen mutta siirtää omistajalle katselmointityötä ja vaatii, että
osa on dokumentoitu ja testattu niin hyvin, että ulkopuolinen pystyy
muuttamaan sitä turvallisesti.

## Käytännössä

- **Jokaisella osalla on yksi omistajatiimi.** Ei kahta, ei yksilöä,
  ei ”kaikki”.
- **Tarkista omistajuus koneellisesti.** `CODEOWNERS`-kattavuus ja
  yhden tuntijan osat ovat halpoja mitata.
- **Omistajuus sisältää tuotannon.** Jos eri tiimi kehittää ja eri
  päivystää, kumpikaan ei omista palvelua.
- **Mittaa alustaa sen käyttäjiltä.** Kuinka nopeasti uusi palvelu
  pääsee tuotantoon? Kuinka moni käyttää oletuspolkua?

## Itsearviointi

- Osaat verrata omistajuusmalleja ja tarkistaa `CODEOWNERS`-tiedoston
  kattavuuden.
- Osaat arvioida Git-historiasta osien tuntijat ja bussikertoimen.
- Osaat perustella periaatteen ”tee se, aja se” ja kuvata alustan
  tuotteena.
