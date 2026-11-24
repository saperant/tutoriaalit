# Differentiaaliyhtälöiden ratkaisijat

Alkuarvotehtävä $y' = f(t, y)$, $y(t_0) = y_0$ kuvaa järjestelmää,
jonka muutosnopeus riippuu sen tilasta: piirin jännitteet, kappaleen
liike, reaktioiden pitoisuudet ja epidemian kulku. Taito
*Differentiaaliyhtälöt ja Laplace-muunnos* käsittelee mallintamisen ja
analyyttiset ratkaisut sekä SciPyn `solve_ivp`:n käytön. Tässä luvussa
katsotaan ratkaisijoiden sisään: kertaluku, stabiilisuus, jäykkyys ja
askeleen valinta. Ne selittävät, miksi ratkaisija joskus vaatii
miljoonia askelia tai tuottaa järjettömiä lukuja.

Systeemi $y' = f(t, y)$ voi olla vektorimuotoinen, ja korkeamman
kertaluvun yhtälö palautetaan ensimmäisen kertaluvun systeemiksi:
$y'' = g$ kirjoitetaan muotoon $y_1' = y_2$, $y_2' = g$. Seuraavat
menetelmät toimivat sellaisinaan vektoreille.

## Yksiaskelmenetelmät ja kertaluku

**Eulerin menetelmä** kulkee tangentin suuntaan:
$y_{k+1} = y_k + hf(t_k, y_k)$. Yhden askeleen virhe (paikallinen
virhe) on $O(h^2)$, ja koska askelia on $T/h$, kokonaisvirhe on $O(h)$.
**Rungen–Kuttan menetelmät** laskevat funktion arvoja askeleen sisällä
ja yhdistävät ne niin, että Taylorin kehitelmä täsmää korkeampaan
kertalukuun asti. Heunin menetelmä on kertalukua 2 ja klassinen RK4
kertalukua 4.

```{.python tiedosto="esimerkit/08-kertaluku.py" osa="askeleet"}
```

```{.python tiedosto="esimerkit/08-kertaluku.py" osa="ratkaise"}
```

```{.python tiedosto="esimerkit/08-kertaluku.py" osa="mittaus"}
```

```{.tuloste tiedosto="esimerkit/08-kertaluku.odotettu"}
```

Kun askelten määrä kaksinkertaistuu, Eulerin virhe puolittuu, Heunin
virhe pienenee neljäsosaan ja RK4:n kuudestoistaosaan. Kertaluvut 1, 2
ja 4 näkyvät mittauksessa. RK4 laskee neljä funktion arvoa askeleella
ja Euler yhden, mutta samalla työllä RK4 on silti monta
kertaluokkaa tarkempi. Siksi Eulerin menetelmää ei käytetä tarkkaan
laskentaan, vaikka se on yksinkertaisin ymmärtää.

## Stabiilisuus

Tarkkuuden lisäksi menetelmän on oltava **stabiili**: virheet eivät
saa kasvaa askeleesta toiseen. Stabiilisuutta tutkitaan
testiyhtälöllä $y' = \lambda y$, jonka ratkaisu vaimenee, kun
$\operatorname{Re}\lambda < 0$. Eulerin menetelmä antaa
$y_{k+1} = (1 + h\lambda)y_k$, joten numeerinen ratkaisu vaimenee vain,
jos $|1 + h\lambda| \le 1$. Reaaliselle negatiiviselle $\lambda$:lle
ehto on

$$h \le \frac{2}{|\lambda|}.$$

Joukko kompleksitason pisteitä $z = h\lambda$, joilla menetelmä on
stabiili, on menetelmän **stabiilisuusalue**.

**Implisiittinen Euler** $y_{k+1} = y_k + hf(t_{k+1}, y_{k+1})$
käyttää derivaattaa askeleen *lopussa*. Testiyhtälölle
$y_{k+1} = y_k / (1 - h\lambda)$, joka vaimenee kaikilla
$\operatorname{Re}\lambda < 0$ askeleen pituudesta riippumatta.
Menetelmä on **A-stabiili**. Hinta on se, että jokaisella askeleella
pitää ratkaista yhtälö (yleensä Newtonin menetelmällä, luku 3) uuden
arvon $y_{k+1}$ selvittämiseksi.

