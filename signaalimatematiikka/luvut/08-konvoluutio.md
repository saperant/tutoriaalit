# Konvoluutio

Suodatin, kaiku, kameran epätarkkuus ja mittalaitteen hitaus
ovat kaikki saman operaation esimerkkejä. Jokainen ulostulon arvo on
painotettu summa sisääntulon arvoista lähiajalta, ja painot ovat samat
joka hetkellä. Tämä operaatio on **konvoluutio**. Se on lineaaristen,
ajan suhteen muuttumattomien järjestelmien kieli, ja Fourier-muunnos
tekee siitä kertolaskun. Tässä luvussa konvoluutio määritellään,
toteutetaan ja tarkistetaan; järjestelmien teoria on taidon
*Signaalit ja järjestelmät* aihe.

## Määritelmä

Kahden jonon $x[n]$ ja $h[n]$ **diskreetti konvoluutio** on

$$y[n] = (x * h)[n] = \sum_k x[k]\,h[n - k].$$

Summan voi lukea kahdella tavalla. Ensimmäisessä jokainen sisääntulon
näyte $x[k]$ lähettää ulostuloon kopion jonosta $h$ siirrettynä
kohtaan $k$ ja skaalattuna arvolla $x[k]$, ja kopiot lasketaan yhteen.
Jono $h$ on siis järjestelmän **impulssivaste**: se, mitä yksittäinen
ykkösnäyte tuottaa. Toisessa luennassa ulostulo $y[n]$ on sisääntulon
painotettu summa, jossa painojono on käännetty ympäri ja siirretty
kohtaan $n$. Kääntäminen tekee konvoluutiosta **vaihdannaisen**:
$x * h = h * x$.

Jos $x$:ssä on $N_x$ ja $h$:ssa $N_h$ näytettä, tuloksessa on
$N_x + N_h - 1$ näytettä. Suora laskeminen vaatii noin $N_x N_h$
kertolaskua.

```{.python tiedosto="esimerkit/08-konvoluutio.py" osa="oma"}
```

```{.tuloste tiedosto="esimerkit/08-konvoluutio.odotettu"}
```

Konvoluutio viivästetyn impulssin kanssa siirtää signaalia: kaksi
nollaa impulssin edessä viivästää koko signaalia kahdella näytteellä.
Impulssi itse ($h = [1]$) on konvoluution neutraalialkio.

Konvoluutio on myös polynomien kertolasku. Kun jonot ovat polynomien
kertoimia, $x = [1, 2, 3]$ tarkoittaa polynomia $1 + 2z + 3z^2$, ja
konvoluution tulos on tulopolynomin kertoimet. Tästä yhteydestä
syntyy Z-muunnos.

## Liukuva keskiarvo

Yksinkertaisin suodatin on **liukuva keskiarvo**, jonka impulssivaste
on $M$ näytettä arvoltaan $1/M$. Jokainen ulostulon näyte on $M$
viimeisimmän näytteen keskiarvo. Jos kohinan näytteet ovat
riippumattomia ja niiden keskihajonta on $\sigma$, keskiarvon
keskihajonta on $\sigma/\sqrt M$. Hidas signaali sen sijaan säilyy
lähes ennallaan, koska sen peräkkäiset näytteet ovat lähes samat.

Esimerkissä signaali on sinimuotoinen, jakso 200 näytettä, ja kohina on
tasajakautunutta väliltä $[-1, 1]$, jolloin $\sigma = 1/\sqrt3$. Kohina
tuotetaan kiinteällä siemenellä, jotta tulos on joka ajolla sama.
Argumentti `mode="valid"` palauttaa vain ne näytteet, joissa ikkuna on
kokonaan signaalin sisällä.

```{.python tiedosto="esimerkit/08-keskiarvo.py" osa="keskiarvo"}
```

```{.tuloste tiedosto="esimerkit/08-keskiarvo.odotettu"}
```

![Esimerkin mitattu signaali ja sen liukuvat keskiarvot (katkoviiva on
kohinaton signaali). Pidempi ikkuna poistaa enemmän kohinaa, mutta
64 näytteen ikkuna alkaa jo vaimentaa itse
signaalia.](kuvat/keskiarvo.png){width=95%}

