# Koneoppimisen lukumuodot

Neuroverkon laskenta on enimmäkseen matriisituloja, joiden tulokset
kulkevat epälineaaristen funktioiden läpi. Yksittäisen painon
tarkkuudella on vähän merkitystä, mutta muistin määrällä ja
kaistanleveydellä on paljon. Kun luku vie 16 tai 8 bittiä 32:n sijaan,
malli mahtuu pienempään muistiin, data siirtyy nopeammin, ja
laitteisto mahtuu tekemään enemmän kertolaskuja samassa ajassa. Tästä
syystä koneoppiminen on tuonut uusia lukumuotoja IEEE 754:n rinnalle.

## binary16 ja bfloat16

IEEE:n binary16 (puolitarkkuus, `float16`) jakaa 16 bittiä viiteen
eksponenttibittiin ja kymmeneen mantissabittiin. Tarkkuus on kohtuullinen,
mutta arvoalue on kapea: suurin luku on 65 504 ja pienin normaali
noin $6 \cdot 10^{-5}$. Neuroverkon gradientit ovat usein tätä
pienempiä, joten binary16-koulutus tarvitsee häviön skaalausta (*loss
scaling*).

Googlen bfloat16 (*brain floating point*) tekee toisin päin: kahdeksan
eksponenttibittiä kuten binary32:ssa ja vain seitsemän mantissabittiä.
Arvoalue on sama kuin `float`-tyypillä, joten skaalausta ei tarvita, ja
muunnos on yksinkertainen: bfloat16 on binary32:n ylin puolisko.
Muunnos tehdään pyöristäen lähimpään parilliseen, ei katkaisemalla:

```{.c tiedosto="esimerkit/08-bfloat16.c" osa="bf16"}
```

```{.tuloste tiedosto="esimerkit/08-bfloat16.odotettu"}
```

π on bfloat16:na 3,140625, eli tarkkuutta on vain 2–3 desimaalia. Arvo
65 504 (binary16:n suurin) pyöristyy 65 536:een, ja 1,00390625 on
tasapeli, joka pyöristyy parilliseen eli 1,0:aan.

## FP8

Kahdeksan bitin liukuluvuista on vakiintunut kaksi muotoa (OCP:n
standardi 2023, NVIDIA Hopper ja uudemmat). E4M3 käyttää neljä bittiä
eksponentille ja kolme mantissalle, ja sitä käytetään painoille ja
aktivaatioille. E5M2 käyttää viisi bittiä eksponentille ja kaksi
mantissalle, ja sitä käytetään gradienteille, joiden arvoalue on
laajempi. E4M3 poikkeaa IEEE-säännöistä: sillä ei ole ääretöntä, ja
NaN on vain yksi bittikuvio. Näin suurin luku on 448 eikä 240.

Pienet muodot on helpointa ymmärtää purkamalla kaikki bittikuviot.
Seuraava luokka purkaa minkä tahansa muodon, kun eksponentti- ja
mantissabittien määrä annetaan:

```{.python tiedosto="esimerkit/08-pienet.py" osa="muoto"}
```

```{.python tiedosto="esimerkit/08-pienet.py" osa="taulukko"}
```

Toteutus tarkistetaan NumPyä vasten kaikilla 65 536 binary16- ja
bfloat16-koodilla:

```{.python tiedosto="esimerkit/08-pienet.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/08-pienet.odotettu"}
```

Taulukko kertoo muotojen erot. Epsilon on ykkösen ja seuraavan luvun
väli eli suhteellinen tarkkuus. E4M3:n suhteellinen virhe voi olla 6 %,
joten FP8-laskennassa jokaisella tensorilla on oma skaalauskerroin,
joka siirtää arvot muodon parhaalle alueelle.

## Kvantisointi kokonaisluvuiksi

