# Väylä ja oheislaitteet

Järjestelmässä on useita kohteita: muisti, sarjaportti, ajastin ja
monta muuta. Ohjelmisto näkee ne osoitteina, ja *osoitekartta* kertoo,
mikä osoitealue kuuluu millekin laitteelle. Väylämalli on TLM:n
välittäjä: se ottaa vastaan aloittajan transaktion, valitsee kohteen
osoitteen perusteella ja välittää transaktion eteenpäin. Tämä luku
rakentaa väylän, kaksi oheislaitetta ja ohjelmistoa jäljittelevän
aloittajan.

## Osoitekartta

```{.cpp tiedosto="esimerkit/10-vayla/main.cpp" osa="kartta"}
```

Kartta on järjestelmän tärkein yhteinen määrittely: sama tieto on
ohjelmiston otsaketiedostoissa, laitepuussa (*device tree*), RTL:n
väylädekooderissa ja verifioinnin rekisterimallissa. Isoissa projekteissa
se generoidaan yhdestä lähteestä, esimerkiksi IP-XACT- tai
SystemRDL-kuvauksesta (taito *SoC-integraatio*).

## Väylämalli

Väylän kohdesocket `multi_passthrough_target_socket` ottaa vastaan
useita aloittajia, ja sen aloittajasocket
`multi_passthrough_initiator_socket` kytketään useisiin kohteisiin. Kutsun
mukana tulee indeksi, joka kertoo, mistä socketin liitännästä kutsu
tuli.

```{.cpp tiedosto="esimerkit/mallit/vayla.hpp" osa="vayla"}
```

Dekoodaus etsii alueen, jolle osoite kuuluu, ja muuttaa osoitteen
kohteen omaksi siirtymäksi. Kohteen ei siis tarvitse tietää, mihin
osoitteeseen se on kartoitettu, ja saman mallin voi sijoittaa mihin
tahansa. Kun kohde on vastannut, väylä palauttaa alkuperäisen
osoitteen: aloittaja saa payloadinsa takaisin sellaisena kuin sen
lähetti, vastausta lukuun ottamatta.

```{.cpp tiedosto="esimerkit/mallit/vayla.hpp" osa="dekoodaus"}
```

Väylä lisää jokaiseen siirtoon oman viiveensä, 5 ns. Tämä on karkea
malli: se ei mallinna sitä, että kaksi aloittajaa joutuisi oikeassa
väylässä odottamaan toisiaan (*arbitration*, *contention*). LT-malleissa
kilpailu jätetään tavallisesti pois tai mallinnetaan tilastollisesti,
koska sen tarkka mallintaminen vaatisi juuri sitä synkronointia, josta
LT-tyylillä halutaan eroon. Kilpailun vaikutusta tutkitaan AT-malleilla
(luku 10).

## Rekisterilohkot

Oheislaitteen rajapinta on joukko 32-bittisiä rekistereitä. Yhteinen
pohjaluokka tarkistaa pyynnön muodon ja jättää aliluokalle vain
rekisterien merkityksen:

```{.cpp tiedosto="esimerkit/mallit/rekisterit.hpp" osa="rekisterit"}
```

Sarjaportin malli (`mallit/uart.hpp`) on yksinkertaisin mahdollinen:
datarekisterin kirjoitus lähettää merkin, ja tilarekisterin bitti 0
kertoo lähettimen olevan vapaana. Malli ei mallinna siirtonopeutta,
joten lähetin on aina vapaana. Se kerää merkit riveiksi ja tulostaa ne
aikaleiman kanssa; aikaleima on aloittajan aika (`sc_time_stamp() +
viive`), kuten pohjaluokka sen välittää.

Ajastin palauttaa kuluneet kellojaksot. Parametri `aikatietoinen`
valitsee, käyttääkö malli aloittajan paikallista aikaa vai pelkkää
simulaatioaikaa; ero tulee merkitykselliseksi luvussa 9.

```{.cpp tiedosto="esimerkit/mallit/ajastin.hpp" osa="ajastin"}
```

Rekisterin luvulla tai kirjoituksella on usein sivuvaikutus: tilarekisterin
luku nollaa lipun, datarekisterin kirjoitus käynnistää lähetyksen,
keskeytyksen kuittaus vaatii kirjoituksen tiettyyn bittiin. Nämä
kuvataan mallissa samoin kuin laitteen käsikirjassa, koska ajuri
luottaa niihin. Oheislaitemallin tarkkuus mitataan siis rekisteritasolla:
jokainen ohjelmiston näkemä bitti ja sivuvaikutus on oikein, mutta
sisäinen toteutus saa olla mikä tahansa.

