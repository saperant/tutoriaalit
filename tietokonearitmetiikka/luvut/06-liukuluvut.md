# Liukuluvut: IEEE 754

Liukuluku esittää luvun muodossa $\pm m \cdot 2^e$, jossa mantissa $m$
on väliltä $[1, 2)$. Muoto on sama kuin tieteellisessä merkintätavassa
$6{,}022 \cdot 10^{23}$, mutta kantaluku on 2. Kiinteä määrä bittejä
riittää näin sekä hyvin pieniin että hyvin suuriin lukuihin, ja
suhteellinen tarkkuus pysyy samana koko alueella. Hinta on, että
useimmat desimaaliluvut, kuten 0,1, eivät ole tarkasti esitettävissä.

Lähes kaikki laitteistot noudattavat IEEE 754 -standardia (versiot 1985,
2008 ja 2019). Standardi määrittelee bittiesityksen, pyöristyksen,
erikoisarvot ja sen, että perusoperaatiot ($+ - \times /$ ja
neliöjuuri) tuottavat tarkan tuloksen *pyöristettynä*. Siksi
liukulukulaskenta on deterministista: sama laskutoimitus samassa
järjestyksessä antaa joka koneella saman tuloksen.

## Kentät

Liukuluku koostuu kolmesta kentästä:

| Muoto | C-tyyppi | Eksponentti | Mantissa | Desimaalit | Suurin |
|-------|----------|-------------|----------|------------|--------|
| binary64 | `double` | 11 bittiä, bias 1023 | 52 | 15–17 | $1{,}8 \cdot 10^{308}$ |
| binary32 | `float` | 8 bittiä, bias 127 | 23 | 6–9 | $3{,}4 \cdot 10^{38}$ |
| binary16 | `_Float16` | 5 bittiä, bias 15 | 10 | 3–5 | 65 504 |

Etumerkki on kaikissa muodoissa yksi bitti. Eksponentti tallennetaan siirrettynä (*bias*): kentän arvosta
vähennetään binary64:ssä 1023, jotta negatiiviset eksponentit eivät tarvitse
etumerkkiä. Mantissan ensimmäinen bitti on aina 1, joten sitä ei
tallenneta (*piilobitti*). 52 tallennettua bittiä antaa näin 53 bitin
tarkkuuden. Pienimmässä muodossa kentät näkee kerralla:

![Luku −2,5 binary16-muodossa. Suuremmissa muodoissa kentät ovat samat
mutta leveämmät.](kuvat/liukukentat.png){width=80%}

Seuraava ohjelma purkaa samat kentät binary64-luvuista. Luku 1,0 on
eksponentti 0 ja mantissa 0:

```{.c tiedosto="esimerkit/06-kentat.c" osa="purku"}
```

```{.tuloste tiedosto="esimerkit/06-kentat.odotettu"}
```

Eksponenttikentän ääriarvot on varattu. Nolla tarkoittaa nollaa ja
*subnormaaleja* lukuja (piilobitti 0), ja kaikki ykköset tarkoittavat
ääretöntä (mantissa 0) tai NaN:ia (mantissa muu kuin 0).

## Liukuluvut lukusuoralla

Liukuluvut eivät ole lukusuoralla tasavälein. Mantissan bitit jakavat
jokaisen kahden potenssin välin yhtä moneen osaan, joten lukuja on
tiheässä nollan lähellä ja harvassa kaukana siitä. Rakenteen näkee
muodosta, joka on niin pieni, että kaikki arvot voi piirtää. Kuvan
lelumuodossa on kolme eksponenttibittiä ja kaksi mantissabittiä, ja sen
arvot on purettu luvun 8 esimerkin luokalla:

![Kuuden bitin liukulukumuodon kaikki positiiviset arvot. Värit
vaihtuvat eksponentin mukaan.](kuvat/lukusuora.png){width=100%}

Kuvasta näkyy kolme asiaa, jotka pätevät kaikkiin IEEE 754 -muotoihin:

- **Väli on vakio eksponentin sisällä ja kaksinkertaistuu seuraavassa.**
  Absoluuttinen tarkkuus huononee luvun kasvaessa, mutta suhteellinen
  tarkkuus pysyy samana: logaritmisella asteikolla arvot ovat tasaisesti.
- **Subnormaalit täyttävät aukon nollan ympärillä.** Ilman niitä
  pienimmän normaalin luvun ja nollan väli olisi tyhjä, ja kahden
  lähekkäisen pienen luvun erotus pyöristyisi nollaksi. Subnormaalien
  ansiosta $x - y = 0$ vain, kun $x = y$ (*asteittainen alivuoto*).
  Hinta on tarkkuus: subnormaalissa luvussa on vähemmän merkitseviä
  bittejä, ja monissa prosessoreissa niillä laskeminen on hidasta.
- **Suurimman luvun jälkeen ei ole mitään.** Sitä suurempi tulos
  pyöristyy äärettömäksi.

