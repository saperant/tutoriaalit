# Näytteistys ja aliasointi

Näytteistys muuttaa jatkuvan signaalin $x(t)$ jonoksi
$x[n] = x(nT_s)$. Kysymys on, menetetäänkö jotain. Vastaus riippuu
signaalin taajuuksista: jos signaalissa ei ole taajuuksia näytetaajuuden
puolikkaan yläpuolella, näytteet määräävät signaalin täysin. Muuten
korkeat taajuudet naamioituvat mataliksi, eikä virhettä voi jälkikäteen
korjata. Tässä luvussa lasketaan, mihin aliasoitunut taajuus päätyy,
rekonstruoidaan signaali näytteistä ja näytetään, miksi
näytetaajuutta pienennettäessä on suodatettava ensin.

## Aliasointi

Edellisen luvun monikäsitteisyys hertseinä: kun näytetaajuus on $f_s$,
taajuudet $f$ ja $f + k f_s$ antavat samat näytteet kaikilla
kokonaisluvuilla $k$, ja kosinille myös $f$ ja $-f$ ovat samat.
**Nyquistin taajuus** $f_s/2$ on suurin taajuus, joka näkyy näytteissä
omana itsenään. Sitä korkeampi taajuus näkyy taajuutena, joka saadaan
siirtämällä $f_s$:n monikerroilla ja tarvittaessa peilaamalla Nyquistin
taajuuden ympäri. Tätä kutsutaan **aliasoinniksi** tai laskostumiseksi,
koska taajuusakseli taittuu kuin haitari.

```{.python tiedosto="esimerkit/03-aliasointi.py" osa="laskos"}
```

Kuvassa 7 kHz:n kosini näytteistetään 10 kHz:n taajuudella. Näytteet
osuvat täsmälleen 3 kHz:n kosinille, eikä näytteistä voi päätellä, kumpi
signaali oli alkuperäinen.

![7 kHz:n ja 3 kHz:n kosinit tuottavat samat näytteet, kun $f_s = 10$
kHz.](kuvat/aliasointi.png){width=100%}

```{.python tiedosto="esimerkit/03-aliasointi.py" osa="samat"}
```

Sinillä peilaus kääntää merkin: $\sin(2\pi \cdot 7\,\text{kHz}\cdot t)$
näytteistettynä on $-\sin(2\pi \cdot 3\,\text{kHz}\cdot t)$. Peilattu
taajuus vastaa negatiivista taajuutta, ja reaalisen signaalin
negatiivinen taajuus on liittoluku: vaihe vaihtaa merkkiään. Myöskään
spektri ei paljasta alkuperää:

```{.python tiedosto="esimerkit/03-aliasointi.py" osa="spektri"}
```

```{.tuloste tiedosto="esimerkit/03-aliasointi.odotettu"}
```

Arkinen esimerkki on elokuvan vaunun pyörä, joka näyttää pyörivän
hitaasti tai takaperin: kamera näytteistää pyörän asentoa 24 kertaa
sekunnissa, ja pinnojen nopea liike aliasoituu hitaaksi. Mittauksissa
aliasointi on salakavalampi. Verkkojännitteen 50 Hz:n harmoninen
1 050 Hz näytteistettynä 1 kHz:n taajuudella näkyy 50 Hz:n
komponenttina, joka näyttää aidolta.

## Näytteistysteoreema

**Nyquist–Shannonin näytteistysteoreema** sanoo: jos signaalin
Fourier-muunnos on nolla taajuuksilla $|f| \ge B$, signaali määräytyy
yksikäsitteisesti näytteistään, kunhan $f_s > 2B$. Perustelu on
taajuustasossa. Näytteistys toistaa signaalin spektrin $f_s$:n välein,
ja jos spektrin leveys $2B$ on pienempi kuin $f_s$, kopiot eivät mene
päällekkäin. Silloin alkuperäinen spektri saadaan erotettua ihanteellisella
alipäästösuotimella, jonka rajataajuus on $f_s/2$.

Ehto koskee *kaistaa* eikä signaalin näkyvää muotoa: 180 Hz:n sini
tarvitsee yli 360 näytettä sekunnissa, vaikka se näyttäisi
yksinkertaiselta. Toisaalta kantataajuuden ulkopuolinen kaistanpäästösignaali
voidaan näytteistää alle kaksinkertaisella taajuudella, jos kaista
osuu sopivasti. Tätä alinäytteistystä käytetään radiovastaanottimissa.

## Rekonstruktio

Ihanteellisen alipäästösuotimen impulssivaste on sinc-funktio, joten
rekonstruktio on **Whittakerin–Shannonin interpolaatiokaava**

$$x(t) = \sum_n x[n]\,\operatorname{sinc}\!\left(f_s t - n\right),
\qquad \operatorname{sinc}(u) = \frac{\sin \pi u}{\pi u}.$$

Jokainen näyte lähettää sinc-pulssin, joka on näytehetkellä 1 ja
muiden näytteiden kohdalla 0, ja pulssit lasketaan yhteen. NumPyn
`numpy.sinc` käyttää juuri tätä normitettua määritelmää.

```{.python tiedosto="esimerkit/03-rekonstruktio.py" osa="sinc"}
```

