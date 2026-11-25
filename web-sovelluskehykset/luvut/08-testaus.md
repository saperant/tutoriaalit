# Yksi testisarja

Väite, että viisi toteutusta ovat sama sovellus, on tähän asti ollut
kirjoittajan sana. Tässä luvussa se todistetaan: yksi testisarja ajetaan
jokaista toteutusta vasten oikeassa selaimessa, ja kaikkien on läpäistävä
se. Samalla nähdään, miksi tällaiset testit kestävät kehyksen vaihdon
ja mitä ne paljastivat matkan varrella.

Testaamisen perusteet (testipyramidi, komponenttitestit, Playwright) on
käyty läpi taidossa *Web-sovellukset*, eikä niitä toisteta.

## Testit, jotka eivät tunne kehystä

Playwrightin asetuksissa jokainen toteutus on oma projektinsa, ja
kaikilla on sama testihakemisto:

```{.typescript tiedosto="esimerkit/playwright.config.ts" osa="asetukset"}
```

Testit puhuvat sovellukselle niin kuin käyttäjä ja ruudunlukija:
roolien, nimien ja näkyvän tekstin kautta. Niissä ei ole luokkien
nimiä, komponenttien nimiä eikä kehyksen testiapuvälineitä.

```{.typescript tiedosto="esimerkit/e2e/sovellus.spec.ts" osa="alku"}
```

Jos testit hakisivat elementtejä kehyksen tuottamilla tunnisteilla tai
komponenttien nimillä, niitä olisi viisi versiota. Rooleihin nojaava
testi on myös saavutettavuustesti: jos painiketta ei löydy nimellä
"Lisää", sitä ei löydä ruudunlukijakaan.

## Sama rakenne

Ensimmäinen testi vertaa koko sivun saavutettavuuspuuta yhteen
kuvaukseen. Se on tiukin mahdollinen tapa sanoa, että toteutukset
tuottavat saman käyttöliittymän: samat roolit, samat nimet, sama
järjestys.

```{.typescript tiedosto="esimerkit/e2e/sovellus.spec.ts" osa="rakenne"}
```

Saavutettavuuspuu ei välitä siitä, että Angularin DOM:ssa on
isäntäelementtejä ja muiden ei. Ylimääräinen elementti ilman roolia ei
näy puussa, ja juuri siksi vertailu tehdään tällä tasolla eikä HTML-
merkkijonona.

## Käyttäytyminen

Lomakkeen testi käy läpi luvun 6 säännöt: virhe näkyy vasta
lähetysyrityksen jälkeen, kohdistus palaa kenttään, ja lisätty tehtävä
näkyy listassa ja yhteenvedossa.

```{.typescript tiedosto="esimerkit/e2e/sovellus.spec.ts" osa="lomake"}
```

Avainten testi merkitsee yhden rivin DOM-solmun suoraan ja tarkistaa,
että merkki on poiston jälkeen yhä saman tehtävän rivillä:

```{.typescript tiedosto="esimerkit/e2e/sovellus.spec.ts" osa="avaimet"}
```

Jos jokin toteutus piirtäisi listan uudelleen tai kierrättäisi rivejä
järjestysnumeron mukaan, merkki katoaisi tai siirtyisi väärälle
riville. Testi on kehyksetöntä toteutusta varten yhtä tarpeellinen
kuin muille: sen `paivitaRivit` on käsin kirjoitettu versio samasta
asiasta.

## Mitä testit paljastivat

Testisarja ei ollut heti oikein, eivätkä kaikki toteutukset läpäisseet
sitä ensimmäisellä kerralla. Kolme löydöstä kertoo kehysten eroista
enemmän kuin onnistuneet ajot.

**Tyhjätila.** Ensimmäinen versio lomaketestistä vertasi rivin koko
tekstisisältöä: `"Kirjoita muistio kiireellinen"`. React-toteutuksessa
nimen ja merkin välissä ei ollut välilyöntiä, koska kehykset
käsittelevät elementtien välistä tyhjätilaa eri tavoin (luku 4).
Testi korjattiin tarkistamaan valintaruudun nimi ja merkin teksti
erikseen. Virhe oli testin oletuksessa, ei toteutuksessa.

