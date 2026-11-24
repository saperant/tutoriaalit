# Integraalin sovelluksia

Integraali vastaa jokaiseen kysymykseen, jossa suuretta kertyy jatkuvasti:
pinta-ala, kokonaisenergia, keskiarvo, työ ja todennäköisyys. Luvussa
käydään ensin läpi, miten integraali lasketaan numeerisesti, kun kaavaa
ei ole tai integraalifunktiota ei löydy, ja sitten tavallisimmat
insinöörisovellukset.

## Numeerinen integrointi

Mittausdata on näytteitä, ja monella integroitavalla ei ole
alkeisfunktiona kirjoitettavaa integraalifunktiota (luku 5). Silloin
integraali lasketaan näytteistä. Kaksi perusmenetelmää korvaa funktion
osaväleillä yksinkertaisella käyrällä, jonka integraali tunnetaan:

- **Puolisuunnikassääntö** yhdistää peräkkäiset näytteet suoralla.
  Suorakulmioiden sijaan lasketaan puolisuunnikkaiden aloja:
  $h\bigl(\tfrac12 y_0 + y_1 + \dots + y_{n-1} + \tfrac12 y_n\bigr)$.
- **Simpsonin sääntö** sovittaa kolmen peräkkäisen näytteen kautta
  paraabelin. Osavälejä on oltava parillinen määrä, ja painot ovat
  vuorotellen 4 ja 2: $\tfrac h3(y_0 + 4y_1 + 2y_2 + 4y_3 + \dots + y_n)$.

```{.python tiedosto="esimerkit/06-numeerinen.py" osa="saannot"}
```

Testifunktiona on $\int_0^\pi \sin x\,dx = 2$. Kun osavälien määrä
kaksinkertaistuu, puolisuunnikassäännön virhe pienenee neljäsosaan ja
Simpsonin säännön virhe kuudestoistaosaan: virheet ovat kertalukua $h^2$
ja $h^4$.

```{.python tiedosto="esimerkit/06-numeerinen.py" osa="vertailu"}
```

Kirjastoissa nämä säännöt ovat valmiina. SciPyn `trapezoid` ja `simpson`
ottavat näytteet, ja `quad` ottaa funktion. `quad` valitsee
laskentapisteet itse ja tihentää niitä siellä, missä funktio vaihtelee
nopeasti, kunnes virhearvio alittaa toleranssin (**adaptiivinen
integrointi**).

```{.python tiedosto="esimerkit/06-numeerinen.py" osa="kirjasto"}
```

```{.tuloste tiedosto="esimerkit/06-numeerinen.odotettu"}
```

Nyrkkisääntö: näytteille Simpson tai puolisuunnikas, funktiolle `quad`.
Virhekertalukujen johtaminen, Gaussin kvadratuurit ja adaptiivisuuden
yksityiskohdat käsitellään taidossa *Numeeriset menetelmät*.

## Pinta-ala ja keskiarvo

Kahden käyrän väliin jäävä pinta-ala on ylemmän ja alemman käyrän
erotuksen integraali niiden leikkauspisteiden välillä. Leikkauspisteet
ratkaistaan ensin, ja välillä on tarkistettava, kumpi käyrä on ylempänä.

```{.python tiedosto="esimerkit/06-sovellukset.py" osa="ala"}
```

Funktion **keskiarvo** välillä $[a, b]$ on integraali jaettuna välin
pituudella:

$$\bar f = \frac{1}{b - a}\int_a^b f(x)\,dx.$$

Sähkötekniikassa tärkeämpi on **tehollisarvo** (*root mean square*,
RMS): neliön keskiarvon neliöjuuri. Vaihtojännitteen tehollisarvo on se
tasajännite, joka tuottaa vastuksessa saman keskimääräisen tehon.
Sinimuotoiselle jännitteelle tehollisarvo on huippuarvo jaettuna
$\sqrt2$:lla: 325 voltin huippuarvo vastaa 230 voltin verkkojännitettä.

```{.python tiedosto="esimerkit/06-sovellukset.py" osa="tehollisarvo"}
```

## Kaaren pituus ja pyörähdyskappaleet

