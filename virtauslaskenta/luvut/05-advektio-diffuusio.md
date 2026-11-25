# Advektio ja diffuusio yhdessä

Todellisessa virtauksessa advektio ja diffuusio ovat mukana yhtä aikaa,
ja niiden suhde vaihtelee paikasta toiseen. Tässä luvussa selviää,
milloin edellisen luvun epästabiili keskeisdifferenssi onkin paras
valinta, mikä on hilan Péclet'n luku ja miksi vastavirtakaavio tekee
vinossa virtauksessa virheen, jota yksiulotteinen koe ei paljasta.

## Hilan Péclet'n luku

Tasapainotilassa virtaus kuljettaa ainetta oikealle ja diffuusio
levittää sitä takaisin:

$$u\,\frac{dc}{dx} = D\,\frac{d^2c}{dx^2},
  \qquad c(0) = 0, \quad c(1) = 1.$$

Tehtävän luonteen määrää **Péclet'n luku** $\mathrm{Pe} = uL/D$,
advektion suhde diffuusioon. Tarkka ratkaisu on
$c = (e^{\mathrm{Pe}\,x} - 1)/(e^{\mathrm{Pe}} - 1)$. Kun
$\mathrm{Pe}$ on suuri, pitoisuus on lähes nolla koko välillä ja nousee
arvoon yksi vasta ohuessa rajakerroksessa oikean reunan vieressä.
Kerroksen paksuus on $D/u$ eli $L/\mathrm{Pe}$.

```{.python tiedosto="esimerkit/05-peclet.py" osa="tehtava"}
```

Koodissa yhtälö on kerrottu luvulla $h^2/D$, jolloin jäljelle jää yksi
parametri: **hilan Péclet'n luku** $\mathrm{Pe}_h = uh/D$. Se vertaa
ruudun kokoa rajakerroksen paksuuteen.

```{.tuloste tiedosto="esimerkit/05-peclet.odotettu"}
```

![Rajakerros kahdella hilalla. Vasemmalla ruutu on rajakerrosta
paksumpi: keskeisdifferenssi heilahtaa negatiiviseksi ja vastavirta
levittää kerroksen. Oikealla ruutu on rajakerrosta ohuempi, ja
keskeisdifferenssi on lähes tarkka.](kuvat/peclet.png){width=95%}

Raja kulkee arvossa $\mathrm{Pe}_h = 2$.

- **Sen yläpuolella** keskeisdifferenssi heilahtelee: pitoisuus käy
  negatiivisena. Syyn näkee kertoimista. Myötävirran naapurin kerroin
  on $-1 + \mathrm{Pe}_h/2$, ja kun se muuttuu positiiviseksi, pisteen
  arvo ei enää ole naapuriensa painotettu keskiarvo.
- **Sen alapuolella** keskeisdifferenssi on rajattu ja toista
  kertalukua. Virhe pienenee neljäsosaan hilaa puolitettaessa.
- **Vastavirtakaavio** ei heilahtele millään arvolla, mutta sen virhe
  pienenee vain puoleen. Hilan Péclet'n luvulla 0,6 sen virhe on lähes
  kahdeksankertainen keskeisdifferenssiin verrattuna.

Diffuusio siis stabiloi keskeisdifferenssin, kunhan hila on niin tiheä,
että se erottaa rajakerroksen. Liikemäärän yhtälössä diffuusiokertoimen
paikalla on viskositeetti, ja sama luku on nimeltään **hilan Reynoldsin
luku** $uh/\nu$.

Käytännön ongelma on, että ehtoa $\mathrm{Pe}_h < 2$ ei yleensä voi
toteuttaa kaikkialla. Ilmavirtauksessa, jossa $u = 1$ m/s ja
$\nu = 1{,}5 \cdot 10^{-5}$ m²/s, se vaatisi 30 mikrometrin ruudut. Siksi
tarvitaan kaavioita, jotka sietävät suurta hilan Péclet'n lukua:
vastavirta, rajoittimet tai näiden sekoitus.

## Väärä diffuusio

Luvun 3 savuvana laskettiin vastavirtakaaviolla, ja sen leveys osui
teoriaan, vaikka hilan Péclet'n luku oli tiheimmälläkin hilalla 6.
Numeerista diffuusiota oli
runsaasti, mutta se vaikutti vain tuulen suuntaan, ja tasapainotilassa
tuulen suuntainen levitys ei näy vanan leveydessä.

Käännetään tuuli vinoon. Kaksiulotteinen vastavirtakaavio on kaksi
yksiulotteista: se levittää ainetta $x$-suuntaan kertoimella $uh/2$ ja
$y$-suuntaan kertoimella $vh/2$. Kun virtaus on kulmassa $\alpha$
hilaan nähden, osa tästä levityksestä on virtausta vastaan kohtisuoraa.
Kohtisuoran suunnan kerroin on

$$D_\perp = \frac{Uh}{2}\,\sin\alpha\,\cos\alpha\,(\sin\alpha + \cos\alpha),$$

ja sitä sanotaan **vääräksi diffuusioksi** (*false diffusion*). Se on
nolla, kun virtaus on hilan suuntainen, ja suurimmillaan 45 asteen
kulmassa.

```{.python tiedosto="esimerkit/05-vino.py" osa="tehtava"}
```

```{.python tiedosto="esimerkit/05-vino.py" osa="leveys"}
```

```{.tuloste tiedosto="esimerkit/05-vino.odotettu"}
```

![Sama savuvana hilan suuntaisessa ja vinossa tuulessa sekä vanan
poikkileikkaus mittauskohdassa. Fysiikka on molemmissa sama; ero on
kaavion tuottamaa.](kuvat/vino.png){width=95%}

