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

Testin *herkkyys* (*sensitivity*) $P(+ \mid \text{sairas})$ on 99 % ja
*tarkkuus* (*specificity*) $P(- \mid \text{terve})$ 95 %. Tarkkuus
tarkoittaa tässä lääketieteen tapaan terveiden oikein tunnistettua
osuutta; koneoppimisen *accuracy* ja *precision* ovat eri suureita.
Kuinka todennäköisesti positiivisen tuloksen saanut on sairas? Vastaus
riippuu ratkaisevasti siitä, kuinka yleinen tila on:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="bayes"}
```

```{.tuloste tiedosto="esimerkit/03-bayes-testi.odotettu" rivit="1-3"}
```

Kun esiintyvyys on 1 %, vain kuudesosa positiivisista on sairaita:
harvinaisessa joukossa terveiden väärät positiiviset ovat
lukumääräisesti enemmistö. Laskun näkee helpoimmin lukumäärinä.
Kymmenestätuhannesta testatusta sata on sairaita, ja testi löytää
heistä 99. Terveitä on 9 900, ja heistä 5 % eli 495 saa väärän
positiivisen tuloksen. Positiivisia on yhteensä 594, ja heistä sairaita
$99/594 \approx 0{,}167$.

```{.dot otsikko="Testitulos luonnollisina frekvensseinä, kun esiintyvyys on 1 %. Positiivisista (tummennetut) vain 99 on sairaita."}
digraph {
  nodesep=0.3; ranksep=0.45;
  node [shape=box];
  kaikki [label="10 000 testattua"];
  sairas [label="100 sairasta"]; terve [label="9 900 tervettä"];
  tp [label="99 positiivista", fillcolor="#C9D3D6"];
  fn [label="1 negatiivinen"];
  fp [label="495 positiivista", fillcolor="#C9D3D6"];
  tn [label="9 405 negatiivista"];
  kaikki -> sairas [label="1 %"]; kaikki -> terve [label="99 %"];
  sairas -> tp [label="99 %"]; sairas -> fn [label="1 %"];
  terve -> fp [label="5 %"]; terve -> tn [label="95 %"];
}
```

Simulaatio miljoonasta henkilöstä vahvistaa laskun:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/03-bayes-testi.odotettu" rivit="4-4"}
```

Bayesin kaava on *päivityssääntö*: ennen testiä sairauden
todennäköisyys on esiintyvyys (*priori*), ja testitulos päivittää sen
arvoksi $P(\text{sairas} \mid +)$ (*posteriori*). Sama testi siirtää
arviota eri verran eri lähtötasoilta:

![Positiivisen testituloksen jälkeinen sairauden todennäköisyys
esiintyvyyden funktiona. Pisteet ovat esimerkin kolme lähtötasoa. Jos
ensimmäisen positiivisen tuloksen jälkeen tehdään toinen, riippumaton
testi, lähtötasona on ensimmäisen testin tulos: 1 %:n esiintyvyydestä
päädytään arvoon 0,167 ja sen kohdalta käyrää ylös arvoon
0,80.](kuvat/bayes.png){width=62%}

Sama ilmiö tekee valvontajärjestelmistä meluisia. Hälytin, joka
havaitsee 95 % vioista ja hälyttää turhaan vain 1 %:ssa tunneista,
näyttää hyvältä, mutta jos vika on harvinainen, valtaosa hälytyksistä
on turhia:

```{.python tiedosto="esimerkit/03-bayes-testi.py" osa="halytys"}
```

```{.tuloste tiedosto="esimerkit/03-bayes-testi.odotettu" rivit="5-"}
```

Tämä on *perustason harha* (*base rate fallacy*): todisteen voimaa ei
voi arvioida tuntematta lähtötilannetta.

## Riippumattomuus

Tapahtumat ovat *riippumattomia*, jos $P(A \cap B) = P(A)\,P(B)$:
toisen tapahtuminen ei kerro mitään toisesta. Riippumattomuus tekee
laskuista helppoja, ja siksi se oletetaan usein liian kevyesti.
Kahden palvelimen rinnakkaisjärjestelmä on alhaalla vain, jos
molemmat ovat, mikä riippumattomilla vioilla on harvinaista:

```{.python tiedosto="esimerkit/03-riippumattomuus.py" osa="teoria"}
```

```{.tuloste tiedosto="esimerkit/03-riippumattomuus.odotettu" rivit="1-3"}
```

Todellisuudessa palvelimilla on yhteisiä vikasyitä: sama sähkönsyöttö,
sama verkko, sama ohjelmistoversio. Lisätään simulaatioon harvinainen
sähkökatko, joka kaataa molemmat:

```{.python tiedosto="esimerkit/03-riippumattomuus.py" osa="yhteinen"}
```

```{.tuloste tiedosto="esimerkit/03-riippumattomuus.odotettu" rivit="4-"}
```

Yhteinen vikasyy kasvattaa kahden vian samanaikaisuuden yli
kaksikymmenkertaiseksi, ja kahdennus parantaa saatavuutta vain
vähän. Riippumattomuus on mallin oletus, joka on perusteltava.
Seuraava osio tekee oletuksen tietoisesti, vaikka se ei pidä.

## Naiivi Bayes -luokittelija

Roskapostisuodatin arvioi, kumpaan luokkaan viesti kuuluu sen sanojen
perusteella. *Naiivi* Bayes olettaa sanat toisistaan riippumattomiksi
luokan sisällä, jolloin todennäköisyydet voi kertoa keskenään kuten
edellisessä osiossa:
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
- Osaat tarkistaa riippumattomuuden ja arvioida yhteisen vikasyyn
  vaikutuksen saatavuuteen.
- Osaat toteuttaa naiivin Bayes-luokittelijan logaritmeilla ja
  Laplace-tasoituksella.