## Ohjelmisto aloittajana

Aloittaja kirjoittaa sarjaporttiin merkkijonon kuten yksinkertainen
ajuri: se odottaa, että lähetin on vapaana, ja kirjoittaa merkin.
Lopuksi se kokeilee kahta virhettä ja debug-lukua:

```{.cpp tiedosto="esimerkit/10-vayla/main.cpp" osa="ohjelma"}
```

```{.cpp tiedosto="esimerkit/10-vayla/main.cpp" osa="kytkenta"}
```

```{.tuloste tiedosto="esimerkit/10-vayla/odotettu"}
```

Kukin merkki vie 50 ns: tilarekisterin luku ja datarekisterin kirjoitus
maksavat kumpikin väylän 5 ns ja laitteen 20 ns. Ä-kirjaimet ovat
UTF-8:ssa kaksi tavua, joten 14 merkin rivi on 17 tavua.
Kartoittamaton osoite antaa osoitevirheen väylältä ja kirjoitus vain
luettavaan rekisteriin komentovirheen ajastimelta.

## Debug-liikenne

`transport_dbg` lukee tai kirjoittaa kohteen sisältöä ilman
simulaatioaikaa ja ilman sivuvaikutuksia. Sitä käyttävät debuggerin
muistinäkymä, ohjelman lataaja ja testipenkki, joka tarkistaa muistin
tilan. Esimerkin debug-luku palauttaa siirrettyjen tavujen määrän (4) ja
muistiin kirjoitetun arvon, eikä simulaatioaika etene.

Muisti toteuttaa debug-liikenteen samalla tarkistuksella ja kopioinnilla
kuin `b_transport`in, mutta ilman viivettä ja tilastoja. Oheislaitteiden rekisterilohko ei toteuta sitä lainkaan, jolloin
`simple_target_socket` palauttaa nollan. Se on turvallinen valinta: debug-
luku, joka tyhjentäisi vastaanottojonon tai kuittaisi keskeytyksen,
muuttaisi ohjelman käyttäytymistä sen mukaan, katsooko debuggeri
muistia.

## Käytännössä

- **Kohde ei tiedä osoitettaan.** Väylä muuntaa osoitteet, joten saman
  oheislaitemallin voi sijoittaa useaan kohtaan ja useaan
  järjestelmään. Kartta kuvataan yhdessä paikassa.
- **Rekisterimalli käsikirjasta.** Rekisterien osoitteet, kentät,
  nollausarvot ja sivuvaikutukset tulevat laitteen määrittelystä, ja
  mieluiten samasta koneluettavasta lähteestä, josta RTL ja ajurin
  otsakkeet generoidaan.
- **Virheet kuten laitteistossa.** Kartoittamaton osoite, väärä leveys
  ja kirjoitus vain luettavaan rekisteriin palauttavat virheen, joka
  vastaa oikean väylän virhettä. Malli, joka hyväksyy kaiken, piilottaa
  ajurin virheet, jotka tulevat esiin vasta piirillä.
- **Debug ilman sivuvaikutuksia.** `transport_dbg` toteutetaan muistille
  ja muistinkaltaisille kohteille. Rekistereille se toteutetaan vain, jos
  luvulla ei ole sivuvaikutuksia.
- **Kilpailu on oma päätöksensä.** LT-väylä, joka ei mallinna
  kilpailua, antaa liian optimistisen suorituskyvyn. Se riittää
  ohjelmistokehitykseen, mutta suorituskykyarvioihin tarvitaan AT-malli
  tai vähintään kuormaan perustuva viivekorjaus.

## Itsearviointi

- Osaat kirjoittaa väylämallin, joka dekoodaa osoitteet, muuntaa ne
  kohteen siirtymiksi ja palauttaa virheen kartoittamattomasta osoitteesta.
- Osaat mallintaa oheislaitteen rekisterit, mukaan lukien vain luettavat
  rekisterit ja sivuvaikutukset.
- Osaat selittää, mihin `transport_dbg`ia käytetään ja miksi sillä ei saa
  olla sivuvaikutuksia.
- Osaat kertoa, mitä LT-väylä jättää mallintamatta ja milloin se on
  ongelma.
