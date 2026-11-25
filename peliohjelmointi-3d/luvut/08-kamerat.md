# Kamerat

Kaksiulotteisessa pelissä kamera on suorakulmio, joka seuraa pelaajaa.
Kolmessa ulottuvuudessa kamera on pelin olio: sillä on paikka ja
asento, pelaaja ohjaa sitä, se liikkuu omalla tahdillaan ja törmää
maailmaan. Huono kamera pilaa hyvänkin pelin, koska pelaaja näkee
kaiken sen läpi. Tässä luvussa tehdään kaksi peruskameraa,
ensimmäisen ja kolmannen persoonan kamera, ja niiden kaksi tärkeintä
yksityiskohtaa: pehmennys ja törmäys.

## Ensimmäisen persoonan kamera

Kamera on pelaajan silmissä. Hiiri kääntää katsetta, näppäimet
liikuttavat pelaajaa. Asento tallennetaan kahtena kulmana, kääntönä ja
nyökkäyksenä: tämä on luvun *Orientaatio ja Eulerin kulmat* tapaus,
jossa kulmat ovat oikea esitys.

```{.cpp tiedosto="esimerkit/08-fps.cpp" osa="fps"}
```

Kolme yksityiskohtaa erottaa toimivan kameran toimimattomasta:

- **Nyökkäys rajataan** hieman alle 90 asteeseen. Kamera ei käänny
  ylösalaisin eikä osu lukkiutumiskohtaan.
- **Kävelysuunta riippuu vain käännöstä.** Jos liike laskettaisiin
  koko katselusuunnasta, alas katsova pelaaja kävelisi hitaammin ja
  yrittäisi painua lattian läpi.
- **Vinoon ei liikuta nopeammin.** Eteen ja sivulle yhtä aikaa antaa
  vektorin, jonka pituus on $\sqrt{2}$; se normalisoidaan.

```{.cpp tiedosto="esimerkit/08-fps.cpp" osa="kavely"}
```

```{.tuloste tiedosto="esimerkit/08-fps.odotettu" rivit="1-4"}
```

Jokainen kolmesta sekunnin kävelystä on neljän metrin mittainen, myös
vinoon ja alas katsoen.

Näkymämatriisi on kameran maailmamuunnoksen käänteismuunnos. Sen voi
rakentaa funktiolla `katse` tai suoraan kameran asennosta; tulos on
sama:

```{.cpp tiedosto="esimerkit/08-fps.cpp" osa="nakyma"}
```

```{.tuloste tiedosto="esimerkit/08-fps.odotettu" rivit="5-5"}
```

### Kertyvä kierto kallistaa horisontin

Houkutteleva tapa toteuttaa hiiren ohjaus on pitää asento kvaterniona
ja kertoa sitä joka ruudulla pienellä kierrolla kameran omien akselien
ympäri. Se näyttää toimivan, kunnes hiirtä liikutetaan ympyrää:

```{.cpp tiedosto="esimerkit/08-fps.cpp" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/08-fps.odotettu" rivit="6-6"}
```

Kymmenen hiiren ympyrän jälkeen horisontti on lähes viisi astetta
vinossa. Syy on kiertojen vaihdannaisuuden puute: kääntö ja nyökkäys
kameran omien akselien ympäri tuottavat yhdessä myös kallistusta, joka
kertyy. Kun kulmat tallennetaan ja asento rakennetaan niistä joka kerta
alusta, käännön akseli on aina maailman pystyakseli eikä kallistusta
synny.

## Kolmannen persoonan kamera

