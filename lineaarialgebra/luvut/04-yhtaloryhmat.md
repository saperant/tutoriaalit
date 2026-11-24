# Lineaariset yhtälöryhmät

Lineaarinen yhtälöryhmä on joukko yhtälöitä, joissa tuntemattomat
esiintyvät vain ensimmäisessä potenssissa:

$$\begin{aligned}
15 i_1 - 5 i_2 &= 12 \\
-5 i_1 + 20 i_2 - 10 i_3 &= 0 \\
-10 i_2 + 25 i_3 &= 5
\end{aligned}$$

Matriisimuodossa se on $Ax = b$: kertoimet ovat matriisi $A$,
tuntemattomat vektori $x$ ja oikeat puolet vektori $b$. Tällaisia
ryhmiä syntyy kaikkialla: virtapiirit (Kirchhoffin lait), rakenteiden
voimat, sekoitussuhteet, lämmön ja jännityksen jakaumat, kalibrointi
ja interpolointi. Suurissa simulaatioissa yhtälöitä on miljoonia.

Geometrisesti kahden tuntemattoman yhtälö on suora ja kolmen taso.
Ratkaisu on suorien tai tasojen leikkauspiste. Toinen tulkinta on
sarakkeittainen: ratkaisu $x$ kertoo, millä kertoimilla $A$:n sarakkeet
yhdistetään, jotta saadaan $b$.

## Gaussin eliminointi

Gaussin eliminointi muuttaa ryhmän **yläkolmiomuotoon** vähentämällä
rivien monikertoja toisistaan. Rivioperaatiot eivät muuta ratkaisua:
yhtälön monikerran lisääminen toiseen yhtälöön säilyttää kaikki
ratkaisut. Kolmiomuodosta ratkaisu saadaan **takaisinsijoituksella**:
viimeinen yhtälö sisältää vain yhden tuntemattoman, toiseksi viimeinen
kaksi, joista toinen jo tiedetään, ja niin edelleen.

Jokaisessa vaiheessa valitaan **tukialkio** (*pivot*), jolla muut rivit
nollataan. **Osittaistuenta** valitsee tukialkioksi sarakkeen
itseisarvoltaan suurimman alkion ja vaihtaa sen rivin ylös. Ilman sitä
pieni tukialkio tuottaa valtavia kertoimia, ja pyöristysvirhe tuhoaa
tuloksen (luku 12).

```{.python tiedosto="esimerkit/04-gauss.py" osa="gauss"}
```

Esimerkkinä kolmen silmukan virtapiiri. Kunkin silmukan jännitteiden
summa on nolla, mikä antaa yhden yhtälön silmukkaa kohti:

```{.python tiedosto="esimerkit/04-gauss.py" osa="piiri"}
```

```{.tuloste tiedosto="esimerkit/04-gauss.odotettu"}
```

Eliminointi tekee noin $\tfrac{2}{3} n^3$ laskutoimitusta. Sadan
tuntemattoman ryhmä on mikrosekuntien asia, mutta tuhannen ryhmä
puhtaalla Pythonilla kestää jo minuutteja. NumPyn
`np.linalg.solve` käyttää LAPACK-kirjastoa ja on satoja kertoja
nopeampi.

## Astevaltaisuus ja ratkaisujen määrä

Yhtälöryhmällä on joko yksi ratkaisu, ei yhtään ratkaisua tai
äärettömästi ratkaisuja. Mikään muu ei ole mahdollista: jos ratkaisuja
on kaksi, niiden kaikki painotetut keskiarvot ovat myös ratkaisuja.

Ratkaisevaa on matriisin **aste** (*rank*): lineaarisesti
riippumattomien rivien (tai yhtä hyvin sarakkeiden) määrä. Se nähdään
**porrasmuodosta**, joka saadaan jatkamalla eliminointia: aste on
tukialkioiden määrä. Kun $A$:n aste on $r$ ja tuntemattomia on $n$:

- jos laajennetun matriisin $[A \mid b]$ aste on suurempi kuin $r$,
  yhtälöt ovat ristiriitaisia, eikä ratkaisua ole;
- jos asteet ovat samat ja $r = n$, ratkaisu on yksikäsitteinen;
- jos asteet ovat samat ja $r < n$, ratkaisuja on äärettömästi, ja
  $n - r$ muuttujaa voi valita vapaasti.

Aste lasketaan tässä tarkoilla murtoluvuilla (`fractions.Fraction`),
koska liukuluvuilla "nolla" on harvoin täsmälleen nolla, ja raja
nollan ja pienen luvun välillä on numeerinen valinta (luku 12).

```{.python tiedosto="esimerkit/04-aste.py" osa="porras"}
```

```{.python tiedosto="esimerkit/04-aste.py" osa="luokittelu"}
```

```{.tuloste tiedosto="esimerkit/04-aste.odotettu"}
```

Esimerkin kolmas yhtälö on kahden ensimmäisen summa, joten se ei tuo
uutta tietoa. Jos oikea puoli noudattaa samaa riippuvuutta, ratkaisuja
on äärettömästi; jos ei, yhtälöt ovat ristiriidassa.

Insinöörityössä yhtälöitä on usein enemmän kuin tuntemattomia, ja ne
ovat mittausvirheen takia hieman ristiriitaisia. Silloin ratkaisua
ei ole, ja haetaan paras likiratkaisu (luku 9).

## Käytännössä

- **Käytä `np.linalg.solve`a.** Oma eliminointi on opetusväline;
  kirjasto käyttää osittaistuentaa, lohkottua laskentaa ja tarkistaa
  singulaarisuuden.
- **Älä vertaa liukulukua nollaan.** Singulaarisuutta ei tunnista
  ehdolla `== 0`. Käytä toleranssia, joka on suhteessa matriisin
  suuruuteen, tai kuntolukua (luku 12).
- **Käytä tarkkoja lukuja, kun data on tarkkaa.** Kokonais- ja
  murtolukukertoimilla (stoikiometria, kombinatoriikka) `Fraction` tai
  SymPy antaa tarkan asteen ja tarkan ratkaisun.
- **Tarkista ratkaisu jäännöksellä.** $\lVert Ax - b \rVert$ on halpa
  laskea, ja se paljastaa virheellisen mallin tai huonon ratkaisun.
- **Mallinna suureet johdonmukaisin yksiköin.** Kun yhtälöissä on
  ohmeja ja kilo-ohmeja sekaisin, kertoimet ovat eri kokoluokkaa, ja
  numeerinen tarkkuus kärsii.

## Itsearviointi

- Osaat kirjoittaa yhtälöryhmän matriisimuotoon $Ax = b$.
- Osaat toteuttaa Gaussin eliminoinnin osittaistuennalla ja
  takaisinsijoituksella.
- Osaat määrittää matriisin asteen porrasmuodosta ja päätellä siitä,
  onko ratkaisuja yksi, ei yhtään vai äärettömästi.
- Osaat arvioida eliminoinnin työmäärän ja valita kirjastofunktion
  tuotantokäyttöön.