```{.python tiedosto="esimerkit/08-stabiilisuus.py" osa="eulerit"}
```

```{.python tiedosto="esimerkit/08-stabiilisuus.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-stabiilisuus.odotettu"}
```

![Eulerin menetelmän (ympyrä) ja RK4:n stabiilisuusalueet
kompleksitasossa. Implisiittinen Euler on stabiili koko sävytetyllä
alueella, johon kuuluu koko vasen puolitaso.](kuvat/stabiilisuus.png){width=58%}

Tarkka ratkaisu on $\cos t$, joka muuttuu hitaasti, mutta yhtälön
$\lambda = -1000$ vaimentaa poikkeamat siitä erittäin nopeasti.
Eksplisiittinen Euler toimii vain askeleella $h < 0{,}002$; heti rajan
yli virhe kasvaa joka askeleella, ja tulos räjähtää. Implisiittinen
Euler on tarkka kaikilla askelilla, joilla ratkaisun *oma* muutos
($\cos t$) on hyvin esitetty.

## Jäykkyys

Yhtälö on **jäykkä**, kun siinä on samaan aikaan hyvin nopeita,
nopeasti vaimenevia ilmiöitä ja hitaita ilmiöitä, joita halutaan seurata.
Eksplisiittisen menetelmän askel määräytyy silloin stabiilisuudesta
(nopein aikavakio) eikä tarkkuudesta (hidas ratkaisu). Jäykkiä ovat
esimerkiksi kemialliset reaktiot, joissa on nopeita ja hitaita
reaktioita, sähköpiirit, joissa on pieniä ja suuria aikavakioita, sekä
diskretoidut lämmönjohtumisyhtälöt.

**Van der Polin oskillaattori** suurella parametrilla $\mu$ on klassinen
testitehtävä: ratkaisu muuttuu hitaasti pitkiä aikoja ja hyppää välillä
äkkiä.

```{.python tiedosto="esimerkit/08-jaykka.py" osa="malli"}
```

```{.python tiedosto="esimerkit/08-jaykka.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-jaykka.odotettu"}
```

Kaikki kolme antavat saman tuloksen, mutta eksplisiittinen RK45
tarvitsee yli kymmenkertaisen määrän funktion arvoja, koska sen askel on
stabiilisuuden rajaama koko hitaan vaiheen ajan. Implisiittiset
**Radau** (Rungen–Kuttan menetelmä) ja **BDF** (taaksepäin derivaattojen
kaavat) ottavat pitkiä askelia hitaissa vaiheissa. Niiden askel on
kalliimpi, koska ne tarvitsevat Jacobin matriisin ja ratkaisevat
yhtälöryhmän, mutta askelia tarvitaan paljon vähemmän.

Jos et tiedä, onko tehtävä jäykkä, `LSODA` vaihtaa automaattisesti
eksplisiittisen ja implisiittisen menetelmän välillä. Merkki jäykkyydestä
on, että eksplisiittinen ratkaisija etenee hyvin pienin askelin, vaikka
ratkaisu näyttää sileältä.

## Adaptiivinen askel

Kiinteä askel on joko liian pieni loivissa kohdissa tai liian suuri
jyrkissä. **Adaptiivinen ratkaisija** arvioi paikallisen virheen joka
askeleella ja säätää askeleen pituutta. Virhearvio saadaan
**upotetusta parista**: kaksi eri kertaluvun menetelmää käyttävät samoja
funktion arvoja, ja niiden erotus arvioi alemman kertaluvun virheen.
Jos arvio on yli toleranssin, askel hylätään ja yritetään lyhyemmällä.
Uusi askel valitaan kaavalla

$$h_\text{uusi} = 0{,}9\,h\left(\frac{\text{tol}}{\text{arvio}}\right)^{1/(p+1)},$$

jossa $p$ on alemman menetelmän kertaluku ja 0,9 on varmuuskerroin.

