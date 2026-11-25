# Entiteetit ja ECS

Pelimaailma on täynnä *entiteettejä*: pelaaja, viholliset, ammukset,
kolikot ja ovet. Niiden mallintaminen on pelin arkkitehtuurin
keskeisin päätös. Oliohierarkia on luonteva alku, mutta pelien
yhdistelmät kasvavat sen yli, ja suuret oliomäärät tekevät sen hitaaksi.

## Oliohierarkian ongelma

Hierarkiassa jokainen kyky on luokka: liikkuva, lentävä, ampuva.
Kun suunnittelija pyytää lentävää ampujaa, puuhun ei ole paikkaa.

```{.cpp tiedosto="esimerkit/06-hierarkia.cpp" osa="hierarkia"}
```

```{.tuloste tiedosto="esimerkit/06-hierarkia.odotettu"}
```

Lentävä ampuja kopioi koodia toisesta haarasta. Kymmenen kyvyn
yhdistelmiä on tuhat, ja puu muuttuu "jumalaluokaksi", jossa kaikki
kyvyt ovat yhdessä kantaluokassa lippuina.

## Komponentit

Ratkaisu on *koostaminen*: entiteetti on joukko komponentteja, ja
kyvyt ovat komponentteja. Komponenttipohjaisessa mallissa (Unityn
GameObject ja Godotin solmut) komponentit ovat olioita, joilla on omat
metodinsa. *Entiteettikomponenttijärjestelmässä* (ECS) mennään
pidemmälle:

- **Entiteetti** on pelkkä tunniste.
- **Komponentti** on pelkkää dataa ilman metodeja.
- **Järjestelmä** on funktio, joka käsittelee kaikki entiteetit, joilla
  on tietyt komponentit.

```{.cpp tiedosto="esimerkit/06-ecs/main.cpp" osa="komponentit"}
```

```{.cpp tiedosto="esimerkit/06-ecs/main.cpp" osa="kokoaminen"}
```

```{.cpp tiedosto="esimerkit/06-ecs/main.cpp" osa="jarjestelmat"}
```

Lentävä ampuja syntyy lisäämällä komponentit; uutta koodia ei tarvita.
Järjestelmät eivät tiedä, mitä entiteettiä ne käsittelevät, vaan vain
mitä dataa niillä on.

## Harva joukko

ECS:n suorituskyky tulee datan asettelusta. Kunkin komponenttityypin
arvot ovat tiiviisti peräkkäin taulukossa, joten järjestelmä käy
muistin läpi järjestyksessä. Tämä esimerkki käyttää *harvaa joukkoa*
(sparse set), jota myös EnTT-kirjasto käyttää.

```{.cpp tiedosto="esimerkit/06-ecs/rekisteri.hpp" osa="joukko"}
```

![Harva joukko, kun olioilla 1, 4 ja 3 on nopeuskomponentti. Harva
taulukko on indeksoitu olion tunnuksella ja kertoo paikan tiheässä
taulukossa; tiheä taulukko ja komponenttien arvot ovat samassa
järjestyksessä ilman aukkoja, ja järjestelmä käy läpi vain
ne.](kuvat/harva-joukko.png){width=80%}

Poisto siirtää viimeisen alkion aukkoon, joten taulukossa ei ole
reikiä, ja haku on vakioaikainen. Hinta: järjestys muuttuu poistossa, ja
usean komponentin kysely joutuu hakemaan muut komponentit harvan
taulukon kautta.

```{.cpp tiedosto="esimerkit/06-ecs/rekisteri.hpp" osa="rekisteri"}
```

Entiteetin tunnisteessa on indeksi ja sukupolvi. Kun entiteetti
tuhotaan, indeksi kierrätetään, mutta sukupolvi kasvaa. Vanha tunniste
ei siis osoita uuteen entiteettiin, vaikka joku olisi tallentanut sen
(esimerkiksi ohjus kohteensa).

```{.cpp tiedosto="esimerkit/06-ecs/rekisteri.hpp" osa="entiteetti"}
```

```{.cpp tiedosto="esimerkit/06-ecs/main.cpp" osa="sukupolvi"}
```

```{.tuloste tiedosto="esimerkit/06-ecs.odotettu"}
```

## Hinta mitattuna

Oliohierarkiassa jokainen olio on erikseen keossa, ja päivitys hakee
osoittimen, olion ja virtuaalitaulun. Pitkään pyörineessä pelissä
oliot ovat hajallaan muistissa, ja jokainen haku voi olla välimuistin
ohitus. Taulukoiden rakenteessa (structure of arrays) päivitys lukee
vain tarvittavat kentät peräkkäin.

```{.cpp tiedosto="esimerkit/mittaus/src/oliot-vs-taulukot.cpp" osa="oliot"}
```

```{.cpp tiedosto="esimerkit/mittaus/src/oliot-vs-taulukot.cpp" osa="taulukot"}
```

Mittaus käännetään optimoiden esimerkkihakemiston Makefilellä
(`make mittaa`). Tuloste on vertailu, jotta testi on toistettava:

```{.tuloste tiedosto="esimerkit/mittaus/oliot-vs-taulukot.odotettu"}
```

Tutoriaalin testikoneella miljoonan olion päivitys oli taulukoilla
lähes 20 kertaa nopeampi kuin olioilla. Suuruusluokka on kymmenen
millisekuntia vastaan alle yksi, ja 60 Hz:n pelissä koko ruudun
budjetti on 16,7 ms. Tarkat luvut riippuvat koneesta, suhde paljon
vähemmän. Ero syntyy muistista eikä virtuaalikutsusta: tiiviissä taulukossa prosessori lukee peräkkäisiä
välimuistirivejä ja kääntäjä vektoroi silmukan (ks. taito *Suorituskyvyn
analyysi ja optimointi*).

## Käytännössä

- **Koostaminen periytymisen sijaan.** Syvät pelioliohierarkiat ovat
  tunnettu antimalli; useimmat moottorit perustuvat komponentteihin.
- **ECS kun olioita on paljon.** Tuhansia samankaltaisia olioita
  (ammukset, partikkelit, joukot) hyötyy tiiviistä datasta. Muutama
  kymmen ainutlaatuista oliota ei tarvitse ECS:ää.
- **Tunniste, ei osoitin.** Entiteettien väliset viittaukset tehdään
  sukupolvellisilla tunnisteilla, jotka voi tarkistaa.
- **Järjestelmien järjestys on pelimekaniikkaa:** syöte, tekoäly,
  liike, törmäykset, vahingot, siivous. Järjestys kirjoitetaan
  näkyviin yhteen paikkaan.
- Valmiit C++-kirjastot: EnTT (harvat joukot) ja flecs
  (arkkityypit). Unityn DOTS ja Bevy (Rust) ovat ECS-moottoreita.

## Itsearviointi

- Osaat selittää, miksi oliohierarkia ei skaalaudu pelien kykyjen
  yhdistelmiin.
- Osaat toteuttaa harvan joukon ja ECS-kyselyn usealle komponentille.
- Osaat käyttää sukupolvellisia tunnisteita ja kertoa, mitä ongelmaa
  ne ratkaisevat.
- Osaat perustella datan asettelun vaikutuksen suorituskykyyn ja mitata
  sen.