**Efektin ajoitus.** Pysyvyystesti muutti tilaa ja latasi sivun
heti uudelleen. Angular-toteutuksessa muutos katosi, koska
tallennusefektiä ei ollut vielä ajettu, kun sivu ladattiin (luku 7).
Korjattu testi odottaa efektin näkyvää seurausta, sivun otsikkoa:

```{.typescript tiedosto="esimerkit/e2e/sovellus.spec.ts" osa="pysyvyys"}
```

**Alkutilan kilpailu.** Latauksen virhetesti asensi pyynnön
sieppauksen ennen kuin sivun ensimmäinen lataus oli valmis, jolloin
sieppaus osui väärään pyyntöön. Tämä ei liity kehyksiin, mutta se on
tavallisin syy epävakaisiin selaintesteihin: testi olettaa järjestyksen,
jota mikään ei takaa. Apufunktio odottaa nyt ensin, että ensimmäinen
lataus näkyy sivulla.

Rakennetesti ohjasi lisäksi yhtä suunnitteluratkaisua. Angularin
tavallinen elementtivalitsin olisi tuottanut `<ul>`:n lapseksi
elementin `<app-tehtava-rivi>` eikä `<li>`:tä, ja lista olisi ollut
sekä virheellistä HTML:ää että eri rakenne kuin muissa. Siksi
rivikomponentin valitsin on attribuutti (luku 5).

## Logiikka ilman selainta

Sovelluksen säännöt ovat moduulissa, joka ei tunne kehyksiä, joten ne
testataan ilman selainta ja ilman kehystä Noden omalla testiajurilla.
Testit ajetaan sekunnin murto-osassa, ja ne ovat samat riippumatta
siitä, millä käyttöliittymä on tehty.

Väliin jää kerros, jota tässä ei ole: **komponenttitestit**, joissa
yksi komponentti renderöidään eristettynä. Ne ovat kehyskohtaisia.
Jokaisella kehyksellä on omat apuvälineensä, ja testit on
kirjoitettava uudelleen, jos kehys vaihtuu. Ne ovat silti hyödyllisiä
suurissa sovelluksissa, koska ne ovat selaintestejä nopeampia ja
osoittavat virheen tarkemmin.

| Taso | Mitä testataan | Kehyksestä riippuva | Tässä |
|-----|-----------|-------|---------|
| logiikka | säännöt puhtaina funktioina | ei | `logiikka.test.ts` |
| komponentti | yksi komponentti eristettynä | kyllä | ei toteutettu |
| selain | koko sovellus käyttäjän silmin | ei | `e2e/sovellus.spec.ts` |

## Käytännössä

- **Kirjoita selaintestit käyttäjän sanoin.** Roolit, nimet ja
  näkyvä teksti. Tällainen testi kestää uudelleenkirjoituksen, koska
  se kuvaa sovelluksen eikä toteutusta.
- **Selaintestit ovat paras turva kehyksen vaihdossa ja suuressa
  versiopäivityksessä.** Ne ovat ainoa testitaso, jota ei tarvitse
  kirjoittaa uudelleen. Jos siirtymä on näköpiirissä, kirjoita ne ensin
  vanhaa toteutusta vasten.
- **Älä odota aikaa, odota seurausta.** `expect(…).toHaveTitle(…)`
  yrittää uudelleen, kunnes ehto täyttyy. Kiinteä viive on joko liian
  lyhyt tai hidastaa jokaista ajoa.
- **Pidä säännöt kehyksen ulkopuolella, niin ne voi testata halvalla.**
  Mitä enemmän logiikkaa on komponenteissa, sitä enemmän testeistä on
  hitaita ja kehyskohtaisia.
- **Epäonnistunut testi ei aina tarkoita virhettä toteutuksessa.**
  Kaikissa kolmessa löydöksessä vika oli testin oletuksessa: siinä,
  mitä testi piti kehyksestä riippumattomana.

## Itsearviointi

- Osaat kirjoittaa selaintestin, joka ei riipu sovelluksen kehyksestä,
  ja perustella, miksi se hakee elementit rooleilla.
- Osaat selittää, miksi rakennetta verrataan saavutettavuuspuuna eikä
  HTML:nä.
- Osaat kertoa, mitkä testitasot ovat kehyskohtaisia ja mitkä eivät.
- Osaat nimetä tavallisia syitä siihen, että sama testi käyttäytyy eri
  kehyksillä eri tavoin.
