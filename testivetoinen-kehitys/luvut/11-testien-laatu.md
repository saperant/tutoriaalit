# Hyvä testi

Testikoodia on usein enemmän kuin tuotantokoodia, ja sitä luetaan
hankalimmalla hetkellä: kun jokin on rikki. Silti testejä kirjoitetaan
usein huolimattomammin kuin koodia, jota ne testaavat. Tämä luku kokoaa
edellisten lukujen havainnot: millainen on testi, jota on helppo lukea
ja ylläpitää ja jonka epäonnistuminen kertoo jotain.

## Neljä ominaisuutta

Hyvältä testiltä vaaditaan neljää asiaa, ja ne vetävät osin eri
suuntiin:

- **Se löytää virheet.** Jos käytös muuttuu vääräksi, testi epäonnistuu.
  Luvun 8 mutaatiotestaus mittaa tätä.
- **Se kestää refaktoroinnin.** Jos rakenne muuttuu mutta käytös ei,
  testi pysyy vihreänä. Luvun 3 vuorovaikutustestit eivät kestäneet.
- **Se on nopea ja deterministinen.** Sama tulos joka ajolla, sekunnin
  murto-osassa. Luvun 9 aiheet.
- **Se on luettava.** Epäonnistuessaan se kertoo, mikä sääntö on rikki,
  ilman että lukijan pitää avata toteutus.

Ensimmäinen ja toinen ovat jännitteessä. Mitä tarkemmin testi
tarkistaa, miten koodi toimii, sitä useamman virheen se löytää ja sitä
useammin se hajoaa syyttä. Ratkaisu on tarkistaa **käytöstä julkisen
rajapinnan kautta**: tulos on täsmällinen, mutta tapa, jolla siihen
päästään, on vapaa.

## Haisevat testit

**Testihaju** (*test smell*) on rakenne, joka ei ole virhe mutta
ennustaa ongelmia. Seuraavassa testissä on niistä tavallisimmat. Se
menee läpi:

```{.python tiedosto="esimerkit/11-hajut/test_1_haju.py" osa="haju"}
```

- **Nimi ei kerro mitään.** Kun `test_1` epäonnistuu, raportista ei näe,
  mikä ominaisuus on rikki.
- **Yksi testi, monta asiaa.** Testi tarkistaa summan, rivien määrän ja
  paljousalennuksen. Ensimmäinen epäonnistuva väite pysäyttää testin,
  ja loput jäävät tarkistamatta.
- **Testi kurkistaa sisään.** `kori._rivit` on toteutuksen
  yksityiskohta. Jos rivit vaihdetaan sanakirjaksi, testi hajoaa,
  vaikka summa on oikein.
- **Testi laskee odotuksen itse.** Silmukka toistaa toteutuksen
  alennuskaavan. Jos kaavassa on virhe, se on molemmissa, ja testi
  menee läpi. Lisäksi testissä on nyt logiikkaa, jossa voi olla oma
  virheensä.
- **Jaettu tila.** Kori luodaan moduulin tasolla, ja `test_2` toimii
  vain, jos `test_1` on ajettu ensin. Yksin tai eri järjestyksessä
  ajettuna se epäonnistuu.
- **Taikaluvut.** Luku 4394 ei kerro, mistä se tulee.

Samat asiat kirjoitettuna uudelleen:

```{.python tiedosto="esimerkit/11-hajut/test_2_siisti.py" osa="siisti"}
```

```{.tuloste tiedosto="esimerkit/11-hajut/odotettu"}
```

Jokainen testi luo oman korinsa, tarkistaa yhden säännön julkisen
metodin kautta ja vertaa lukuun, jonka alkuperä näkyy rivillä. Nimi on
lause, joka on tosi, kun testi menee läpi.

Muita tavallisia hajuja:

| Haju | Miksi se haittaa | Korjaus |
|---------------------|------------------------------|----------------------------|
| ehtolause tai silmukka testissä | testissä on logiikkaa, jota kukaan ei testaa | parametrointi; yksi polku testiä kohden |
| pitkä alustus | olennainen hukkuu kohinaan | rakentajafunktio oletusarvoilla |
| väite ilman sisältöä | `assert tulos` tai `is not None` hyväksyy lähes kaiken | täsmällinen odotusarvo |
| liikaa mockeja | testi kuvaa toteutuksen, ei käytöstä | väärennös tai oikea olio (luku 3) |
| `sleep` testissä | hidas ja epävakaa | väärennetty kello (luku 9) |
| poikkeus niellään | `try`/`except` testissä piilottaa virheen | `pytest.raises` ja viestin tarkistus |
| kommentoitu tai ohitettu testi | näyttää suojalta, ei suojaa | korjaa tai poista |

## Rakenne ja nimi

Testin kolme osaa, **alkutilanne, toiminto ja väite** (*arrange, act,
assert*), erotetaan tyhjällä rivillä. Gherkinin *Oletetaan, Kun, Niin*
on sama rakenne toisilla sanoilla. Kun toimintoja on kaksi, testejä on
yleensä kaksi.

"Yksi väite testiä kohden" on hyödyllinen nyrkkisääntö mutta liian
tiukka sääntönä. Tarkempi muotoilu on *yksi käytös testiä kohden*:
kolme väitettä samasta tuloksesta (osien määrä, summa ja tasaisuus
luvussa 7) kuuluvat yhteen testiin.

