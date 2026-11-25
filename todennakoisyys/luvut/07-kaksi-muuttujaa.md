# Kaksi muuttujaa: kovarianssi, korrelaatio ja regressio

Tähän asti satunnaismuuttujia on tarkasteltu yksi kerrallaan tai
oletettu riippumattomiksi. Mittauksissa suureet kuitenkin vaihtelevat
usein yhdessä: kuorma ja vasteaika, lämpötila ja virhemäärä, kaksi
saman häiriön alaista kanavaa. Tämä luku antaa yhteisvaihtelulle mitan
(kovarianssi ja korrelaatio), näyttää, mitä mitta ei kerro
(riippumattomuutta eikä syy-yhteyttä), ja sovittaa lopuksi suoran
kahden muuttujan välille. Edellisen luvun summan varianssi saa samalla
puuttuvan terminsä.

## Yhteisjakauma ja reunajakauma

Kahden satunnaismuuttujan **yhteisjakauma** kertoo jokaisen arvoparin
todennäköisyyden $P(X = x, Y = y)$. Äärellisessä tapauksessa se on
taulukko. Esimerkissä $X$ kertoo, osuiko pyyntö välimuistiin, ja $Y$
on pyynnön tekemien tietokantakyselyjen määrä:

| Välimuisti | $Y = 0$ | $Y = 1$ | $Y = 2$ | $P(X = x)$ |
|---|---|---|---|---|
| $X = 1$ (osuma) | 0,60 | 0,10 | 0 | 0,70 |
| $X = 0$ (huti) | 0 | 0,20 | 0,10 | 0,30 |
| $P(Y = y)$ | 0,60 | 0,30 | 0,10 | 1 |

Rivin tai sarakkeen summa on **reunajakauma**: yhden muuttujan jakauma,
kun toisesta ei välitetä. Muuttujat ovat riippumattomia täsmälleen
silloin, kun jokainen taulukon alkio on reunatodennäköisyyksien tulo.
Tässä niin ei ole: osuma ja kaksi kyselyä ei satu koskaan, vaikka
tulo olisi $0{,}70 \cdot 0{,}10$.

```{.python tiedosto="esimerkit/07-yhteisjakauma.py" osa="taulukko"}
```

```{.tuloste tiedosto="esimerkit/07-yhteisjakauma.odotettu" rivit="1-3"}
```

## Kovarianssi ja korrelaatiokerroin

**Kovarianssi** on poikkeamien tulon odotusarvo:

$$\operatorname{Cov}(X, Y) = E\big[(X - E[X])(Y - E[Y])\big]
  = E[XY] - E[X]\,E[Y].$$

Se on positiivinen, kun muuttujat poikkeavat odotusarvostaan yleensä
samaan suuntaan, negatiivinen, kun vastakkaisiin, ja nolla, kun
muuttujat ovat riippumattomia. Muuttujan kovarianssi itsensä kanssa on
sen varianssi. Kovarianssin suuruus riippuu yksiköistä, joten vertailua
varten se jaetaan keskihajonnoilla. Tulos on **korrelaatiokerroin**

$$\rho = \frac{\operatorname{Cov}(X, Y)}{\sigma_X\, \sigma_Y},
  \qquad -1 \le \rho \le 1,$$

yksikötön luku, joka on $\pm 1$ täsmälleen silloin, kun pisteet ovat
samalla suoralla.

```{.python tiedosto="esimerkit/07-yhteisjakauma.py" osa="kovarianssi"}
```

```{.tuloste tiedosto="esimerkit/07-yhteisjakauma.odotettu" rivit="4-"}
```

Välimuistiosuma ja kyselyjen määrä korreloivat vahvasti negatiivisesti.
Ehdolliset odotusarvot kertovat saman käytännön kielellä: osuma tekee
keskimäärin 0,14 kyselyä, huti 1,33.

Kovarianssi täydentää edellisen luvun laskusäännön:

$$\operatorname{Var}(X + Y) = \operatorname{Var}(X) +
  \operatorname{Var}(Y) + 2 \operatorname{Cov}(X, Y).$$

Positiivisesti korreloivat virheet kasautuvat pahemmin kuin
riippumattomat, ja negatiivisesti korreloivat kumoavat toisiaan.