Kohina pienenee teorian mukaisesti, mutta pitkä ikkuna alkaa vaimentaa
myös signaalia: 64 näytteen ikkuna kattaa kolmasosan signaalin jaksosta,
ja amplitudista katoaa 16 prosenttia. Suodattimen pituus on aina
kompromissi kohinan ja signaalin välillä. Kompromissin ymmärtäminen
vaatii taajuustason, johon palataan konvoluutiolauseen jälkeen.

## Jatkuva konvoluutio

Jatkuvan ajan signaaleille summa korvautuu integraalilla:

$$(x * h)(t) = \int_{-\infty}^{\infty} x(s)\,h(t - s)\,ds.$$

Numeerisesti integraali on diskreetti konvoluutio kerrottuna
näytevälillä $\Delta t$. Klassinen esimerkki on kahden kanttipulssin
konvoluutio: kun pulssi liukuu toisen yli, päällekkäisen osan pituus
kasvaa tasaisesti nollasta yhteen ja pienenee taas nollaan, joten
tulos on **kolmiopulssi** $\max(0, 1 - |t|)$.

```{.python tiedosto="esimerkit/08-jatkuva.py" osa="kolmio"}
```

## Konvoluutiolause

Fourier-muunnoksen tärkein ominaisuus on **konvoluutiolause**:

$$\mathcal{F}\{x * h\} = X \cdot H.$$

Konvoluutio aikatasossa on kertolasku taajuustasossa. Perustelu on
lyhyt. Konvoluutio on summa siirretyistä ja skaalatuista kopioista
signaalista $h$, ja aikasiirto $s$ kertoo muunnoksen luvulla
$e^{-2\pi i f s}$. Muunnos on siis
$\int x(s)e^{-2\pi i f s}H(f)\,ds = X(f)H(f)$. Toinen tapa nähdä sama:
kompleksinen eksponentti $e^{2\pi i f t}$ kulkee konvoluution läpi
muuttumatta muotoaan, kertoimella $H(f)$. Eksponentit ovat konvoluution
**ominaisfunktioita** ja $H(f)$ vastaava ominaisarvo, aivan kuten
diagonalisoituvalla matriisilla on ominaisvektorinsa. Fourier-muunnos
on kannanvaihto, jossa konvoluutio muuttuu diagonaaliseksi.

Kolmiopulssi on kanttipulssin konvoluutio itsensä kanssa, joten sen
muunnos on $\operatorname{sinc}^2 f$. Ohjelma laskee kolmion muunnoksen
numeerisesti ja vertaa.

```{.python tiedosto="esimerkit/08-jatkuva.py" osa="spektri"}
```

```{.tuloste tiedosto="esimerkit/08-jatkuva.odotettu"}
```

Diskreeteille jonoille konvoluutiolause tarvitsee diskreetin
Fourier-muunnoksen. Syklinen konvoluutio, nopea konvoluutio FFT:llä ja
liukuvan keskiarvon taajuusvaste lasketaan siksi seuraavan luvun
lopussa, kun DFT on määritelty.

## Käytännössä

- **Tunnista konvoluutio.** Kun jokainen ulostulo on samoin painoin
  laskettu summa sisääntulon naapurustosta, kyseessä on konvoluutio,
  ja painojono on impulssivaste.
- **Valitse `mode` tietoisesti.** `"full"` antaa kaikki
  $N_x + N_h - 1$ näytettä, `"same"` sisääntulon pituisen keskiosan ja
  `"valid"` vain näytteet, joissa ikkuna on kokonaan sisällä.
- **Muista konvoluutiolause.** Konvoluutio aikatasossa on kertolasku
  taajuustasossa, joten suodattimen vaikutuksen näkee sen muunnoksesta.

## Itsearviointi

- Osaat laskea kahden lyhyen jonon konvoluution käsin ja toteuttaa sen
  silmukoilla.
- Osaat selittää impulssivasteen ja perustella, miksi liukuva keskiarvo
  pienentää riippumatonta kohinaa kertoimella $1/\sqrt M$.
- Osaat muotoilla konvoluutiolauseen, perustella sen aikasiirron
  avulla ja tarkistaa sen numeerisesti jatkuvalle signaalille.
