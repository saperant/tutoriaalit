# Obfuskointi ja sen purkaminen

*Obfuskointi* vaikeuttaa takaisinmallinnusta muuttamatta ohjelman
toimintaa. Sitä käytetään koodin suojaamiseen ja haittaohjelmien
piilottamiseen, joten molemmat osapuolet tuntevat samat tekniikat.
Tässä luvussa puretaan kolme tavallista: merkkijonojen salaus,
ohjausvuon litistys ja läpinäkymätön predikaatti, sekä ohitetaan
debuggerin havaitseminen. Kaikki kohteet ovat paketin omia ohjelmia:
tarkoitus on näyttää, miksi tällaiset keinot hidastavat mutta eivät
estä analyysia, ja mitä se tarkoittaa omaa ohjelmaa suojattaessa.

## Salatut merkkijonot

Merkkijonot ovat analyysin nopein vihje, joten obfuskaattorit salaavat
ne ja purkavat ajon aikana. Esimerkin ohjelman merkkijonot on XOR-salattu
avaimella, joka vaihtuu merkeittäin:

```{.c tiedosto="esimerkit/11-xor/palvelu.c" osa="pura"}
```

`strings` ei löydä mitään, mutta purku on helppo kahdella tavalla.
Staattisesti: avaimen parametrit luetaan purkufunktiosta (alkuarvo
`mov`-käskystä, askel `add`-käskystä), ja `.rodata`-osio käydään läpi
etsien kohtia, joista purkuna alkaa tulostuva, nollaan päättyvä jono:

```{.bash tiedosto="esimerkit/11-xor/aja.sh" osa="staattinen"}
```

```{.tuloste tiedosto="esimerkit/11-xor/odotettu" osa="t3"}
```

Dynaamisesti vielä helpommin: ohjelma purkaa merkkijonot itse, joten ne
voi lukea muistista ajon aikana. gdb pysäyttää tulostusfunktion ja
lukee argumentin:

```{.tuloste tiedosto="esimerkit/11-xor/odotettu" osa="t4"}
```

Tämä on salattujen merkkijonojen perusopetus: ohjelman on purettava ne
käyttääkseen niitä, joten ne ovat aina saatavilla ajonaikaisesti.
Salaus nostaa rimaa mutta ei estä analyysia.

## Ohjausvuon litistys

*Ohjausvuon litistys* (*control-flow flattening*) hävittää funktion
rakenteen: alkuperäiset peruslohkot pannaan yhden `switch`-rakenteen
haaroiksi, ja tilamuuttuja ohjaa, mikä lohko suoritetaan seuraavaksi.
Hyppyjen verkko korvautuu välittäjällä (*dispatcher*), eikä rakennetta
näe suoraan. Esimerkin Luhn-tarkistus on litistetty käsin:

```{.c tiedosto="esimerkit/12-litistys/luhn.c" osa="litistetty"}
```

Litistyksen tunnistaa välittäjästä: silmukka, jonka alussa samaa
muistipaikkaa verrataan moneen vakioon:

```{.tuloste tiedosto="esimerkit/12-litistys/odotettu" osa="t3"}
```

Purku palauttaa tilakoneen. Skripti `litistys.py` tunnistaa
tilamuuttujan (eniten vertailtu paikka), lukee välittäjästä taulun
tila → lohko ja kerää kustakin lohkosta tilat, jotka se voi asettaa
seuraavaksi:

```{.tuloste tiedosto="esimerkit/12-litistys/odotettu" osa="t4"}
```

Tilat on nyt järjestetty suoritusjärjestykseen (T0 → T1 → …), ja
rakenteen näkee: T1 on silmukan ehto (kaksi seuraajaa, joista toinen on
paluu), T7 palaa takaisin ehtoon. Litistys kasvattaa käskymäärän yli
kaksinkertaiseksi mutta ei estä rakenteen palautusta, kun välittäjän
logiikan ymmärtää.

## Läpinäkymätön predikaatti

*Läpinäkymätön predikaatti* (*opaque predicate*) on ehto, jonka arvon
hyökkääjä tietää mutta jota työkalu ei helposti päättele. Sillä
lisätään koodiin haaroja, jotka eivät koskaan suoritu, tai tehdään
analyysista raskasta. Esimerkissä haara riippuu ehdosta
$(i \cdot (i+1)) \bmod 2 = 0$:

Kahden peräkkäisen kokonaisluvun tulo on aina parillinen, joten ehto on
aina tosi ja toinen haara on kuollutta koodia. Väitteen voi tarkistaa
kokeilemalla:

```{.tuloste tiedosto="esimerkit/12-litistys/odotettu" osa="t5"}
```

Yleisiä läpinäkymättömiä predikaatteja ovat $x^2 \ge 0$,
$2 \mid x(x+1)$ ja $7 \mid (x^3 - x)$. Symbolinen suoritus (esim. angr)
ja SMT-ratkaisijat tunnistavat monet niistä automaattisesti todistamalla,
että ehto on vakio. Kuollut haara näkyy myös siitä, ettei siihen tule
ristiviittauksia muualta kuin aina-epätodesta ehdosta.

## Debuggerin havaitseminen

Suojattu ohjelma yrittää usein havaita analyysin. Kaksi tavallista
Linux-keinoa ovat `ptrace(PTRACE_TRACEME)`, joka epäonnistuu, jos
debuggeri on jo liittynyt, ja `/proc/self/status`-tiedoston
`TracerPid`, joka on nollasta poikkeava jäljitettäessä:

```{.c tiedosto="esimerkit/13-antidebug/suojattu.c" osa="havaitse"}
```

Ohjelma havaitsee sekä gdb:n että stracen. Havaitsemisen voi ohittaa
monella tasolla. gdb voi muuttaa yksittäisen tarkistuksen paluuarvon
tai koko päätösfunktion tuloksen:

```{.text tiedosto="esimerkit/13-antidebug/ohita-kaikki.gdb" osa="ohita-kaikki"}
```

```{.tuloste tiedosto="esimerkit/13-antidebug/odotettu" osa="t4"}
```

Pysyvämpi keino on paikata ohjelmatiedosto. Skripti `paikkaa.py` etsii
`main`-funktiosta kutsun `debuggeri_havaittu` ja korvaa sen käskyillä
`xor eax,eax` (paluuarvo nollaksi) ja `nop`:

```{.python tiedosto="esimerkit/13-antidebug/paikkaa.py" osa="main"}
```

```{.tuloste tiedosto="esimerkit/13-antidebug/odotettu" osa="t5"}
```

Vain neljä tavua muuttui, ja paikattu ohjelma suorittaa suojatun
toiminnon myös debuggerissa. Tämä on olennainen opetus omaa ohjelmaa
suojattaessa: havaitsemistarkistus on vain haara konekielessä, ja sen
voi aina kääntää tai ohittaa. Anti-debug nostaa vaivaa mutta ei suojaa
mitään, mitä ohjelmassa itsessään on; todellinen salaisuus kuuluu
palvelimelle tai suojattuun laitteistoon, ei asiakasohjelman koodiin.

## Käytännössä

- **Älä pysähdy obfuskointiin, kierrä se.** Salatut merkkijonot
  purkautuvat ajossa, litistys palautuu välittäjää lukemalla,
  läpinäkymättömät predikaatit todistetaan vakioiksi.
- **Käytä dynaamista analyysia obfuskoinnin ohi.** Ohjelman on
  purettava, deobfuskoitava ja suoritettava oikea koodi; muistista ja
  jäljityksestä sen näkee.
- **Tunnista kuvioita työkaluilla**: tilakoneen palautus, kuolleiden
  haarojen etsintä ja symbolinen suoritus automatisoituvat.
- **Paikkaa tarkistus, älä ratkaise sitä**, kun tavoite on vain ohittaa
  este omassa ohjelmassa; neljän tavun muutos riittää usein.
- **Älä luota obfuskointiin omana suojauksena.** Se hidastaa, ei estä.
  Suojaa salaisuudet siellä, missä hyökkääjä ei suorita koodia.

## Itsearviointi

- Osaat purkaa salatut merkkijonot sekä staattisesti purkufunktiosta
  että dynaamisesti muistista.
- Osaat tunnistaa ohjausvuon litistyksen välittäjästä ja palauttaa
  tilakoneen.
- Osaat todistaa läpinäkymättömän predikaatin vakioksi ja osoittaa
  kuolleen haaran.
- Osaat ohittaa debuggerin havaitsemisen gdb:llä ja pysyvästi
  paikkaamalla sekä perustella, miksi anti-debug ei ole suojaus.
