# Entiteetit, arkkitehtuurit ja hierarkia

VHDL-malli koostuu *suunnitteluyksiköistä*, jotka analysoidaan
kirjastoon. Iso piiri kootaan pienistä entiteeteistä instansioimalla,
kuten piirilevylle juotetaan komponentteja.

## Suunnitteluyksiköt ja kirjastot

| Yksikkö | Sisältö |
|---------|---------|
| `entity` | rajapinta: generic-parametrit ja portit |
| `architecture` | entiteetin toteutus; entiteetillä voi olla useita |
| `package` | yhteiset tyypit, vakiot ja aliohjelmien esittelyt |
| `package body` | paketin aliohjelmien toteutukset |
| `configuration` | valitsee, mikä arkkitehtuuri kuhunkin instanssiin sidotaan |

Analysoitu yksikkö tallentuu *kirjastoon*. Oma koodi menee oletuksena
kirjastoon `work`. Kirjasto `std` (paketit `standard`, `textio`,
`env`) on aina näkyvissä, ja `ieee` sisältää standardipaketit
`std_logic_1164`, `numeric_std`, `math_real` ja `fixed_pkg`. Tiedoston
alussa `library` tekee kirjaston nimen näkyväksi ja `use` tuo sen
sisällön käyttöön:

```text
library ieee;                    -- kirjaston nimi näkyviin
use ieee.std_logic_1164.all;     -- kaikki paketin nimet käyttöön
use ieee.numeric_std.all;
```

`library`- ja `use`-lauseet koskevat vain seuraavaa suunnitteluyksikköä.
Siksi samassa tiedostossa jokaisen entiteetin edellä toistetaan omat
`use`-lauseet. Arkkitehtuuri ja paketin runko perivät entiteetin tai
paketin näkyvyyden.

## Entiteetti ja portit

Portin suunta on yksi seuraavista:

| Suunta | Merkitys |
|--------|----------|
| `in` | tulo; vain luettavissa |
| `out` | lähtö; VHDL-2008:sta alkaen myös luettavissa |
| `inout` | kaksisuuntainen, käytännössä vain piirin nastoissa (kolmitila) |
| `buffer` | vanha tapa lukea lähtöä; ei tarvita VHDL-2008:ssa |

VHDL-93:ssa lähtöporttia ei voinut lukea, joten vanhassa koodissa
näkee usein sisäisen signaalin, joka kopioidaan lähtöön. VHDL-2008:ssa
tämä ei ole tarpeen, mutta tapa on edelleen yleinen ja harmiton.

Tuloporttiin sijoittaminen on virhe jo analyysissä. Seuraavassa
hälytyksen pitopiirissä suunnittelija yrittää "kuitata kuittauksen"
nollaamalla tulon:

```{.vhdl tiedosto="esimerkit/02-suunta.ei-kaanny.vhd"}
```

```{.tuloste tiedosto="esimerkit/02-suunta.odotettu"}
```

Virheilmoitus on `port "kuittaus" can't be assigned`. Kuittauksen
nollaaminen kuuluu sille, joka kuittauksen tuottaa. Vastuu jokaisesta
signaalista on yhdellä lohkolla, mikä on myös laitteiston rakenne:
johtoa ohjaa yksi lähtö.

## Instansiointi ja hierarkia

Seuraava esimerkki kokoaa kaksinumeroisen seitsensegmenttinäytön
kahdesta dekooderista. Dekooderi on oma entiteettinsä:

```{.vhdl tiedosto="esimerkit/02-naytto/bcd7seg.vhd" osa="dekooderi"}
```

Valitseva sijoitus `with ... select` on kombinaatiologiikan
totuustaulu. `when others` kattaa loput arvot, myös metatilat kuten
`'U'` ja `'X'`, joten lähtö on aina määritelty.

Ylemmän tason entiteetti instansioi dekooderin kahdesti ja sammuttaa
kymmenten numeron, kun se on nolla:

```{.vhdl tiedosto="esimerkit/02-naytto/naytto.vhd" osa="naytto"}
```

*Suora entiteetti-instanssi* `entity work.bcd7seg` viittaa
kirjastossa olevaan entiteettiin. Instanssilla on nimi
(`dek_kymmenet`), jolla se näkyy simulaattorin hierarkiassa ja
synteesiraporteissa. Sisäinen signaali `vasen_raaka` yhdistää
instanssin lähdön muuhun logiikkaan, kuten johdin piirilevyllä.

Testipenkki käy läpi kaikki luvut 0–99 ja tarkistaa molemmat numerot
vertailutaulukkoa vasten. Taulukko on kirjoitettu erikseen eikä
laskettu samalla logiikalla kuin testattava malli, jotta sama virhe ei
toistu molemmissa:

```{.vhdl tiedosto="esimerkit/02-naytto/testipenkki.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/02-naytto.odotettu"}
```

## Komponentit ja konfiguraatiot

Ennen VHDL-93:a instansiointiin tarvittiin *komponentti*, eli
entiteetin rajapinnan kopio arkkitehtuurin esittelyosassa. Saman
näytön toinen arkkitehtuuri on kirjoitettu näin:

