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

## Kertolasku ja paluu alkuperäiseen muotoon

Q1.15 × Q1.15 on Q2.30, 32-bittinen tulo. Takaisin Q1.15-muotoon
päästään pudottamalla 15 alinta bittiä (pyöristäen) ja ylin bitti, joka
on yhtä kuin etumerkkibitti kaikissa paitsi kulmatapauksessa $-1 \times -1$:

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

```{.tuloste tiedosto="esimerkit/03-bittikasvu.odotettu"}
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

## Itsearviointi

- Osaat laskea summan, tulon ja $K$ tulon kertymän muodon ja leveyden.
- Osaat palauttaa Q1.15-tulon Q1.15-muotoon ja käsitellä tapauksen
  $-1 \times -1$.
- Osaat mitoittaa kertymän vartijabitit sekä tulojen määrän että
  kertoimien $\ell_1$-normin perusteella.
- Osaat selittää, miksi DSP-suorittimissa on 40-bittinen kertymä.