## Tarkka arvo

0,1 on binäärinä päättymätön $0{,}0\overline{0011}_2$, joten se
pyöristetään lähimpään esitettävään lukuun. Pythonin `Decimal` ja
`Fraction` näyttävät, mikä luku muuttujaan todella tallentui:

```{.python tiedosto="esimerkit/06-muodot.py" osa="tarkka"}
```

Sama arvo pyöristyy eri muotoihin eri tavoin, ja kaikki ovat hieman
väärin:

```{.python tiedosto="esimerkit/06-muodot.py" osa="kentat"}
```

```{.tuloste tiedosto="esimerkit/06-muodot.odotettu"}
```

`printf("%.17g")` ja Pythonin `repr` tulostavat binary64-luvun niin
monella numerolla, että sama luku saadaan takaisin. Pythonin `repr`
valitsee lyhyimmän tällaisen esityksen, joten `0.1` näkyy muodossa
`0.1` vaikka arvo ei ole tarkka. `float.hex()` ja C:n `%a` ovat
tarkkoja ja ilman pyöristystä: niillä liukuluvut kannattaa kirjoittaa
testiaineistoon ja tiedostoihin, jos täsmällisyydellä on väliä.

## Peräkkäisten lukujen väli

Kahden peräkkäisen liukuluvun välimatka on *ulp* (unit in the last
place). Se on luvun suuruuteen nähden vakio, noin $2^{-52}$ kertaa
luku binary64:ssä. Ulp luvun 1 kohdalla on *konetarkkuus* (machine
epsilon): $2^{-52}$ binary64:ssä (`DBL_EPSILON`) ja $2^{-23}$
binary32:ssa (`FLT_EPSILON`). Yhden laskutoimituksen suhteellinen
pyöristysvirhe on enintään puolet siitä. Kirjallisuudessa epsiloniksi
kutsutaan kumpaakin, joten määritelmä kannattaa tarkistaa.

Suurilla luvuilla väli on suuri: yli $2^{53}$:n binary64 ei esitä enää
kaikkia kokonaislukuja, ja binary32 lopettaa jo luvussa
$2^{24} = 16\,777\,216$.

![Peräkkäisten lukujen väli kolmessa muodossa. Jokainen porras on yksi
eksponentin arvo.](kuvat/ulp.png){width=78%}

```{.c tiedosto="esimerkit/06-ulp.c" osa="ulp"}
```

Tämä on oikean elämän virhe: anturin aikaleima sekunteina
`float`-muuttujassa, jota kasvatetaan millisekunnin välein.

```{.c tiedosto="esimerkit/06-ulp.c" osa="aikaleima"}
```

```{.tuloste tiedosto="esimerkit/06-ulp.odotettu"}
```

Kello pysähtyy 32 768 sekunnissa eli vähän yli yhdeksässä tunnissa.
Siinä kohdassa ulp on 0,0039, ja 0,001 on alle puolet siitä, joten
yhteenlasku pyöristyy takaisin samaan lukuun. Kuvassa tämä on kohta,
jossa `float`-käyrä ylittää kahden millisekunnin viivan. Aikaleimat
tallennetaan kokonaislukuina (`int64_t` mikro- tai nanosekunteina) ja
muunnetaan liukuluvuksi vasta laskettaessa. Luvussa 9 sama kello saadaan
käymään toisella pyöristystavalla.

## Muunnokset kokonaislukujen kanssa

Muunnos kokonaisluvusta liukuluvuksi pyöristää, jos luvussa on enemmän
merkitseviä bittejä kuin mantissassa. Muunnos toiseen suuntaan
katkaisee murto-osan kohti nollaa, ja jos arvo ei mahdu
kohdetyyppiin tai on NaN, muunnos on C:ssä määrittelemätön. Prosessorit
myös käyttäytyvät eri tavoin: x86-64 tuottaa pienimmän kokonaisluvun,
ARM kyllästää.

```{.c tiedosto="esimerkit/06-muunnos.c" osa="tarkkuus"}
```

Ulkoa tuleva liukuluku tarkistetaan siksi ennen muunnosta. Vertailu
kirjoitetaan niin, että NaN ei läpäise sitä:

```{.c tiedosto="esimerkit/06-muunnos.c" osa="turvallinen"}
```

```{.tuloste tiedosto="esimerkit/06-muunnos.odotettu"}
```

## Erikoisarvot

Ylivuoto tuottaa äärettömän, ja määrittelemätön tulos, kuten $0/0$ tai
$\infty - \infty$, tuottaa NaN:in (*not a number*). Liukulukulaskenta ei
siis kaadu kuten kokonaislukujen ylivuoto. Erikoisarvot leviävät
tuloksiin ja paljastuvat vasta lopussa. Standardi määrittelee lisäksi
viisi tilalippua (virheellinen operaatio, nollalla jako, ylivuoto,
alivuoto ja epätarkka tulos), jotka jäävät päälle, kunnes ohjelma
nollaa ne. C:ssä ne luetaan funktiolla `fetestexcept`: pitkän laskennan
jälkeen voi tarkistaa yhdellä kutsulla, syntyikö matkalla NaN tai
ääretön.

