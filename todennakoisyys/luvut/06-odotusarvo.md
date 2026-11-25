# Odotusarvo ja varianssi

Jakauma kuvaa satunnaismuuttujan kokonaan, mutta usein riittää kaksi
lukua: odotusarvo $E[X]$ ja varianssi $\operatorname{Var}(X)$, jotka
määriteltiin luvussa *Diskreetit jakaumat*. Tähän asti ne on laskettu
määritelmästä tai luettu taulukosta. Tämä luku opettaa laskusäännöt,
joilla monimutkaisen suureen odotusarvo ja varianssi saadaan sen osien
tunnusluvuista ilman, että jakaumaa tarvitsee tuntea.

## Odotusarvon lineaarisuus

Odotusarvo on lineaarinen: $E[aX + bY] = aE[X] + bE[Y]$, **vaikka**
$X$ ja $Y$ olisivat riippuvia. Tämä on todennäköisyyslaskennan
tehokkain temppu: monimutkainen lukumäärä kirjoitetaan
*indikaattoreiden* summaksi. Indikaattori on 1, jos tapahtuma sattuu,
muuten 0, ja sen odotusarvo on tapahtuman todennäköisyys.

Satunnaisen permutaation kiintopisteiden määrä on $n$ indikaattorin
summa, ja kunkin todennäköisyys on $1/n$. Odotusarvo on siis 1
jokaisella $n$, vaikka indikaattorit riippuvat toisistaan:

```{.python tiedosto="esimerkit/06-odotusarvo.py" osa="kiintopisteet"}
```

Samalla tavalla saadaan eri arvojen odotettu määrä, kun $n$ arvoa
valitaan $d$:stä: jokainen $d$:stä arvosta on mukana todennäköisyydellä
$1 - (1 - 1/d)^n$. Tämä kertoo esimerkiksi, kuinka monta eri
hajautustaulun lokeroa täyttyy.

```{.python tiedosto="esimerkit/06-odotusarvo.py" osa="erilaiset"}
```

```{.tuloste tiedosto="esimerkit/06-odotusarvo.odotettu"}
```

## Varianssin laskusäännöt

Varianssille pätee $\operatorname{Var}(aX + b) = a^2
\operatorname{Var}(X)$: siirto ei muuta hajontaa ja skaalaus muuttaa
sitä neliöllisesti. Riippumattomien muuttujien summan varianssi on
varianssien summa:
$$\operatorname{Var}(X + Y) = \operatorname{Var}(X) +
\operatorname{Var}(Y), \qquad \text{kun } X \text{ ja } Y
\text{ ovat riippumattomia.}$$
Keskihajonnat eivät siis summaudu vaan niiden neliöt. Jos muuttujat
riippuvat toisistaan, kaavaan tulee lisätermi, joka mittaa niiden
yhteisvaihtelua. Se on kovarianssi, ja se määritellään seuraavassa
luvussa.

Odotusarvon voi laskea myös ehdolla: *ehdollinen odotusarvo*
$E[X \mid A]$ on $X$:n odotusarvo niissä tapauksissa, joissa $A$
sattuu. Kokonaisodotusarvo on ehdollisten painotettu keskiarvo,
$E[X] = E[X \mid A]\,P(A) + E[X \mid \bar A]\,P(\bar A)$, samaan
tapaan kuin kokonaistodennäköisyys luvussa *Ehdollinen todennäköisyys
ja Bayesin kaava*.

## Toleranssien kasautuminen

Kymmenen 100 ohmin vastusta kytketään sarjaan, ja kunkin toleranssi on
±1 % kolmen sigman tasolla. Pahimman tapauksen analyysi laskee
poikkeamat yhteen, mutta kaikki vastukset eivät ole yhtä aikaa
äärilaidalla. Tilastollinen analyysi (*root sum square*, RSS) laskee
varianssit yhteen:

```{.python tiedosto="esimerkit/06-toleranssit.py" osa="kasautuminen"}
```

Simulaatio puoltaa tilastollista tulosta: summan hajonta kasvaa kuten
$\sqrt{n}$, ja pahimman tapauksen lähellekään päätyminen on käytännössä
mahdotonta.

```{.python tiedosto="esimerkit/06-toleranssit.py" osa="simulointi"}
```

Skaalaussäännön tarkistus: yksikkömuunnos fahrenheiteiksi kertoo
varianssin luvulla $1{,}8^2$.

```{.python tiedosto="esimerkit/06-toleranssit.py" osa="skaalaus"}
```

```{.tuloste tiedosto="esimerkit/06-toleranssit.odotettu"}
```

## Käytännössä

- **Pilko lukumäärä indikaattoreiksi.** Odotusarvon lineaarisuus pätee
  riippuvuuksista huolimatta, ja monimutkainen lukumäärä ratkeaa
  todennäköisyyksien summana.
- **Summaa varianssit, älä keskihajontoja.** Riippumattomat
  epävarmuudet kasautuvat kuten $\sqrt{n}$, eivät kuten $n$.
- **Valitse toleranssianalyysi tilanteen mukaan.** RSS sopii suurille
  sarjoille ja riippumattomille komponenteille. Pahin tapaus sopii
  turvallisuuskriittisiin kohteisiin ja silloin, kun komponentit
  tulevat samasta erästä ja niiden virheet riippuvat toisistaan.
- **Tarkista riippumattomuus.** Kun virheillä on yhteinen syy, kuten
  lämpötila tai valmistuserä, RSS aliarvioi kokonaisvirheen (luku
  *Kaksi muuttujaa: kovarianssi, korrelaatio ja regressio*).

## Itsearviointi

- Osaat laskea odotusarvon lineaarisuuden ja indikaattoreiden avulla.
- Osaat soveltaa varianssin laskusääntöjä skaalaukseen ja
  riippumattomien muuttujien summaan.
- Osaat tehdä pahimman tapauksen ja tilastollisen
  toleranssianalyysin ja perustella valinnan.
