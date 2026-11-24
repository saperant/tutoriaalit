# Raporttien jäsentäminen

Jokainen työkalu raportoi omalla tavallaan. Yosys tulostaa
solutaulukon, STA-työkalu polun viiveineen, Verilator varoitusrivejä
ja simulaattori sen, mitä testipenkki tulostaa. Raportit on tehty
ihmisen luettaviksi, ja niiden muoto voi muuttua työkalun versiosta
toiseen. Vuon on silti saatava niistä luvut: montako solua, mikä on
slack, menivätkö testit läpi.

Ratkaisu on jakaa työ kahteen osaan. Jokaiselle raporttityypille
kirjoitetaan jäsennin, joka muuttaa raportin yhteisen tietomallin
olioksi. Kaikki muu, kuten koosteet, laatuportit ja historia, käyttää
vain tietomallia. Kun työkalu vaihtuu tai sen raportti muuttuu,
muutetaan vain yhtä jäsennintä.

## Yhteinen tietomalli

```{.python tiedosto="esimerkit/vuo/malli.py" osa="malli"}
```

Malli on tarkoituksella työkaluriippumaton. `Resurssit` on yhtä hyvin
Yosysin, FPGA-työkalun tai kaupallisen synteesin tulos, ja
`Ajoitus` mikä tahansa STA-raportin pahin polku. Kenttä, jota ajo ei
tuottanut, on `None`, ei nolla: nolla solua on eri asia kuin
puuttuva synteesi. `Raportti.tallenna` kirjoittaa koko mallin JSONiksi
järjestetyin avaimin, joten saman ajon kaksi tallennusta ovat
tavulleen samat ja niitä voi verrata `diff`-työkalulla.

## Konekielinen raportti ensin

Jos työkalu osaa kirjoittaa konekielisen raportin, sitä käytetään.
Yosysin `stat -json` antaa solut tyypeittäin:

```{.python tiedosto="esimerkit/vuo/raportit.py" osa="yosys"}
```

Kiikut tunnistetaan solutyypin nimestä: Yosysin sisäiset kiikkutyypit
ovat muotoa `$_DFF..._`, ja niiden tarkka nimi riippuu nollauksesta ja
sallintasignaalista. Ilman JSON-muotoa `ltp`-raportista luetaan
pisin polku säännöllisellä lausekkeella, joka etsii vain luvun
`(length=N)`. Mitä vähemmän raportin tekstistä jäsennin olettaa, sitä
paremmin se kestää työkalun päivitykset.

## Ihmiselle tarkoitettu raportti

Ajoitusraportti on tekstiä. Tämä on opetus-sta:n tallennettu raportti
8-bittisestä laskurista:

```{.tuloste tiedosto="esimerkit/naytteet/sta.txt"}
```

Jäsennin etsii jokaisen kentän omalla lausekkeellaan ja tarkistaa
raportin sisäisen johdonmukaisuuden:

```{.python tiedosto="esimerkit/vuo/raportit.py" osa="sta"}
```

Tarkistukset ovat tärkeämpiä kuin miltä ne näyttävät. Jos työkalun
uusi versio lisää raporttiin rivin, jossa on myös sana `slack`,
lauseke voi osua väärään riviin. Silloin slack ei enää ole vaaditun
ajan ja saapumisajan erotus, ja jäsennin hylkää raportin sen sijaan,
että vuo raportoisi väärän luvun. Puuttuva kenttä on myös virhe:
jäsennin ei arvaa oletusarvoa.

Verilatorin varoitus alkaa rivillä, jossa ovat koodi, tiedosto, rivi,
sarake ja viesti, esimerkiksi `%Warning-WIDTHTRUNC: rtl/ohjain.sv:16:22:
Operator ASSIGNDLY expects 4 bits ...`. Sen jälkeen tulee
jatkorivejä, joilla on lähdekoodin rivi, osoitin sarakkeeseen ja
vihjeitä. Jatkorivit alkavat välilyönnillä, joten lauseke, joka on
ankkuroitu rivin alkuun, ohittaa ne:

```{.python tiedosto="esimerkit/vuo/raportit.py" osa="verilator"}
```

Polut muutetaan suhteellisiksi projektin juureen nähden. Sama varoitus
on silloin sama tieto, ajettiinpa vuo kehittäjän koneella tai CI:n
kontissa, ja sallittujen varoitusten lista (luku 6) voi viitata
tiedostoon `rtl/ohjain.sv`. Icarus Verilogin ilmoitukset ovat muotoa
`tiedosto:rivi: laji: viesti`, ja niiden jäsennin `lue_icarus` on
samanlainen.

## Simuloinnin tulos ja kattavuus

Testipenkki on vuon kannalta raportin kirjoittaja. Sen tulosteen
muodosta sovitaan kuten minkä tahansa rajapinnan muodosta. Tämän
projektin testipenkki tulostaa virheet `VIRHE`-alkuisina riveinä,
toiminnallisen kattavuuden lokerot `KATTAVUUS`-riveinä ja lopuksi
tulosrivin:

```{.tuloste tiedosto="esimerkit/naytteet/sim.log"}
```

