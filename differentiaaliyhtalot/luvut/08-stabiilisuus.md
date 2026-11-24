# Stabiilisuus

Järjestelmä on **stabiili**, jos pieni häiriö ei kasva rajatta. Lineaarisen
järjestelmän stabiilisuus on yksinkertainen sääntö: kaikkien napojen
(tilaesityksessä ominaisarvojen) reaaliosien pitää olla negatiivisia.
Säätötekniikassa kysymys on harvoin näin suora, koska navat riippuvat
suunnittelijan valitsemista parametreista. Tässä luvussa tutkitaan,
miten vahvistus vaikuttaa stabiilisuuteen ilman, että juuria tarvitsee
ratkaista, ja miten epälineaaristen järjestelmien tasapainot
luokitellaan.

## Takaisinkytkentä

Säädin mittaa lähtöä, vertaa sitä asetusarvoon ja ohjaa prosessia
erotuksen perusteella. Yksinkertaisin säädin on **P-säädin**, joka
kertoo erotuksen vahvistuksella $K$.

```{.dot otsikko="Takaisinkytketty säätö: P-säädin ja prosessi G(s)."}
digraph {
  rankdir=LR;
  r [label="asetusarvo R", shape=plaintext, style=""];
  e [label="+\n-", shape=circle, width=0.45, fixedsize=true];
  k [label="K"];
  g [label="G(s)"];
  y [label="lähtö Y", shape=plaintext, style=""];
  r -> e;
  e -> k [label="erotus"];
  k -> g;
  g -> y;
  g -> e [label="mittaus", constraint=false];
}
```

Suljetun silmukan siirtofunktio on

$$T(s) = \frac{K\,G(s)}{1 + K\,G(s)},$$

ja sen navat ovat **karakteristisen yhtälön** $1 + K\,G(s) = 0$ juuret.
Prosessille $G(s) = 1/(s(s+1)(s+2))$ karakteristinen polynomi on
$s^3 + 3s^2 + 2s + K$. Mikä vahvistus on liikaa?

## Routhin–Hurwitzin kriteeri

**Routhin–Hurwitzin kriteeri** kertoo, montako polynomin juurta on
oikeassa puolitasossa, ratkaisematta juuria. Polynomin kertoimista
muodostetaan taulukko: kaksi ensimmäistä riviä ovat parittomien ja
parillisten indeksien kertoimet, ja jokainen seuraava rivi lasketaan
kahdesta edellisestä ristikkäistuloilla. Ensimmäisen sarakkeen
merkinvaihtojen määrä on oikean puolitason juurten määrä.

```{.python tiedosto="esimerkit/08-routh.py" osa="routh"}
```

Kun vahvistus on symboli, taulukon ensimmäinen sarake antaa
stabiilisuusehdot epäyhtälöinä:

```{.python tiedosto="esimerkit/08-routh.py" osa="vahvistus"}
```

```{.tuloste tiedosto="esimerkit/08-routh.odotettu"}
```

Vahvistuksella $K = 6$ suljettu silmukka on stabiilisuuden rajalla:
napapari on imaginaariakselilla, ja järjestelmä värähtelee
vaimenematta. Suuremmilla vahvistuksilla kaksi napaa on oikeassa
puolitasossa, ja värähtely kasvaa. Tämä on säätötekniikan perusristiriita:
suuri vahvistus tekee säädöstä nopean ja tarkan, mutta liian suuri
vahvistus tekee siitä epästabiilin.

Käytännössä juuret lasketaan numeerisesti (`np.roots`), mutta Routhin
taulukko on edelleen hyödyllinen, kun halutaan stabiilisuusalue
parametrin funktiona tai kun polynomin kertoimissa on symboleja.

## Epälineaaristen tasapainojen luokittelu

Epälineaarisella järjestelmällä $\mathbf{x}' = \mathbf{f}(\mathbf{x})$
voi olla useita tasapainoja. Tasapainon $\mathbf{x}^*$ lähellä
järjestelmää approksimoi sen linearisointi

$$\mathbf{x}' \approx J(\mathbf{x}^*)\,(\mathbf{x} - \mathbf{x}^*),
\qquad J = \frac{\partial \mathbf{f}}{\partial \mathbf{x}},$$

