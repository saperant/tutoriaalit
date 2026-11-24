# Derivaatan sovelluksia

Derivaatta on insinöörin työkalu kolmeen tehtävään: etsiä paras ratkaisu
(ääriarvot), ratkaista yhtälö, jota ei voi ratkaista kaavalla (Newtonin
menetelmä), ja arvioida, kuinka herkästi tulos reagoi syötteen virheisiin
(linearisointi). Tässä luvussa tehdään kaikki kolme.

## Ääriarvot ja optimointi

Derivoituvan funktion paikallisessa ääriarvokohdassa tangentti on
vaakasuora, joten $f'(a) = 0$. Tällaiset kohdat ovat **kriittisiä
pisteitä**. Kaikki kriittiset pisteet eivät ole ääriarvoja ($x^3$
nollassa ei ole), joten ne luokitellaan:

- **Toisen derivaatan testi:** jos $f''(a) > 0$, kuvaaja kaartuu ylöspäin
  ja kohdassa on minimi; jos $f''(a) < 0$, maksimi. Jos $f''(a) = 0$,
  testi ei kerro mitään.
- **Merkkikaavio:** derivaatan merkki kriittisen pisteen molemmin
  puolin kertoo, kasvaako vai väheneekö funktio.

Klassinen optimointitehtävä on tölkki. Puolen litran lieriönmuotoiseen
tölkkiin halutaan mahdollisimman vähän peltiä eli pienin pinta-ala
$A = 2\pi r^2 + 2\pi r h$. Tilavuusehto $\pi r^2 h = 500$ cm³ sitoo
korkeuden säteeseen, jolloin pinta-ala riippuu vain yhdestä muuttujasta.

```{.python tiedosto="esimerkit/04-optimointi.py" osa="tolkki"}
```

Optimaalisen tölkin korkeus on sama kuin halkaisija. Kaupan
juomatölkit ovat tätä selvästi korkeampia, koska todellinen kustannus
sisältää myös kannen paksumman pellin, käsiteltävyyden ja hyllytilan.
Matemaattinen optimi on vain niin hyvä kuin kustannusfunktio.

**Suljetulla välillä** jatkuva funktio saa suurimman ja pienimmän
arvonsa joko kriittisessä pisteessä tai välin päätepisteessä
(Weierstrassin lause, luku 2). Siksi ehdokkaiksi otetaan molemmat.

```{.python tiedosto="esimerkit/04-optimointi.py" osa="suljettu"}
```

```{.tuloste tiedosto="esimerkit/04-optimointi.odotettu"}
```

Esimerkissä suurin arvo on välin päätepisteessä $x = 5$ eikä kumpikaan
kriittinen piste. Päätepisteiden unohtaminen on yleinen virhe.

## Newtonin menetelmä

Yhtälöllä $f(x) = 0$ ei yleensä ole ratkaisukaavaa. **Newtonin
menetelmä** korvaa funktion tangentillaan ja ratkaisee tangentin
nollakohdan:

