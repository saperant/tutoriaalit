# Välikieli

Syntaksipuu on lähdekielen muotoinen: siinä on sisäkkäisiä lausekkeita,
lohkoja ja silmukoita. Suoritin taas tekee yhden pienen operaation
kerrallaan ja hyppii osoitteesta toiseen. **Välikieli** on näiden
välissä. Kide käyttää **kolmiosoitekoodia** (*three-address code*):
jokainen käsky tekee yhden operaation korkeintaan kahdelle operandille
ja kirjoittaa tuloksen kolmanteen paikkaan, esimerkiksi
`%3 = add a, %2`.

Kolmiosoitekoodi on lähellä konekieltä, mutta siinä on kaksi
yksinkertaistusta. Rekistereitä on rajattomasti (*virtuaalirekisterit*),
ja kutsukonventio on piilotettu `call`-käskyyn. Näin optimoinnit voivat
käsitellä ohjelmaa välittämättä kohdekoneen yksityiskohdista.

## Käskyt ja peruslohkot

```{.cpp tiedosto="esimerkit/kide/ir.hpp" osa="kasky"}
```

Käskyt on ryhmitelty **peruslohkoihin** (*basic block*). Peruslohko
on käskyjono, johon tullaan vain alusta ja josta lähdetään vain
lopusta: viimeinen käsky on hyppy (`jmp`), ehdollinen haara (`br`) tai
paluu (`ret`), eikä lohkon keskellä ole hyppyjä sisään tai ulos.
Lohkot ja niiden väliset hypyt muodostavat **ohjausvuograafin**
(*control flow graph*, CFG), jonka solmuja lohkot ovat. Graafi on
kaikkien myöhempien analyysien perusta: datavuoanalyysi kulkee sen
kaaria pitkin (luku 10), ja SSA-muoto rakennetaan sen dominanssista
(luku 12).

Lähdekoodin muuttujat ovat virtuaalirekistereitä omilla nimillään, ja
lausekkeiden välitulokset ovat numeroituja rekistereitä `%1`, `%2` ...
Kertomaohjelma välikielenä ilman optimointeja (`--vaihe=ir -O0`):

```{.tuloste tiedosto="esimerkit/naytteet/ir-kertoma.txt"}
```

Jokainen vakio on oma käskynsä, ja jokainen sijoitus on kopio. Koodi on
tarkoituksella naiivia: alentaminen tuottaa yksinkertaista koodia, ja
optimoinnit siivoavat sen. Tämä jako on tuotantokääntäjissä sama;
Clangin `-O0`-tuloste LLVM:n välikielenä on yhtä suorasukaista.

## Alentaminen

Syntaksipuun **alentaminen** (*lowering*) välikieleksi on rekursiivinen
läpikäynti, joka lisää käskyjä *nykyiseen lohkoon*. Apufunktiot luovat
rekistereitä ja lohkoja ja lisäävät käskyjä:

```{.cpp tiedosto="esimerkit/kide/alennus.cpp" osa="apu"}
```

Lauseke palauttaa rekisterin, jossa sen arvo on. Luku tuottaa
`Vakio`-käskyn, binäärioperaatio alentaa ensin operandinsa ja sitten
lisää laskentakäskyn uuteen rekisteriin, ja kutsu alentaa argumentit
vasemmalta oikealle. Muuttuja on jo rekisteri, joten sen alentaminen ei
tuota käskyä lainkaan. Esittely ja sijoitus ovat kopioita muuttujan
rekisteriin.

Ohjausrakenteet luovat lohkoja ja hyppyjä. `while`-silmukasta tulee
kolme lohkoa: ehdon testi, runko ja silmukan jälkeinen koodi. Rungon
lopusta hypätään takaisin testiin, ja tämä *paluukaari* tekee
graafiin silmukan:

```{.cpp tiedosto="esimerkit/kide/alennus.cpp" osa="kun"}
```

`return`-lauseen jälkeen aloitetaan uusi lohko, johon ei hypätä
mistään. Sinne päätyvä koodi on *saavuttamatonta*, ja se poistetaan
ennen koodingenerointia. Lohkot numeroidaan lopuksi siinä
järjestyksessä, jossa ne aloitettiin, jotta silmukan runko tulee
ehtonsa perään ja koodingeneraattori voi jättää monta hyppyä pois.

