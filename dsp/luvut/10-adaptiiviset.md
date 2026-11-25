# Adaptiiviset suotimet

Kaikki tähän asti suunnitellut suotimet tunsivat tehtävänsä etukäteen.
Kaiunpoistaja ei tunne huoneen akustiikkaa, eikä häiriönpoistaja
tiedä, millä vaiheella verkkohurina saapuu mittaukseen. **Adaptiivinen
suodin** säätää kertoimiaan ajon aikana niin, että virhe pienenee.
Tämä luku esittelee yleisimmän algoritmin, LMS:n, ja sen normitetun
muunnelman.

## Asetelma

Adaptiivisella suotimella on kaksi syötettä: suodatettava signaali
$x[n]$ ja haluttu signaali $d[n]$. Suotimen ulostulo on
$y[n] = \mathbf{w}^\top \mathbf{x}[n]$, missä $\mathbf{x}[n]$ on
viivelinjan $N$ viimeistä näytettä ja $\mathbf{w}$ painot. Virhe on
$e[n] = d[n] - y[n]$. Sama rakenne ratkaisee eri tehtäviä sen mukaan,
mitkä signaalit kytketään syötteisiin:

| Tehtävä | $x$ | $d$ | Hyödyllinen tulos |
|--------------------|-------------------------|------------------|-------------------------|
| järjestelmän tunnistus | tuntemattoman järjestelmän syöte | sen ulostulo | painot $\mathbf{w}$ |
| kaiunpoisto | kaiuttimen signaali | mikrofonin signaali | virhe $e$ (kaiku poistettu) |
| häiriönpoisto | häiriön viite | mitattu signaali | virhe $e$ |
| ennustus | viivästetty signaali | signaali | ennustusvirhe tai painot |

Keskineliövirheen minimoivat painot ovat **Wienerin ratkaisu**
$\mathbf{w}^* = \mathbf{R}^{-1}\mathbf{p}$, missä $\mathbf{R}$ on syötteen
autokorrelaatiomatriisi ja $\mathbf{p}$ syötteen ja halutun signaalin
ristikorrelaatio. Sen laskeminen vaatii tilastot etukäteen ja matriisin
kääntämisen. Lisäksi tilastot muuttuvat, kun ympäristö muuttuu.

## LMS ja NLMS

**LMS** (*least mean squares*, Widrow ja Hoff 1960) korvaa
gradientin hetkellisellä arviolla. Neliövirheen gradientti painojen
suhteen on $-2e[n]\mathbf{x}[n]$, joten jokaisella näytteellä

$$\mathbf{w}[n+1] = \mathbf{w}[n] + \mu\,e[n]\,\mathbf{x}[n].$$

Päivitys maksaa $N$ kertolaskua suodatuksen $N$:n lisäksi, joten
algoritmi on halpa ja sopii reaaliaikaan. Askelkoko $\mu$ riippuu
syötteen tehosta: kaksinkertainen signaali tekee askeleesta
nelinkertaisen. **NLMS** normittaa askeleen viivelinjan energialla:

$$\mathbf{w}[n+1] = \mathbf{w}[n] + \frac{\mu}{\varepsilon +
\lVert\mathbf{x}[n]\rVert^2}\,e[n]\,\mathbf{x}[n], \qquad 0 < \mu < 2.$$

Pieni $\varepsilon$ estää nollalla jakamisen hiljaisuudessa.

```{.python tiedosto="esimerkit/10-tunnistus.py" osa="nlms"}
```

Tunnistetaan tuntematon kahdeksan kertoimen suodin. Mittauksessa on
kohinaa −40 dB:n tasolla.

```{.python tiedosto="esimerkit/10-tunnistus.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/10-tunnistus.odotettu"}
```

Molemmat oppivat suotimen. NLMS on alussa nopeampi, koska sen askel on
syötteen tehoon sovitettu. Kun painot ovat lähellä oikeaa, virhe ei
enää pienene vaan heiluu: mittauskohina tuottaa jokaisella näytteellä
satunnaisen päivityksen. Suuri askel oppii nopeasti, mutta heiluu
enemmän.

## Askelkoko

Askelkoko on LMS:n ainoa parametri, ja se ratkaisee kolme asiaa:

- **Suppenemisnopeus** kasvaa $\mu$:n mukana.
- **Jäännösvirhe** kasvaa myös: ylimääräinen keskineliövirhe suhteessa
  mittauskohinaan on pienillä askelilla noin $\mu N \sigma_x^2 / 2$
  (*misadjustment*).
- **Stabiilisuus** menetetään, kun $\mu$ on liian suuri. Karkea raja on
  $\mu < 2/(N\sigma_x^2)$, mutta käytännön raja on selvästi pienempi.

```{.python tiedosto="esimerkit/10-askel.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/10-askel.odotettu"}
```

![LMS:n oppimiskäyrät kolmella askelkoolla. Katkoviiva on
mittauskohinan taso.](kuvat/lms.png){width=100%}

Pienillä askelilla malli $\mu N/2$ ennustaa jäännösvirheen hyvin.
Rajan $2/(N\sigma^2) = 0{,}125$ lähellä jäännösvirhe on jo moninkertainen,
ja raja ylittävä askel hajoaa. Käytännössä askel valitaan noin
kymmenesosaksi rajasta ja säädetään sovelluksen mukaan. Jos ympäristö
muuttuu nopeasti, tarvitaan suurempi askel ja hyväksytään suurempi
jäännösvirhe.

