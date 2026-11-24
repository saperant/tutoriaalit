# Mallintaminen

Useimmat insinöörin differentiaaliyhtälöt syntyvät **taseesta**:

$$\frac{d}{dt}(\text{varasto}) = \text{sisään} - \text{ulos}.$$

Varasto voi olla suolan määrä säiliössä, varaus kondensaattorissa,
lämpöenergia kappaleessa tai yksilöiden määrä populaatiossa. Mallintaja
päättää, mikä on varasto, mitkä virtaukset siihen liittyvät ja miten
virtaukset riippuvat varastosta. Tässä luvussa tehdään neljä mallia, ja
huomataan, että ne ovat matemaattisesti samaa perhettä.

## Kasvu: eksponentiaalinen ja logistinen

Jos populaation jokainen yksilö tuottaa jälkeläisiä samalla nopeudella,
kasvu on verrannollinen kokoon: $N' = rN$. Ratkaisu on eksponentiaalinen,
ja kaksinkertaistumisaika on vakio $\ln 2 / r$ riippumatta siitä, kuinka
suuri populaatio jo on.

```{.python tiedosto="esimerkit/02-logistinen.py" osa="eksponentti"}
```

Rajoittamaton kasvu on hyvä malli vain lyhyellä aikavälillä. Ravinto,
tila tai markkinat rajoittavat kasvua, ja **logistinen malli** hidastaa
kasvua, kun koko lähestyy **kantokykyä** $K$:

$$N' = r N \left(1 - \frac{N}{K}\right).$$

Yhtälö on epälineaarinen, mutta SymPy ratkaisee sen. Ratkaisu kannattaa
aina tarkistaa sijoittamalla se takaisin yhtälöön: symbolinen ohjelma
voi palauttaa muodon, joka on oikea vain osalla parametrien arvoista.

```{.python tiedosto="esimerkit/02-logistinen.py" osa="logistinen"}
```

Kasvunopeus $rN(1 - N/K)$ on paraabeli, joka on suurimmillaan
puolessa kantokyvystä. Logistisen käyrän käännepiste on siis kohdassa
$N = K/2$, ja suurin kasvunopeus on $rK/4$. Tämä luku palaa luvussa 3,
kun kysytään, kuinka paljon kalakannasta voi kalastaa kestävästi.

```{.python tiedosto="esimerkit/02-logistinen.py" osa="kaannepiste"}
```

```{.tuloste tiedosto="esimerkit/02-logistinen.odotettu"}
```

## Sekoitussäiliö

Säiliössä on 200 litraa vettä, johon virtaa 5 l/min suolaliuosta, jonka
pitoisuus on 0,04 kg/l. Säiliö sekoittuu täydellisesti, ja ulos virtaa
sama määrä liuosta. Varasto on suolan määrä $x(t)$ kilogrammoina:

- **sisään** virtaa $q c = 0{,}2$ kg/min,
- **ulos** virtaa pitoisuus $x/V$ kertaa virtaama $q$.

```{.dot otsikko="Sekoitussäiliön tase: varasto, sisään- ja ulosvirtaus."}
digraph {
  rankdir=LR;
  sisaan [label="liuos sisään\nq c = 0,2 kg/min", shape=plaintext, style=""];
  sailio [label="säiliö\nx(t) kg suolaa\nV = 200 l"];
  ulos [label="liuos ulos\nq x / V", shape=plaintext, style=""];
  sisaan -> sailio;
  sailio -> ulos;
}
```

```{.python tiedosto="esimerkit/02-sailio.py" osa="tase"}
```

Tasapainossa sisään ja ulos virtaa yhtä paljon suolaa, joten säiliön
pitoisuus on sama kuin tulevan liuoksen: 8 kg 200 litrassa. Tasapainoon
päästään eksponentiaalisesti, ja **aikavakio** $\tau = V/q$ on aika,
jossa säiliön tilavuus ehtii vaihtua kerran.

```{.python tiedosto="esimerkit/02-sailio.py" osa="aikavakio"}
```

```{.tuloste tiedosto="esimerkit/02-sailio.odotettu"}
```

Insinöörin nyrkkisääntö on, että ensimmäisen kertaluvun järjestelmä on
asettunut noin viiden aikavakion jälkeen: jäljellä on alle prosentti
alkuperäisestä erosta.

## RC-piiri

Elektroniikan perusteissa (taito *Elektroniikan perusteet ja SPICE*)
kondensaattorin varautuminen ratkaistiin simuloimalla. Kirchhoffin
jännitelaista ja kondensaattorin yhtälöstä $i = C\,du_C/dt$ saadaan

$$RC \frac{du_C}{dt} + u_C = U.$$

