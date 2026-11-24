# Todistaminen ja invariantit

Testi näyttää, että ohjelma toimii kokeilluilla syötteillä. Todistus
näyttää, että se toimii kaikilla. Ohjelmoijan ei tarvitse kirjoittaa
muodollisia todistuksia, mutta todistustekniikat ovat ajattelun
työkaluja: induktio on rekursion ja silmukan oikeellisuuden perustelu,
ja invariantti on paras tapa ymmärtää, miksi algoritmi toimii, ja
huomata, milloin se ei toimi.

## Todistustekniikat

**Suora todistus** etenee oletuksesta johtopäätökseen. Väite ”jos $n$
on pariton, $n^2$ on pariton”: pariton $n = 2k + 1$, joten
$n^2 = 4k^2 + 4k + 1 = 2(2k^2 + 2k) + 1$, joka on pariton.

**Kontrapositio** todistaa väitteen $p \to q$ todistamalla
$\neg q \to \neg p$ (luku *Propositiologiikka*). Väite ”jos $n^2$ on
parillinen, $n$ on parillinen” seuraa edellisestä: jos $n$ ei ole
parillinen, $n^2$ ei ole parillinen.

**Vastaoletus** olettaa väitteen vääräksi ja johtaa ristiriidan.
Klassinen esimerkki: alkulukuja on äärettömän monta. Jos niitä olisi
vain $p_1, \ldots, p_k$, luku $p_1 p_2 \cdots p_k + 1$ ei olisi
jaollinen millään niistä, joten sillä olisi alkutekijä listan
ulkopuolelta.

**Vastaesimerkki** kumoaa yleisen väitteen. Yksikin riittää, ja
ohjelma on niiden etsimisessä erinomainen.

## Induktio

**Matemaattinen induktio** todistaa väitteen $P(n)$ kaikille
luonnollisille luvuilla kahdessa vaiheessa:

1. **Perusaskel**: $P(0)$ pätee.
2. **Induktioaskel**: jos $P(n)$ pätee (induktio-oletus), niin
   $P(n + 1)$ pätee.

Dominoperiaate: ensimmäinen kaatuu, ja jokainen kaatuva kaataa
seuraavan. Esimerkiksi $\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$:
perusaskel $n = 0$ antaa $0 = 0$, ja induktioaskeleessa
$\frac{n(n+1)}{2} + (n + 1) = \frac{(n+1)(n+2)}{2}$.

Ohjelma ei voi tarkistaa äärettömän montaa tapausta, mutta se tarkistaa
tuhat sekunnissa ja paljastaa väärän kaavan heti:

```{.python tiedosto="esimerkit/06-induktio.py" osa="kaavat"}
```

Tarkistuksen ja todistuksen ero näkyy Eulerin polynomissa
$n^2 + n + 41$, joka antaa alkuluvun 40 peräkkäisellä arvolla ja
sitten ei:

```{.python tiedosto="esimerkit/06-induktio.py" osa="vastaesimerkki"}
```

**Vahva induktio** olettaa väitteen kaikille luvuille $k < n$, ei vain
edelliselle. Se sopii väitteisiin, joissa ongelma pilkkoutuu
mielivaltaisen kokoisiin osiin. Jokainen luku $n \ge 2$ on
alkulukujen tulo: joko $n$ on alkuluku, tai $n = ab$, jossa
$a, b < n$, ja induktio-oletus koskee molempia. Rekursiivinen funktio
on tämän todistuksen suora käännös:

```{.python tiedosto="esimerkit/06-induktio.py" osa="vahva"}
```

```{.tuloste tiedosto="esimerkit/06-induktio.odotettu"}
```

Rekursion oikeellisuus todistetaan aina induktiolla: perustapaus on
perusaskel, ja rekursiivinen kutsu pienemmällä syötteellä on
induktio-oletus. Jos rekursio ei pienennä syötettä jonkin hyvin
järjestetyn mitan suhteen, se ei välttämättä pääty.

