# Ensimmäisen kertaluvun yhtälöt

Ensimmäisen kertaluvun yhtälössä esiintyy vain ensimmäinen derivaatta:
$y' = f(t, y)$. Kaksi ratkaisutekniikkaa kattaa suurimman osan
käytännön tapauksista: **erottelu** separoituville yhtälöille ja
**integroiva tekijä** lineaarisille. Kun kumpikaan ei auta, yhtälöstä
saa silti paljon tietoa: **suuntakenttä** näyttää ratkaisujen muodon ja
**tasapainopisteiden** analyysi niiden pitkän aikavälin käytöksen.

## Separoituvat yhtälöt

Yhtälö on **separoituva**, jos oikea puoli on tulo $g(t)\,h(y)$. Silloin
muuttujat voi erotella eri puolille ja integroida:

$$\frac{dy}{dt} = g(t)\,h(y) \quad\Longrightarrow\quad
\int \frac{dy}{h(y)} = \int g(t)\,dt + C.$$

Esimerkiksi $y' = t\,y$ antaa $\ln|y| = t^2/2 + C$ eli
$y = C' e^{t^2/2}$. Vakio määräytyy alkuehdosta. SymPyn `checkodesol`
tarkistaa, että ratkaisu toteuttaa yhtälön.

```{.python tiedosto="esimerkit/03-separoituva.py" osa="erottelu"}
```

Epälineaarisen yhtälön ratkaisu voi lakata olemasta äärellisessä
ajassa, vaikka yhtälö näyttää harmittomalta. Yhtälön $y' = y^2$ ratkaisu
alkuehdolla $y(0) = 1$ on $1/(1-t)$, joka kasvaa rajatta hetkellä
$t = 1$. Ilmiö on **räjähtäminen** (*blow-up*), ja numeerinen ratkaisija
ilmoittaa siitä askeleen pienenemisenä tai virheenä.

```{.python tiedosto="esimerkit/03-separoituva.py" osa="rajahtaa"}
```

```{.tuloste tiedosto="esimerkit/03-separoituva.odotettu"}
```

## Lineaarinen yhtälö ja integroiva tekijä

**Lineaarinen** ensimmäisen kertaluvun yhtälö on muotoa

$$y' + p(t)\,y = q(t).$$

Kun yhtälö kerrotaan **integroivalla tekijällä**
$\mu(t) = e^{\int p\,dt}$, vasen puoli on tulon derivaatta
$(\mu y)'$, ja yhtälön voi integroida suoraan:

$$y = \frac{1}{\mu} \left( \int \mu\,q\,dt + C \right).$$

Esimerkki tekee saman askel kerrallaan SymPyllä ja vertaa tulosta
`dsolve`-funktioon. Muodot näyttävät erilaisilta, mutta erotuksen
sieventäminen nollaksi osoittaa, että ne ovat sama funktio.

```{.python tiedosto="esimerkit/03-lineaarinen.py" osa="tekija"}
```

```{.python tiedosto="esimerkit/03-lineaarinen.py" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-lineaarinen.odotettu"}
```

Lineaarisen yhtälön ratkaisu koostuu aina kahdesta osasta: homogeenisen
yhtälön ratkaisusta $C/\mu$, joka riippuu alkuehdosta, ja
**yksityisratkaisusta**, joka riippuu herätteestä $q$. Sama rakenne
toistuu toisen kertaluvun yhtälöissä luvussa 4.

## Suuntakenttä

Yhtälö $y' = f(t, y)$ kertoo ratkaisukäyrän kulmakertoimen jokaisessa
pisteessä. Kun kulmakertoimet piirretään lyhyinä janoina, syntyy
**suuntakenttä**, ja ratkaisut ovat käyriä, jotka kulkevat janojen
suuntaisesti. Alla on logistisen mallin suuntakenttä ja neljä ratkaisua
eri alkuarvoista.

![Logistisen yhtälön $N' = 0{,}5\,N(1 - N/1000)$ suuntakenttä ja
ratkaisuja. Kaikki positiiviset ratkaisut lähestyvät kantokykyä
$K$.](kuvat/suuntakentta.png){width=78%}

Suuntakentästä näkee ratkaisua laskematta, että $N = 0$ ja $N = K$ ovat
vakioratkaisuja, että ratkaisut eivät leikkaa toisiaan ja että
kantokyvyn yläpuolelta lähtevä populaatio pienenee kohti kantokykyä.

## Tasapainot ja stabiilisuus

**Autonomisessa** yhtälössä $y' = f(y)$ oikea puoli ei riipu ajasta.
Sen **tasapainopisteet** ovat yhtälön $f(y^*) = 0$ ratkaisut:
vakioratkaisut, joihin järjestelmä voi jäädä. Tasapaino on

- **stabiili**, jos $f'(y^*) < 0$: pieni poikkeama pienenee, koska
  tasapainon yläpuolella $f < 0$ ja alapuolella $f > 0$;