Mittausaineistosta kovarianssi ja korrelaatio arvioidaan
**otoskovarianssilla** ja **otoskorrelaatiolla** $r$ (Pearsonin
korrelaatiokerroin), joissa odotusarvojen paikalla ovat keskiarvot ja
jakajana $n - 1$:

```{.python tiedosto="esimerkit/07-korrelaatio.py" osa="korrelaatio"}
```

```{.tuloste tiedosto="esimerkit/07-korrelaatio.odotettu" rivit="1-4"}
```

Aineisto kannattaa aina myös piirtää. **Hajontakuviossa** jokainen
havaintopari on piste, ja korrelaatio näkyy pistepilven muotona:

![Hajontakuvioita eri korrelaatioilla. Mitä lähempänä $|r|$ on yhtä,
sitä kapeampi pilvi on. Oikeanpuoleisessa kuviossa $Y$ määräytyy
kokonaan $X$:stä, mutta korrelaatio on lähes
nolla.](kuvat/korrelaatio.png){width=100%}

```{.python tiedosto="esimerkit/07-korrelaatio.py" osa="yksikot"}
```

```{.tuloste tiedosto="esimerkit/07-korrelaatio.odotettu" rivit="5-7"}
```

Yksikön vaihto sekunneista millisekunteihin tuhatkertaistaa
kovarianssin mutta ei muuta korrelaatiota.

## Mitä korrelaatio ei kerro

**Korrelaatio ei ole riippuvuuden yleinen mitta.** Se mittaa vain
suoraviivaista yhteyttä. Riippumattomien muuttujien korrelaatio on
nolla, mutta käänteinen ei päde: nollakorrelaatio ei takaa
riippumattomuutta. Lisäksi yksittäinen poikkeava havainto voi yksin
tuottaa suuren korrelaation pienessä aineistossa.

```{.python tiedosto="esimerkit/07-korrelaatio.py" osa="epalineaarinen"}
```

```{.tuloste tiedosto="esimerkit/07-korrelaatio.odotettu" rivit="8-"}
```

**Korrelaatio ei ole syy-yhteys.** Kun kaksi suuretta korreloi,
selityksiä on neljä: $X$ vaikuttaa $Y$:hyn, $Y$ vaikuttaa $X$:ään,
kolmas tekijä vaikuttaa molempiin, tai kyse on sattumasta. Kolmatta
tekijää kutsutaan **sekoittavaksi tekijäksi** (*confounder*).
Palvelimen muistinkäyttö ja vasteaika korreloivat vahvasti, vaikka
muisti ei hidasta mitään: molemmat kasvavat kuorman mukana.

```{.dot otsikko="Sekoittava tekijä: kuorma vaikuttaa sekä muistinkäyttöön että vasteaikaan, ja ne korreloivat keskenään ilman syy-yhteyttä (katkoviiva)"}
digraph {
  nodesep=0.8; ranksep=0.5;
  node [shape=box];
  muisti [label="muistinkäyttö"];
  kuorma -> muisti; kuorma -> vasteaika;
  muisti -> vasteaika [style=dashed, dir=none, constraint=false,
                       label="r = 0,87"];
  { rank=same; muisti; vasteaika; }
}
```

```{.python tiedosto="esimerkit/07-sekoittaja.py" osa="sekoittaja"}
```

```{.tuloste tiedosto="esimerkit/07-sekoittaja.odotettu"}
```

Kun kuorma pidetään lähes vakiona, korrelaatio katoaa. Jos tästä
aineistosta pääteltäisiin, että muistin lisääminen nopeuttaa
palvelua, päätös olisi väärä. Syy-yhteyden osoittaa luotettavasti vain
koe, jossa yhtä tekijää muutetaan ja muut pidetään ennallaan tai
arvotaan satunnaisesti. Tästä syystä A/B-testi (luku *Hypoteesitestaus
ja A/B-testit*) jakaa käyttäjät ryhmiin arpomalla.

## Lineaarinen regressio

Korrelaatio kertoo, kuinka tiukasti pisteet ovat suoran ympärillä.
**Regressio** kertoo, mikä se suora on. Mallissa $y = a + bx$
kertoimet valitaan niin, että **jäännösten** $y_i - (a + b x_i)$
neliöiden summa on pienin mahdollinen (pienimmän neliösumman
menetelmä). Ratkaisu on

$$b = \frac{\operatorname{Cov}(x, y)}{\operatorname{Var}(x)}
    = r\, \frac{s_y}{s_x}, \qquad a = \bar y - b\, \bar x.$$

