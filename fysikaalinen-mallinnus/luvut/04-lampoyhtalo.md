# Lämpöyhtälö ajassa

Kun lämpötila muuttuu ajassa, hilan jokaisesta pisteestä tulee
tavallinen differentiaaliyhtälö, ja ne kaikki ratkaistaan yhtä aikaa.
Taidon *Numeeriset menetelmät* käsitteet stabiilisuusalue ja jäykkyys
saavat tässä konkreettisen muodon: eksplisiittisen menetelmän
aika-askeleen yläraja riippuu hilavälin neliöstä. Luvussa nähdään,
miten raja syntyy ja miltä sen ylitys näyttää, verrataan kahta
implisiittistä menetelmää ja käytetään ratkaisijaa sen selvittämiseen,
milloin paikkariippuvaa mallia ei tarvita lainkaan.

## Viivamenetelmä

Diskretoidaan lämpöyhtälö $u_t = \alpha u_{xx}$ ensin vain paikan
suhteen. Jokaiselle sisäpisteelle tulee yhtälö

$$\frac{du_i}{dt} = \frac{\alpha}{h^2}\,(u_{i-1} - 2u_i + u_{i+1}),$$

eli vektorimuodossa $\dot{\mathbf u} = -\frac{\alpha}{h^2} A\,\mathbf u$,
jossa $A = \mathrm{tridiag}(-1, 2, -1)$. Tämä **viivamenetelmä**
(*method of lines*) palauttaa osittaisdifferentiaaliyhtälön
tavallisten differentiaaliyhtälöiden ryhmäksi, johon käy mikä tahansa
aikaintegroija.

Ryhmä on **jäykkä**. Matriisin $A$ ominaisarvot ovat välillä
$(0, 4)$, joten hitain vaimeneva muoto vaimenee nopeudella
$\pi^2\alpha/L^2$ ja nopein nopeudella $4\alpha/h^2$. Nopeuksien suhde
on noin $0{,}4\,n^2$, kun välejä on $n$: sadalla välillä 4000 ja
tuhannella 400 000. Nopein muoto on hilan sahalaita, joka vaimenee
lähes heti eikä kiinnosta ketään, mutta se määrää eksplisiittisen
menetelmän askeleen.

## Eksplisiittinen menetelmä ja stabiilisuusraja

Eksplisiittinen Euler ajassa ja keskeisdifferenssi paikassa (lyhenne
FTCS, *forward time, centered space*) antaa kaavan

$$u_i^{n+1} = u_i^n + r\,(u_{i-1}^n - 2u_i^n + u_{i+1}^n),
  \qquad r = \frac{\alpha\,\Delta t}{h^2}.$$

```{.python tiedosto="esimerkit/04-ftcs.py" osa="askel"}
```

Luku $r$ on hilan Fourier'n luku: aika-askel mitattuna ajassa, jossa
lämpö ehtii yhden hilavälin yli. Kun kaavaan sijoitetaan sahalaita
$u_i = (-1)^i$, se kertoutuu joka askeleella luvulla $1 - 4r$.
Itseisarvo pysyy enintään ykkösenä vain, jos

$$r \le \tfrac12 \quad\Longleftrightarrow\quad \Delta t \le \frac{h^2}{2\alpha}.$$

Sama tulos saadaan eksplisiittisen Eulerin stabiilisuusehdosta
$\Delta t\,\lambda_{\max} \le 2$. Kokeessa alkutilaan lisätään
miljoonasosan suuruinen sahalaita kuvaamaan pyöristys- ja mittausvirheitä.

```{.python tiedosto="esimerkit/04-ftcs.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/04-ftcs.odotettu"}
```

![Sama alkutila kahdella aika-askeleella. Rajalla $r = 0{,}5$ ratkaisu
vaimenee oikein. Kahden prosentin ylitys riittää: miljoonasosan häiriö
kasvaa 440 askeleessa moninkertaiseksi ratkaisuun
nähden.](kuvat/ftcs.png){width=95%}

Raja on jyrkkä. Arvolla 0,50 kaikki toimii, arvolla 0,51 suurin arvo
on hetkellä 0,1 jo yli sata ja arvolla 0,55 luokkaa $10^{29}$. Kasvu on
eksponentiaalista askelten määrässä, joten epästabiilia laskua ei voi
korjata laskemalla tarkemmin tai lyhyemmän aikaa.