missä $J$ on **Jacobin matriisi** (taito *Differentiaali- ja
integraalilaskenta*). Jacobin matriisin ominaisarvot luokittelevat
tasapainon kuten luvun 5 taulukko. **Hartmanin–Grobmanin lause** takaa,
että luokittelu on oikea, kun mikään ominaisarvo ei ole
imaginaariakselilla.

```{.python tiedosto="esimerkit/08-linearisointi.py" osa="jacobi"}
```

```{.tuloste tiedosto="esimerkit/08-linearisointi.odotettu"}
```

Vaimennetun heilurin alin asento on stabiili spiraali ja ylin asento
satulapiste, kuten luvun 5 vaihetasokuvassa. Ylin asento on
**satulapiste**: tasapaino, johon pääsee vain yhtä käyrää pitkin ja josta
pienikin poikkeama vie pois. Robotiikan ja säätötekniikan klassinen
tehtävä, käänteisen heilurin pitäminen pystyssä, on juuri tämän
satulapisteen stabilointi takaisinkytkennällä.

## Rajasyklit

Linearisointi kertoo tasapainon lähiympäristöstä, mutta epälineaarisella
järjestelmällä voi olla myös **rajasykli**: eristetty jaksollinen rata,
jota kohti naapuriradat kiertyvät. Klassinen esimerkki on **van der
Polin oskillaattori**

$$x'' - \mu\,(1 - x^2)\,x' + x = 0.$$

Pienellä amplitudilla vaimennustermi on negatiivinen ja syöttää
energiaa, suurella positiivinen ja kuluttaa sitä. Origon tasapaino on
epästabiili (Jacobin matriisin jälki on $\mu > 0$), mutta radat eivät
karkaa äärettömyyteen, vaan asettuvat samaan värähtelyyn alkuehdosta
riippumatta.

```{.python tiedosto="esimerkit/08-vanderpol.py" osa="vanderpol"}
```

```{.python tiedosto="esimerkit/08-vanderpol.py" osa="jakso"}
```

```{.tuloste tiedosto="esimerkit/08-vanderpol.odotettu"}
```

![Van der Polin oskillaattorin ($\mu = 1$) radat. Origon läheltä
lähtevä rata kiertyy ulospäin ja kaukaa lähtevä sisäänpäin, ja molemmat
päätyvät samalle rajasyklille.](kuvat/rajasykli.png){width=72%}

Rajasyklit ovat oskillaattorien perusta: elektroninen oskillaattori,
sydämen tahdistinsolut ja kellopiirien rengasoskillaattori värähtelevät
amplitudilla, jonka järjestelmä määrää itse. Lineaarisella
järjestelmällä rajasyklejä ei ole: keskuksen radat ovat jaksollisia,
mutta jokainen amplitudi on mahdollinen, ja pienikin mallivirhe saa
värähtelyn vaimenemaan tai kasvamaan.

## Käytännössä

- **Tarkista stabiilisuus napojen reaaliosista.** Kaikki negatiivisia:
  stabiili. Yksikin positiivinen: epästabiili. Imaginaariakselilla:
  rajatapaus, jossa pienikin mallivirhe ratkaisee.
- **Käytä Routhin taulukkoa parametrialueen etsimiseen.** Se antaa
  stabiilisuusehdon suoraan vahvistuksen funktiona.
- **Jätä vahvistusvaraa.** Malli on aina epätarkka; suunnittele
  selvästi stabiilisuusrajan sisäpuolelle.
- **Luokittele epälineaariset tasapainot Jacobin matriisilla.**
  Tarkista simuloimalla, kun ominaisarvo on lähellä
  imaginaariakselia.

## Itsearviointi

- Osaat muodostaa takaisinkytketyn järjestelmän karakteristisen
  polynomin.
- Osaat laatia Routhin taulukon ja päätellä siitä oikean puolitason
  juurten määrän ja stabiilisuusehdon.
- Osaat linearisoida epälineaarisen järjestelmän Jacobin matriisilla ja
  luokitella tasapainot.
- Osaat selittää, miksi suuri vahvistus voi tehdä säädöstä
  epästabiilin.