Integraali laskee myös geometrisia suureita. Käyrän $y = f(x)$ **kaaren
pituus** välillä $[a, b]$ saadaan jakamalla käyrä lyhyisiin janoihin,
joiden pituus on Pythagoraan lauseen mukaan
$\sqrt{dx^2 + dy^2} = \sqrt{1 + f'(x)^2}\,dx$:

$$s = \int_a^b \sqrt{1 + f'(x)^2}\,dx.$$

Juurilauseke tekee integraalista usein hankalan, joten kaaren pituus on
tyypillinen numeerisen integroinnin tehtävä. Esimerkissä lasketaan
riippusillan kaapelin pituus, kun kaapelin muotoa approksimoidaan
paraabelilla. Kaapeli on 200 metrin jännevälillä noin 8 metriä jänneväliä
pidempi.

```{.python tiedosto="esimerkit/06-geometria.py" osa="kaari"}
```

Kun käyrä pyörähtää $x$-akselin ympäri, syntyy **pyörähdyskappale**.
Kohtisuora leikkaus kohdassa $x$ on ympyräkiekko, jonka säde on $f(x)$
ja ala $\pi f(x)^2$, joten tilavuus on kiekkojen alojen integraali:

$$V = \pi \int_a^b f(x)^2\,dx.$$

Kartion ja pallon tilavuuskaavat seuraavat suoraan. Samalla periaatteella
lasketaan säiliöiden, pullojen ja sorvattujen kappaleiden tilavuudet, kun
profiili tunnetaan mittauksista.

```{.python tiedosto="esimerkit/06-geometria.py" osa="tilavuus"}
```

```{.tuloste tiedosto="esimerkit/06-geometria.odotettu"}
```

## Työ ja energia

Kun voima on vakio, työ on voima kertaa matka. Muuttuva voima integroidaan
matkan yli: $W = \int F(s)\,ds$. Jousen voima on Hooken lain mukaan
$F = ks$, joten jousen venyttämiseen tarvittava työ on
$\tfrac12 k s^2$, joka on jouseen varastoitunut energia.

Samalla tavalla energia on tehon integraali ajan yli:
$E = \int P(t)\,dt$. Akun tai laitteen kuluttama energia lasketaan
mitatusta tehosta numeerisesti integroimalla. Huomaa yksiköt: tehon
integraali sekunteina antaa jouleja, ja wattitunti on 3600 joulea.

```{.python tiedosto="esimerkit/06-sovellukset.py" osa="tyo"}
```

## Todennäköisyys

Jatkuvan satunnaismuuttujan todennäköisyys on **tiheysfunktion**
integraali: $P(a < X < b) = \int_a^b p(x)\,dx$. Tiheysfunktion integraali
koko reaaliakselin yli on 1. Standardoidun normaalijakauman
todennäköisyys osua välille $[-1, 1]$ on noin 68 %, mikä on tuttu
"yhden keskihajonnan sääntö". Eksponenttijakauman todennäköisyys, että
laite kestää yli kaksi keskimääräistä elinikää, on $e^{-2} \approx 13{,}5$ %.

```{.python tiedosto="esimerkit/06-sovellukset.py" osa="todennakoisyys"}
```

```{.tuloste tiedosto="esimerkit/06-sovellukset.odotettu"}
```

Jakaumat ja niiden tunnusluvut käsitellään taidossa *Todennäköisyys ja
tilastot*. Integraali on niiden laskennallinen perusta: odotusarvo on
$\int x\,p(x)\,dx$ ja varianssi $\int (x - \mu)^2 p(x)\,dx$.

## Samat laskut Maximalla

Maximassa numeerinen integrointi tehdään QUADPACK-kirjaston funktioilla
(`quad_qags` ja muut), samoilla rutiineilla, joita SciPyn `quad`
käyttää. `romberg` on vanhempi menetelmä, joka tarkentaa
puolisuunnikassääntöä Richardsonin ekstrapoloinnilla.

```{.maxima tiedosto="esimerkit/maxima/06-numeerinen.mac" osa="numeerinen"}
```

```{.tuloste tiedosto="esimerkit/maxima/06-numeerinen.odotettu"}
```

## Käytännössä

- **Valitse menetelmä datan mukaan.** Näytteet: `trapezoid` tai
  `simpson`. Kaava: `quad`. Symbolinen tulos: `integrate`, jos se on
  saatavilla.
- **Lue virhearvio.** `quad` palauttaa sen aina. Jos arvio on suuri tai
  kirjasto varoittaa, funktiossa on todennäköisesti piikki, epäjatkuvuus
  tai hidas suppeneminen.
- **Pidä yksiköt mukana.** Integraalin yksikkö on integroitavan yksikkö
  kertaa muuttujan yksikkö: wattia kertaa sekunti on joule.
- **Tehollisarvo, ei keskiarvo.** Vaihtosuureiden teho ja lämpeneminen
  määräytyvät tehollisarvosta. Keskiarvo on sinimuotoiselle signaalille
  nolla.

## Itsearviointi

- Osaat laskea integraalin puolisuunnikas- ja Simpsonin säännöllä sekä
  kertoa niiden virheiden kertaluvut.
- Osaat valita SciPyn integrointifunktion datan tai funktion mukaan ja
  tulkita `quad`-funktion virhearvion.
- Osaat laskea käyrien väliin jäävän pinta-alan, funktion keskiarvon ja
  tehollisarvon.
- Osaat laskea kaaren pituuden ja pyörähdyskappaleen tilavuuden.
- Osaat laskea työn ja energian integraalina sekä todennäköisyyden
  tiheysfunktion integraalina.
