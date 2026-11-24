# Pelisilmukka

Pelisilmukan tärkein päätös on, miten pelin aika etenee suhteessa
seinäkelloon. Näyttöjen virkistystaajuudet vaihtelevat (60, 120, 144 Hz
tai muuttuva), ja yksittäinen ruutu voi viivästyä levyhaun tai
käyttöjärjestelmän takia. Pelin pitää silti toimia samoin kaikilla
koneilla.

## Muuttuva aika-askel

Yksinkertaisin silmukka mittaa edellisen ruudun keston ja antaa sen
päivitykselle: `paivita(dt)`. Liike näyttää oikealta, mutta simulaation
tulos riippuu ruudunpäivitysnopeudesta. Diskreetti integrointi tekee
jokaisella askeleella pienen virheen, ja virheen suuruus riippuu
askeleen pituudesta.

```{.cpp tiedosto="esimerkit/02-muuttuva.cpp" osa="huippu"}
```

```{.tuloste tiedosto="esimerkit/02-muuttuva.odotettu"}
```

Hitaalla koneella hahmo hyppää korkeammalle ja ylettyy tasanteelle,
johon nopealla koneella ei pääse. Sama ilmiö tekee törmäyksistä
satunnaisia ja moninpelistä mahdotonta, koska koneet eivät päädy samaan
tilaan.

## Kiinteä aika-askel ja kertymä

Ratkaisu on päivittää peliä aina samalla askeleella, esimerkiksi
1/60 sekuntia, ja ajaa askelia niin monta kuin seinäkellon mukaan
kuuluu. Ruudun kesto lisätään *kertymään* (accumulator), josta otetaan
kokonaisia askelia. Ylijäämä siirtyy seuraavaan ruutuun.

```{.cpp tiedosto="esimerkit/02-kiintea.cpp" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/02-kiintea.odotettu"}
```

Kolme erilaista ruutujen kestosarjaa tuottaa bitilleen saman tilan,
koska simulaatio näkee vain kiinteät askeleet. Kaksi yksityiskohtaa
ratkaisevat, toimiiko menetelmä:

- **Aika kokonaislukuina.** Jos kertymä olisi `double`, toistuva
  vähennys kerryttäisi pyöristysvirhettä, ja eri kestosarjat voisivat
  tuottaa eri määrän askelia. `std::chrono::nanoseconds` on tarkka.
- **Kuolemanspiraalin esto.** Jos päivitys on hitaampi kuin
  reaaliaika, kertymä kasvaa, jokainen ruutu ajaa yhä useamman askeleen
  ja peli pysähtyy. Ruudun kesto rajataan (`MAKSIMI`), jolloin peli
  hidastuu mutta ei jumiudu. Sama raja estää hypyn, kun ikkunaa
  raahataan tai debuggeri pysäyttää ohjelman.

## Interpolointi

Kiinteä askel ei osu yksiin näytön virkistyksen kanssa. 60 Hz:n
simulaatio 144 Hz:n näytöllä tuottaa ruutuja, joista osa näyttää saman
tilan kahdesti, osa yhden askeleen eteenpäin. Liike nykii, vaikka
simulaatio on tasainen. Ratkaisu on piirtää tila kahden viimeisen
simulaatiotilan välistä, kertymän osuuden mukaan.

```{.cpp tiedosto="esimerkit/02-interpolointi.cpp" osa="interpolointi"}
```

```{.cpp tiedosto="esimerkit/02-interpolointi.cpp" osa="piirto"}
```

```{.tuloste tiedosto="esimerkit/02-interpolointi.odotettu"}
```

Ilman interpolointia sijainti etenee portaittain (0, 0, 1, 1, 2, 2, 2,
3), interpoloituna tasaisesti noin 0,42 pikseliä ruudussa. Hinta on
yhden askeleen viive: piirretty kuva on aina enintään 1/60 sekuntia
simulaatiota jäljessä. Vaihtoehto on *ekstrapolointi* nykytilasta
eteenpäin, joka poistaa viiveen mutta näyttää joskus väärän paikan
(esimerkiksi seinän sisällä).

## Determinismi

Deterministinen peli tuottaa samasta alkutilasta ja samasta syötteestä
saman lopputilan. Se mahdollistaa uusinnat, automaattiset testit,
vianetsinnän tallenteista ja lukitusaskeleen moninpelin. Determinismi ei
tule ilmaiseksi:

- **Kiinteä aika-askel**, kuten edellä.
- **Oma satunnaislukugeneraattori** kiinteällä siemenellä. C++:n
  `std::uniform_int_distribution` ja muut jakaumat ovat
  toteutuskohtaisia: sama siemen tuottaa eri luvut libstdc++:ssa ja
  MSVC:ssä. Generaattori ja välin valinta kannattaa toteuttaa itse.
- **Järjestys.** `std::unordered_map`in läpikäyntijärjestys voi vaihdella
  toteutuksesta toiseen; pelilogiikan ei pidä riippua siitä.
- **Liukuluvut.** Sama ohjelma samalla alustalla on deterministinen,
  mutta eri kääntäjäasetukset (`-ffast-math`, FMA-käskyt) tai alustat
  voivat tuottaa eri tuloksen. Alustojen välinen determinismi vaatii
  kiinteän pilkun lukuja tai tarkasti rajatut kääntäjäasetukset.

```{.cpp tiedosto="esimerkit/02-satunnaisuus.cpp" osa="pcg"}
```

```{.cpp tiedosto="esimerkit/02-satunnaisuus.cpp" osa="noppa"}
```

```{.tuloste tiedosto="esimerkit/02-satunnaisuus.odotettu"}
```

PCG32 on pieni, nopea ja tilastollisesti hyvä. `valilta` hylkää
vinouman aiheuttavat arvot: pelkkä `seuraava() % 6` suosisi pieniä
lukuja hieman, koska 2^32 ei ole jaollinen kuudella.

## Käytännössä

- **Kiinteä askel simulaatiolle, vapaa piirrolle.** Lähes kaikki
  fysiikkamoottorit (Box2D, PhysX, Godotin ja Unityn fysiikka) vaativat
  kiinteän askeleen. Pelin muu logiikka kannattaa ajaa samassa
  askeleessa, jolloin kaikki on toistettavaa.
- **Aika kokonaislukuina ja ruudun kesto rajattuna.** Nanosekunnit tai
  mikrosekunnit `int64`-lukuina; maksimikesto 0,1–0,25 sekuntia.
- **Interpoloi piirrettävät muunnokset**, ei koko tilaa. Tallenna
  edellinen sijainti ja kierto niille kappaleille, jotka liikkuvat.
- **Erota kello pelistä.** Pelilogiikka ei kutsu kelloa vaan saa
  `dt`:n. Silloin testi voi ajaa tuhat ruutua sekunnissa ja uusinta
  toistuu samana.
- **Hinta:** kiinteä askel maksaa yhden askeleen viiveen ja
  pahimmillaan useita päivityksiä ruudussa. Jos päivitys on raskas,
  askelta ei lyhennetä vaan päivitystä nopeutetaan.

## Itsearviointi

- Osaat selittää, miksi muuttuva aika-askel tekee pelistä
  laitteistoriippuvaisen.
- Osaat toteuttaa kiinteän aika-askeleen kertymällä ja estää
  kuolemanspiraalin.
- Osaat interpoloida piirron kahden simulaatiotilan välillä ja kertoa
  sen hinnan.
- Osaat luetella determinismin edellytykset ja toteuttaa siemenellä
  toistettavan satunnaislukugeneraattorin.