Nimi kertoo tilanteen ja odotuksen. Hyvän nimen tunnistaa siitä, että
epäonnistuneiden testien lista on luettavissa vikaraporttina:

```text
FAIL  test_paljousalennus_koskee_vain_omaa_riviaan
FAIL  test_tasan_viidenkymmenen_euron_tilaus_on_ilmainen
```

Nimeämistapoja on monta, ja tiimin kannattaa valita yksi. Tärkeintä on,
että nimessä on käytös eikä metodin nimi: `test_summa` ei kerro, mitä
summasta väitetään.

## Testidatan rakentaminen

Kun testattava olio tarvitsee kymmenen kenttää ja testiä kiinnostaa
yksi, alustus peittää olennaisen. **Rakentajafunktio** antaa kaikille
kentille kelvolliset oletusarvot ja ottaa argumentteina vain sen, mikä
tässä testissä on tärkeää. Esimerkin `kori_jossa` on pienin mahdollinen
rakentaja; isommalle oliolle sama näyttää tältä:

```text
def tilaus(*, summa=2_000, paino=1_000, kanta_asiakas=False) -> Tilaus:
    ...

def test_kanta_asiakas_saa_ilmaisen_toimituksen_30_eurosta():
    t = tilaus(summa=3_000, kanta_asiakas=True)
```

Lukija näkee testistä suoraan, mitkä kaksi asiaa vaikuttavat tulokseen.
Kun olioon lisätään kenttä, vain rakentaja muuttuu.

Pytestin fixturet sopivat resursseihin, joilla on elinkaari:
väliaikainen hakemisto, tietokantayhteys, käynnistetty palvelu.
Testidatan piilottaminen fixtureen kaukana testistä on eri asia: jos
lukija joutuu avaamaan `conftest.py`:n ymmärtääkseen, miksi odotettu
summa on 4 394, data on väärässä paikassa.

Testikoodissa toisto on pienempi paha kuin tuotantokoodissa. Kaksi
testiä, joissa on sama kolmen rivin alustus, ovat helpompia lukea kuin
kaksi testiä, jotka jakavat apufunktion, jolla on neljä valinnaista
argumenttia. Yhteinen koodi kannattaa erottaa vasta, kun se tekee
testistä selkeämmän.

## Testisarja kokonaisuutena

Yksittäisten testien lisäksi sarjalla on omat laatuvaatimuksensa:

- **Nopeus.** Yksikkötestien pitää valmistua sekunneissa, jotta ne
  ajetaan jokaisen muutoksen jälkeen. Hitaat testit erotetaan omaksi
  joukokseen (taito *Integraatiotestaus ja Testcontainers* käsittelee
  testipyramidin).
- **Riippumattomuus.** Testit menevät läpi missä tahansa järjestyksessä
  ja rinnakkain. Satunnainen ajojärjestys paljastaa jaetun tilan
  varhain.
- **Luotettavuus.** Punainen tarkoittaa virhettä ja vihreä sitä, ettei
  tunnettuja virheitä ole. Jokainen epävakaa testi syö tätä
  luottamusta.
- **Ylläpito.** Testi, joka ei enää vastaa mitään vaatimusta,
  poistetaan. Testisarja ei ole arkisto.

Katselmoinnissa testit luetaan ennen toteutusta. Niistä näkee, mitä
muutoksen on tarkoitus tehdä, ja puuttuva testi on usein selvempi
merkki puuttuvasta tapauksesta kuin itse koodi.

## Käytännössä

- **Nimeä testi käytöksen mukaan.** Tilanne ja odotus samassa
  lauseessa.
- **Testaa julkisen rajapinnan kautta.** Jos jotain ei voi tarkistaa
  ulkoa, kysy, onko se vaatimus vai toteutuksen yksityiskohta.
- **Kirjoita odotusarvo näkyviin.** Luku tai merkkijono, ei kaava. Jos
  johto ei ole ilmeinen, kommentti kertoo sen.
- **Ei logiikkaa testiin.** Ehtolause testissä on kaksi testiä, silmukka
  on parametrointi.
- **Jokainen testi luo oman tilansa.** Moduulitason muuttujat ja
  testien välinen järjestys ovat epävakauden lähteitä.
- **Katso testin epäonnistuvan.** Riko koodi hetkeksi ja lue
  virheilmoitus. Jos se ei kerro, mikä on vialla, paranna väitettä tai
  nimeä.
- **Pidä testikoodi samassa kunnossa kuin tuotantokoodi.** Sama
  muotoilija, sama katselmointi, samat nimeämisen vaatimukset.

## Itsearviointi

- Osaat nimetä hyvän testin neljä ominaisuutta ja selittää, miksi
  virheiden löytäminen ja refaktoroinnin kestäminen ovat jännitteessä.
- Osaat tunnistaa testistä tavallisimmat hajut ja korjata ne.
- Osaat kirjoittaa testin, jossa alkutilanne, toiminto ja väite erottuvat
  ja jonka nimi kertoo käytöksen.
- Osaat kirjoittaa rakentajafunktion ja perustella, milloin testidata
  kuuluu testiin ja milloin fixtureen.
- Osaat arvioida testisarjaa kokonaisuutena: nopeus, riippumattomuus ja
  luotettavuus.
