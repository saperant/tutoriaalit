# Obfuskointi ja sen purkaminen

*Obfuskointi* vaikeuttaa takaisinmallinnusta muuttamatta ohjelman
toimintaa. Sitä käytetään koodin suojaamiseen ja haittaohjelmien
piilottamiseen. Tekniikat pitää tuntea kahdesta syystä:
haittaohjelma-analyytikon on nähtävä niiden läpi, jotta hän saa
selville, mitä näyte tekee, ja ohjelman suunnittelijan on tiedettävä,
mitä ne kestävät, jotta hän ei rakenna suojausta niiden varaan. Tässä
luvussa tunnistetaan ja puretaan kolme tavallista tekniikkaa:
merkkijonojen salaus, ohjausvuon litistys ja läpinäkymätön
predikaatti. Lopuksi osoitetaan omalla esimerkkiohjelmalla, miksi
debuggerin havaitseminen ei suojaa ohjelmaa.

Kaikki kohteet ovat paketin omia, itse käännettyjä ohjelmia. Luvun
opetus on suunnittelijalle: obfuskointi ja asiakasohjelman omat
tarkistukset hidastavat analyysia mutta eivät estä sitä, joten
suojattava asia ei saa olla niiden varassa. Toisten ohjelmien
kopiosuojausten ja lisenssitarkistusten kiertämiseen luvun keinoja ei
ole tarkoitettu, eikä laki sitä salli (luku 1).

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

*Pakkaaja* (*packer*, esimerkiksi UPX) soveltaa samaa ajatusta koko
ohjelmaan: varsinainen koodi on tiedostossa pakattuna tai salattuna, ja
pieni purkukoodi palauttaa sen muistiin käynnistyksessä. Pakatun
ohjelman tunnistaa luvun 9 keinoin: entropia on lähes koko tiedostossa
korkea, tuonteja ja merkkijonoja on vain muutama, ja osioiden nimet ja
koot ovat epätavallisia. Periaate on sama kuin merkkijonoissa: koodi
on ajon aikana muistissa purettuna, joten analyysi jatkuu sieltä.

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

```{.dot otsikko="Litistyksen periaate. Vasemmalla alkuperäinen silmukka, oikealla sama litistettynä: jokainen lohko asettaa seuraavan tilan ja palaa välittäjään, joten lohkojen järjestys ei näy hypyistä."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.35; compound=true;
  subgraph cluster_a {
    label="alkuperäinen"; color="#5B6B70"; style=dashed;
    a0 [label="alustus"]; a1 [label="ehto"]; a2 [label="runko"];
    a3 [label="paluu"];
    a0 -> a1; a1 -> a2 [label=" tosi"]; a2 -> a1;
    a1 -> a3 [label=" epätosi"];
  }
  subgraph cluster_b {
    label="litistetty"; color="#5B6B70"; style=dashed;
    v [label="välittäjä:\nswitch (tila)", shape=diamond, style=filled];
    b0 [label="alustus\ntila = B"]; b1 [label="ehto\ntila = C tai D"];
    b2 [label="runko\ntila = B"]; b3 [label="paluu"];
    v -> b0 [label="A", dir=both]; v -> b1 [label="B", dir=both];
    v -> b2 [label="C", dir=both]; v -> b3 [label="D"];
  }
}
```

Purku palauttaa tilakoneen. Skripti `litistys.py` tunnistaa
tilamuuttujan (eniten vertailtu paikka), lukee välittäjästä taulun
tila → lohko ja kerää kustakin lohkosta tilat, jotka se voi asettaa
seuraavaksi:

```{.tuloste tiedosto="esimerkit/12-litistys/odotettu" osa="t4"}
```

Tilat on nyt järjestetty suoritusjärjestykseen (T0 → T1 → …).
Valitsimella `--dot` skripti tulostaa saman tilakoneen
Graphviz-kaaviona, josta rakenteen näkee yhdellä silmäyksellä:

```{.dot tiedosto="esimerkit/12-litistys/odotettu" osa="kaavio" otsikko="Skriptin `litistys.py` palauttama tilakone. T1 on silmukan ehto ja T7 palaa siihen; T2:n haara T5:een on seuraavan kohdan läpinäkymätön predikaatti."}
```

T1 on silmukan ehto: sillä on kaksi seuraajaa, joista T3 päättyy
paluuseen. T7 palaa takaisin ehtoon, eli T2–T7 on silmukan runko, ja
T4:n haarautuminen on rungon `if`-lause. Litistys kasvattaa käskymäärän
yli kaksinkertaiseksi mutta ei estä rakenteen palautusta, kun
välittäjän logiikan ymmärtää.

## Läpinäkymätön predikaatti

*Läpinäkymätön predikaatti* (*opaque predicate*) on ehto, jonka arvon
obfuskoija tietää etukäteen mutta jota työkalu ei helposti päättele. Sillä
lisätään koodiin haaroja, jotka eivät koskaan suoritu, tai tehdään
analyysista raskasta. Esimerkissä haara riippuu ehdosta
$(i \cdot (i+1)) \bmod 2 = 0$.

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

Suojattu ohjelma yrittää usein havaita analyysin, ja haittaohjelmat
tekevät samoin, jotta ne käyttäytyisivät analyytikon koneella
viattomasti. Kaksi tavallista Linux-keinoa ovat
`ptrace(PTRACE_TRACEME)`, joka epäonnistuu, jos debuggeri on jo
liittynyt, ja `/proc/self/status`-tiedoston `TracerPid`, joka on
nollasta poikkeava jäljitettäessä:

```{.c tiedosto="esimerkit/13-antidebug/suojattu.c" osa="havaitse"}
```

Ohjelma havaitsee sekä stracen että gdb:n (tulosteessa tässä
järjestyksessä) ja lopettaa:

```{.tuloste tiedosto="esimerkit/13-antidebug/odotettu" osa="t2"}
```

Kuinka paljon tämä suojaa? Kokeillaan omalla ohjelmalla. Tarkistus on
funktio, joka palauttaa luvun, ja debuggeri hallitsee tutkittavan
prosessin rekistereitä ja muistia. Luvun 8 keino riittää: gdb
palauttaa päätösfunktiosta heti nollan, eikä tarkistuksia suoriteta
lainkaan:

```{.text tiedosto="esimerkit/13-antidebug/ohita-kaikki.gdb" osa="ohita-kaikki"}
```

```{.tuloste tiedosto="esimerkit/13-antidebug/odotettu" osa="t4"}
```

Sama pätee levyllä olevaan tiedostoon: ohjelman haltija voi muuttaa
sen tavuja. Skripti `paikkaa.py` etsii paketin esimerkkiohjelman
`main`-funktiosta kutsun `debuggeri_havaittu` ja korvaa sen käskyillä
`xor eax,eax` (paluuarvo nollaksi) ja `nop`:

```{.python tiedosto="esimerkit/13-antidebug/paikkaa.py" osa="main"}
```

```{.tuloste tiedosto="esimerkit/13-antidebug/odotettu" osa="t5"}
```

Vain neljä tavua muuttui, ja muutettu ohjelma suorittaa suojatun
toiminnon myös debuggerissa. Koe näyttää, mitä asiakasohjelman
tarkistus on: yksi haara konekielessä, koneella, jota tarkistettava
itse hallitsee. Sama koskee jokaista tarkistusta, jonka tulos jää
asiakkaan koneelle, kuten lisenssin, käyttöoikeuden tai pelin
tuloksen tarkistusta.

Suunnittelijan johtopäätökset:

- **Salaisuus ei kuulu asiakasohjelmaan.** Avain, salasana tai
  algoritmi, joka on ohjelmatiedostossa, on sen haltijan luettavissa.
  Salaisuus pidetään palvelimella tai laitteiston suojatussa osassa
  (turvapiiri, TPM, luotettu suoritusympäristö).
- **Päätös tehdään siellä, missä käyttäjä ei hallitse koodia.**
  Käyttöoikeus tarkistetaan palvelimella jokaisessa pyynnössä, eikä
  asiakkaan ilmoitukseen luoteta (*Tietoturvan perusteet*).
- **Eheys varmistetaan allekirjoituksella**, jonka tarkistaa
  käyttöjärjestelmä tai käynnistysketju, ei ohjelma itse.
- **Obfuskointi ja debuggerin havaitseminen ovat hidasteita.** Niillä
  voi ostaa aikaa, mutta suojausta ei mitoiteta niiden varaan.

Analyytikolle sama havainto on työkalu: kun haittaohjelmanäyte
lopettaa heti eristetyssä analyysiympäristössä, syy on usein tällainen
tarkistus, ja sen tunnistaa tuonneista (`ptrace`) ja merkkijonoista
(`/proc/self/status`, `TracerPid`).

## Käytännössä

- **Tunnista tekniikka ennen kuin puret sitä.** Salatun merkkijonon
  tuntee siitä, ettei `strings` löydä mitään, litistyksen välittäjästä
  ja läpinäkymättömän predikaatin haarasta, johon ei tule muita
  viittauksia.
- **Yhdistä staattinen ja dynaaminen analyysi.** Ohjelman on itse
  purettava merkkijononsa ja suoritettava oikea koodinsa, joten
  muistista ja jäljityksestä näkee sen, minkä staattinen kuva peittää.
- **Automatisoi kuviot**: tilakoneen palautus, kuolleiden haarojen
  etsintä ja symbolinen suoritus ovat skriptattavia.
- **Analysoi tuntematon näyte eristetyssä ympäristössä**:
  virtuaalikone ilman verkkoa ja tilannevedos, johon palataan.
  Haittaohjelmaa ei ajeta omalla työkoneella.
- **Älä rakenna omaa suojausta obfuskoinnin tai asiakaskoodin
  tarkistusten varaan.** Ne hidastavat mutta eivät estä. Salaisuus ja
  päätös kuuluvat palvelimelle tai suojattuun laitteistoon.
- **Pysy omissa ja luvallisissa kohteissa.** Luvun kokeet tehtiin
  paketin omalle ohjelmalle; toisen ohjelman suojauksen kiertäminen
  ei kuulu lain sallimiin poikkeuksiin (luku 1).

## Itsearviointi

- Osaat tunnistaa salatut merkkijonot ja lukea ne sekä staattisesti
  purkufunktion avulla että dynaamisesti muistista.
- Osaat tunnistaa ohjausvuon litistyksen välittäjästä ja palauttaa
  tilakoneen.
- Osaat todistaa läpinäkymättömän predikaatin vakioksi ja osoittaa
  kuolleen haaran.
- Osaat tunnistaa debuggerin havaitsemisen (`ptrace`, `TracerPid`)
  ohjelmasta.
- Osaat selittää oman esimerkkiohjelman avulla, miksi asiakaskoodin
  tarkistus ei ole suoja, ja mihin salaisuus ja päätös kuuluu
  sijoittaa.
