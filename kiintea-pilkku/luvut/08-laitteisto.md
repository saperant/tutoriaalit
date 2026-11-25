# Kiinteä pilkku vai liukuluku laitteistossa

Ohjelmistossa liukuluku on yleensä oikea valinta: suorittimessa on
valmiina nopea liukulukuyksikkö, ja ohjelmoijan aika on kalliimpaa
kuin muutama ylimääräinen kellojakso. Laitteistossa jokainen
aritmetiikkayksikkö rakennetaan erikseen, ja niiden pinta-ala, viive ja
teho näkyvät suoraan piirin hinnassa ja energiankulutuksessa. Kysymys
esitetään vasta nyt, koska vastaus tarvitsee edellisten lukujen
välineet: kiinteän pilkun hinta on bittikasvun ja kavennusten
kirjanpito, ja sen heikkous on luvussa 6 mitattu absoluuttinen
tarkkuus.

## Pinta-ala

Karkea malli laskee yksiköt täyssummaimina ja multipleksereinä, jotka
ovat suunnilleen yhtä suuria. Kiinteän pilkun summain on $n$ täyssummainta,
kertoja noin $n^2$. Liukulukusummain tarvitsee lisäksi eksponenttien
vertailun, kohdistussiirtäjän, normalisoinnin (etunollien laskenta ja
toinen siirtäjä) ja pyöristyksen. Liukulukukertoja kertoo vain
mantissat, joten se on lähellä saman levyistä kokonaislukukertojaa:

```{.python tiedosto="esimerkit/08-kustannus.py" osa="malli"}
```

```{.python tiedosto="esimerkit/08-kustannus.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/08-kustannus.odotettu"}
```

Malli ei korvaa synteesiä, mutta suuruusluokat ovat oikeat.
binary32-summain on yli kymmenen kertaa
32-bittistä kokonaislukusummainta suurempi, kun taas binary32-kertoja on
pienempi kuin 32-bittinen kokonaislukukertoja, koska mantissa on vain 24
bittiä. bfloat16:n pieni mantissa tekee kertojasta erityisen halvan, mikä
on yksi syy sen suosioon neuroverkkokiihdyttimissä.

## Viive ja teho

Liukulukusummaimen kriittinen polku kulkee kohdistuksen, yhteenlaskun,
etunollien laskennan ja normalisoinnin läpi, joten se on tyypillisesti
kaksi tai kolme kertaa kokonaislukusummaimen polkua pidempi. Se joko
hidastaa kelloa tai vaatii lisää liukuhihnavaiheita, mikä pidentää
latenssia ja kasvattaa takaisinkytkettyjen silmukoiden ongelmia.

Teho seuraa pinta-alaa ja kytkentäaktiivisuutta. Siirtäjät ovat
aktiivisia lähes joka operaatiossa, ja normalisointi muuttaa monia
bittejä kerralla. Kiinteän pilkun datapolun energiankulutus operaatiota
kohti on siksi selvästi pienempi, mikä ratkaisee akkukäyttöisissä
laitteissa ja suurissa kiihdyttimissä.

## Dynamiikka-alue

Liukuluvun etu on arvoalue. Dynamiikka-alue on suurimman ja pienimmän
nollasta eroavan arvon suhde desibeleinä:

```{.python tiedosto="esimerkit/08-dynamiikka.py" osa="alueet"}
```

```{.tuloste tiedosto="esimerkit/08-dynamiikka.odotettu" asti="binary32"}
```

Liukulukujen alueet on laskettu subnormaaleilla luvuilla, ja ne ovat
tähtitieteellisiä. Tärkeämpää on, että liukuluvun suhteellinen tarkkuus
on sama koko alueella. Kiinteän pilkun 16 bittiä antaa 90 dB, mutta
vain täyden skaalan signaalille; hiljaiset signaalit menettävät
tarkkuutta suhteessa tasoonsa, kuten luvussa 6 mitattiin.

## Lohkoliukuluku

Lohkoliukuluku (*block floating point*, BFP) on kompromissi: joukko
näytteitä jakaa yhden eksponentin, ja jokainen näyte on kiinteän pilkun
mantissa. Laitteisto laskee lohkon kiinteällä pilkulla ja käsittelee
eksponenttia vain kerran lohkoa kohti:

```{.python tiedosto="esimerkit/08-dynamiikka.py" osa="lohko"}
```

```{.python tiedosto="esimerkit/08-dynamiikka.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-dynamiikka.odotettu" alkaen="taso"}
```

![SQNR signaalin tason funktiona. Q1.15 menettää desibelin jokaista
signaalin desibeliä kohti. Lohkoliukuluku pysyy samalla tasolla kuin
Q1.15 täydellä skaalalla, ja binary32 on tasainen leveämmän mantissansa
korkeudella. Käyrät on laskettu esimerkin
funktioilla.](kuvat/lohkoliukuluku.png){width=80%}

Tavallisen Q1.15:n SQNR putoaa
signaalin tason mukana, mutta lohkoliukuluku pitää sen yli 90 dB:ssä,
koska jokainen lohko skaalataan täyteen skaalaan. Hinta on yksi
eksponentti lohkoa kohti ja lohkon suurimman arvon etsiminen ennen
kvantisointia. BFP on tavallinen FFT-kiihdyttimissä (jokaisen
perhosvaiheen jälkeen lohko skaalataan), radioiden kantataajuuspoluissa
ja uudemmissa koneoppimisen muodoissa, kuten MX-formaateissa, joissa 32
alkion lohko jakaa 8-bittisen skaalan.

## Käytännössä

- **Kiinteä pilkku, kun dynamiikka on tunnettu.** Signaalinkäsittely,
  jossa signaalitasot tunnetaan suunnitteluvaiheessa (suodattimet,
  modulaattorit, moottorinohjaus), kannattaa toteuttaa kiinteällä
  pilkulla.
- **Liukuluku, kun dynamiikka on tuntematon.** Yleiskäyttöinen
  laskenta, tieteellinen laskenta ja algoritmit, joiden välitulosten
  suuruusluokka vaihtelee paljon (matriisien käänteisluvut,
  iteratiiviset ratkaisijat), tarvitsevat liukulukuja.
- **Lohkoliukuluku välimaastoon.** Kun signaalin taso vaihtelee hitaasti
  tai lohkoittain, BFP antaa lähes liukuluvun tarkkuuden lähes kiinteän
  pilkun hinnalla.
- **Sekamuodot ovat normaaleja.** Neuroverkkokiihdyttimet kertovat
  bfloat16:lla tai int8:lla ja kerryttävät binary32:een tai
  int32:een. Kustannus ratkaistaan operaatio kerrallaan, ei koko
  järjestelmälle kerralla.

## Itsearviointi

- Osaat arvioida kiinteän pilkun ja liukuluvun summaimen ja kertojan
  suhteellisen pinta-alan ja selittää eron lähteet.
- Osaat laskea lukumuodon dynamiikka-alueen ja selittää eron absoluuttisen
  ja suhteellisen tarkkuuden välillä.
- Osaat toteuttaa lohkoliukuluvun ja kertoa, missä sitä käytetään.
- Osaat perustella lukumuodon valinnan sovelluksen dynamiikan
  perusteella.