Päättelyssä (*inference*) mallin painot voidaan muuntaa 8-bittisiksi
kokonaisluvuiksi. Liukuluku $x$ esitetään muodossa
$x \approx s \cdot (q - z)$, jossa $q$ on int8-arvo, $s$ skaalauskerroin
ja $z$ nollapiste. Painoille käytetään yleensä *symmetristä*
kvantisointia ($z = 0$), koska painot ovat nollan molemmin puolin:

```{.python tiedosto="esimerkit/08-kvantisointi.py" osa="symmetrinen"}
```

Aktivaatiot ovat usein epäsymmetrisiä, esimerkiksi ReLU:n jälkeen
pelkästään positiivisia. *Asymmetrinen* kvantisointi kuvaa koko
arvoalueen $[\min, \max]$ int8:n 256 arvoon, jotta mitään ei hukata:

```{.python tiedosto="esimerkit/08-kvantisointi.py" osa="asymmetrinen"}
```

Tiheän kerroksen tulo lasketaan kokonaisluvuilla. Kertolaskut tehdään
int8-arvoilla, tulot kertyvät 32-bittiseen summaan, ja skaalauskertoimet
kerrotaan vasta lopuksi:

```{.python tiedosto="esimerkit/08-kvantisointi.py" osa="kerros"}
```

```{.tuloste tiedosto="esimerkit/08-kvantisointi.odotettu"}
```

Painot vievät neljäsosan tilasta, ja virhe on alle prosentin, mikä
riittää useimmille malleille. Kertymä on 32-bittinen, koska kahden
int8-luvun tulo vie jo 15 bittiä ja 64 tulon summa ylittää 16 bitin
rajan. Kapeampi kertymä kiertäisi hiljaa:

```{.c tiedosto="esimerkit/08-kertyma.c" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/08-kertyma.odotettu"}
```

Laitteistot on rakennettu tämän mukaan. x86:n VNNI-käskyt, ARM:n
SDOT-käskyt ja GPU:iden tensoriytimet kertovat int8-arvoja ja
kerryttävät tulot 32-bittisiin rekistereihin yhdellä käskyllä.

## Käytännössä

- **Muoto käyttötarkoituksen mukaan.** Koulutus: bfloat16 tai float32
  (painojen pääkopio), gradientit tarvittaessa FP8 E5M2. Päättely:
  int8 tai FP8 E4M3, isoilla kielimalleilla 4-bittiset muodot.
  Tarkkuuskriittiset vaiheet, kuten normalisointi ja softmax, lasketaan
  float32:lla.
- **Kertymä on aina leveämpi.** int8-tulot int32-kertymään, bfloat16-
  ja FP8-tulot float32-kertymään. Tämä on kirjastojen ja laitteiden
  oletus, ja oma toteutus tekee samoin.
- **Kalibroi skaalauskertoimet.** Asymmetrisen kvantisoinnin arvoalue
  mitataan edustavalla datalla. Yksittäinen poikkeava arvo levittää
  alueen ja syö tarkkuuden, joten alue rajataan usein persentiileihin.
- **Mittaa tarkkuus tehtävällä, ei luvuilla.** Kvantisoinnin vaikutus
  arvioidaan mallin tuloksella, kuten tarkkuudella tai virheellä, koska
  yksittäisen kerroksen suhteellinen virhe ei kerro kaikkea.
- **Pyöristä parilliseen.** Muunnokset (float32 → bfloat16, float →
  int8) pyöristetään, ei katkaista. Katkaisu vinouttaa tuloksia
  järjestelmällisesti yhteen suuntaan.

## Itsearviointi

- Osaat kertoa binary16:n, bfloat16:n, FP8 E4M3:n ja E5M2:n
  bittijaon, arvoalueen ja tarkkuuden sekä niiden käyttötarkoitukset.
- Osaat muuntaa float32-luvun bfloat16-muotoon pyöristäen lähimpään
  parilliseen.
- Osaat kvantisoida painot symmetrisesti ja aktivaatiot asymmetrisesti
  ja laskea kerroksen tulon kokonaisluvuilla.
- Osaat selittää, miksi kertymä on leveämpi kuin syötteet.
