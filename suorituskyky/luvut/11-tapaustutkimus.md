# Tapaustutkimus: kuvan sumennus

Tämä luku kokoaa edelliset yhteen. Kuvankäsittelyn laatikkosumennus
(engl. box blur) korvaa jokaisen pikselin sen ympäristön keskiarvolla.
Se on monen kuvasuodattimen, kuten Gaussin sumennuksen likiarvon,
rakennuspala. Toteutus nopeutetaan neljässä vaiheessa, ja jokainen
vaihe testataan ensimmäistä vastaan ja mitataan kahdella tavalla:
ajalla ja Cachegrindin käskymäärillä.

## Lähtötaso

Kuva on harmaasävykuva, yksi tavu pikseliä kohden riveittäin.
Sumennuksen säde on $R = 4$, eli ikkuna on $9 \times 9$ pikseliä.
Reunoilla ikkunan ulkopuoliset koordinaatit rajataan lähimpään
reunapikseliin. Suoraviivainen toteutus laskee jokaiselle pikselille 81
luvun summan:

```{.c tiedosto="esimerkit/11-sumennus.c" osa="v1"}
```

Keskiarvo pyöristetään lisäämällä puolet jakajasta ennen
kokonaislukujakoa. Kaikki vaiheet käyttävät kokonaislukuja, joten ne
voivat antaa bitilleen saman tuloksen, ja testi vertaa koko kuvan
tiivisteitä. Testikuva on $123 \times 123$, jotta reunat ja
parittomat koot tulevat testatuiksi:

```{.tuloste tiedosto="esimerkit/11-sumennus.odotettu"}
```

Luvun 3 termein pikseli maksaa $(2R+1)^2 = 81$ latausta ja
yhteenlaskua sekä 162 rajausta. Työ kasvaa säteen neliönä.

## Vaihe 2: erota suunnat

Laatikon summa on sen rivisummien summa. Ensin lasketaan jokaiselle
pikselille vaakasuuntainen yhdeksän pikselin summa väliaikaiseen
taulukkoon, sitten näiden pystysuuntainen summa:

```{.c tiedosto="esimerkit/11-sumennus.c" osa="v2"}
```

Pikseliä kohden on nyt $2(2R+1) = 18$ latausta 81:n sijaan.
Väliaikainen taulukko on 16-bittinen, koska yhdeksän tavun summa on
enintään 2295. Muutos on algoritminen: säteen neliö muuttui
lineaariseksi.

## Vaihe 3: liukuva summa

Kun ikkuna siirtyy yhden pikselin oikealle, summaan tulee yksi uusi
arvo ja siitä poistuu yksi. Summaa ei tarvitse laskea uudelleen:

```{.c tiedosto="esimerkit/11-sumennus.c" osa="v3"}
```

Pikseliä kohden on nyt kaksi yhteenlaskua kummassakin suunnassa
säteestä riippumatta. Pystysuunta kulkee kuitenkin sarake
kerrallaan, ja kuten luvussa 5 nähtiin, sarakkeittainen läpikäynti
hyppii muistissa rivin pituuden askelin.

## Vaihe 4: rivit peräkkäin

Pystysuunnan liukuvan summan voi pitää jokaiselle sarakkeelle omana
lukunaan taulukossa. Silloin rivi kerrallaan edetessä kaikki sarakkeet
päivitetään peräkkäin: lisätään ikkunaan tuleva rivi ja vähennetään
siitä poistuva.

```{.c tiedosto="esimerkit/11-sumennus.c" osa="v4"}
```

Sisin silmukka käy kolmea taulukkoa riveittäin ilman kierrosten
välisiä riippuvuuksia, joten kääntäjä voi vektoroida sen ja päivittää
kahdeksan tai kuusitoista 16-bittistä summaa yhdellä käskyllä.
`restrict`-osoittimet kertovat, että rivit ja summataulukko eivät ole
päällekkäin. Jakolasku vakiolla 81 on kääntäjälle kertolasku ja
siirto, joka myös vektoroituu.

## Tulokset

Cachegrind laskee käskyt ja välimuistihudit vaiheittain
$256 \times 256$ -kuvalle:

```{.tuloste tiedosto="esimerkit/tulokset/tarkista-sumennus.txt"}
```

Käskyjä on pikseliä kohden noin 1560, 250, 44 ja 31. Vaiheen 3
L1-hutit ovat kaksikymmenkertaiset muihin nähden: sarakkeittainen
pystysuunta koskee jokaisella askeleella eri riviin. Vaihe 4 lukee
enemmän dataa kuin vaihe 3, koska se käy sekä tulevan että poistuvan
rivin läpi, mutta riveittäin ja ilman hutia. Ajat
$2048 \times 2048$ -kuvalle kirjoittajan koneella:

```{.tuloste tiedosto="esimerkit/tulokset/11-sumennus.txt"}
```

![Vaiheet rinnakkain logaritmisella asteikolla (samat luvut kuin
tulosteissa). Vaihe 3 vähentää käskyjä mutta kasvattaa L1-hudit
kaksikymmenkertaisiksi, joten aika pitenee; vaihe 4 poistaa
hudit.](kuvat/sumennus.png){width=92%}

Vaihe 2 toi algoritmisella muutoksella noin seitsenkertaisen
nopeuden. Vaihe 3 vähensi käskyt vielä kuudesosaan, mutta suuri kuva
hidastui: sarakkeittaisen läpikäynnin hudit maksoivat enemmän kuin
säästetyt käskyt. Vasta vaihe 4, joka tekee saman liukuvan summan
riveittäin, lunasti algoritmin hyödyn ja oli noin seitsemän kertaa
vaihetta 2 nopeampi. Yhteensä sumennus nopeutui kymmeniä kertoja,
ja tulos on bitilleen sama. Mittaukset on käännetty tasolla `-O2`,
jolla GCC 14 ei vektoroi näitä silmukoita, joten vaiheiden 3 ja 4 ero
tulee pelkästä muistin käyttötavasta. Luvun 9 optimointitasojen
vertailussa vektoroitu vaihe 4 (`-O3`) oli vielä selvästi nopeampi.

## Mihin seuraavaksi

Amdahlin laki kertoo, mihin kannattaa katsoa seuraavaksi. Vaiheessa
4 vaakasuuntainen liukuva summa on rivin sisällä riippuvuusketju, eikä
se vektoroidu, kun taas pystysuunta vektoroituu. Mahdollisia jatkoja:

- **Rajauksen poisto sisäosasta.** Kuvan reunat käsitellään erikseen,
  ja sisäosan silmukat kirjoitetaan ilman `rajaa`-kutsuja.
- **Vaakasuunnan vektorointi.** Usean rivin vaakasummat lasketaan
  rinnakkain vektorin eri kaistoilla tai lohko transponoidaan
  välimuistissa.
- **Pienemmät tyypit.** Väliaikainen taulukko on 16-bittinen; 8-bittinen
  ulostulo laskettuna suoraan summista säästää kaistaa.
- **Rinnakkaisuus.** Rivit ovat riippumattomia lukuun ottamatta
  liukuvan summan aloitusta, joten kuvan voi jakaa vaakasuuntaisiin
  kaistoihin säikeittäin. Tämä on taidon *Rinnakkaisohjelmointi*
  aihe, ja näytönohjain on taidon *GPU-laskenta* aihe.

Jokainen näistä on mitattava erikseen. Kun ajo on enää muutamia
millisekunteja, kuvan lukeminen levyltä ja purkaminen voi viedä
moninkertaisesti enemmän aikaa, ja silloin sumennuksen nopeuttaminen
ei enää näy käyttäjälle.

## Käytännössä

- **Aloita algoritmista.** Vaiheiden 2 ja 3 muutokset pienensivät
  työn kertaluokkaa; mikään laitteistotemppu ei olisi tehnyt samaa.
- **Seuraa muistin käyttötapaa.** Kun työ on pientä, välimuisti
  ratkaisee: vaihe 4 teki enemmän latauksia kuin vaihe 3 mutta oli
  moninkertaisesti nopeampi.
- **Testaa jokainen vaihe ensimmäistä vastaan.** Kokonaislukulaskenta
  ja tiiviste tekevät vertailusta tarkan; liukuluvuilla tarvitaan
  toleranssi.
- **Käytä kahta mittaria.** Käskymäärä on toistettava ja kertoo työn
  määrän, aika kertoo hinnan.
- **Lopeta, kun Amdahlin laki sanoo niin.** Kun osa ei enää näy
  profiilissa, sen optimointi ei näy käyttäjälle.

## Itsearviointi

- Osaat muuttaa kaksiulotteisen ikkunasuodattimen erottuvaksi ja
  perustella, miksi tulos ei muutu.
- Osaat toteuttaa liukuvan summan ja selittää, miksi sen työ ei
  riipu säteestä.
- Osaat järjestää pystysuuntaisen laskennan riveittäiseksi ja
  selittää Cachegrindin luvuilla, miksi se on nopeampi.
- Osaat arvioida Amdahlin lailla, mikä osa ohjelmasta kannattaa
  optimoida seuraavaksi.
