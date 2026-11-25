# Yhteen- ja kertolasku

Kiinteän pilkun yhteen- ja kertolasku ovat tavallista
kokonaislukuaritmetiikkaa. Uutta on vain kirjanpito: mikä on tuloksen
muoto, ja montako bittiä tulos tarvitsee. Laitteistossa jokainen bitti
on johdin, rekisterin kiikku ja summaimen solu, joten leveydet
lasketaan tarkasti eikä varmuuden vuoksi.

## Bittikasvu

Kahden $n$-bittisen etumerkillisen luvun summa tarvitsee $n+1$ bittiä,
koska $(-2^{n-1}) + (-2^{n-1}) = -2^n$. Tulo tarvitsee $2n$ bittiä,
mutta vain yhden kulmatapauksen takia: $(-2^{n-1})^2 = 2^{2n-2}$ on ainoa
tulo, joka ei mahdu $2n-1$ bittiin. Säännöt kannattaa tarkistaa
tyhjentävästi pienillä leveyksillä:

```{.python tiedosto="esimerkit/03-bittikasvu.py" osa="tarve"}
```

```{.python tiedosto="esimerkit/03-bittikasvu.py" osa="tarkistus"}
```

Murtobitit kasvavat samalla tavalla. Summan murtobittejä on yhtä monta
kuin yhteenlaskettavilla (kun pilkut on kohdistettu), tulon murtobitit
ovat tekijöiden murtobittien summa. Yleiset säännöt:

| Operaatio | Tuloksen muoto |
|-----------|----------------|
| Qa.b + Qa.b | Q(a+1).b |
| Qa.b × Qc.d | Q(a+c).(b+d) |
| $K$ kappaletta Qa.b summattuna | Q(a + $\lceil \log_2 K \rceil$).b |
| UQa.b × Qc.d | Q(a+c).(b+d) |
| UQa.b + Qc.b | Q(max(a+1, c) + 1).b |

Kaksi viimeistä riviä koskevat etumerkittömän ja etumerkillisen luvun
sekoittamista, joka on RTL-koodin tavallisimpia virhelähteitä.
Etumerkitön luku ei ole etumerkillinen luku, jonka ylin bitti sattuu
olemaan nolla: UQ8.0-arvo 200 on kahdeksanbittisenä etumerkillisenä
−56. Ennen kuin etumerkitön operandi yhdistetään etumerkilliseen, se
levennetään yhdellä nollabitillä etumerkilliseksi (UQa.b → Q(a+1).b), ja
vasta sitten sovelletaan tavallisia sääntöjä. Tulossa lisäbitti ei näy
lopputuloksen leveydessä, koska etumerkittömän operandin suurin arvo on
positiivinen:

```{.python tiedosto="esimerkit/03-bittikasvu.py" osa="sekamuodot"}
```

```{.tuloste tiedosto="esimerkit/03-bittikasvu.odotettu" alkaen="UQ4 ja Q4"}
```

## Kertolasku ja paluu alkuperäiseen muotoon

Q1.15 × Q1.15 on Q2.30, 32-bittinen tulo. Takaisin Q1.15-muotoon
päästään pudottamalla 15 alinta bittiä (pyöristäen) ja ylin bitti, joka
on yhtä kuin etumerkkibitti kaikissa paitsi kulmatapauksessa $-1 \times -1$.
Pyöristystavat ovat luvun 4 ja saturaatio luvun 5 aihe; tässä riittää,
että pyöristys valitsee lähimmän koodin ja saturaatio leikkaa tuloksen
alueen rajaan.

![Tulon bittikentät. Binääripilkku on kahden ylimmän bitin jälkeen.
Q1.15-tulos on bitit 30…15: alimmat 15 bittiä pyöristetään pois, ja
ylin bitti on etumerkin kopio aina paitsi tulossa
$-1 \times -1$.](kuvat/tulo.png){width=100%}

```{.c tiedosto="esimerkit/03-kertolasku.c" osa="kerto"}
```

```{.c tiedosto="esimerkit/03-kertolasku.c" osa="kokeet"}
```

```{.tuloste tiedosto="esimerkit/03-kertolasku.odotettu"}
```

