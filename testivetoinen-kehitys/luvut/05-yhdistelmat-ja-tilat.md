# Päätöstaulut, tilat ja parit

Edellisen luvun tekniikat käsittelivät yhtä syötettä kerrallaan. Moni
virhe syntyy vasta, kun ehdot yhdistyvät, kun toimintojen järjestys
vaihtuu tai kun kaksi asetusta osuu yhteen. Tässä luvussa on kolme
tekniikkaa näihin tilanteisiin.

## Päätöstaulu

Kun tulos riippuu usean ehdon yhdistelmästä, sanallinen sääntö jättää
lähes aina jonkin yhdistelmän auki. Esimerkkinä kaupan alennussääntö:

> Alennukset eivät kasaannu, vaan suurin yksittäinen alennus pätee.
> Kampanjakoodi antaa 10 %, kanta-asiakkuus 5 % ja vähintään 100 euron
> tilaus 5 %. Poikkeus: kanta-asiakkaan iso tilaus saa 10 %, ja jos
> hänellä on lisäksi kampanjakoodi, 15 %.

**Päätöstaulussa** jokainen ehto on rivi ja jokainen ehtojen yhdistelmä
sarake. Kolmesta kyllä–ei-ehdosta tulee kahdeksan saraketta, ja
jokaiselle on kirjattava tulos:

| Ehto / sääntö | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---------------------|---|---|---|---|---|---|---|---|
| kanta-asiakas | E | E | E | E | K | K | K | K |
| kampanjakoodi | E | E | K | K | E | E | K | K |
| tilaus ≥ 100 e | E | K | E | K | E | K | E | K |
| **alennus-%** | 0 | 5 | 10 | 10 | 5 | 10 | 10 | 15 |

Taulun täyttäminen on jo testausta, vaikka koodia ei ole. Sarake 7
(kanta-asiakas ja koodi, pieni tilaus) ei näy sanallisessa säännössä
erikseen, ja joku joutuu päättämään, onko tulos 10 vai 15. Taulu
tekee aukon näkyväksi ennen kuin ohjelmoija täyttää sen arvaamalla.

Toteutus ja sen viallinen versio, jossa ehtojen järjestys nielee
viimeisen sarakkeen:

```{.python tiedosto="esimerkit/05-paatostaulu/alennus.py" osa="alennus"}
```

```{.python tiedosto="esimerkit/05-paatostaulu/alennus_viallinen.py" osa="viallinen"}
```

Kun jokainen ehto testataan erikseen, viallinen toteutus menee läpi:

```{.python tiedosto="esimerkit/05-paatostaulu/test_1_ehdot_erikseen.py" osa="erikseen"}
```

Päätöstaulusta johdettu testi on taulu sellaisenaan. Viimeinen testi
varmistaa, ettei taulusta puutu yhdistelmiä:

```{.python tiedosto="esimerkit/05-paatostaulu/test_2_paatostaulu.py" osa="taulu"}
```

```{.tuloste tiedosto="esimerkit/05-paatostaulu/odotettu"}
```

Täysi taulu kasvaa nopeasti: kymmenellä ehdolla sarakkeita on 1 024.
Sarakkeita voi yhdistää, kun jokin ehto ei vaikuta tulokseen
(esimerkissä sarakkeet 3 ja 4: koodilla tilauksen koko ei ratkaise,
ellei asiakas ole kanta-asiakas). Yhdistäminen on kuitenkin väite
toteutuksesta, ja täysi taulu on turvallisempi aina, kun se mahtuu
ruudulle.

## Tilasiirtymät

Jos sama syöte tuottaa eri tuloksen sen mukaan, mitä aiemmin on
tapahtunut, ohjelmalla on tila. Tilauksen voi perua ennen lähetystä
mutta ei sen jälkeen. Tällainen käytös kuvataan **tilakoneena**:

```{.dot otsikko="Tilauksen elinkaari"}
digraph {
  rankdir=LR;
  node [shape=ellipse];
  alku [shape=point, width=0.12];
  alku -> UUSI;
  UUSI -> MAKSETTU [label="maksa"];
  MAKSETTU -> LAHETETTY [label="laheta"];
  LAHETETTY -> TOIMITETTU [label="toimita"];
  UUSI -> PERUTTU [label="peru"];
  MAKSETTU -> PERUTTU [label="peru"];
}
```

Kaavio näyttää sallitut siirtymät. Testauksen kannalta yhtä tärkeitä
ovat ne, joita kaaviossa *ei* ole. Viisi tilaa ja neljä tapahtumaa
tekevät kaksikymmentä paria, joista viisi on sallittuja ja viidentoista
pitää päättyä virheeseen.

Toteutus, jossa siirtymät ovat taulukossa, ja toinen, jossa ne on
kirjoitettu ehtolauseiksi:

```{.python tiedosto="esimerkit/05-tilat/tilaus.py" osa="siirtymat"}
```

```{.python tiedosto="esimerkit/05-tilat/tilaus_viallinen.py" osa="viallinen"}
```

Tyypilliset polut toimivat molemmissa:

```{.python tiedosto="esimerkit/05-tilat/test_1_polut.py" osa="polut"}
```

Siirtymätaulusta johdettu testi käy läpi jokaisen tilan ja tapahtuman
parin. Sallitun siirtymän pitää päätyä oikeaan tilaan ja muiden nostaa
virhe:

```{.python tiedosto="esimerkit/05-tilat/test_2_siirtymat.py" osa="kaikki"}
```

```{.tuloste tiedosto="esimerkit/05-tilat/odotettu"}
```