Rajan seuraus on raskas: kun hilaväli puolitetaan, askelia tarvitaan
nelinkertainen määrä ja pisteitä on kaksinkertainen määrä, joten työ
kahdeksankertaistuu. Kahdessa ulottuvuudessa raja on $r \le 1/4$ ja
kolmessa $r \le 1/6$.

## Implisiittiset menetelmät

Implisiittinen Euler laskee erotuksen uudella aikatasolla, jolloin
jokaisella askeleella ratkaistaan yhtälöryhmä. **Theta-menetelmä**
yhdistää kolme kaaviota yhteen parametriin:

$$(I + \theta r A)\,\mathbf u^{n+1} = (I - (1-\theta)\,r A)\,\mathbf u^n.$$

Arvo $\theta = 0$ on eksplisiittinen Euler, $\theta = 1$
implisiittinen Euler ja $\theta = \tfrac12$ **Crank–Nicolsonin
menetelmä** eli puolisuunnikassääntö. Matriisi on kolmilävistäjäinen,
joten askel maksaa saman kertaluvun työn kuin eksplisiittinen.

```{.python tiedosto="esimerkit/04-implisiittinen.py" osa="theta"}
```

Kun $\theta \ge \tfrac12$, menetelmä on stabiili kaikilla askelilla.
Askelen pituuden määrää silloin tarkkuus. Mitataan kertaluku ajan
suhteen niin tiheällä hilalla, että paikan virhe ei näy:

```{.python tiedosto="esimerkit/04-implisiittinen.py" osa="kertaluku"}
```

```{.tuloste tiedosto="esimerkit/04-implisiittinen.odotettu" rivit="1-5"}
```

Implisiittinen Euler on ensimmäistä ja Crank–Nicolson toista kertalukua.
Neljälläkymmenellä askeleella Crank–Nicolsonin virhe on
kaksisataakertaisesti pienempi.

Crank–Nicolsonilla on kuitenkin heikkous, joka näkyy, kun alkutila on
epäjatkuva ja askel pitkä. Lämpöyhtälön tarkka ratkaisu ei koskaan luo
uusia huippuja: jos profiilissa on aluksi yksi maksimi, niin on
myöhemminkin (*maksimiperiaate*). Kokeessa tangon keskiosa on aluksi
ykkönen ja muu nolla, ja askel on 40 kertaa eksplisiittistä rajaa
pidempi.

```{.python tiedosto="esimerkit/04-implisiittinen.py" osa="porras"}
```

```{.tuloste tiedosto="esimerkit/04-implisiittinen.odotettu" alkaen="porrasalkutila"}
```

![Porrasalkutila kahden pitkän askeleen jälkeen. Implisiittinen Euler
tasoittaa portaan, Crank–Nicolson jättää sen reunoille
piikit.](kuvat/porras.png){width=68%}

Implisiittinen Euler kertoo sahalaitamuodon luvulla
$1/(1 + 4r)$, joka on pitkällä askeleella lähes nolla: nopeat muodot
häviävät, kuten fysiikassa. Crank–Nicolsonin kerroin on
$(1 - 2r)/(1 + 2r)$, joka lähestyy arvoa −1: nopeat muodot eivät kasva,
mutta eivät myöskään vaimene, vaan vaihtavat merkkiä joka askeleella.
Menetelmä on stabiili mutta ei vaimenna jäykkiä muotoja. Tavallinen
käytäntö on ottaa muutama ensimmäinen askel implisiittisellä Eulerilla
tai lyhyellä askeleella ja jatkaa sitten Crank–Nicolsonilla.

## Konvektioreuna ja Biot'n luku

Taidossa *Differentiaaliyhtälöt ja Laplace-muunnos* jäähtyvää
kappaletta kuvattiin yhdellä lämpötilalla ja Newtonin jäähtymislailla.
Malli olettaa, että kappale on koko ajan tasalämpöinen. Nyt oletuksen
voi tarkistaa ratkaisemalla koko profiilin.