**RLS** (*recursive least squares*) suppenee paljon nopeammin ja on
riippumaton syötteen spektristä, koska se arvioi $\mathbf{R}^{-1}$:n
rekursiivisesti. Hinta on $O(N^2)$ laskentaa näytettä kohti ja
numeeriset ongelmat kiinteässä pilkussa. Sitä käytetään lyhyillä
suotimilla, kuten tietoliikenteen kanavakorjaimissa.

## Häiriönpoisto viitesignaalilla

Biosignaalin mittaukseen kytkeytyy verkkohurina, jonka taajuus vaeltaa
hieman ja jossa on yliaaltoja. Kiinteä lovisuodin osuu vain
nimellistaajuuteen. Jos häiriöstä on saatavilla viite, esimerkiksi
suoraan verkkojännitteestä, adaptiivinen suodin oppii, millä vahvistuksella
ja vaiheella hurina saapuu mittaukseen, ja vähentää sen.

```{.python tiedosto="esimerkit/10-kohinanpoisto.py" osa="tilanne"}
```

```{.python tiedosto="esimerkit/10-kohinanpoisto.py" osa="suodata"}
```

```{.python tiedosto="esimerkit/10-kohinanpoisto.py" osa="tulos"}
```

```{.tuloste tiedosto="esimerkit/10-kohinanpoisto.odotettu"}
```

![Tehospektrit mittauksen jälkipuoliskolta; vaalea käyrä on
hyötysignaali. Kiinteä lovi jättää vaeltavan 50 Hz:n hurinan reunat ja
koko 150 Hz:n yliaallon. Adaptiivinen suodin poistaa 50 Hz:n
komponentin ja vaimentaa yliaaltoa noin 25
dB.](kuvat/hurina.png){width=100%}

Virhesignaali $e$ on tässä hyödyllinen ulostulo: suodin poistaa siitä
kaiken, minkä viite selittää, ja hyötysignaali jää jäljelle, koska se
ei korreloi viitteen kanssa. Kiinteä lovi parantaa tilannetta 10 dB,
adaptiivinen suodin 28 dB, koska se seuraa taajuuden vaellusta ja
poistaa myös kolmannen yliaallon. Jos viite korreloisi hyötysignaalin
kanssa, suodin poistaisi myös hyötysignaalia. Siksi viitteen on
oltava puhdas häiriöstä.

## NLMS C:llä

C-toteutus laskee viivelinjan energian juoksevasti: uusin näyte lisätään
ja vanhin vähennetään. Näin normitus ei maksa $N$ kertolaskua lisää.
Juokseva summa kerryttää pyöristysvirhettä ja voi painua hieman
negatiiviseksi, kun signaali vaimenee hiljaiseksi, joten se rajoitetaan
nollaan. Pitkään käyvässä järjestelmässä energia lasketaan
silloin tällöin uudelleen alusta.

```{.c tiedosto="esimerkit/10-lms/lms.h" osa="tyyppi"}
```

```{.c tiedosto="esimerkit/10-lms/lms.c" osa="askel"}
```

```{.c tiedosto="esimerkit/10-lms/main.c" osa="tunnistus"}
```

```{.tuloste tiedosto="esimerkit/10-lms.odotettu"}
```

Vertailuohjelma ajaa C-toteutuksen ja Python-mallin samalla datalla ja
vaatii, että virhesignaalit täsmäävät toleranssilla $10^{-9}$. Malli
laskee energian joka askeleella alusta, joten se on riippumaton
tarkistus myös juoksevalle summalle.

```{.python tiedosto="esimerkit/vertailu/mallit.py" osa="nlms"}
```

## Käytännössä

- **Käytä NLMS:ää** LMS:n sijaan, kun syötteen taso vaihtelee. Askel
  $0 < \mu < 2$ ei silloin riipu signaalin voimakkuudesta.
- **Valitse askel kompromissina**: nopea seuranta vaatii suurta, pieni
  jäännösvirhe pientä. Aloita noin kymmenesosasta stabiilisuusrajaa.
- **Lisää $\varepsilon$ normitukseen** ja rajoita juokseva energia
  nollaan. Hiljaisuus ei saa tuottaa jakoa nollalla.
- **Varmista, ettei viite korreloi hyötysignaalin kanssa.** Muuten
  suodin poistaa myös sen, mitä halutaan säilyttää.
- **Testaa järjestelmän tunnistuksella**: tunnettu suodin, kohina ja
  painojen virhe desibeleinä ovat toistettava ja tulkittava testi.

## Itsearviointi

- Osaat kytkeä adaptiivisen suotimen järjestelmän tunnistukseen,
  kaiunpoistoon ja häiriönpoistoon ja nimetä niissä hyödyllisen
  ulostulon.
- Osaat johtaa LMS-päivityksen hetkellisestä gradientista ja selittää
  NLMS:n normituksen.
- Osaat valita askelkoon suppenemisnopeuden, jäännösvirheen ja
  stabiilisuuden perusteella.
- Osaat toteuttaa NLMS:n C:llä juoksevalla energialla ja testata sen
  Python-mallia vastaan.
