# Rekursio ja rekursioyhtälöt

Rekursiivinen määritelmä kuvaa asian sen pienempien tapausten avulla:
Fibonaccin luku on kahden edellisen summa, lista on tyhjä tai alkio ja
lista. Rekursiivinen algoritmi pilkkoo tehtävän pienemmiksi samanlaisiksi
tehtäviksi. Rekursioyhtälö kertoo, paljonko työtä pilkkominen maksaa,
ja sen ratkaisu on algoritmin aikavaativuus. Luku käyttää edellisen
luvun induktiota (rekursion oikeellisuus) ja luvun *Joukot ja
funktiot* kertaluokkamerkintöjä $O$ ja $\Theta$ (rekursion hinta).

## Rekursiivinen määritelmä ja hinta

Fibonaccin luvut määritellään $F(0) = 0$, $F(1) = 1$ ja
$F(n) = F(n-1) + F(n-2)$. Määritelmän suora käännös on oikein mutta
hidas:

```{.python tiedosto="esimerkit/07-fibonacci.py" osa="naiivi"}
```

Kutsujen määrä $K(n)$ toteuttaa oman rekursioyhtälönsä:
$K(n) = K(n-1) + K(n-2) + 1$, ja sen ratkaisu on $K(n) = 2F(n+1) - 1$.
Funktio siis tekee yhtä monta kutsua kuin sen tulos on suuri, ja
$F(n)$ kasvaa kuin $\varphi^n$, jossa $\varphi = (1 + \sqrt{5})/2
\approx 1{,}618$ on kultainen leikkaus.

```{.python tiedosto="esimerkit/07-fibonacci.py" osa="kutsut"}
```

```{.tuloste tiedosto="esimerkit/07-fibonacci.odotettu" rivit="1-3"}
```

Hitaus johtuu siitä, että samat osatehtävät lasketaan uudelleen ja
uudelleen: $F(n-2)$ lasketaan sekä suoraan että $F(n-1)$:n sisällä.
Kutsupuusta sen näkee suoraan:

```{.dot otsikko="Kutsun fib_naiivi(5) kutsupuu: 15 kutsua. Tummennettu alipuu F(3) lasketaan kahdesti ja F(2) kolmesti."}
digraph {
  nodesep=0.12; ranksep=0.3;
  node [shape=box, fontsize=9, height=0.25, width=0.4];
  edge [arrowsize=0.5];
  a [label="F(5)"]; b [label="F(4)"]; c [label="F(3)", fillcolor="#C9D3D6"];
  d [label="F(3)", fillcolor="#C9D3D6"]; e [label="F(2)"];
  f [label="F(2)"]; g [label="F(1)"]; h [label="F(2)"]; i [label="F(1)"];
  j [label="F(1)"]; k [label="F(0)"]; l [label="F(1)"]; m [label="F(0)"];
  n [label="F(1)"]; o [label="F(0)"];
  a -> b; a -> c; b -> d; b -> e; c -> f; c -> g;
  d -> h; d -> i; e -> j; e -> k; f -> l; f -> m; h -> n; h -> o;
}
```

Kun osatulokset muistetaan, jokainen arvo lasketaan kerran ja työ
putoaa lineaariseksi. Tämä on **dynaamisen ohjelmoinnin** ydin, ja se
käsitellään taidossa *Algoritmit*. Muistava rekursio etenee ylhäältä
alas: se lähtee arvosta $F(n)$ ja laskeutuu perustapauksiin. Silmukka
laskee samat arvot alhaalta ylös, perustapauksista kohti arvoa $F(n)$,
eikä tarvitse pinoa:

```{.python tiedosto="esimerkit/07-fibonacci.py" osa="nopeat"}
```

## Suljettu muoto

Lineaarisen rekursioyhtälön voi ratkaista suljettuun muotoon.
Fibonaccin yhtälön karakteristinen yhtälö $x^2 = x + 1$ antaa juuret
$\varphi$ ja $\psi = (1 - \sqrt{5})/2$, ja

$$F(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}}.$$

Kaava on matemaattisesti tarkka mutta liukuluvuilla ei: kun $F(n)$
ylittää liukuluvun 53 bitin tarkkuuden, pyöristys antaa väärän luvun.
Kokonaislukulaskenta on Pythonissa rajoittamattoman tarkkaa, joten
silmukka on sekä nopea että oikein:

```{.python tiedosto="esimerkit/07-fibonacci.py" osa="binet"}
```

```{.tuloste tiedosto="esimerkit/07-fibonacci.odotettu" rivit="4-"}
```

## Rekursiosyvyys

Jokainen rekursiivinen kutsu varaa pinokehyksen. Pythonin oletusraja on
noin tuhat kehystä, ja syvempi rekursio kaatuu:

```{.python tiedosto="esimerkit/07-syvyys.kaatuu.py" osa="syvyys"}
```

```{.tuloste tiedosto="esimerkit/07-syvyys.virhe"}
```

Monissa funktionaalisissa kielissä häntärekursio optimoidaan
silmukaksi (taito *Funktionaalinen ohjelmointi (Racket)*), mutta Python ja
useimmat valtavirtakielet eivät tee niin. Rekursio, jonka syvyys
kasvaa syötteen mukana lineaarisesti, kirjoitetaan silmukaksi tai
eksplisiittisellä pinolla. Rekursio, jonka syvyys on logaritminen
(tasapainoinen puu, puolitus), on turvallinen.

## Hajota ja hallitse

**Hajota ja hallitse** (*divide and conquer*) jakaa syötteen
$b$ osaan, ratkaisee $a$ osatehtävää rekursiivisesti ja yhdistää
tulokset. Sen aikavaativuus toteuttaa yhtälön