- **epästabiili**, jos $f'(y^*) > 0$: poikkeama kasvaa.

Jos $f'(y^*) = 0$, linearisointi ei ratkaise asiaa, ja tasapainon laatu
selviää vain tutkimalla $f$:n merkkiä tasapainon molemmin puolin.

Esimerkissä kalakanta kasvaa logistisesti, ja siitä kalastetaan
vakiomäärä $h$ tonnia vuodessa. Kalastus siirtää paraabelia alaspäin,
ja tasapainot lähestyvät toisiaan:

```{.python tiedosto="esimerkit/03-tasapainot.py" osa="tasapainot"}
```

```{.python tiedosto="esimerkit/03-tasapainot.py" osa="kriittinen"}
```

```{.tuloste tiedosto="esimerkit/03-tasapainot.odotettu"}
```

Kalastuksen kasvaessa stabiili ja epästabiili tasapaino lähestyvät
toisiaan ja yhtyvät, kun $h = rK/4$. Pienikin lisäys kalastukseen
hävittää tasapainot kokonaan, ja kanta romahtaa. Ilmiö on
**haarautuminen** (*bifurkaatio*): parametrin pieni muutos muuttaa
järjestelmän laadullista käytöstä. Käytännössä parametrit tunnetaan
epätarkasti, joten kalastuskiintiö kannattaa asettaa selvästi kriittisen
arvon alapuolelle.

## Olemassaolo ja yksikäsitteisyys

Onko alkuarvotehtävällä $y' = f(t, y)$, $y(t_0) = y_0$ ratkaisu, ja onko
se ainoa? **Picardin–Lindelöfin lause** takaa yksikäsitteisen ratkaisun
alkupisteen ympäristössä, jos $f$ on jatkuva ja **Lipschitz-jatkuva**
$y$:n suhteen. Käytännössä riittää, että $\partial f/\partial y$ on
jatkuva.

Ehto ei ole vain teoreettinen. Yhtälön $y' = \sqrt{|y|}$ oikean puolen
derivaatta ei ole rajoitettu nollan lähellä, ja alkuehdolla $y(0) = 0$
ratkaisuja on useita: sekä $y = 0$ että $y = t^2/4$ kelpaavat.

```{.python tiedosto="esimerkit/03-yksikasitteisyys.py" osa="kaksi"}
```

```{.tuloste tiedosto="esimerkit/03-yksikasitteisyys.odotettu"}
```

Numeerinen ratkaisija valitsee yhden ratkaisuista hiljaa, ja alkuarvon
pieni muutos vaihtaa valinnan. Fysikaalisessa mallissa
epäyksikäsitteisyys kertoo yleensä, että malli on yksinkertaistettu
liikaa, esimerkiksi kitka tai vuoto on jätetty pois.

## Samat laskut Maximalla

Maximan `ode2` tunnistaa ensimmäisen ja toisen kertaluvun yhtälöiden
tavalliset tyypit, ja `ic1` sijoittaa alkuehdon. Yleisessä ratkaisussa
integroimisvakio on `%c`.

```{.maxima tiedosto="esimerkit/maxima/03-ensimmainen.mac" osa="ensimmainen"}
```

```{.tuloste tiedosto="esimerkit/maxima/03-ensimmainen.odotettu"}
```

## Käytännössä

- **Tunnista tyyppi ennen ratkaisemista.** Separoituva, lineaarinen vai
  ei kumpikaan? Lineaarisen yhtälön ratkaisu on aina homogeeninen osa
  plus yksityisratkaisu.
- **Piirrä suuntakenttä, kun yhtälö on uusi.** Se näyttää
  tasapainot, ratkaisujen suunnan ja mahdolliset räjähtämiset ennen
  kuin yhtään ratkaisua lasketaan.
- **Analysoi tasapainot derivaatan merkillä.** Stabiilisuus kertoo,
  mihin järjestelmä päätyy, ja on usein tärkeämpi tieto kuin tarkka
  ratkaisu.
- **Varo parametrien kriittisiä arvoja.** Haarautumispisteen lähellä
  pieni mallivirhe muuttaa johtopäätöksen laadullisesti.

## Itsearviointi

- Osaat ratkaista separoituvan yhtälön erottelemalla ja tarkistaa
  ratkaisun SymPyllä.
- Osaat ratkaista lineaarisen ensimmäisen kertaluvun yhtälön
  integroivalla tekijällä.
- Osaat lukea suuntakenttää ja päätellä siitä ratkaisujen käytöksen.
- Osaat määrittää autonomisen yhtälön tasapainot ja niiden
  stabiilisuuden.
- Osaat selittää, milloin alkuarvotehtävän ratkaisu ei ole
  yksikäsitteinen, ja miksi sillä on käytännön merkitystä.