Yhtälö on täsmälleen samaa muotoa kuin kahvin ja säiliön yhtälö: lähtö
lähestyy eksponentiaalisesti tasapainoarvoa aikavakiolla $\tau = RC$.

```{.python tiedosto="esimerkit/02-rc.py" osa="rc"}
```

```{.tuloste tiedosto="esimerkit/02-rc.odotettu"}
```

Logiikkapiirin tulo, jota RC-suodin ohjaa, vaihtaa tilaa noin $1{,}2\,\tau$
jälkeen. Tämä on se viive, jonka *Elektroniikan perusteiden*
kosketinvärähtelyn suodatus lisää painonapin signaaliin.

## Parametrit mittauksista

Mallin parametreja ei yleensä tiedetä etukäteen: kupin
jäähtymisvakio, säiliön todellinen tilavuus tai komponentin toleranssin
sisällä vaihteleva kapasitanssi. Ne **sovitetaan mittauksiin**.
Esimerkissä luvun 1 kahvin lämpötila on mitattu viiden minuutin välein
kohinaisella anturilla.

```{.python tiedosto="esimerkit/02-sovitus.py" osa="mittaukset"}
```

Sovitukseen on kaksi tapaa. `curve_fit` etsii suoraan mallin
parametrit, joilla mallin ja mittausten neliövirheiden summa on pienin,
ja antaa kovarianssimatriisista parametrien epävarmuuden. Toinen tapa
on **linearisoida** malli: koska $\ln(T - T_y) = \ln(T_0 - T_y) - kt$,
logaritmit ovat ajan suhteen suora, jonka kulmakerroin on $-k$.

```{.python tiedosto="esimerkit/02-sovitus.py" osa="sovitus"}
```

```{.tuloste tiedosto="esimerkit/02-sovitus.odotettu"}
```

Molemmat menetelmät löytävät todellisen arvon 0,045 epävarmuuden
rajoissa. Linearisointi on nopea ja havainnollinen, mutta se painottaa
virheitä väärin: kun $T$ lähestyy huoneen lämpötilaa, pieni mittausvirhe
muuttuu logaritmissa suureksi. Suora epälineaarinen sovitus on siksi
oletusvalinta, ja linearisointia käytetään alkuarvauksen saamiseen.

## Mallin anatomia

Kaikki tämän luvun lineaariset mallit ovat muotoa

$$\tau \frac{dy}{dt} + y = y_\infty,$$

missä $y_\infty$ on tasapainoarvo ja $\tau$ aikavakio. Ratkaisu on aina
$y(t) = y_\infty + (y_0 - y_\infty)\,e^{-t/\tau}$. Kun tunnistaa mallista
nämä kaksi lukua, tietää vastauksen laskematta.

| Järjestelmä | Varasto $y$ | Aikavakio $\tau$ | Tasapaino $y_\infty$ |
|-------------|-------------|-------------------|----------------------|
| kahvikuppi | lämpötila | $1/k$ | huoneen lämpötila |
| sekoitussäiliö | suolan määrä | $V/q$ | $c V$ |
| RC-piiri | jännite $u_C$ | $RC$ | syöttöjännite $U$ |
| lämpömittari | lukema | anturin lämpökapasiteetti / johtavuus | mitattava lämpötila |

## Käytännössä

- **Aloita taseesta ja yksiköistä.** Kirjoita varasto ja virtaukset
  yksikköineen. Jos yhtälön termeillä on eri yksiköt, malli on väärin.
- **Tunnista aikavakio ennen ratkaisemista.** Se kertoo, kuinka nopeasti
  järjestelmä reagoi, ja millä aika-askeleella simulointi kannattaa
  tehdä.
- **Tarkista ratkaisu sijoittamalla.** `sp.checkodesol` tai suora
  sijoitus paljastaa symbolisen ohjelman yllätykset, kuten
  parametrialueen, jolla ratkaisu ei päde.
- **Pidä parametrit symboleina mahdollisimman pitkään.** Yleinen
  ratkaisu näyttää rakenteen ja kertoo, mihin parametriin tulos on
  herkkä; numeroarvot sijoitetaan vasta lopuksi.

## Itsearviointi

- Osaat muodostaa tasemallin sanallisesta kuvauksesta ja tarkistaa sen
  yksiköt.
- Osaat ratkaista eksponentiaalisen ja logistisen kasvun mallin ja
  tulkita kaksinkertaistumisajan ja kantokyvyn.
- Osaat tunnistaa ensimmäisen kertaluvun mallista aikavakion ja
  tasapainoarvon ja kirjoittaa ratkaisun suoraan niiden avulla.
- Osaat ratkaista mallin SymPyllä ja tarkistaa ratkaisun sijoittamalla.
- Osaat sovittaa mallin parametrin mittauksiin `curve_fit`-funktiolla ja
  arvioida sen epävarmuuden.