$$T(n) = a\, T(n/b) + f(n),$$

jossa $f(n)$ on jakamisen ja yhdistämisen työ. Lomituslajittelu jakaa
listan kahtia ($a = b = 2$) ja lomittaa lineaarisessa ajassa:

```{.python tiedosto="esimerkit/07-hajota.py" osa="lomitus"}
```

Yhtälö $T(n) = 2T(n/2) + n$ ratkeaa **rekursiopuulla**: tasoja on
$\log_2 n$, ja jokaisella tasolla lomitetaan yhteensä $n$ alkiota,
joten $T(n) = \Theta(n \log n)$.

```{.dot otsikko="Lomituslajittelun rekursiopuu, kun n = 8. Solmussa on osatehtävän koko; jokaisen tason lomitustyö on yhteensä n."}
digraph {
  nodesep=0.15; ranksep=0.3;
  node [shape=box, fontsize=9, height=0.25, width=0.35];
  edge [arrowsize=0.5];
  a [label="8"]; b1 [label="4"]; b2 [label="4"];
  c1 [label="2"]; c2 [label="2"]; c3 [label="2"]; c4 [label="2"];
  d1 [label="1"]; d2 [label="1"]; d3 [label="1"]; d4 [label="1"];
  d5 [label="1"]; d6 [label="1"]; d7 [label="1"]; d8 [label="1"];
  a -> b1; a -> b2; b1 -> c1; b1 -> c2; b2 -> c3; b2 -> c4;
  c1 -> d1; c1 -> d2; c2 -> d3; c2 -> d4;
  c3 -> d5; c3 -> d6; c4 -> d7; c4 -> d8;
  node [shape=plaintext, style="", width=0];
  t0 [label="1 · 8 = n"]; t1 [label="2 · 4 = n"];
  t2 [label="4 · 2 = n"]; t3 [label="perustapaukset"];
  edge [style=invis];
  t0 -> t1 -> t2 -> t3;
  { rank=same; a; t0; } { rank=same; b2; t1; }
  { rank=same; c4; t2; } { rank=same; d8; t3; }
}
```

Mittaus vahvistaa kertaluokan: vertailujen määrän suhde lukuun
$n \log_2 n$ pysyy rajoitettuna.

```{.python tiedosto="esimerkit/07-hajota.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/07-hajota.odotettu" rivit="1-4"}
```

## Master-lause

Master-lause ratkaisee yhtälön $T(n) = a\,T(n/b) + \Theta(n^d)$
vertaamalla yhdistämistyötä $n^d$ ja osatehtävien määrän kasvua
$n^{\log_b a}$:

| Tapaus | Ehto | Ratkaisu | Mikä hallitsee |
|--------|------|----------|----------------|
| 1 | $d < \log_b a$ | $\Theta(n^{\log_b a})$ | lehtien määrä |
| 2 | $d = \log_b a$ | $\Theta(n^d \log n)$ | kaikki tasot yhtä paljon |
| 3 | $d > \log_b a$ | $\Theta(n^d)$ | juuren työ |

```{.python tiedosto="esimerkit/07-hajota.py" osa="master"}
```

```{.tuloste tiedosto="esimerkit/07-hajota.odotettu" rivit="5-"}
```

Taulukko selittää kuuluisia algoritmeja: Karatsuba kertoo kaksi
$n$-numeroista lukua kolmella puolikkaan kokoisella kertolaskulla
neljän sijaan ja saa vaativuuden $n^{1{,}58}$ koulumenetelmän $n^2$:n
sijaan. Strassen tekee saman matriiseille. Yksi rekursiivinen
kutsu vähemmän muuttaa eksponenttia, mikä on hajota ja hallitse
-suunnittelun ydinoivallus. Algoritmien analyysi jatkuu taidossa
*Algoritmit*.

## Käytännössä

- **Kirjoita rekursio ensin määritelmän mukaan, optimoi sitten.**
  Suora käännös on helppo todistaa oikeaksi; muistaminen tai silmukka
  tehdään vasta, kun hinta tiedetään, ja niitä verrataan suoraan
  versioon.
- **Muista osatulokset, kun osatehtävät toistuvat.** `functools.cache`
  muuttaa eksponentiaalisen rekursion usein lineaariseksi. Huomaa, että
  välimuisti kasvaa ja argumenttien on oltava hajautettavia.
- **Tarkista rekursiosyvyys.** Syötteen mukana lineaarisesti kasvava
  rekursio kaatuu Pythonissa noin tuhannessa tasossa. Muuta se
  silmukaksi tai käytä eksplisiittistä pinoa.
- **Analysoi rekursiopuulla.** Piirrä tasot, laske työ tasoa kohden ja
  tasojen määrä. Master-lause on oikotie, mutta puu kertoo, miksi.
- **Älä luota suljetun muodon liukulukulaskentaan.** Kokonaislukujen
  kaavat lasketaan kokonaisluvuilla; liukuluvut hukkaavat tarkkuuden
  hiljaa (taito *Miten tietokone laskee*).

## Itsearviointi

- Osaat kirjoittaa rekursiivisen määritelmän ohjelmaksi ja muodostaa
  rekursioyhtälön sen kutsujen määrälle tai työlle.
- Osaat selittää, miksi naiivi Fibonacci on eksponentiaalinen ja miten
  muistaminen tekee siitä lineaarisen.
- Osaat ratkaista hajota ja hallitse -yhtälön rekursiopuulla ja
  master-lauseella.
- Osaat tunnistaa rekursiosyvyyden rajoittaman funktion ja muuttaa sen
  silmukaksi.
