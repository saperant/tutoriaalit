# Simulaatioaskel, pinot ja lepo

Edelliset luvut rakensivat moottorin osat. Tässä luvussa ne kootaan
simulaatioaskeleeksi ja lisätään kaksi asiaa, joita ilman kokonainen
kohtaus ei toimi: laaja vaihe, joka karsii turhat törmäystestit, ja
lepotila, joka pysäyttää paikallaan olevien kappaleiden laskennan.

## Askeleen vaiheet

```{.dot otsikko="Simulaatioaskeleen vaiheet. Nuolien vieressä on data, joka siirtyy vaiheesta toiseen." leveys="100%"}
digraph {
  rankdir=LR;
  ranksep=0.22;
  node [shape=box, margin="0.06,0.04"];
  voimat [label="1. voimat\nnopeuksiksi"];
  laaja [label="2. laaja\nvaihe"];
  kapea [label="3. kapea\nvaihe"];
  ratk [label="4. ratkaisija"];
  paikat [label="5. paikat ja\nasennot"];
  lepo [label="6. lepotila"];
  voimat -> laaja;
  laaja -> kapea [label="parit"];
  kapea -> ratk [label="monistot"];
  ratk -> paikat [label="nopeudet"];
  paikat -> lepo;
}
```

Järjestys on puoli-implisiittisen Eulerin järjestys: nopeudet ensin,
paikat lopuksi. Rajoitteet ratkaistaan välissä, jolloin paikat
integroidaan nopeuksilla, jotka jo toteuttavat ne.

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="maailma"}
```

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="askel"}
```

Maailma on pelkkää dataa. Edellisen askeleen monistot ovat osa tilaa,
koska lämmin käynnistys lukee niistä kertyneet impulssit. Tällä on
merkitystä luvussa 13.

## Laaja vaihe

