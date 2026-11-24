# Jatkuvat jakaumat

Aika, jännite ja pituus voivat saada minkä tahansa arvon väliltä.
Jatkuvan satunnaismuuttujan yksittäisen arvon todennäköisyys on nolla;
todennäköisyys kuuluu väleille. *Tiheysfunktio* $f(x)$ kertoo, kuinka
tiheään arvot osuvat, ja *kertymäfunktio*
$F(x) = P(X \le x) = \int_{-\infty}^{x} f(t)\,dt$ kertoo
todennäköisyyden olla korkeintaan $x$.

| Jakauma | Tiheys | $E[X]$ | $\operatorname{Var}(X)$ | Käyttö |
|---------|--------|--------|--------------------------|--------|
| Tas($a$, $b$) | $1/(b-a)$ | $(a+b)/2$ | $(b-a)^2/12$ | pyöristysvirhe, vaihe |
| Exp($\lambda$) | $\lambda e^{-\lambda x}$ | $1/\lambda$ | $1/\lambda^2$ | väliajat, elinajat |
| N($\mu$, $\sigma^2$) | $\frac{1}{\sigma\sqrt{2\pi}}e^{-(x-\mu)^2/2\sigma^2}$ | $\mu$ | $\sigma^2$ | mittausvirhe, kohina |

## Tasainen jakauma

Tasajakaumassa jokainen välin kohta on yhtä todennäköinen. Se kuvaa
esimerkiksi kvantisointivirhettä, joka on tasaisesti jakautunut puolen
kvantisointiaskeleen välille (taito *Kiinteän pilkun aritmetiikka*):

```{.python tiedosto="esimerkit/05-jatkuvat.py" osa="tasainen"}
```

## Eksponenttijakauma

Jos tapahtumien määrä aikavälillä noudattaa Poisson-jakaumaa, niiden
väliset ajat noudattavat eksponenttijakaumaa samalla taajuudella
$\lambda$. Hännän todennäköisyys on yksinkertainen:
$P(T > t) = e^{-\lambda t}$.

```{.python tiedosto="esimerkit/05-jatkuvat.py" osa="eksponentti"}
```

Eksponenttijakauma on geometrisen jakauman jatkuva vastine ja yhtä
lailla muistiton. Elektronisen komponentin vikaantuminen vakiotaajuudella
on muistiton: käytetty komponentti on yhtä hyvä kuin uusi. Mekaaninen
kuluminen ei ole, ja sitä mallinnetaan esimerkiksi Weibull-jakaumalla.

## Normaalijakauma

Normaalijakauma syntyy, kun monta pientä riippumatonta tekijää
summautuu (luku *Raja-arvolauseet*). Siksi mittausvirheet ja kohina
ovat usein likimain normaalijakautuneita. Sen todennäköisyydet
lasketaan virhefunktiolla:
$P(|X - \mu| < k\sigma) = \operatorname{erf}(k/\sqrt{2})$.

```{.python tiedosto="esimerkit/05-jatkuvat.py" osa="normaali"}
```

```{.tuloste tiedosto="esimerkit/05-jatkuvat.odotettu"}
```

Tästä tulee nyrkkisääntö 68–95–99,7: yhden, kahden ja kolmen
keskihajonnan sisään osuu noin 68 %, 95 % ja 99,7 % arvoista. Kolmen
sigman toleranssi tarkoittaa siis, että kolme kappaletta tuhannesta on
toleranssin ulkopuolella.

## Käytännössä

- **Älä oleta normaalijakaumaa vasteajoille.** Ajat ovat positiivisia
  ja niillä on pitkä häntä; normaalimalli aliarvioi hitaat tapaukset
  dramaattisesti. Luku *Mittausten tulkinta* palaa tähän.
- **Käytä eksponenttijakaumaa satunnaisille väliajoille.** Se on
  Poisson-prosessin pari, ja sen avulla simuloidaan saapumisia
  jonomalleissa.
- **Tarkista muistittomuus aineistosta.** Jos odotettu jäljellä oleva
  aika muuttuu odotetun ajan mukana, eksponenttimalli ei sovi.
- **Laske todennäköisyydet virhefunktiolla.** `math.erf` ja `math.erfc`
  riittävät normaalijakauman häntiin ilman ulkoisia kirjastoja.

## Itsearviointi

- Osaat selittää tiheys- ja kertymäfunktion eron ja laskea
  todennäköisyyden välille.
- Osaat valita tasaisen, eksponentti- tai normaalijakauman tilanteen
  mukaan ja perustella valinnan.
- Osaat käyttää eksponenttijakauman muistittomuutta ja tunnistaa,
  milloin se ei päde.
- Osaat laskea normaalijakauman todennäköisyyksiä virhefunktiolla ja
  käyttää 68–95–99,7-sääntöä.