Kamera kiertää hahmoa kiinteällä etäisyydellä. Pelaaja ohjaa samoja
kahta kulmaa, mutta nyt ne määräävät kameran paikan pallon pinnalla
kohteen ympärillä:

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="kierto"}
```

Kohde ei ole hahmon jalat vaan piste hieman sen yläpuolella, yleensä
olkapäiden korkeudella, jotta hahmo ei peitä näkymää.

## Pehmennys

Kamera, joka on jäykästi kiinni hahmossa, välittää pelaajalle jokaisen
askelman ja töytäisyn. Siksi kameran paikkaa ja etäisyyttä
*pehmennetään*: kamera liikkuu kohti tavoitettaan, mutta ei hyppää
siihen.

Tavallisin toteutus on virheellinen. Rivi "siirry joka ruudulla
kymmenesosa matkasta kohti tavoitetta" näyttää pehmennykseltä, mutta
sen nopeus riippuu ruutunopeudesta. Oikea muoto on eksponentiaalinen:
jäljellä olevasta erosta poistuu sama osuus samassa *ajassa*.

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="pehmennys"}
```

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="ruutunopeus"}
```

```{.tuloste tiedosto="esimerkit/08-seuranta.odotettu" rivit="1-4"}
```

Kiinteän osuuden kamera jää 30 ruudun sekuntinopeudella puolitoista
metriä jälkeen ja 120 ruudun nopeudella 37 senttiä: peli tuntuu
erilaiselta eri koneilla. Eksponentiaalisen pehmennyksen jälkeenjäänti
on lähes sama kaikilla nopeuksilla. Pieni ero syntyy siitä, että kohde
itse liikkuu tässä kokeessa askelittain.

Sama kaava sopii kaikkeen, mikä seuraa tavoitetta: kameran etäisyyteen,
hahmon kääntymiseen liikesuuntaan ja animaatioiden painoihin.

## Kameran törmäys

Kun hahmo kävelee seinän viereen, kiinteän etäisyyden päässä oleva
kamera joutuu seinän taakse, ja pelaaja näkee seinän sisäpuolen.
Yksinkertaisin korjaus on säde kohteesta toivottuun kameran paikkaan.
Jos säde osuu johonkin, kamera siirretään osumakohdan eteen.

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="tormays"}
```

```{.cpp tiedosto="esimerkit/08-seuranta.cpp" osa="kavely"}
```

```{.tuloste tiedosto="esimerkit/08-seuranta.odotettu" rivit="6-15"}
```

![Sama hetki ilman kameran törmäystä ja sen kanssa. Vasemmalla kamera
on viiden metrin päässä seinän takana ja näkee vain seinän. Oikealla
se on vedetty seinän eteen 2,4 metrin
päähän.](kuvat/kamera.png){width=90%}

Käytännön kamerassa on vielä kaksi lisäystä. Lähemmäs tullaan heti,
koska seinän läpi näkeminen on pahempi virhe kuin äkillinen liike,
mutta takaisin kauemmas palataan pehmeästi. Lisäksi yhden säteen
sijasta käytetään pyyhkäistyä palloa tai muutamaa sädettä, jotta
kameran lähitaso ei leikkaa seinää kulmissa. Luvun *Lyhty* pelissä on
näistä ensimmäinen.

## Käytännössä

- **Kamera päivitetään hahmon jälkeen.** Jos kamera lasketaan ennen
  liikettä, se on aina yhden askeleen jäljessä ja tärisee.
- **Kulmat kameran tilana.** Kääntö ja nyökkäys tallennetaan, ja
  asento rakennetaan niistä. Kertyvä kierto kallistaa horisontin.
- **Pehmennys on ajan funktio.** Muoto `1 - exp(-nopeus * dt)` toimii
  millä tahansa ruutunopeudella; kiinteä kerroin ei.
- **Liike kameran suhteen.** Kolmannessa persoonassa "eteen" tarkoittaa
  kameran katselusuuntaa maan tasossa, ei hahmon nenän suuntaa.
- **Älä pehmennä pelaajan syötettä.** Hiiren liikkeen viivästäminen
  tuntuu tahmealta. Pehmennetään sitä, mikä seuraa pelaajaa, ei sitä,
  mitä pelaaja ohjaa.
- **Kamera kuuluu piirtoon.** Kameran voi päivittää jokaisella
  piirretyllä ruudulla, vaikka peli etenee kiinteällä askeleella,
  kunhan se seuraa hahmon interpoloitua paikkaa.

## Itsearviointi

- Osaat toteuttaa ensimmäisen persoonan kameran ja perustella
  nyökkäyksen rajauksen, vaakatason kävelysuunnan ja vinon liikkeen
  normalisoinnin.
- Osaat selittää, miksi kertyvä kierto kameran omien akselien ympäri
  kallistaa horisontin.
- Osaat toteuttaa pehmennyksen, joka ei riipu ruutunopeudesta, ja
  näyttää, miksi kiinteä kerroin riippuu.
- Osaat estää kolmannen persoonan kameraa joutumasta seinän taakse.
