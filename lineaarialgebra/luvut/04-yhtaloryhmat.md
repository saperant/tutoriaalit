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
yhdistetään, jotta saadaan $b$. Luku etenee ratkaisumenetelmästä
(Gaussin eliminointi) kysymykseen, milloin ratkaisu on olemassa ja
yksikäsitteinen (aste), ja lopuksi siihen, kuinka paljon ratkaisuun voi
luottaa, kun kertoimissa on virhettä (ehtoluku).

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
tuloksen (esimerkki luvussa *Numeeriset näkökohdat*).

```{.python tiedosto="esimerkit/04-gauss.py" osa="gauss"}
```

Esimerkkinä kolmen silmukan virtapiiri. Kunkin silmukan jännitteiden
summa on nolla, mikä antaa yhden yhtälön silmukkaa kohti:

```{.python tiedosto="esimerkit/04-gauss.py" osa="piiri"}
```

```{.tuloste tiedosto="esimerkit/04-gauss.odotettu"}
```

Eliminointi tekee noin $\tfrac{2}{3} n^3$ laskutoimitusta, joten
tuntemattomien määrän kymmenkertaistaminen tuhatkertaistaa työn.
Yllä oleva puhtaan Pythonin toteutus ratkaisee sadan tuntemattoman
ryhmän sekunnin sadasosissa, mutta tuhannen tuntemattoman ryhmään
kuluu jo kymmeniä sekunteja. NumPyn `np.linalg.solve` käyttää
LAPACK-kirjastoa ja on satoja kertoja nopeampi: sata tuntematonta
ratkeaa alle millisekunnissa ja tuhat sekunnin sadasosissa.

## Astevaltaisuus ja ratkaisujen määrä

Yhtälöryhmällä on joko yksi ratkaisu, ei yhtään ratkaisua tai
äärettömästi ratkaisuja. Mikään muu ei ole mahdollista: jos ratkaisuja
on kaksi, niiden kaikki painotetut keskiarvot ovat myös ratkaisuja.

![Kahden tuntemattoman yhtälöpari: suorat leikkaavat yhdessä
pisteessä, ovat yhdensuuntaiset tai ovat sama
suora.](kuvat/suorat.png){width=95%}

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
nollan ja pienen luvun välillä on numeerinen valinta (luku
*Singulaariarvohajotelma*).

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
ei ole, ja haetaan paras likiratkaisu (luku *Pienimmän neliösumman
sovitus*).

## Herkkyys ja ehtoluku

Yksikäsitteinenkään ratkaisu ei aina ole luotettava. Kertoimet ja
oikeat puolet ovat mittauksia tai pyöristettyjä lukuja, ja kysymys on,
kuinka paljon pieni virhe niissä siirtää ratkaisua. Geometrisesti
vastaus riippuu suorien välisestä kulmasta: kohtisuorien suorien
leikkauspiste siirtyy yhtä vähän kuin suora, mutta lähes
yhdensuuntaisten suorien leikkauspiste liukuu kauas.

```{.python tiedosto="esimerkit/04-ehtoluku.py" osa="herkkyys"}
```

```{.tuloste tiedosto="esimerkit/04-ehtoluku.odotettu"}
```

![Toista suoraa siirretään saman verran (katkoviiva). Kohtisuorien
suorien leikkauspiste (musta → valkoinen) tuskin liikkuu, lähes
yhdensuuntaisten siirtyy kauas. Kuvassa suorien kulmaero on
tuhatkertainen esimerkkiin verrattuna, jotta suorat erottuvat
toisistaan; siksi kuvan ehtoluku on 42 eikä
40 002.](kuvat/ehtoluku.png){width=88%}

Matriisin **ehtoluku** $\kappa(A)$ (*condition number*; myös nimitystä
kuntoluku käytetään) mittaa tämän herkkyyden: se kertoo, kuinka
moninkertaiseksi syötteen suhteellinen virhe voi pahimmillaan kasvaa
ratkaisussa,

$$\frac{\lVert \Delta x \rVert}{\lVert x \rVert} \le \kappa(A)\,
  \frac{\lVert \Delta b \rVert}{\lVert b \rVert}.$$

Pienin mahdollinen arvo on 1, ja singulaarisen matriisin ehtoluku on
ääretön. Matriisia, jonka ehtoluku on suuri, sanotaan
**huonokuntoiseksi** ja pienen ehtoluvun matriisia hyväkuntoiseksi.
Nyrkkisääntö: kun $\kappa \approx 10^k$, ratkaisusta menetetään noin
$k$ merkitsevää numeroa. 64-bittisessä liukuluvussa numeroita on noin
16, joten esimerkin ehtoluvulla $4 \cdot 10^4$ niistä jää noin 11,
mutta neljän numeron tarkkuudella mitatuista kertoimista ei jää
yhtään. NumPy laskee ehtoluvun funktiolla `np.linalg.cond`.

Ehtoluku on ongelman ominaisuus, ei ratkaisumenetelmän: huonokuntoista
ryhmää ei voi ratkaista tarkasti millään algoritmilla, koska jo
syötteen virhe muuttaa oikeaa ratkaisua. Täsmällinen määritelmä
singulaariarvojen avulla on luvussa *Singulaariarvohajotelma*, ja
luku *Numeeriset näkökohdat* näyttää, miten ehtoluku ja algoritmin
valinta yhdessä määräävät tuloksen tarkkuuden.

## Käytännössä

- **Käytä `np.linalg.solve`a.** Oma eliminointi on opetusväline;
  kirjasto käyttää osittaistuentaa, lohkottua laskentaa ja tarkistaa
  singulaarisuuden.
- **Älä vertaa liukulukua nollaan.** Singulaarisuutta ei tunnista
  ehdolla `== 0`. Käytä toleranssia, joka on suhteessa matriisin
  suuruuteen, tai ehtolukua.
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
- Osaat selittää ehtoluvun geometrisesti ja arvioida sen avulla, montako
  merkitsevää numeroa ratkaisusta voi menettää.
