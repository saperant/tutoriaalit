# Parametrit, taulukot ja tarkistukset

Oikeat lohkot toistavat rakenteita: DMA-ohjaimessa on kanavia,
ajastinpiirissä ajastimia ja keskeytysohjaimessa lähteitä. Määrä
vaihtelee tuotteittain. Tässä luvussa kuvataan toistuvat rakenteet
taulukkoina, tehdään niiden määrästä parametri, lisätään kuvaukseen
omia tietoja ja katsotaan, mitä kääntäjä tarkistaa.

## Rekisteriryhmät ja taulukot

DMA-ohjaimen jokaisella kanavalla on samat neljä rekisteriä. Ne
kuvataan kerran rekisteriryhmänä (`regfile`), ja ryhmästä tehdään
taulukko:

```{.systemverilog tiedosto="esimerkit/rdl/dma.rdl" osa="dma"}
```

`kanava KANAVA[KANAVIA] @ 0x100 += 0x10;` sijoittaa ensimmäisen
kanavan osoitteeseen 0x100 ja seuraavat 0x10 tavun välein.
Askeleen (`+=`) voi jättää pois, jolloin kääntäjä käyttää ryhmän kokoa.
Eksplisiittinen askel on kuitenkin parempi, koska kanavan rekisterien
lisääminen ei silloin siirrä seuraavia kanavia.

Taulukko säilyy mallissa taulukkona. Generaattori voi purkaa sen
(`unroll=True`) yksittäisiksi rekistereiksi tai tuottaa taulukon
sellaisenaan: C-otsakkeeseen syntyy rakennetaulukko, SVD-tiedostoon
klusteri, jolla on toistomäärä, ja RTL:ään `generate`-silmukka tai
taulukko.

## Parametrit

`addrmap dma #(longint unsigned KANAVIA = 4)` tekee kanavamäärästä
parametrin oletusarvoineen. Parametri annetaan instantioinnissa
(`dma #(.KANAVIA(2)) DMA0`), komentorivillä (`peakrdl ... -P
KANAVIA=2`) tai Pythonista elaborointiin:

```{.python tiedosto="esimerkit/04-parametrit.py" osa="parametrit"}
```

```{.tuloste tiedosto="esimerkit/04-parametrit.odotettu"}
```

Sama kuvaus tuottaa kolme eri kokoista lohkoa, ja osoitteet lasketaan
kuvauksesta. Parametri kannattaa rajata siihen, mikä todella vaihtelee
tuotteiden välillä. Jokainen parametri kasvattaa niiden kokoonpanojen
määrää, jotka on verifioitava.

## Omat ominaisuudet

Standardin ominaisuudet eivät kata kaikkea, mitä projektin
työkaluketju tarvitsee: turvallisuusluokan, laitepuun
yhteensopivuusmerkkijonon tai keskeytysnumeron. SystemRDL sallii omat
ominaisuudet (*user-defined properties*). Niille määritellään tyyppi ja
komponentit, joihin ne saa liittää:

```{.systemverilog tiedosto="esimerkit/rdl/ominaisuudet.rdl" osa="udp"}
```

Kääntäjä tarkistaa omat ominaisuudet kuten standardin omat: väärän
tyyppinen arvo tai väärä komponentti on virhe. Generaattori, joka ei
tunne ominaisuutta, ohittaa sen. DMA-kuvauksen `SUOJAUS`-rekisteri on
merkitty turvalliseksi, ja oma generaattori voi esimerkiksi jättää sen
pois ei-suojatun ohjelmiston otsakkeesta tai merkitä sen
dokumentaatioon:

```{.python tiedosto="esimerkit/04-parametrit.py" osa="turvallinen"}
```

Tiedosto `ominaisuudet.rdl` sisällytetään esiprosessorilla
(`` `include ``), ja sen sisältö on suojattu kaksinkertaiselta
sisällyttämiseltä (`` `ifndef ``), koska sekä DMA:n että koko piirin
kuvaus sisällyttävät sen. Esiprosessori on SystemVerilogin kaltainen.
Lisäksi SystemRDL:ssä on Perl-tyylinen esiprosessori, jolla voi
tuottaa toistuvaa tekstiä, mutta parametrit ja taulukot ovat sitä
selkeämpiä.

## Kääntäjän tarkistukset

Kuvauksen tarkistukset ovat standardin suurin hyöty omaan muotoon
verrattuna. Taidossa *EDA-työkaluketjujen automatisointi* oma
tarkistin kirjoitettiin itse, ja se löysi tahallaan rikotusta
kuvauksesta kahdeksan virhettä. SystemRDL-kääntäjä tarkistaa samat
asiat ja paljon muuta ilman omaa koodia. Esimerkki `02-virheet.py`
kääntää neljä tahallaan virheellistä kuvausta:

```{.tuloste tiedosto="esimerkit/02-virheet.odotettu"}
```

Virheitä on kahta lajia. Tavalliset virheet (*error*) kerätään, ja
käännös pysähtyy vasta, kun kaikki on tarkistettu. Kirjoittaja voi
korjata kaikki kerralla. Kohtalokas virhe (*fatal*), kuten viittaus
olemattomaan kenttään tai sopimaton ominaisuuden arvo, pysäyttää
käännöksen heti, koska mallia ei voi rakentaa pidemmälle.

Kentän pääsyn ja käyttäytymisen ristiriidat (`onwrite` ilman
ohjelmiston kirjoitusoikeutta) jäisivät omassa muodossa helposti
tarkistamatta. Ne tuottaisivat lohkon, jonka käyttäytyminen ei vastaa
kenenkään aikomusta.

## Käytännössä

- **Toistuva rakenne on taulukko,** ei kopioitu kuvaus. Kanavan
  muutos tehdään silloin yhteen paikkaan.
- **Anna taulukon askel näkyvästi.** Kanavan laajentaminen ei silloin
  siirrä seuraavien kanavien osoitteita.
- **Parametroi vain se, mikä vaihtelee.** Jokainen parametri on uusi
  kokoonpano verifioitavaksi.
- **Omat ominaisuudet yhteen tiedostoon,** joka sisällytetään
  suojattuna. Näin kaikki kuvaukset käyttävät samoja määrittelyjä, ja
  kääntäjä tarkistaa niiden tyypit.
- **Aja kääntäjä jokaisessa muutoksessa.** Tarkistus kestää sekunnin,
  ja se löytää virheet, jotka muuten löytyisivät simuloinnista tai
  laboratoriosta.

## Itsearviointi

- Osaat kuvata toistuvan rekisteriryhmän taulukkona osoitteineen ja
  askelineen.
- Osaat parametroida kuvauksen ja antaa parametrin instantioinnissa,
  komentorivillä tai Pythonista.
- Osaat määritellä oman ominaisuuden tyyppeineen ja käyttää sitä omassa
  generaattorissa.
- Osaat lukea kääntäjän virheilmoitukset ja erottaa tavallisen ja
  kohtalokkaan virheen.
