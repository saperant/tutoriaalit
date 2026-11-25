# Diskreetit jakaumat

*Satunnaismuuttuja* liittää kokeen tulokseen luvun: hävinneiden
pakettien määrän, yritysten määrän ennen onnistumista tai sekunnissa
saapuneiden pyyntöjen määrän. Sen *jakauma* kertoo, millä
todennäköisyydellä se saa kunkin arvon. Tämä luku määrittelee ensin
jakauman kaksi tärkeintä tunnuslukua, odotusarvon ja varianssin, ja
esittelee sitten neljä jakaumaa, jotka kattavat suuren osan insinöörin
tarpeista.

## Odotusarvo ja varianssi

**Odotusarvo** on satunnaismuuttujan arvojen todennäköisyyksillä
painotettu keskiarvo,

$$E[X] = \sum_x x\, P(X = x).$$

Se on luku, jota kohti pitkän havaintosarjan keskiarvo asettuu; nimestä
huolimatta se ei välttämättä ole arvo, jota "odotetaan" (nopan
odotusarvo on 3,5). **Varianssi** mittaa, kuinka kaukana odotusarvosta
arvot tyypillisesti ovat: se on poikkeaman neliön odotusarvo,

$$\operatorname{Var}(X) = E\big[(X - E[X])^2\big].$$

Varianssin yksikkö on alkuperäisen yksikön neliö, joten hajonta
ilmoitetaan yleensä sen neliöjuurena, **keskihajontana**
$\sigma = \sqrt{\operatorname{Var}(X)}$. Odotusarvoa merkitään usein
kirjaimella $\mu$.

```{.python tiedosto="esimerkit/04-tunnusluvut.py" osa="noppa"}
```

```{.tuloste tiedosto="esimerkit/04-tunnusluvut.odotettu" rivit="1-3"}
```

Otoksen keskiarvo ja varianssi ovat näiden lukujen arvioita. Tässä
luvussa odotusarvo ja varianssi lasketaan määritelmästä; luku
*Odotusarvo ja varianssi* opettaa laskusäännöt, joilla ne saadaan
ilman summaa.

## Jakaumat taulukkona

| Jakauma | Malli | $P(X = k)$ | $E[X]$ | $\operatorname{Var}(X)$ |
|--------------|------------------------------|--------------------------|--------|--------------|
| Bernoulli($p$) | yksi yritys | $p$ tai $1 - p$ | $p$ | $p(1-p)$ |
| Bin($n$, $p$) | onnistumiset $n$:ssä yrityksessä | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | $np(1-p)$ |
| Geom($p$) | yritykset ensimmäiseen onnistumiseen | $(1-p)^{k-1}p$ | $1/p$ | $(1-p)/p^2$ |
| Poisson($\lambda$) | tapahtumat aikavälillä | $\lambda^k e^{-\lambda}/k!$ | $\lambda$ | $\lambda$ |

Taulukon odotusarvot ja varianssit seuraavat määritelmästä.
Binomijakaumalle sen voi tarkistaa summaamalla:

```{.python tiedosto="esimerkit/04-tunnusluvut.py" osa="binomi"}
```

```{.tuloste tiedosto="esimerkit/04-tunnusluvut.odotettu" rivit="4-"}
```

## Binomijakauma: pakettihäviö

Linkki hävittää kunkin paketin toisistaan riippumatta 2 %:n
todennäköisyydellä. Kuinka todennäköisesti sadasta paketista häviää
vähintään viisi? Hävinneiden määrä noudattaa binomijakaumaa: $k$
häviämisen paikat voidaan valita $\binom{n}{k}$ tavalla.

```{.python tiedosto="esimerkit/04-binomi.py" osa="pmf"}
```

```{.tuloste tiedosto="esimerkit/04-binomi.odotettu" rivit="1-7"}
```

NumPy arpoo binomijakaumasta suoraan, eikä yksittäisiä paketteja
tarvitse simuloida:

```{.python tiedosto="esimerkit/04-binomi.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/04-binomi.odotettu" rivit="8-"}
```

![Hävinneiden pakettien määrän pistetodennäköisyydet. Korostetut pylväät
ovat häntä $X \ge 5$. Ääriviivapylväät ovat Poisson-jakauma samalla
odotusarvolla 2; se on lähes sama, mihin palataan osiossa
*Poisson-jakauma*.](kuvat/diskreetit.png){width=68%}