## Hyppykoodi

Ehtolauseessa totuusarvoa ei tarvita rekisterissä: riittää hypätä
oikeaan lohkoon. **Hyppykoodi** (*jumping code*) alentaa ehdon
suoraan haaroiksi. `a && b` testaa ensin `a`:n ja hyppää epätoteen
heti, jos se on epätosi; `!a` vaihtaa kohteet keskenään:

```{.cpp tiedosto="esimerkit/kide/alennus.cpp" osa="ehto"}
```

Kun `&&`-lausekkeen arvoa käytetään arvona (`var c = a && b;`),
tarvitaan rekisteri. Tulos kirjoitetaan kahdessa eri lohkossa samaan
rekisteriin:

```{.cpp tiedosto="esimerkit/kide/alennus.cpp" osa="arvo"}
```

Kumpikin tapa näkyy samassa ohjelmassa:

```{.rust tiedosto="esimerkit/naytteet/ehto.kide"}
```

```{.tuloste tiedosto="esimerkit/naytteet/ir-ehto.txt"}
```

Funktiossa `molemmat` ehdosta ei synny totuusarvoa lainkaan, vain kaksi
haaraa. Funktiossa `main` rekisteri `%1` kirjoitetaan lohkoissa L0 ja
L1. Huomaa myös, että `1 / 0` on lohkossa L1, jota ei suoriteta,
koska `2 > 1` on tosi.

## Ohjausvuograafin kaaret

Kunkin lohkon seuraajat luetaan sen viimeisestä käskystä, ja
edeltäjät saadaan kääntämällä kaaret. Tulosteen kommentit
`; edeltäjät:` näyttävät ne. Lohko, jolla on useita edeltäjiä, on
*yhtymäkohta* (*join point*), ja yhtymäkohdat ovat datavuoanalyysin
ja SSA-muodon kannalta kiinnostavimmat paikat: niissä eri polkujen
tiedot yhdistyvät.

Seuraavien kolmen luvun esimerkkinä on funktio, jossa on silmukka ja
sen sisällä ehto:

```{.rust tiedosto="esimerkit/naytteet/summa.kide"}
```

```{.tuloste tiedosto="esimerkit/naytteet/ir-summa.txt"}
```

Graafina näkyy silmukan rakenne: L1 on silmukan otsake, L4 hyppää
takaisin siihen (paluukaari), ja L5 on ainoa poistuminen. L1 ja L4
ovat yhtymäkohtia.

```{.dot tiedosto="kaaviot/cfg-summa.dot" otsikko="Funktion summa ohjausvuograafi (kääntäjän tulosteesta)" leveys="55%"}
```

## Käytännössä

- **Alenna naiivisti, optimoi erikseen.** Alentaminen, joka yrittää
  tuottaa hyvää koodia, on vaikea saada oikeaksi. Yksinkertainen
  alentaminen ja erilliset optimointivaiheet ovat helpompia testata.
- **Peruslohkot ovat analyysien yksikkö.** Lohkon sisällä suoritus on
  suoraviivaista, joten paikalliset analyysit ovat yksinkertaisia, ja
  globaalit analyysit tarvitsevat vain lohkojen yhteenvedot.
- **Käytä hyppykoodia ehdoissa.** Totuusarvon laskeminen rekisteriin ja
  sen testaaminen heti perään on turhaa työtä.
- **Tee välikielestä tulostettava ja luettava.** LLVM:n tekstimuotoinen
  IR on yksi syy LLVM:n suosioon: sitä voi kirjoittaa ja lukea käsin.

## Itsearviointi

- Osaat selittää kolmiosoitekoodin, virtuaalirekisterit ja
  peruslohkon määritelmän.
- Osaat alentaa lausekkeet, `if`- ja `while`-lauseet ja funktiokutsut
  syntaksipuusta peruslohkoiksi.
- Osaat alentaa ehdon hyppykoodiksi ja selittää, miksi `&&` arvona
  rikkoo yhden määrittelyn periaatteen.
- Osaat piirtää funktion ohjausvuograafin välikielen tulosteesta ja
  tunnistaa siitä silmukat ja yhtymäkohdat.
