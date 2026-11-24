# Diskreetit jakaumat

*Satunnaismuuttuja* liittää kokeen tulokseen luvun: hävinneiden
pakettien määrän, yritysten määrän ennen onnistumista tai sekunnissa
saapuneiden pyyntöjen määrän. Sen *jakauma* kertoo, millä
todennäköisyydellä se saa kunkin arvon. Neljä jakaumaa kattaa suuren
osan insinöörin tarpeista.

| Jakauma | Malli | $P(X = k)$ | $E[X]$ | $\operatorname{Var}(X)$ |
|--------------|------------------------------|--------------------------|--------|--------------|
| Bernoulli($p$) | yksi yritys | $p$ tai $1 - p$ | $p$ | $p(1-p)$ |
| Bin($n$, $p$) | onnistumiset $n$:ssä yrityksessä | $\binom{n}{k}p^k(1-p)^{n-k}$ | $np$ | $np(1-p)$ |
| Geom($p$) | yritykset ensimmäiseen onnistumiseen | $(1-p)^{k-1}p$ | $1/p$ | $(1-p)/p^2$ |
| Poisson($\lambda$) | tapahtumat aikavälillä | $\lambda^k e^{-\lambda}/k!$ | $\lambda$ | $\lambda$ |

## Binomijakauma: pakettihäviö

Linkki hävittää kunkin paketin toisistaan riippumatta 2 %:n
todennäköisyydellä. Kuinka todennäköisesti sadasta paketista häviää
vähintään viisi? Hävinneiden määrä noudattaa binomijakaumaa: $k$
häviämisen paikat voidaan valita $\binom{n}{k}$ tavalla.

```{.python tiedosto="esimerkit/04-binomi.py" osa="pmf"}
```

NumPy arpoo binomijakaumasta suoraan, eikä yksittäisiä paketteja
tarvitse simuloida:

```{.python tiedosto="esimerkit/04-binomi.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/04-binomi.odotettu"}
```

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

```{.python tiedosto="esimerkit/04-geometrinen.py" osa="simulointi"}
```

Geometrinen jakauma on *muistiton*: aiemmat epäonnistumiset eivät
lähennä onnistumista. Jos viisi yritystä on jo epäonnistunut, jäljellä
olevien yritysten odotusarvo on yhä $1/p$:

```{.python tiedosto="esimerkit/04-geometrinen.py" osa="muistiton"}
```

```{.tuloste tiedosto="esimerkit/04-geometrinen.odotettu"}
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

Poisson on binomijakauman raja-arvo, kun yrityksiä on paljon ja kunkin
todennäköisyys pieni: monella käyttäjällä on kullakin pieni
todennäköisyys lähettää pyyntö juuri tällä sekunnilla.

```{.python tiedosto="esimerkit/04-poisson.py" osa="raja"}
```

Poisson-jakauman odotusarvo ja varianssi ovat molemmat $\lambda$.
Tämä on käytännöllinen tarkistus: jos mitattujen lukumäärien varianssi
on selvästi keskiarvoa suurempi, tapahtumat tulevat ryöpyissä eivätkä
toisistaan riippumatta.

```{.python tiedosto="esimerkit/04-poisson.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/04-poisson.odotettu"}
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

- Osaat tunnistaa, milloin tilanne noudattaa binomi-, geometrista tai
  Poisson-jakaumaa.
- Osaat laskea pistetodennäköisyydet ja hännän todennäköisyyden sekä
  tarkistaa ne simuloimalla.
- Osaat mitoittaa uudelleenyritysten ylärajan tai puskurin halutulle
  todennäköisyydelle.
- Osaat käyttää varianssin ja keskiarvon suhdetta Poisson-oletuksen
  tarkistuksena.