Keskimäärin häviää kaksi pakettia, mutta joka kahdeskymmenes sadan
paketin erä menettää viisi tai enemmän. Mitoitus odotusarvon mukaan
alittaa todellisen tarpeen säännöllisesti.

## Geometrinen jakauma: uudelleenyritykset

Yhteys onnistuu kullakin yrityksellä 30 %:n todennäköisyydellä.
Yritysten määrä ensimmäiseen onnistumiseen noudattaa geometrista
jakaumaa. Yli $k$ yritystä tarvitaan täsmälleen silloin, kun $k$
ensimmäistä epäonnistuvat:

```{.python tiedosto="esimerkit/04-geometrinen.py" osa="teoria"}
```

```{.tuloste tiedosto="esimerkit/04-geometrinen.odotettu" rivit="1-5"}
```

```{.python tiedosto="esimerkit/04-geometrinen.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/04-geometrinen.odotettu" rivit="6-6"}
```

Geometrinen jakauma on *muistiton*: aiemmat epäonnistumiset eivät
lähennä onnistumista. Jos viisi yritystä on jo epäonnistunut, jäljellä
olevien yritysten odotusarvo on yhä $1/p$:

```{.python tiedosto="esimerkit/04-geometrinen.py" osa="muistiton"}
```

```{.tuloste tiedosto="esimerkit/04-geometrinen.odotettu" rivit="7-"}
```

Uudelleenyrityksille kannattaa siksi asettaa yläraja, jonka
todennäköisyys on hyväksyttävän pieni: kymmenen yritystä riittää yli
97 %:ssa tapauksista.

## Poisson-jakauma: tapahtumia aikavälillä

Kun tapahtumia sattuu toisistaan riippumatta vakiotaajuudella
$\lambda$, aikavälin tapahtumien määrä noudattaa Poisson-jakaumaa.
Palvelimelle saapuu keskimäärin kolme pyyntöä sekunnissa. Kuinka usein
sekunnissa tulee yli kahdeksan?

```{.python tiedosto="esimerkit/04-poisson.py" osa="poisson"}
```

```{.tuloste tiedosto="esimerkit/04-poisson.odotettu" rivit="1-5"}
```

Poisson on binomijakauman raja-arvo, kun yrityksiä on paljon ja kunkin
todennäköisyys pieni: monella käyttäjällä on kullakin pieni
todennäköisyys lähettää pyyntö juuri tällä sekunnilla.

```{.python tiedosto="esimerkit/04-poisson.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/04-poisson.odotettu" rivit="6-9"}
```

Poisson-jakauman odotusarvo ja varianssi ovat molemmat $\lambda$.
Tämä on käytännöllinen tarkistus: jos mitattujen lukumäärien varianssi
on selvästi keskiarvoa suurempi, tapahtumat tulevat ryöpyissä eivätkä
toisistaan riippumatta.

```{.python tiedosto="esimerkit/04-poisson.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/04-poisson.odotettu" rivit="10-"}
```

## Käytännössä

- **Valitse jakauma mallin mukaan.** Kiinteä määrä riippumattomia
  yrityksiä: binomi. Odotus ensimmäiseen onnistumiseen: geometrinen.
  Tapahtumat aikavälillä vakiotaajuudella: Poisson.
- **Mitoita hännän mukaan.** Puskurit, jonot ja uudelleenyritysten
  rajat mitoitetaan esimerkiksi 99,9 %:n persentiilin mukaan, ei
  odotusarvon.
- **Tarkista Poisson-oletus.** Varianssi selvästi keskiarvoa suurempi
  kertoo ryöppyisyydestä (*overdispersion*), jolloin Poisson-malli
  aliarvioi huiput.
- **Muista muistittomuus.** Riippumattomat yritykset eivät ”kerry”:
  monen epäonnistumisen jälkeenkin seuraava onnistuu samalla
  todennäköisyydellä.

## Itsearviointi

- Osaat määritellä odotusarvon, varianssin ja keskihajonnan ja laskea
  ne diskreetin jakauman pistetodennäköisyyksistä.
- Osaat tunnistaa, milloin tilanne noudattaa binomi-, geometrista tai
  Poisson-jakaumaa.
- Osaat laskea pistetodennäköisyydet ja hännän todennäköisyyden sekä
  tarkistaa ne simuloimalla.
- Osaat mitoittaa uudelleenyritysten ylärajan tai puskurin halutulle
  todennäköisyydelle.
- Osaat käyttää varianssin ja keskiarvon suhdetta Poisson-oletuksen
  tarkistuksena.