Laskettu leveys vastaa kaavan ennustetta jokaisella rivillä, joten
levenemisen syy on tunnistettu oikein. Seuraukset ovat vakavia:

- Hilalla 80 × 80 ja 45 asteen kulmassa väärä diffuusio on 2,25 kertaa
  fysikaalinen. Vana on 1,8 kertaa liian leveä ja sen huippupitoisuus
  vastaavasti liian pieni.
- Hilan tihentäminen kaksinkertaiseksi vain puolittaa virheen. Vielä
  hilalla 320 × 320 väärä diffuusio on yli puolet fysikaalisesta.
- Tulos näyttää moitteettomalta: sileä, positiivinen ja tase kohdallaan.
  Mikään yksittäisessä ajossa ei paljasta virhettä.

Keskeisdifferenssi antaa samalla hilalla oikean leveyden, mutta lähteen
ympärillä pitoisuus heilahtelee rajusti negatiivisen puolelle, koska
hilan Péclet'n luku on 6.

## Mitä tälle tehdään

Kumpikaan peruskaavio ei siis kelpaa sellaisenaan, kun advektio
hallitsee. Keinoja on kolme, ja oikeissa ohjelmissa käytetään kaikkia.

1. **Parempi kaavio.** Luvun 4 rajoitettu toisen kertaluvun kaavio
   yleistyy tasoon suunta kerrallaan. Sen numeerinen diffuusio on
   murto-osa vastavirtakaavion diffuusiosta, eikä se heilahtele.
2. **Hila virtauksen suuntaan.** Väärä diffuusio häviää, kun ruutujen
   pinnat ovat virtauksen suuntaiset. Rajakerroksissa ja
   putkivirtauksissa hila rakennetaan siksi seinän ja päävirtauksen
   mukaan.
3. **Tiheä hila sinne, missä pitoisuus muuttuu jyrkästi.**
   Virhe on verrannollinen sekä ruudun kokoon että ratkaisun
   kaarevuuteen.

| Pinnan arvo | Kertaluku | Rajattu | Käyttö |
|---|---|---|---|
| keskiarvo (keskeisdifferenssi) | 2 | vain kun $\mathrm{Pe}_h < 2$ | tarkat laskut tiheällä hilalla |
| tulosuunnan ruutu (vastavirta) | 1 | aina | laskun käynnistys, vianetsintä |
| sekoitus kertoimella $\gamma$ | 1–2 | lähes | kompromissi; $\gamma$ valitaan hilan Péclet'n luvun mukaan |
| rajoitettu toinen kertaluku | 2 sileässä | aina | yleinen oletus |

Luvun 7 virtausratkaisijassa on kaksi ensimmäistä ja niiden sekoitus.
Sekoituksessa pinnan arvo on keskiarvon ja tulosuunnan arvon painotettu
summa, ja paino $\gamma$ on parametri nollan ja yhden väliltä.

## Kaksi rajaa aika-askeleelle

Kun yhtälö ratkaistaan ajassa eksplisiittisesti, kumpikin termi
asettaa oman rajansa, ja pienempi määrää:

$$\Delta t \le \frac{h}{u} \quad\text{(advektio)}, \qquad
  \Delta t \le \frac{h^2}{2D} \quad\text{(diffuusio, tasossa } \frac{h^2}{4D}).$$

Rajojen suhde on hilan Péclet'n luku. Kun se on suuri, advektio määrää
askeleen ja askel pienenee samassa suhteessa kuin ruutu. Kun se on
pieni, diffuusio määrää ja askel pienenee ruudun koon neliössä, jolloin
diffuusio kannattaa käsitellä implisiittisesti kuten lämpöyhtälössä.

## Käytännössä

- **Laske hilan Péclet'n tai Reynoldsin luku.** Se kertoo, erottaako
  hila rajakerroksen ja mikä kaavio on mahdollinen. Valmiissa
  ohjelmassa sen voi piirtää kenttänä.
- **Vinossa virtauksessa vastavirtakaavio valehtelee.** Jos virtaus
  kulkee ruutujen poikki ja pitoisuudella on jyrkkä reuna, ensimmäisen
  kertaluvun tulos on liian sileä. Leikkauskerrokset, suihkut ja vanat
  ovat tyypillisiä uhreja.
- **Vertaa kahta kaaviota.** Jos vastavirran ja toisen kertaluvun
  kaavion tulokset eroavat selvästi, hila on liian harva
  ensimmäiselle. Vertailu on halpa tapa löytää numeerinen diffuusio.
- **Heilahtelu kertoo liian harvasta hilasta.** Keskeisdifferenssin
  sahalaita on varoitus siitä, että jossain on rajakerros, jota hila ei
  erota. Vastavirtakaavio piilottaa saman ongelman.
- **Suuntaa hila.** Rakenteinen, virtauksen suuntainen hila seinien
  lähellä on tarkempi kuin samankokoinen mielivaltainen hila.

## Itsearviointi

- Osaat laskea hilan Péclet'n luvun ja kertoa, mitä sen arvo kaksi
  tarkoittaa keskeisdifferenssille.
- Osaat selittää, miksi vastavirtakaavio on aina rajattu mutta vain
  ensimmäistä kertalukua.
- Osaat selittää, mistä väärä diffuusio syntyy, milloin se on
  suurimmillaan ja miten sen suuruus arvioidaan.
- Osaat nimetä kolme tapaa pienentää numeerista diffuusiota.
- Osaat päätellä hilan Péclet'n luvusta, kumpi raja määrää
  eksplisiittisen aika-askeleen.