$$x_{n+1} = x_n - \frac{f(x_n)}{f'(x_n)}.$$

![Newtonin menetelmä yhtälölle $x^2 - 2 = 0$ alkuarvosta $x_0 = 3$.
Jokainen askel seuraa tangenttia $x$-akselille.](kuvat/newton.png){width=62%}

Menetelmä on muutaman rivin funktio. Se tarkistaa nollalla jakamisen
eli vaakasuoran tangentin.

```{.python tiedosto="esimerkit/04-newton.py" osa="newton"}
```

Lähellä yksinkertaista juurta Newtonin menetelmä suppenee
**neliöllisesti**: virhe seuraavalla kierroksella on verrannollinen
nykyisen virheen neliöön. Käytännössä oikeiden desimaalien määrä
kaksinkertaistuu joka kierroksella. Viidellä kierroksella saavutetaan
$\sqrt2$:n tarkkuus liukulukujen rajoissa, kun puolitushaku tarvitsisi
noin 50 kierrosta.

```{.python tiedosto="esimerkit/04-newton.py" osa="sqrt2"}
```

Nopeudella on hintansa: menetelmä ei takaa suppenemista. Kolme tyypillistä
epäonnistumista ovat karkaaminen, kehä ja vaakasuora tangentti.
Kuutiojuurella $x^{1/3}$ Newtonin askel on $x_{n+1} = -2x_n$, joten
iteraatio karkaa juuresta, vaikka alkuarvo olisi kuinka lähellä.
Funktiolla $x^3 - 2x + 2$ alkuarvo 0 vie pisteeseen 1 ja takaisin.

```{.python tiedosto="esimerkit/04-newton.py" osa="epaonnistuu"}
```

Kirjastoissa yhdistetään varmuus ja nopeus. SciPyn `brentq` pitää yllä
väliä, jolla merkki vaihtuu (kuten puolitushaku), mutta käyttää
nopeampaa interpolointia aina, kun se on turvallista. Kun juurta
ympäröivä väli on tiedossa, se on lähes aina oikea valinta.

```{.python tiedosto="esimerkit/04-newton.py" osa="scipy"}
```

```{.tuloste tiedosto="esimerkit/04-newton.odotettu"}
```

Newtonin menetelmä yleistyy yhtälöryhmiin (derivaatan tilalle tulee
Jacobin matriisi, luku 8) ja on monien ratkaisijoiden, kuten
piirisimulaattorien toimintapisteen laskennan, ydin. Suppenemisen
analyysi ja muut juurenhakumenetelmät käsitellään taidossa
*Numeeriset menetelmät*.

## Linearisointi

Tangentti on funktion paras lineaarinen approksimaatio kohdan lähellä:

$$f(a + \Delta x) \approx f(a) + f'(a)\,\Delta x.$$

Lauseke on Taylorin polynomi astetta 1 (luku 7). Esimerkiksi
$\sqrt{x}$ kohdan 100 lähellä on noin $10 + (x - 100)/20$.
Approksimaatio on erinomainen lähellä kohtaa ja heikkenee, kun
etäisyys kasvaa.

```{.python tiedosto="esimerkit/04-linearisointi.py" osa="lineaarinen"}
```

Linearisointi on tekniikan arkipäivää. Epälineaarinen piiri, kuten
transistorivahvistin, analysoidaan pienillä signaaleilla linearisoituna
toimintapisteensä ympärillä, ja säätötekniikka linearisoi epälineaarisen
järjestelmän tasapainotilan lähellä.

## Herkkyys ja virheen eteneminen

Linearisoinnista saadaan **virheen etenemisen** sääntö: jos syötteen
virhe on $\Delta x$, tuloksen virhe on noin $f'(x)\,\Delta x$.
Suhteellisena muutoksena

$$\frac{\Delta f}{f} \approx \underbrace{\frac{x}{f}\,f'(x)}_{\text{herkkyys}}
\cdot \frac{\Delta x}{x}.$$

**Herkkyys** kertoo, montako prosenttia tulos muuttuu, kun syöte muuttuu
prosentin. Heilurin jaksonajalle $T = 2\pi\sqrt{L/g}$ herkkyys varren
pituuden suhteen on $\tfrac12$: pituuden kahden prosentin mittausvirhe
näkyy jaksonajassa noin prosentin virheenä.

```{.python tiedosto="esimerkit/04-linearisointi.py" osa="heiluri"}
```

```{.tuloste tiedosto="esimerkit/04-linearisointi.odotettu"}
```

Potenssilakien $f = c\,x^n$ herkkyys on aina $n$, mikä on hyödyllinen
nyrkkisääntö. Vastuksen teho $P = U^2/R$ on jännitteen suhteen herkkyydeltään 2:
jännitteen prosentin heilahdus muuttaa tehoa kaksi prosenttia. Usean
muuttujan virheen eteneminen tehdään osittaisderivaatoilla (luku 8).

## Samat laskut Maximalla

Maximassa kriittiset pisteet ratkaistaan `solve`-funktiolla, joka antaa
kuutioyhtälön kaikki kolme juurta, myös kompleksiset. Reaalinen juuri
valitaan suodattamalla pois juuret, joissa on imaginaariyksikkö `%i`.
Numeerinen juuri haetaan funktiolla `find_root`, ja `taylor` astetta 1
antaa linearisoinnin.

```{.maxima tiedosto="esimerkit/maxima/04-sovellukset.mac" osa="sovellukset"}
```

```{.tuloste tiedosto="esimerkit/maxima/04-sovellukset.odotettu"}
```

## Käytännössä

- **Kirjoita optimointitehtävä yhden muuttujan funktioksi.** Sidosehdot
  (tilavuus, budjetti) ratkaistaan ensin ja sijoitetaan
  kohdefunktioon.
- **Tarkista päätepisteet ja luokittele kriittiset pisteet.** Derivaatan
  nollakohta voi olla minimi, maksimi tai ei kumpikaan.
- **Käytä Newtonia, kun alkuarvo on hyvä, ja haarukoivaa menetelmää,
  kun ei ole.** `brentq` ja vastaavat yhdistävät molempien edut.
  Rajoita kierrosmäärä ja tarkista lopuksi, että $f(x)$ on todella
  pieni.
- **Laske herkkyydet ennen mittauksia.** Ne kertovat, minkä suureen
  mittaukseen kannattaa panostaa: suure, jonka herkkyys on suuri,
  tarvitsee tarkimman mittauksen.

## Itsearviointi

- Osaat ratkaista optimointitehtävän: muodostaa kohdefunktion,
  sijoittaa sidosehdon, löytää kriittiset pisteet ja luokitella ne.
- Osaat toteuttaa Newtonin menetelmän ja tunnistaa sen tyypilliset
  epäonnistumiset.
- Osaat valita juurenhakumenetelmän tilanteen mukaan ja käyttää SciPyn
  `brentq`-funktiota.
- Osaat linearisoida funktion ja arvioida linearisoinnin virheen.
- Osaat laskea suhteellisen herkkyyden ja käyttää sitä mittausvirheen
  etenemisen arvioinnissa.