Kaksikymmentä millimetriä paksu teräslevy on 200-asteinen ja jäähtyy
molemmilta pinnoiltaan. Symmetrian vuoksi lasketaan puolikas: keskellä
vuo on nolla ja pinnassa on Robinin ehto
$-k\,u_x = h\,(u - T_\infty)$. Pintatilavuuden yhtälössä johtuminen
puolen hilavälin läpi ja konvektio ovat sarjassa, samoin kuin luvun 3
seinässä.

```{.python tiedosto="esimerkit/04-biot.py" osa="profiili"}
```

```{.python tiedosto="esimerkit/04-biot.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/04-biot.odotettu"}
```

![Levyn puolikkaan lämpötilaprofiili kolmessa jäähdytyksessä. Ilmassa
levy on tasalämpöinen, vedessä pinta on lähes 30 astetta keskikohtaa
kylmempi.](kuvat/biot.png){width=68%}

**Biot'n luku** $\mathrm{Bi} = hL/k$ on sisäisen johtumisvastuksen
$L/k$ ja pinnan konvektiovastuksen $1/h$ suhde. Ilmassa se on 0,01:
lämpö ehtii tasoittua levyn sisällä paljon nopeammin kuin se poistuu
pinnasta, ja yhden lämpötilan malli osuu kymmenesosa-asteen päähän.
Vedessä luku on 1,1, pinnan ja keskikohdan ero on 29 astetta, ja yhden
lämpötilan malli on väärässä kaikkialla: se ennustaa levyn kylmemmäksi
kuin sen kylmin kohta. Nyrkkisääntö on, että yhden lämpötilan malli
riittää, kun $\mathrm{Bi} < 0{,}1$.

Tämä on pieni esimerkki validoinnista: yksinkertaisempaa mallia
verrataan tarkempaan ja saadaan raja, jonka sisällä yksinkertainen
kelpaa. Halvin malli, joka vastaa kysymykseen, on oikea malli.

## Käytännössä

- **Diffuusiotehtävät ratkaistaan implisiittisesti.** Eksplisiittinen
  raja $\Delta t \le h^2/(2\alpha)$ tekee tiheistä hiloista
  käyttökelvottomia. Eksplisiittinen menetelmä kannattaa lähinnä
  silloin, kun askel on muutenkin lyhyt tai laskenta tehdään
  grafiikkasuorittimella, jossa yhtälöryhmän ratkaisu on kallis.
- **Stabiili ei tarkoita tarkkaa.** Implisiittinen Euler antaa
  järkevän näköisen tuloksen millä tahansa askeleella. Puolita askel ja
  katso, muuttuuko tulos.
- **Tunne menetelmän vaimennus.** Crank–Nicolson on tarkka sileille
  ratkaisuille, mutta äkillinen muutos (alkuhetki, kytkeytyvä kuorma)
  vaatii aluksi vaimentavan menetelmän. SciPyn jäykät ratkaisijat `BDF`
  ja `Radau` vaimentavat ja valitsevat askeleen itse; ne ovat hyvä
  oletus, kun viivamenetelmän yhtälöt annetaan funktiolle `solve_ivp`.
- **Hajota matriisi kerran.** Kun askel ja aineen ominaisuudet ovat
  vakioita, matriisi ei muutu. Hajotelma lasketaan kerran, ja jokainen
  askel on pelkkä takaisinsijoitus (luku 10).
- **Tarkista Biot'n luku ennen mallin rakentamista.** Jos se on pieni,
  tavallinen differentiaaliyhtälö riittää.

## Itsearviointi

- Osaat selittää, miksi paikan suhteen diskretoitu lämpöyhtälö on
  jäykkä yhtälöryhmä ja miten jäykkyys kasvaa hilan tihentyessä.
- Osaat johtaa eksplisiittisen menetelmän stabiilisuusrajan
  sahalaitamuodon kertoimesta ja kertoa, mitä rajan ylitys tekee.
- Osaat toteuttaa theta-menetelmän kolmilävistäjäisellä ratkaisijalla
  ja mitata sen kertaluvun ajassa.
- Osaat selittää, miksi Crank–Nicolson värähtelee epäjatkuvalla
  alkutilalla, ja tiedät, miten se vältetään.
- Osaat toteuttaa konvektioreunaehdon ja päättää Biot'n luvusta,
  riittääkö yhden lämpötilan malli.