```{.vhdl tiedosto="esimerkit/02-naytto/naytto.vhd" osa="komponentti"}
```

Entiteetillä on nyt kaksi arkkitehtuuria. Instanssi valitsee
arkkitehtuurin suluissa, `entity work.naytto(rakenne)`; ilman valintaa
käytetään viimeksi analysoitua. Testipenkki instansioi molemmat ja
vertaa niiden lähtöjä keskenään.

Komponentti on edelleen tarpeen kolmessa tilanteessa: kun
instansioidaan Verilog- tai SystemVerilog-moduulia, kun instansioidaan
valmistajan IP-lohkoa tai mustaa laatikkoa, jonka VHDL-lähdettä ei ole,
ja kun *konfiguraatiolla* halutaan valita instanssiin eri arkkitehtuuri,
esimerkiksi nopea simulointimalli tai porttitason netlista. Muulloin suora
instanssi on parempi: rajapinta on yhdessä paikassa, eikä kopio voi
vanhentua.

## Liitokset

Porttiliitokset kirjoitetaan nimettyinä (`numero => kymmenet`).
Paikkasidonta (`port map (kymmenet, vasen_raaka)`) on sallittu, mutta
se rikkoutuu hiljaa, kun porttien järjestys muuttuu ja tyypit sattuvat
täsmäämään.

Käyttämätön lähtö liitetään sanalla `open`. Tulo voidaan jättää
liittämättä vain, jos sillä on oletusarvo entiteetissä (`port (a : in
std_logic := '0')`). Muuten elaborointi hylkää mallin. Oletusarvo kannattaa
antaa harkiten, koska se piilottaa unohtuneen liitoksen. VHDL-2008
sallii portin liitoksessa myös lausekkeen, kuten `not nollaa_n` tai
`x"00"`.

## Tiedostot ja nimeäminen

Tavallinen käytäntö on yksi entiteetti arkkitehtuureineen tiedostoa
kohden, ja tiedosto nimetään entiteetin mukaan. Paketti on omassa
tiedostossaan. Analyysijärjestys on käännösjärjestelmän asia: makefile,
VUnitin `run.py` tai FPGA-työkalun projekti selvittää riippuvuudet. GHDL
osaa sen itse komennoilla `ghdl -i *.vhd` (tuo tiedostot kirjastoon) ja
`ghdl -m testipenkki` (analysoi tarvittavat oikeassa järjestyksessä).

VHDL ei erottele isoja ja pieniä kirjaimia nimissä: `Laskuri`,
`LASKURI` ja `laskuri` ovat sama nimi. Yleinen tyyli kirjoittaa
avainsanat ja nimet pienillä ja vakiot ja generic-parametrit isoilla.
Standardi sallii nimissä Latin-1-merkistön kirjaimet, mutta
nykyiset UTF-8-lähdetiedostot ja työkalut eivät käsittele ääkkösiä
nimissä yhtenäisesti. Siksi tämän tutoriaalin nimet kirjoitetaan ilman
niitä (`ykkoset`, `paalla`); kommenteissa ja merkkijonoissa ääkköset
toimivat.

## Käytännössä

- **Suora instanssi, nimetyt liitokset.** `entity work.x` ja `portti =>
  signaali` ovat nykykäytäntö. Komponentti vain Verilog-moduuleille,
  IP-lohkoille ja konfiguraatioille.
- **Yksi ajuri signaalille.** Jokaisella signaalilla on yksi lohko,
  joka sitä ohjaa. Tulo on lukijan, lähtö on kirjoittajan. Tämä
  vastaa laitteistoa, ja luvussa 3 nähdään, mitä tapahtuu, jos sääntö
  rikotaan.
- **Instanssien ja prosessien nimet.** Nimetty prosessi tai instanssi
  (`kooderi : process`) näkyy simulaattorin hierarkiassa, aaltomuodoissa
  ja synteesiraporteissa. Nimettömät saavat työkalun keksimän nimen,
  jota on vaikea jäljittää.
- **Lopetusnimet.** `end entity naytto;` ja `end architecture rtl;`
  ovat vapaaehtoisia, mutta kääntäjä tarkistaa ne, ja pitkissä
  tiedostoissa ne kertovat, mikä lohko päättyy.
- **Arkkitehtuurin nimi kertoo tason.** Yleinen tapa on `rtl`
  synteesikelpoiselle toteutukselle, `rakenne` tai `structural`
  pelkille instansseille ja `sim` testipenkeille ja malleille.

## Itsearviointi

- Osaat kirjoittaa entiteetin, jolla on generic-parametreja ja portteja,
  ja sille arkkitehtuurin.
- Osaat instansioida entiteetin suoraan nimetyillä liitoksilla ja
  koota hierarkian sisäisten signaalien avulla.
- Osaat kertoa, milloin komponenttiesittelyä tarvitaan.
- Osaat kertoa, mitä analyysi, elaborointi ja simulointi tekevät ja
  miksi tiedostojen analyysijärjestys on merkitsevä.