```{.python tiedosto="esimerkit/08-adaptiivinen.py" osa="malli"}
```

```{.python tiedosto="esimerkit/08-adaptiivinen.py" osa="adaptiivinen"}
```

```{.python tiedosto="esimerkit/08-adaptiivinen.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/08-adaptiivinen.odotettu"}
```

Askel vaihtelee yli 500-kertaisesti: pisin askel on 0,13 tasaisessa
osassa, ja lyhin askel on huipun kohdalla. `solve_ivp`:n oletus `RK45`
on **Dormandin–Princen** pari (kertaluvut 5 ja 4), ja se saavuttaa
paremman tarkkuuden alle 500 askeleella. Korkean kertaluvun pari on
yleensä tehokkain, kun tarkkuutta tarvitaan paljon.

Adaptiivisuudesta seuraa kaksi asiaa, jotka yllättävät usein:

- **Toleranssi koskee paikallista virhettä**, ei lopputuloksen
  virhettä. Kokonaisvirhe voi olla suurempi, joten tarkkuus tarkistetaan
  ajamalla ratkaisu tiukemmalla toleranssilla ja vertaamalla tuloksia.
- **Absoluuttinen ja suhteellinen toleranssi** (`atol`, `rtol`)
  toimivat yhdessä: kun ratkaisu on lähellä nollaa, `atol` määrää
  tarkkuuden. Liian suuri `atol` pienelle suureelle (esimerkiksi
  pitoisuus $10^{-9}$) hukkaa koko ratkaisun.

## Sama Octavella

```{.octave tiedosto="esimerkit/octave/08-ode45.m"}
```

```{.tuloste tiedosto="esimerkit/octave/08-ode45.odotettu"}
```

Octaven `ode45` on sama Dormandin–Princen pari kuin SciPyn `RK45`, ja
`ode15s` on jäykkien tehtävien ratkaisija. Toleranssit annetaan
`odeset`-rakenteella.

## Käytännössä

- **Aloita adaptiivisella ratkaisijalla**, ei omalla kiinteällä
  askeleella. `solve_ivp` (RK45) ja Octaven `ode45` sopivat useimpiin
  ei-jäykkiin tehtäviin.
- **Jos ratkaisija on hidas, epäile jäykkyyttä** ja kokeile `Radau`-,
  `BDF`- tai `LSODA`-menetelmää. Anna Jacobin matriisi (`jac`), jos se
  on saatavilla; se nopeuttaa implisiittisiä menetelmiä.
- **Tarkista tarkkuus muuttamalla toleranssia.** Jos tulos muuttuu, kun
  `rtol` pienennetään kymmenesosaan, aiempi tulos ei ollut riittävän
  tarkka.
- **Aseta `atol` kunkin muuttujan mittakaavan mukaan.** Vektori
  `atol` sallii eri toleranssit eri komponenteille.
- **Säilyvät suureet (energia, massa) kertovat virheestä.** Pitkissä
  simulaatioissa, kuten planeettojen radoissa, käytetään
  symplektisiä menetelmiä, jotka säilyttävät energian pitkällä
  aikavälillä paremmin.
- **Tapahtumat** (`events`) pysäyttävät ratkaisun tarkasti, kun ehto
  täyttyy (pallo osuu maahan, säiliö tyhjenee). Älä etsi
  ylitystä jälkikäteen ratkaisupisteiden joukosta.

## Itsearviointi

- Osaat toteuttaa Eulerin, Heunin ja RK4-menetelmän ja mitata niiden
  kertaluvut.
- Osaat johtaa eksplisiittisen Eulerin stabiilisuusehdon
  testiyhtälöstä ja selittää stabiilisuusalueen käsitteen.
- Osaat selittää, miksi implisiittinen menetelmä sopii jäykkiin
  tehtäviin ja mitä se maksaa.
- Osaat tunnistaa jäykän tehtävän ja valita sille sopivan ratkaisijan.
- Osaat selittää upotetun parin virhearvion ja askeleen säädön sekä
  toleranssien merkityksen.