Kattavuuslokerot ovat operaation ja operandien ylimpien bittien
yhdistelmiä, yhteensä 4 × 2 × 2 = 16. Testipenkki laskee ne itse,
joten tulos on sama kaikilla simulaattoreilla eikä riipu
simulaattorin omasta kattavuustietokannan muodosta. Laajempi
kattavuusmalli, kuten SystemVerilogin `covergroup` ja simulaattorien
kattavuustietokannat, käsitellään taidossa *Laitteiston
verifiointi*. Lokin viimeisen rivin `$finish`-ilmoitus on
Verilatorin oma, ja siinä on lähdetiedoston polku. Raakalokia ei siksi
voi verrata sellaisenaan, vaan siitä jäsennetään vain sovitut rivit:

```{.python tiedosto="esimerkit/vuo/raportit.py" osa="sim"}
```

Järjestys on tärkeä: ensin etsitään tulosrivit, sitten aikakatkaisun
merkki, ja jos mitään ei löydy, ajo on virhe. Puuttuva tulosrivi
tarkoittaa, että simulaattori kaatui tai testipenkki päättyi ennen
loppua.

## Koosteet

Tietomallista tehdään koosteita ihmisille. Markdown-taulukko sopii
CI:n yhteenvetosivulle ja pull requestin kommenttiin, HTML
selaimeen ja sähköpostiin:

```{.python tiedosto="esimerkit/vuo/kooste.py" osa="markdown"}
```

HTML-versio `html_taulukko` on samanlainen. Siinä jokainen arvo kulkee
`html.escape`:n läpi, ja solu, jossa on sana `VIRHE`, saa CSS-luokan,
jolla sen voi korostaa. Varoituksen
viestissä voi olla `<`- ja `&`-merkkejä, ja ilman suojausta ne
rikkoisivat sivun. Esimerkki kokoaa raportin tallennetuista näytteistä
ja tekee siitä taulukon, jossa jokaisella mittarilla on arvio:

```{.python tiedosto="esimerkit/05-raportit.py" osa="kokoa"}
```

Funktio `yhteenveto` tekee raportista taulukon rivit: mittarin, arvon
ja arvion (`OK` tai `VIRHE` syineen).

Lopuksi se yrittää jäsentää raportin, jonka slack ei täsmää:

```{.python tiedosto="esimerkit/05-raportit.py" osa="rikki"}
```

```{.tuloste tiedosto="esimerkit/05-raportit.odotettu"}
```

Kooste näyttää yhdellä silmäyksellä, mikä on kunnossa: resurssit ja
ajoitus ovat, simulointi, kattavuus ja lint eivät. Kattavuus 6/16 on
odotettu tulos 12 operaation simuloinnista. Regressio (luku 7) ajaa
saman testin usealla siemenellä ja yhdistää kattavuudet.

## Jäsentimien testaus

Jäsennin on koodia, jolle kirjoitetaan yksikkötestit kuten muullekin
koodille. Testien syötteinä ovat hakemistoon `naytteet/` tallennetut
raportit, joten testit eivät tarvitse työkaluja ja ovat nopeita:

```{.python tiedosto="esimerkit/testit/test_raportit.py" osa="testit"}
```

Parametroitu testi käy läpi simuloinnin tilat, myös hylkäävät:

```{.python tiedosto="esimerkit/testit/test_raportit.py" osa="testit2"}
```

Kun työkalu päivitetään, uuden version raportit tallennetaan
näytteiksi ja testit ajetaan. Jos jokin jäsennin hajoaa, sen näkee
heti eikä vasta silloin, kun kooste näyttää outoja lukuja. Hylkäävät
tapaukset testataan yhtä huolellisesti kuin hyväksyvät: vajaa ja
ristiriitainen raportti, kaatunut simulointi ja aikakatkaisu.

## Käytännössä

- **Yksi jäsennin raporttityyppiä kohden, yksi tietomalli kaikille.**
  Koosteet ja laatuportit eivät koskaan lue raakaraporttia.
- **Konekielinen muoto aina kun mahdollista.** JSON, CSV tai työkalun
  oma Tcl-komento, joka kirjoittaa vain tarvittavat luvut.
- **Hylkää, älä arvaa.** Puuttuva kenttä, ristiriitaiset luvut tai
  tuntematon muoto on virhe, joka pysäyttää vuon.
- **Ankkuroidut lausekkeet.** `^` rivin alkuun ja `re.M`, jotta
  lauseke ei osu viestin keskelle tai jatkoriville.
- **Näytteet versionhallintaan.** Jokaisesta raporttityypistä ja
  jokaisesta käytetystä työkaluversiosta tallennetaan näyte ja testi.

## Itsearviointi

- Osaat suunnitella työkaluriippumattoman tietomallin ja kirjoittaa
  sille jäsentimet Yosysin, STA:n, Verilatorin ja simulaattorin
  raporteista.
- Osaat tarkistaa raportin sisäisen johdonmukaisuuden ja hylätä
  raportin, jota jäsennin ei ymmärrä.
- Osaat tuottaa tietomallista Markdown- ja HTML-koosteen.
- Osaat testata jäsentimet tallennetuilla näyteraporteilla.
