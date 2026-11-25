# Orientaatio ja Eulerin kulmat

Kaksiulotteisessa pelissä kappaleen asento on yksi kulma. Kulmia voi
laskea yhteen, niiden välistä voi interpoloida, ja kahden kierron
järjestyksellä ei ole väliä. Kolmessa ulottuvuudessa mikään näistä ei
päde. Tässä luvussa katsotaan, miksi tutuin esitys, kolme kulmaa, ei
riitä pelin sisäiseksi esitykseksi, ja mihin se silti sopii.

## Kolme vapausastetta

Kappaleen *orientaatio* eli asento avaruudessa on kierto, joka vie
kappaleen omat akselit maailman akseleilta nykyisille paikoilleen.
Kierrolla on kolme vapausastetta, ja luontevin tapa nimetä ne on kolme
kulmaa. Tutoriaalin sopimuksilla ne ovat:

| Kulma | Akseli | Arkikielellä |
|-------|--------|--------------|
| kääntö (*yaw*) | y, ylös | katse vasemmalle ja oikealle |
| nyökkäys (*pitch*) | x, oikealle | katse ylös ja alas |
| kallistus (*roll*) | z, eteen–taakse | pään kallistus olkapäätä kohti |

Näitä kutsutaan *Eulerin kulmiksi*. Ne ovat ihmiselle helpot:
"käänny 30 astetta vasemmalle ja katso 10 astetta alas" on ymmärrettävä
ohje, ja siksi editorit ja asetustiedostot näyttävät asennon kulmina.

## Järjestys vaikuttaa

Kolme kulmaa ei vielä määrää asentoa. On lisäksi sovittava, missä
järjestyksessä kierrot tehdään, koska kiertojen tulo ei ole
vaihdannainen. Esimerkissä lentokoneen nokka osoittaa aluksi suuntaan
−z ja selkä ylös:

```{.cpp tiedosto="esimerkit/02-euler.cpp" osa="asento"}
```

```{.cpp tiedosto="esimerkit/02-euler.cpp" osa="jarjestys"}
```

```{.tuloste tiedosto="esimerkit/02-euler.odotettu" rivit="1-3"}
```

Samat kaksi neljänneskierrosta vievät koneen eri asentoon: toisessa
nokka osoittaa ylös, toisessa vasemmalle. Jokainen ohjelma, joka
käyttää Eulerin kulmia, on valinnut jonkin kuudesta mahdollisesta
järjestyksestä ja lisäksi sen, kiertyvätkö akselit kappaleen mukana.
Kulmia ei siksi voi siirtää ohjelmasta toiseen tarkistamatta sopimusta.
Tässä tutoriaalissa funktio `eulerista` tekee kallistuksen ensin,
sitten nyökkäyksen ja viimeisenä käännön:

```{.cpp tiedosto="esimerkit/yhteinen/kvaternio.hpp" osa="euler"}
```

## Lukkiutuminen

Kun nyökkäys on 90 astetta, kone osoittaa suoraan ylös. Silloin
kallistusakseli on kääntynyt samansuuntaiseksi kääntöakselin kanssa, ja
kääntö ja kallistus tekevät saman asian:

```{.cpp tiedosto="esimerkit/02-euler.cpp" osa="lukko"}
```

```{.tuloste tiedosto="esimerkit/02-euler.odotettu" rivit="5-8"}
```

Kolme eri kulmayhdistelmää tuottaa täsmälleen saman asennon, koska
vain käännön ja kallistuksen erotus vaikuttaa. Yksi vapausaste on
kadonnut. Ilmiön nimi on *lukkiutuminen* (*gimbal lock*), ja se on
ominaisuus kolmen kulman esityksessä, ei kierroissa itsessään: kone voi
olla tässä asennossa aivan hyvin, mutta kulmilla sitä ei voi enää
kääntää jokaiseen suuntaan pienellä kulmien muutoksella. Lähellä
lukkiutumiskohtaa pieni asennon muutos vaatii suuren kulmien muutoksen,
mikä näkyy ohjauksen nykimisenä ja interpoloinnin heilahduksina.

## Kulmien interpolointi

Kulma on jaksollinen, ja jo yhdessä ulottuvuudessa sen interpolointi
vaatii huolellisuutta:

```{.cpp tiedosto="esimerkit/02-euler.cpp" osa="kierahdys"}
```

```{.tuloste tiedosto="esimerkit/02-euler.odotettu" rivit="10-12"}
```

Suunnista 350° ja 10° puolivälissä on 0°, mutta lukujen keskiarvo on
180°: kone käy katsomassa taakseen. Yhden kulman tapauksessa virheen
voi korjata valitsemalla lyhyemmän kaaren. Kolmen kulman interpolointi
on hankalampaa, koska kulmat eivät ole toisistaan riippumattomia: kun
kutakin interpoloidaan erikseen, välipisteet eivät kulje lyhintä reittiä
asennosta toiseen. Seuraava luku mittaa, kuinka kauas ne eksyvät.

## Mihin kulmat sopivat

Eulerin kulmat ovat hyvä esitys silloin, kun vapausasteita on
tarkoituksella rajoitettu:

- **Ensimmäisen persoonan kamera** tallentaa käännön ja nyökkäyksen.
  Kallistusta ei ole, ja nyökkäys rajataan alle 90 asteeseen, joten
  lukkiutumiskohtaan ei päästä (luku *Kamerat*).
- **Maassa kulkeva hahmo** kääntyy vain pystyakselin ympäri. Yksi
  kulma riittää.
- **Editorin kentät ja tiedostot** näyttävät asennon kulmina, koska
  ihminen lukee ja kirjoittaa niitä.

Vapaasti pyörivän kappaleen, kuten lentävän aluksen, heitetyn esineen
tai animoidun nivelen, asento tallennetaan ja lasketaan muulla tavalla.

## Käytännössä

- **Kulmat ovat käyttöliittymä, eivät laskennan esitys.** Asento
  muunnetaan kulmista kvaternioksi tai matriisiksi heti rajalla ja
  pidetään siinä muodossa.
- **Kirjaa kulmien sopimus.** Akselit, järjestys ja kiertosuunta
  kuuluvat rajapinnan kuvaukseen. Väärä järjestys näyttää toimivan
  niin kauan kuin vain yksi kulma poikkeaa nollasta.
- **Älä interpoloi kolmea kulmaa.** Yhden kulman interpolointi on
  turvallista, kun valitsee lyhyemmän kaaren; kolmen ei.
- **Rajaa, älä korjaa.** Kamera, jonka nyökkäys on rajattu, ei
  lukkiudu. Yritys "korjata" lukkiutuminen erikoistapauksilla johtaa
  hyppäyksiin.

## Itsearviointi

- Osaat näyttää esimerkillä, että kahden kierron järjestys muuttaa
  lopputulosta, ja kertoa, mitä kulmien sopimukseen kuuluu.
- Osaat selittää, mikä lukkiutuminen on, missä asennossa se tapahtuu
  ja miksi se on esityksen eikä kiertojen ominaisuus.
- Osaat perustella, missä pelin osissa Eulerin kulmat ovat hyvä valinta
  ja missä eivät.
