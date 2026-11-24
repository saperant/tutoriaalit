# Ehdollinen todennäköisyys ja Bayesin kaava

Havainto muuttaa todennäköisyyksiä. Positiivinen testitulos, hälytys
tai sana ”ilmainen” sähköpostissa ovat todisteita, ja Bayesin kaava
kertoo, kuinka paljon niiden pitäisi muuttaa käsitystämme. Intuitio
erehtyy tässä järjestelmällisesti, joten laskeminen kannattaa.

## Ehdollinen todennäköisyys

Tapahtuman $A$ todennäköisyys, kun tiedetään $B$:n sattuneen, on
$$P(A \mid B) = \frac{P(A \cap B)}{P(B)}.$$
Kertolaskusääntö $P(A \cap B) = P(A \mid B)\,P(B)$ ja
*kokonaistodennäköisyys* $P(B) = P(B \mid A)P(A) + P(B \mid \bar
A)P(\bar A)$ seuraavat suoraan määritelmästä. Niistä saadaan
**Bayesin kaava**:
$$P(A \mid B) = \frac{P(B \mid A)\,P(A)}{P(B)}.$$

## Positiivinen testitulos

Testin *herkkyys* $P(+ \mid \text{sairas})$ on 99 % ja *tarkkuus*
$P(- \mid \text{terve})$ 95 %. Kuinka todennäköisesti positiivisen
tuloksen saanut on sairas? Vastaus riippuu ratkaisevasti siitä, kuinka
yleinen tila on:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="bayes"}
```

Kun esiintyvyys on 1 %, vain kuudesosa positiivisista on sairaita:
harvinaisessa joukossa terveiden väärät positiiviset ovat
lukumääräisesti enemmistö. Simulaatio miljoonasta henkilöstä vahvistaa
laskun:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="simulointi"}
```

Sama ilmiö tekee valvontajärjestelmistä meluisia. Hälytin, joka
havaitsee 95 % vioista ja hälyttää turhaan vain 1 %:ssa tunneista,
näyttää hyvältä, mutta jos vika on harvinainen, valtaosa hälytyksistä
on turhia:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="halytys"}
```

```{.tuloste tiedosto="esimerkit/03-bayes-testi.odotettu"}
```

Tämä on *perustason harha* (*base rate fallacy*): todisteen voimaa ei
voi arvioida tuntematta lähtötilannetta.

## Naiivi Bayes -luokittelija

Roskapostisuodatin arvioi, kumpaan luokkaan viesti kuuluu sen sanojen
perusteella. *Naiivi* Bayes olettaa sanat toisistaan riippumattomiksi
luokan sisällä, jolloin
$$P(\text{luokka} \mid \text{sanat}) \propto P(\text{luokka})
\prod_i P(\text{sana}_i \mid \text{luokka}).$$
Oletus on väärä, mutta luokittelu toimii silti usein hyvin. Opetetaan
malli pienellä aineistolla:

```{.python tiedosto="esimerkit/03-roskaposti.py" osa="aineisto"}
```

Kaksi teknistä yksityiskohtaa ovat välttämättömiä. Todennäköisyyksien
tulo pienenee nopeasti alle liukulukujen tarkkuuden, joten lasketaan
logaritmien summa. Opetusaineistosta puuttuva sana antaisi
todennäköisyyden nolla ja nollaisi koko tulon, joten jokaiseen
lukumäärään lisätään yksi (*Laplace-tasoitus*):

```{.python tiedosto="esimerkit/03-roskaposti.py" osa="malli"}
```

```{.python tiedosto="esimerkit/03-roskaposti.py" osa="luokittelu"}
```

```{.tuloste tiedosto="esimerkit/03-roskaposti.odotettu"}
```

## Riippumattomuus

Tapahtumat ovat *riippumattomia*, jos $P(A \cap B) = P(A)\,P(B)$:
toisen tapahtuminen ei kerro mitään toisesta. Riippumattomuus tekee
laskuista helppoja, ja siksi se oletetaan usein liian kevyesti.
Kahden palvelimen rinnakkaisjärjestelmä on alhaalla vain, jos
molemmat ovat, mikä riippumattomilla vioilla on harvinaista:

```{.python tiedosto="esimerkit/03-riippumattomuus.py" osa="teoria"}
```

Todellisuudessa palvelimilla on yhteisiä vikasyitä: sama sähkönsyöttö,
sama verkko, sama ohjelmistoversio. Lisätään simulaatioon harvinainen
sähkökatko, joka kaataa molemmat:

```{.python tiedosto="esimerkit/03-riippumattomuus.py" osa="yhteinen"}
```

```{.tuloste tiedosto="esimerkit/03-riippumattomuus.odotettu"}
```

Yhteinen vikasyy kasvattaa kahden vian samanaikaisuuden yli
kaksikymmenkertaiseksi, ja kahdennus parantaa saatavuutta vain
vähän. Riippumattomuus on mallin oletus, joka on perusteltava.

## Käytännössä

- **Kysy aina lähtötaso.** Herkkyys ja väärien hälytysten osuus eivät
  yksin kerro, mitä hälytys tarkoittaa; tarvitaan myös tapahtuman
  yleisyys.
- **Laske harvinaisille tapahtumille.** Kun tapahtuma on harvinainen,
  pienikin väärien positiivisten osuus hukuttaa oikeat löydökset.
  Valvonnassa tämä näkyy hälytysväsymyksenä.
- **Laske logaritmeilla.** Monen pienen todennäköisyyden tulo
  alivuotaa; logaritmien summa ei.
- **Tasoita nollat.** Opetusaineistosta puuttuvan tapauksen
  todennäköisyys ei ole nolla, vain tuntematon.
- **Epäile riippumattomuutta.** Rinnakkaisten järjestelmien yhteiset
  vikasyyt hallitsevat saatavuutta. Hajauta sähkö, verkko,
  sijainti ja ohjelmistoversiot, jos kahdennukselta odotetaan
  riippumattomuutta.

## Itsearviointi

- Osaat laskea ehdollisen todennäköisyyden ja soveltaa Bayesin kaavaa
  testitulokseen tai hälytykseen.
- Osaat selittää perustason harhan ja sen merkityksen valvonnalle.
- Osaat toteuttaa naiivin Bayes-luokittelijan logaritmeilla ja
  Laplace-tasoituksella.
- Osaat tarkistaa riippumattomuuden ja arvioida yhteisen vikasyyn
  vaikutuksen saatavuuteen.