Laajennus `(int32_t)a` on C:ssä tärkeä. Ilman sitä `int16_t`-arvot
korotettaisiin `int`-tyyppiin, joka sattuu olemaan 32-bittinen useimmilla
alustoilla, mutta Q1.31 × Q1.31 -tapauksessa vastaava virhe johtaisi
32-bittiseen tuloon ja ylivuotoon. Laitteistossa vastaava valinta on
kertojan leveys: 16 × 16 -kertoja tuottaa 32 bittiä.

Kulmatapaus $-1 \times -1 = +1$ on DSP-laitteistoissa niin tavallinen
ongelma, että monissa niistä on erityinen tila, joka saturoi juuri sen.
Toinen ratkaisu on sopia, ettei −1 koskaan esiinny, eli rajata kertoimet
ja signaalit symmetrisesti välille $[-1 + 2^{-15}, 1 - 2^{-15}]$.

## Kertymät ja vartijabitit

Suodattimet, korrelaatiot ja matriisitulot laskevat tulojen summia:
kertolasku ja kertymä (*multiply-accumulate*, MAC). $K$ tulon summa
tarvitsee tulon leveyden lisäksi $\lceil \log_2 K \rceil$ *vartijabittiä*
(*guard bits*):

```{.python tiedosto="esimerkit/03-bittikasvu.py" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/03-bittikasvu.odotettu" alkaen="K=    2" asti="K= 1000"}
```

Sääntö on yläraja. Se on tarkka kahden potenssin $K$:lla, mutta muuten
tarvitaan joskus bitti vähemmän. Tästä syystä klassiset DSP-suorittimet
käyttävät 40-bittistä kertymää: 32-bittiseen Q2.30-tuloon 8 vartijabittiä,
jotka riittävät 256 täyden skaalan tulon summaan. Ilman vartijabittejä
kertymä vuotaa yli jo muutaman tulon jälkeen:

```{.c tiedosto="esimerkit/03-kertyma.c" osa="kertyma"}
```

```{.tuloste tiedosto="esimerkit/03-kertyma.odotettu"}
```

Todellisissa signaaleissa kaikki tulot eivät ole täyttä skaalaa, joten
tarkka tarve riippuu kertoimista. FIR-suodattimen pahin tapaus on
$\sum_k |h_k|$ kerrottuna syötteen suurimmalla arvolla. Tämä
$\ell_1$-normi on usein selvästi pienempi kuin kertoimien määrä, joten
vartijabittejä tarvitaan vähemmän kuin $\lceil \log_2 K \rceil$.

Koko MAC-datapolku kannattaa piirtää niin, että jokaisen johtimen muoto
on näkyvissä. Kaaviosta näkee yhdellä silmäyksellä, missä bitit kasvavat
ja missä ainoa kavennus tehdään:

```{.dot otsikko="Kuudentoista tulon MAC-datapolku muotoineen. Kertymä kiertää rekisterin kautta täydellä leveydellä; pyöristys ja saturaatio tehdään kerran, kun tulos lähtee datapolulta."}
digraph {
  rankdir=LR;
  node [shape=box];
  x [label="näyte x", shape=plaintext];
  h [label="kerroin h", shape=plaintext];
  kerto [label="×"];
  summa [label="+"];
  rek [label="kertymä-\nrekisteri"];
  kav [label="pyöristys ja\nsaturaatio"];
  y [label="tulos y", shape=plaintext];
  x -> kerto [label="Q1.15"];
  h -> kerto [label="Q1.15"];
  kerto -> summa [label="Q2.30\n32 b."];
  summa -> rek [label="Q6.30\n36 b."];
  rek -> summa [label="Q6.30", constraint=false];
  rek -> kav [label="Q6.30"];
  kav -> y [label="Q1.15"];
}
```

## Jakolasku ja skaalaus vakiolla

Yleinen jakaja on laitteistossa kallis ja hidas: se tuottaa bitin
kellojaksossa tai vaatii kertojia ja iteraatioita. Datapoluissa jako on
kuitenkin lähes aina jako *vakiolla* (keskiarvo, normalisointi,
yksikkömuunnos), ja se tehdään kertomalla vakion käänteisluvulla, joka
on laskettu etukäteen kiinteän pilkun koodiksi. Jako luvulla $d$ on
kertolasku koodilla $\lceil 2^n / d \rceil$ ja siirto $n$ bittiä
oikealle:

```{.python tiedosto="esimerkit/03-jako.py" osa="kaanteisluku"}
```

Käänteisluku ei yleensä ole tarkka (1/10 on binäärilukuna päättymätön),
joten kysymys on, montako murtobittiä tarvitaan, jotta tulos on *sama*
kuin tarkka kokonaislukujako jokaisella syötteellä. Pienellä leveydellä
sen voi tarkistaa tyhjentävästi, kuten bittikasvun säännöt:

```{.python tiedosto="esimerkit/03-jako.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/03-jako.odotettu" asti="oikein kaikilla"}
```

Kuusitoistabittisen luvun jako kymmenellä on siis kertolasku
16-bittisellä vakiolla `0xcccd` ja 19 bitin siirto. Kolme bittiä
vähemmän antaa väärän tuloksen lähes kymmenelletuhannelle syötteelle,
ja virheet alkavat vasta suurista luvuista, joten satunnainen testi
pienillä arvoilla ei löydä niitä. Kääntäjät tekevät saman muunnoksen
ohjelmistossa (taito *Miten tietokone laskee*).

Kun tulos saa olla likiarvo, kuten signaalin skaalauksessa, vakio
pyöristetään lähimpään koodiin ja kertolaskun tulos kavennetaan kuten
mikä tahansa tulo:

```{.python tiedosto="esimerkit/03-jako.py" osa="skaalaus"}
```

```{.tuloste tiedosto="esimerkit/03-jako.odotettu" alkaen="1/3 ="}
```

Suhteellinen virhe on enintään puoli koodin LSB:tä suhteessa vakioon,
tässä $3 \cdot 10^{-5}$. Jos jakaja ei ole vakio, jako pyritään
poistamaan algoritmista (vertaillaan $a < b \cdot c$ eikä $a / b < c$)
tai tehdään hitaalla iteratiivisella jakajalla sivussa datapolusta.

## Käytännössä

- **Laske leveydet koko datapolulle.** Lohkokaavioon merkitään jokaisen
  summaimen ja kertojan tulon muoto bittikasvun sääntöjen mukaan. Vasta
  sitten päätetään, mihin kohtiin tulee pyöristys ja saturaatio.
- **Älä pyöristä kesken kertymän.** Tulot kerätään täyteen leveyteen
  vartijabitteineen, ja pyöristys tehdään kerran lopuksi. Jokainen
  välipyöristys lisää kohinaa.
- **Mitoita vartijabitit kertoimien normilla.** $\lceil \log_2 \sum_k
  |h_k| \rceil$ riittää, jos syöte pysyy alueellaan. Varmuusmarginaali
  dokumentoidaan.
- **Käsittele $-1 \times -1$.** Joko saturoi, rajaa −1 pois tai varaa
  ylimääräinen kokonaisbitti. Kulmatapaus löytyy testeissä vain, jos se
  testataan erikseen.
- **Levennä etumerkitön ennen kuin sekoitat.** Etumerkitön operandi
  saa nollabitin eteensä ja muuttuu etumerkilliseksi, ennen kuin se
  kohtaa etumerkillisen. RTL:ssä yksikin etumerkitön operandi tekee
  koko lausekkeesta etumerkittömän.
- **Jaa vakiolla kertomalla.** Käänteisluvun koodi lasketaan
  suunnitteluvaiheessa, ja sen leveys varmistetaan tyhjentävällä
  testillä tai virherajalla.

## Itsearviointi

- Osaat laskea summan, tulon ja $K$ tulon kertymän muodon ja leveyden.
- Osaat palauttaa Q1.15-tulon Q1.15-muotoon ja käsitellä tapauksen
  $-1 \times -1$.
- Osaat mitoittaa kertymän vartijabitit sekä tulojen määrän että
  kertoimien $\ell_1$-normin perusteella.
- Osaat selittää, miksi DSP-suorittimissa on 40-bittinen kertymä.
- Osaat laskea tuloksen muodon, kun etumerkitön ja etumerkillinen luku
  lasketaan yhteen tai kerrotaan.
- Osaat korvata vakiolla jakamisen kertolaskulla ja siirrolla ja
  tarkistaa, että käänteisluvun leveys riittää.