Kapean vaiheen testi on kallis, ja kappalepareja on $n(n-1)/2$.
*Laaja vaihe* karsii parit, jotka eivät voi koskettaa, vertaamalla
kappaleiden akselien suuntaisia ympäryksiä. Taito *3D-peliohjelmointi*
teki tämän staattiselle maailmalle hierarkialla (BVH). Liikkuville
kappaleille yksinkertaisin toimiva menetelmä on *järjestä ja
pyyhkäise* (*sort and sweep*): ympärykset järjestetään yhden akselin
alkukohdan mukaan, ja kutakin verrataan vain niihin seuraaviin,
joiden alku on ennen sen loppua.

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="laaja"}
```

Kolme yksityiskohtaa ovat tärkeitä. Ympärys on kosketusmarginaalin
verran kappaletta suurempi, jotta lähes koskettavat parit pääsevät
kapeaan vaiheeseen. Pari, jonka kumpikaan kappale ei liiku, ohitetaan.
Ja järjestys on vakaa ja parit lajitellaan lopuksi, jotta sama
kohtaus tuottaa parit aina samassa järjestyksessä.

## Pyramidi

```{.cpp tiedosto="esimerkit/09-pino.cpp" osa="pyramidi"}
```

```{.cpp tiedosto="esimerkit/09-pino.cpp" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/09-pino.odotettu" rivit="1-15"}
```

![Pyramidi nukkuu (harmaa), herää pallon osumasta, romahtaa ja nukahtaa
uudelleen. Viimeisessä kuvassa vain pois vierivä pallo on
hereillä.](kuvat/pyramidi.png){width=100%}

Puolen sekunnin kohdalla 55 mahdollisesta parista laaja vaihe päästää
läpi 22, ja niistä 16 koskettaa. Sekunnin kohdalla sarakkeissa on
nollia: pyramidi nukkuu, eikä sille lasketa mitään. Pallon tultua
energia hyppää, ja siitä eteenpäin se vain pienenee. Suurin yhden
askeleen aikana syntynyt energian lisäys on neljä millijoulea, joka
tulee sijainnin korjauksesta.

## Lepotila

Paikallaan oleva kappale ei ole fysiikalle ilmainen: sen kosketukset
ratkaistaan joka askeleella, ja ratkaisijan pienet virheet saavat sen
värisemään. *Lepotila* (*sleeping*) poistaa kappaleen simulaatiosta,
kun se on ollut riittävän kauan lähes paikallaan.

Kappaletta ei voi nukuttaa yksin. Jos pinon alin laatikko nukahtaa ja
ylempi on vielä liikkeessä, alin muuttuu sen kannalta seinäksi.
Lepotila päätetään siksi *saarittain*. Saari on joukko kappaleita,
jotka ovat yhteydessä toisiinsa kosketusten tai nivelten kautta.
Liikkumaton kappale ei yhdistä saaria, sillä muuten lattia tekisi
koko maailmasta yhden saaren.

```{.cpp tiedosto="esimerkit/yhteinen/maailma.hpp" osa="lepo"}
```

Saaret löydetään *union–find*-rakenteella (taito *Edistyneet
algoritmit ja tietorakenteet*). Saari nukahtaa, kun sen jokainen
kappale on ollut puoli sekuntia nopeusrajan alapuolella, ja herää
kokonaan, kun yksikin sen kappaleista liikkuu. Nukkuva kappale on
ratkaisijalle liikkumaton: sen käänteismassa on nolla.

```{.cpp tiedosto="esimerkit/09-pino.cpp" osa="lepo"}
```

```{.tuloste tiedosto="esimerkit/09-pino.odotettu" alkaen="lopussa unessa"}
```

## Miksi pinot ovat vaikeita

Pino on ratkaisijalle hankalin tavallinen tilanne kolmesta syystä.
Kuorma kulkee ylhäältä alas, mutta korjaukset etenevät kierroksessa
vain yhden kosketuksen verran, joten korkea pino tarvitsee monta
kierrosta. Jokaisessa kosketuksessa on neljä pistettä, joiden rivit
ovat lähes riippuvia toisistaan. Ja pienikin sivuttainen virhe
kasautuu, koska pino on ylösalaisin käännetty heiluri.

Edellisen luvun keinot, eli kertyneet impulssit, lämmin käynnistys ja
kosketusmarginaali, tekevät pinoista mahdollisia. Lepotila tekee
niistä pysyviä: nukkuva pino ei valu eikä värise.

## Käytännössä

- **Laaja vaihe valitaan kohtauksen mukaan.** Järjestä ja pyyhkäise
  toimii, kun kappaleet ovat jakautuneet valitulle akselille. Suuriin
  maailmoihin käytetään dynaamista ympäryshierarkiaa tai ruudukkoa.
  Kappaleet liikkuvat askeleessa vähän, joten edellisen askeleen
  järjestys tai puu kelpaa lähtökohdaksi.
- **Staattinen ja dynaaminen erikseen.** Liikkumaton maailma
  rakennetaan tilarakenteeseen kerran, ja vain liikkuvat kappaleet
  päivitetään.
- **Lepotila on myös laatuominaisuus.** Se säästää laskentaa, mutta
  yhtä tärkeää on, että se lopettaa värinän ja hitaan valumisen.
- **Herätä aina, kun jokin muuttuu.** Nukkuva kappale on herätettävä,
  kun siihen osutaan, sen nivel muuttuu, sen alta poistetaan kappale
  tai peli antaa sille voiman. Unohtunut herätys näkyy ilmassa
  leijuvana laatikkona.
- **Saaret rinnakkain.** Saaret eivät vaikuta toisiinsa askeleen
  aikana, joten ne voi ratkaista eri säikeissä. Tulos säilyy
  toistettavana, kun saarten sisäinen järjestys on kiinteä.
- **Mittaa parit ja pisteet.** Laajan vaiheen läpäisseiden parien ja
  kosketuspisteiden määrät kertovat, mihin fysiikan aika kuluu.

## Itsearviointi

- Osaat luetella simulaatioaskeleen vaiheet ja perustella niiden
  järjestyksen.
- Osaat selittää, miten järjestä ja pyyhkäise karsii parit.
- Osaat kertoa, miksi lepotila päätetään saarittain ja milloin saari
  herää.
- Osaat nimetä syyt, joiden takia korkea pino on ratkaisijalle
  vaikea.