Testi löysi kaksi poikkeamaa. Ensimmäinen on selvä virhe: lähetetyn
tilauksen voi perua. Toinen on tulkintakysymys: onko jo perutun
tilauksen peruminen uudelleen virhe vai harmiton toisto? Taulu pakottaa
päättämään, ja päätös kannattaa tehdä tietoisesti, koska verkon yli
tulevat pyynnöt toistuvat usein (taito *Hajautetut järjestelmät*:
idempotenssi).

Tässä testi kerää poikkeamat yhteen väitteeseen, jotta tulos mahtuu
sivulle. Tavallisesti jokainen pari parametroidaan omaksi testikseen.

Kaikkien parien kokeilu kattaa yksittäiset siirtymät. Pidemmät polut,
kuten "maksa, peru, maksa uudelleen", vaativat peräkkäisten siirtymien
testejä, ja niiden määrä kasvaa nopeasti. Luvun 7 tilakonetesti antaa
polkujen keksimisen koneelle.

## Parittainen testaus

Kolmas tilanne on asetusten yhdistelmät. Tilausvahvistuksen teksti
riippuu neljästä valinnasta:

```{.python tiedosto="esimerkit/05-parit/vahvistus.py" osa="parametrit"}
```

Kaikkia yhdistelmiä on 3 · 3 · 2 · 3 = 54. Tässä se vielä onnistuisi,
mutta kymmenellä neliarvoisella asetuksella yhdistelmiä on yli
miljoona. Toisessa ääripäässä on sarja, jossa jokainen arvo esiintyy
ainakin kerran:

```{.python tiedosto="esimerkit/05-parit/test_1_jokainen_arvo.py" osa="arvot"}
```

Kolme testiä kattaa jokaisen arvon, mutta kahden arvon yhdistelmistä
vain murto-osan. **Parittainen testaus** (*pairwise*, *all-pairs*)
valitsee testit niin, että jokainen kahden eri asetuksen arvopari
esiintyy ainakin yhdessä testissä. Perustelu on kokemusperäinen:
suurin osa asetusvirheistä laukeaa yhden arvon tai kahden arvon
yhdistelmästä, ja kolmen tai useamman arvon yhteisvaikutusta vaativat
viat ovat harvinaisempia.

Pienen parittaisen joukon voi rakentaa ahneesti: valitaan aina se
yhdistelmä, joka kattaa eniten vielä kattamattomia pareja.

```{.python tiedosto="esimerkit/05-parit/parit.py" osa="parit"}
```

```{.python tiedosto="esimerkit/05-parit/test_2_parit.py" osa="testit"}
```

Yhdeksän testiä 54:n sijaan kattaa kaikki parit. Viallisesta
toteutuksesta puuttuu yhden toimitustavan ja kielen yhdistelmän teksti,
ja parittainen sarja osuu siihen:

```{.tuloste tiedosto="esimerkit/05-parit/odotettu"}
```

Säästö kasvaa asetusten määrän mukana. Kaikkien yhdistelmien määrä
kolminkertaistuu jokaisesta uudesta kolmiarvoisesta asetuksesta, mutta
parittainen joukko kasvaa vain hitaasti. Sen koko on vähintään kahden
suurimman asetuksen arvomäärien tulo, tässä yhdeksän:

![Kaikkien yhdistelmien ja luvun generaattorin tuottaman parittaisen
joukon koko, kun jokaisella asetuksella on kolme arvoa. Pystyakseli on
logaritminen.](kuvat/parit.png){width=75%}

Parittainen testaus ei takaa mitään kolmen arvon yhteisvaikutuksista.
Jos vika vaatii laskun, automaatin *ja* ruotsin kielen, parittainen
joukko löytää sen vain sattumalta. Kriittisille asetuksille voi vaatia
kolmikot, tai lisätä käsin ne yhdistelmät, jotka ovat tuotannossa
yleisimpiä.

Esimerkin generaattori käy läpi kaikki yhdistelmät, joten se sopii vain
pieniin tapauksiin, eikä ahne valinta aina löydä pienintä joukkoa.
Suuriin on valmiita työkaluja, kuten Microsoftin PICT ja Pythonin
`allpairspy`, jotka tukevat myös rajoitteita.

## Käytännössä

- **Valitse tekniikka ongelman muodon mukaan.** Ehtojen yhdistelmät:
  päätöstaulu. Järjestyksestä riippuva käytös: tilasiirtymät.
  Riippumattomat asetukset: parit.
- **Tee taulu ennen koodia.** Päätöstaulu ja siirtymätaulu ovat
  määrittelyn muotoja. Ne kannattaa käydä läpi tilaajan kanssa, koska
  avoimet sarakkeet ovat hänen päätöksiään.
- **Pidä taulu koodissa datana.** Kun siirtymät ovat sanakirjassa,
  sama taulu toimii toteutuksena, testin odotusarvona ja
  dokumentaationa.
- **Testaa myös kielletyt siirtymät.** Unohtunut tarkistus ei näy
  yhdessäkään onnistuneessa polussa.
- **Parittainen joukko on lähtötaso.** Lisää siihen yleisimmät ja
  riskialtteimmat yhdistelmät.

## Itsearviointi

- Osaat laatia päätöstaulun sanallisesta säännöstä ja tunnistaa
  yhdistelmät, joihin sääntö ei vastaa.
- Osaat johtaa tilakaaviosta testit sekä sallituille että kielletyille
  siirtymille.
- Osaat selittää, mitä parittainen kattavuus tarkoittaa, miksi se
  riittää usein ja milloin se ei riitä.
- Osaat valita päätöstaulun, tilasiirtymätestauksen ja parittaisen
  testauksen väliltä ongelman perusteella.