Pieni jäännösvirhe syntyy, koska näytteitä on äärellinen määrä ja
sinc vaimenee hitaasti, kuten $1/u$. Siksi virhe mitataan kaukana
reunoista. Käytännön muuntimet eivät laske sinc-summaa. Yksinkertaisin
digitaali–analogiamuunnin pitää edellisen näytteen arvon seuraavaan
näytteeseen asti. Tämä **nollannen asteen pito** tuottaa porrasmaisen
signaalin, jonka spektri on alkuperäinen kerrottuna funktiolla
$\operatorname{sinc}(f/f_s)$. Pito siis vaimentaa korkeita taajuuksia
ja jättää spektriin kopioita, jotka poistetaan analogisella
jälkisuotimella.

```{.python tiedosto="esimerkit/03-rekonstruktio.py" osa="pito"}
```

Jos ehto ei täyty, mikään interpolointi ei auta: 180 Hz:n komponentti
näytteistettynä 300 Hz:n taajuudella rekonstruoituu 120 Hz:n
komponentiksi.

```{.python tiedosto="esimerkit/03-rekonstruktio.py" osa="liian-harva"}
```

```{.tuloste tiedosto="esimerkit/03-rekonstruktio.odotettu"}
```

## Antialias-suodatus ja desimointi

Koska aliasointia ei voi korjata jälkikäteen, taajuudet Nyquistin
taajuuden yläpuolelta poistetaan *ennen* näytteistystä analogisella
**antialias-suotimella**. Sama pätee digitaalisesti, kun näytetaajuutta
pienennetään. Pelkkä joka $q$:nnen näytteen ottaminen on uusi
näytteistys, ja kaikki taajuudet uuden Nyquistin taajuuden $f_s/(2q)$
yläpuolelta aliasoituvat. **Desimointi** tarkoittaa siksi aina kahta
vaihetta: alipäästösuodatus ja sitten harvennus. `scipy.signal.decimate`
tekee molemmat.

```{.python tiedosto="esimerkit/03-desimointi.py" osa="desimointi"}
```

```{.tuloste tiedosto="esimerkit/03-desimointi.odotettu"}
```

Suoraan harvennettuna 2,7 kHz:n häiriö ilmestyy 700 Hz:n
taajuudelle täydellä amplitudilla, ja se näyttää aidolta signaalilta.
Suodatus ensin poistaa sen. Hyötysignaalin amplitudissa näkyy suotimen
päästökaistan pieni aaltoilu. Monitaajuuskäsittelyn tehokkaat rakenteet,
kuten polyfaasisuotimet, ovat taidon *Digitaalinen signaalinkäsittely*
aiheita.

## Kvantisointi lyhyesti

Näytteistys diskretoi ajan, kvantisointi amplitudin. Kun $b$-bittinen
muunnin pyöristää arvon lähimpään tasoon, virhe on enintään puoli
askelta. Jos virhe on tasajakautunut, sen teho on $\Delta^2/12$, missä
$\Delta$ on askel. Täyden asteikon sinin signaali–kohinasuhteeksi tulee
$6{,}02\,b + 1{,}76$ dB: jokainen bitti lisää noin 6 dB.

```{.python tiedosto="esimerkit/03-kvantisointi.py" osa="kvantisointi"}
```

```{.tuloste tiedosto="esimerkit/03-kvantisointi.odotettu"}
```

Kaava pätee, kun signaali on suuri ja vaihteleva suhteessa askeleen
kokoon. Hiljainen tai säännöllinen signaali tuottaa korreloitunutta
virhettä, joka kuuluu särönä eikä kohinana. Kvantisoinnin syvempi
käsittely ja kiinteän pilkun aritmetiikka ovat taitojen *Lukujen esitys
ja kiinteän pilkun aritmetiikka* ja *Digitaalinen signaalinkäsittely*
aiheita.

## Käytännössä

- **Valitse näytetaajuus kaistan mukaan, marginaalilla.** Teoreeman
  $f_s > 2B$ on raja, ei suunnitteluarvo. Antialias-suotimen
  siirtymäkaista vaatii tilaa: äänen 20 kHz:n kaistalle käytetään
  44,1 tai 48 kHz.
- **Älä koskaan harvenna suodattamatta.** `x[::q]` on bugi, ellei
  signaali ole jo valmiiksi kaistarajoitettu. Käytä `decimate`- tai
  `resample_poly`-funktiota.
- **Epäile aliasointia, kun mittauksessa on selittämätön matala
  taajuus.** Laske `nakyva_taajuus`-funktiolla, mitkä korkeat taajuudet
  (harmoniset, kytkentätaajuudet) voisivat laskostua havaittuun kohtaan.
- **Muista pidon sinc-vaimennus.** Nollannen asteen pito vaimentaa
  Nyquistin taajuudella noin 3,9 dB; tarkoissa järjestelmissä se
  kompensoidaan suotimella.

## Itsearviointi

- Osaat laskea, mille taajuudelle tietty taajuus aliasoituu annetulla
  näytetaajuudella, ja selittää peilauksen vaikutuksen siniin.
- Osaat perustella näytteistysteoreeman spektrin kopioilla ja rekonstruoida
  kaistarajoitetun signaalin sinc-interpoloinnilla.
- Osaat selittää, miksi näytetaajuutta pienennettäessä suodatetaan
  ensin, ja käyttää `scipy.signal.decimate`-funktiota.
- Osaat arvioida $b$-bittisen kvantisoinnin signaali–kohinasuhteen.