```{.c tiedosto="esimerkit/06-erikois.c" osa="erikois"}
```

NaN ei ole yhtä suuri kuin mikään, ei edes itsensä kanssa. Kaikki
vertailut NaN:in kanssa ovat epätosia, joten `x < 1` ja `x >= 1` ovat
molemmat epätosia. Tämä rikkoo lajittelualgoritmien oletukset: taulukko,
jossa on NaN, ei välttämättä lajitu. Negatiivinen nolla on yhtä suuri
kuin nolla, mutta sen etumerkki näkyy jakolaskussa ja funktiossa
`signbit`. Glibc tulostaa x86-64:n tuottaman NaN:in muodossa `-nan`,
koska sen etumerkkibitti on 1.

Puuttuvan mittauksen merkitseminen NaN:lla on yleinen käytäntö
(NumPy, pandas, R), mutta silloin jokainen laskenta on tehtävä
puuttuvat ohittaen:

```{.c tiedosto="esimerkit/06-erikois.c" osa="keskiarvo"}
```

```{.tuloste tiedosto="esimerkit/06-erikois.odotettu"}
```

## Vertailu

Koska laskutoimitukset pyöristyvät, kahden eri reittiä lasketun
tuloksen vertailu operaattorilla `==` on yleensä virhe. Vertailuun
tarvitaan toleranssi. Suhteellinen toleranssi
$|a - b| \le \varepsilon \max(|a|, |b|)$ toimii kaiken kokoisilla
luvuilla mutta ei nollan lähellä, jossa tarvitaan lisäksi
absoluuttinen toleranssi:

```{.python tiedosto="esimerkit/06-vertailu.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/06-vertailu.odotettu"}
```

Toleranssin suuruus riippuu laskennasta, ei muodosta. Hyvä lähtökohta
on muutama kymmenen ulp:tä yksinkertaiselle laskulle ja selvästi
enemmän iteratiiviselle algoritmille. Absoluuttinen toleranssi valitaan
sovelluksen yksiköissä: millimetri, sentti tai mittalaitteen tarkkuus.

## Käytännössä

- **`double` oletuksena.** `float` säästää muistia ja on SIMD-käskyissä
  kaksi kertaa nopeampi, mutta 7 numeron tarkkuus loppuu nopeasti
  summissa ja aikaleimoissa. `float` valitaan perustellusti
  (grafiikka, suuret taulukot, koneoppiminen), ei tottumuksesta.
- **Ei liukulukuja rahalle eikä aikaleimoille.** Kumpikin on
  tarkka kokonaislukujen määrä (senttejä, nanosekunteja). Liukuluku
  kelpaa niistä laskettaviin tunnuslukuihin.
- **Ei `==`-vertailua lasketuille arvoille.** Kirjoita vertailufunktio,
  jossa on sekä suhteellinen että absoluuttinen toleranssi, ja käytä
  sitä myös testeissä (`pytest.approx`, `math.isclose`).
- **Tarkista ennen kuin muunnat kokonaisluvuksi.** `(int)x` on
  määrittelemätön, kun `x` on NaN tai liian suuri. Pyöristä ensin
  (`rint`, `lround`) ja vertaa rajoihin.
- **NaN-tietoisuus.** Tarkista syötteet (`isfinite`) rajapinnalla, ja
  käytä puuttuville arvoille NaN-tietoisia funktioita (`np.nanmean`).
  Lajittelussa NaN on käsiteltävä erikseen.
- **Tallenna tarkasti.** Tekstimuotoon liukuluku kirjoitetaan 17
  merkitsevällä numerolla (`%.17g`) tai heksadesimaalina (`%a`), muuten
  luku muuttuu tallennettaessa.

## Itsearviointi

- Osaat purkaa binary64-, binary32- ja binary16-luvun kentiksi ja
  kertoa, mikä luku kentistä seuraa.
- Osaat selittää, miksi 0,1 ei ole tarkka ja miten tallennetun luvun
  tarkan arvon saa näkyviin.
- Osaat piirtää pienen liukulukumuodon arvot lukusuoralle ja selittää,
  mitä subnormaalit tekevät.
- Osaat laskea ulp:n suuruuden ja arvioida, milloin `float` ei riitä,
  esimerkiksi aikaleimalle.
- Osaat muuntaa liukuluvun kokonaisluvuksi niin, että NaN ja
  arvoalueen ylitys käsitellään.
- Osaat ennustaa vertailujen tulokset NaN:lla ja negatiivisella nollalla.
- Osaat valita vertailuun suhteellisen ja absoluuttisen toleranssin.