## Silmukkainvariantit

**Silmukkainvariantti** on väite, joka pätee ennen silmukkaa ja
jokaisen kierroksen jälkeen. Oikeellisuus perustellaan kolmessa
osassa, jotka vastaavat induktiota:

1. **Alustus**: invariantti pätee ennen ensimmäistä kierrosta.
2. **Säilyminen**: jos invariantti pätee ennen kierrosta, se pätee sen
   jälkeen.
3. **Päättyminen**: kun silmukka päättyy, invariantti ja päättymisehto
   yhdessä antavat halutun tuloksen.

Lisäksi tarvitaan **päättymisen perustelu**: jokin luonnollinen luku
pienenee joka kierroksella. Binäärihaku on tunnetusti helppo
kirjoittaa väärin; invariantti tekee sen helpoksi kirjoittaa oikein:

```{.python tiedosto="esimerkit/06-invariantti.py" osa="binaarihaku"}
```

Invariantti kertoo suoraan, miten raja päivitetään: jos
`lista[keski] < arvo`, keski ja kaikki sitä vasemmalla ovat alle
arvon, joten `ala = keski + 1` säilyttää invariantin. Päättyessä
`ala == yla`, joten vasemmalla on vain pienempiä ja oikealla vain
suurempia tai yhtä suuria: vastaus on `ala`. Ilman invarianttia
rajojen `+1`-yksityiskohdat ovat arvailua.

`assert`-lauseet tarkistavat invariantin testiajossa. Ne tekevät
binäärihausta lineaarisen, joten tuotantokoodiin ne eivät kuulu, mutta
kehityksessä ja testeissä ne paljastavat virheen heti kun invariantti
rikkoutuu. Toinen esimerkki on nopea potenssiin korotus, jonka
invariantti $\mathit{tulos} \cdot k^e = \mathit{kanta}^{\mathit{eksponentti}}$
selittää koko algoritmin:

```{.python tiedosto="esimerkit/06-invariantti.py" osa="potenssi"}
```

```{.tuloste tiedosto="esimerkit/06-invariantti.odotettu"}
```

Joka kierroksella $e$ puolittuu, joten kierroksia on noin
$\log_2(\mathit{eksponentti})$. Sama algoritmi laskee
modulaaripotenssit kryptografiassa (luku *Modulaariaritmetiikka*).

## Käytännössä

- **Kirjoita invariantti kommenttiin ennen silmukkaa.** Se on
  silmukan tärkein dokumentaatio ja ohjaa rajojen päivitystä.
  Silmukka, jonka invarianttia et osaa sanoa, on todennäköisesti väärin.
- **Tarkista invariantti testeissä.** `assert` tai erillinen
  tarkistusfunktio kehitysajossa löytää virheet, joita esimerkkitestit
  eivät löydä.
- **Perustele päättyminen.** Nimeä luku, joka pienenee joka
  kierroksella ja jolla on alaraja. Rekursiossa se on syötteen koko.
- **Käytä ominaisuustestausta.** Kun väite koskee kaikkia syötteitä,
  generoi syötteet (esim. Hypothesis-kirjasto Pythonissa) sen sijaan,
  että kirjoitat muutaman esimerkin käsin.
- **Muista, että esimerkit eivät todista.** 40 onnistunutta tapausta
  ei takaa 41. Tarkistus löytää vastaesimerkkejä; vain päättely kattaa
  kaikki tapaukset.

## Itsearviointi

- Osaat käyttää suoraa todistusta, kontrapositiota ja vastaoletusta
  yksinkertaisiin väitteisiin.
- Osaat todistaa summakaavan tai rekursiivisen funktion oikeellisuuden
  induktiolla ja vahvalla induktiolla.
- Osaat muotoilla silmukkainvariantin ja perustella sillä silmukan
  oikeellisuuden ja päättymisen.
- Osaat tarkistaa invariantin ja väitteen ohjelmallisesti ja tiedät,
  mitä tarkistus todistaa ja mitä ei.