Kulmakerroin on siis korrelaatio skaalattuna keskihajontojen suhteella,
ja suora kulkee keskiarvopisteen $(\bar x, \bar y)$ kautta.
**Selitysaste** $R^2$ on se osuus $y$:n vaihtelusta, jonka suora
selittää; yhden selittäjän mallissa se on korrelaatiokertoimen neliö.

```{.python tiedosto="esimerkit/07-regressio.py" osa="sovitus"}
```

```{.python tiedosto="esimerkit/07-regressio.py" osa="suora"}
```

```{.tuloste tiedosto="esimerkit/07-regressio.odotettu" rivit="1-5"}
```

Suorittimen käyttöaste kasvaa noin 0,15 prosenttiyksikköä jokaista
lisäpyyntöä kohti, ja suora selittää 95 % vaihtelusta. Jäännösten
keskihajonta 3,7 prosenttiyksikköä on yksittäisen ennusteen tyypillinen
virhe. Kaava on sama pienimmän neliösumman tehtävä, jonka taito
*Lineaarialgebra* ratkaisee matriiseilla: se yleistyy usealle
selittäjälle ja käyrille, ja sen laskenta kannattaa jättää kirjastolle
(`np.linalg.lstsq`). Huonokuntoiset sovitukset, kuten korkea-asteiset
polynomit, ja niiden vakauttaminen käsitellään taidossa *Numeeriset
menetelmät*.

Selitysaste ei kerro, onko malli oikea. Sen näkee jäännöksistä:
oikean mallin jäännökset näyttävät kohinalta, väärän mallin
jäännöksissä on kuvio.

```{.python tiedosto="esimerkit/07-regressio.py" osa="kayra"}
```

```{.tuloste tiedosto="esimerkit/07-regressio.odotettu" rivit="6-"}
```

![Kaksi sovitusta ja niiden jäännökset. Vasemmalla suora on oikea
malli: jäännökset hajoavat tasaisesti nollan molemmin puolin.
Oikealla selitysaste on 0,84, mutta jäännökset muodostavat kaaren:
vasteaika ei kasva kuorman mukana suoraviivaisesti, ja suora aliarvioi
sen juuri suurilla kuormilla, joilla ennustetta
tarvittaisiin.](kuvat/regressio.png){width=95%}

Kulmakertoimen epävarmuus arvioidaan samoilla välineillä kuin minkä
tahansa estimaatin: luottamusvälillä, esimerkiksi bootstrapilla (luku
*Estimointi ja luottamusvälit*).

## Käytännössä

- **Piirrä hajontakuvio ennen kuin lasket korrelaation.** Yksi luku
  ei erota suoraa yhteyttä, käyrää, kahta ryhmää ja yhtä poikkeavaa
  pistettä toisistaan.
- **Älä päättele syytä korrelaatiosta.** Kysy, mikä kolmas tekijä
  voisi vaikuttaa molempiin: kuorma, kellonaika, laitesukupolvi,
  käyttäjäryhmä. Jos mahdollista, tee koe.
- **Katso jäännökset, älä vain selitysastetta.** Kaari, viuhka tai
  trendi jäännöksissä kertoo, että malli on väärä, vaikka $R^2$ olisi
  suuri.
- **Älä ekstrapoloi.** Suora on sovitettu mitatulle välille. Sen
  ulkopuolella, esimerkiksi kuorman lähestyessä kapasiteettia, yhteys
  on usein aivan toinen.
- **Muista kovarianssi virhebudjetissa.** Yhteisestä syystä johtuvat
  virheet eivät kasaudu kuten $\sqrt{n}$; summan varianssiin tulee
  termi $2\operatorname{Cov}$.

## Itsearviointi

- Osaat laskea reunajakaumat yhteisjakaumasta ja tarkistaa, ovatko
  muuttujat riippumattomia.
- Osaat määritellä kovarianssin ja korrelaatiokertoimen, laskea ne
  aineistosta ja selittää, miksi korrelaatio ei riipu yksiköistä.
- Osaat antaa esimerkin riippuvista muuttujista, joiden korrelaatio
  on nolla, ja selittää sekoittavan tekijän vaikutuksen.
- Osaat sovittaa regressiosuoran, tulkita kulmakertoimen ja
  selitysasteen ja arvioida mallin sopivuuden jäännöksistä.
