# Paine ja porrastettu hila

Tähän asti virtaus on ollut annettu. Nyt se pitää ratkaista, ja vastaan
tulee yhtälöiden toinen erikoisuus: paineelle ei ole omaa yhtälöä. Tässä
luvussa selvitetään, mistä paine määräytyy, miksi paine ja nopeus
tallennetaan hilassa eri paikkoihin ja miten mistä tahansa
nopeuskentästä tehdään lähteetön. Seuraava luku kokoaa osista
virtausratkaisijan.

## Paineen tehtävä

Kirjoitetaan yhtälöt vielä kerran:

$$\frac{\partial \mathbf u}{\partial t}
  = -\nabla\cdot(\mathbf u\,\mathbf u) + \nu\nabla^2\mathbf u - \nabla p,
  \qquad \nabla\cdot\mathbf u = 0.$$

Liikemäärän yhtälö kertoo, miten nopeus muuttuu ajassa. Jatkuvuusyhtälö
ei kerro minkään muuttumisesta: se on **rajoite**, jonka nopeuden on
toteutettava joka hetki. Paineella ei ole aikaderivaattaa missään.

Paine on se kenttä, joka saa rajoitteen toteutumaan. Jos advektio ja
viskositeetti yrittävät kasata nestettä johonkin, paine nousee siellä
juuri sen verran, että sen gradientti työntää ylimäärän pois. Kun
liikemäärän yhtälöstä otetaan divergenssi ja vaaditaan, että nopeus
pysyy lähteettömänä, paineelle saadaan Poissonin yhtälö

$$\nabla^2 p = -\nabla\cdot\bigl(\nabla\cdot(\mathbf u\,\mathbf u)\bigr).$$

Kolme seurausta:

- Paine on **elliptinen**: muutos yhdessä kohdassa vaikuttaa heti
  koko alueeseen. Kokoonpuristumattomassa nesteessä ääni kulkee
  äärettömän nopeasti.
- Joka aika-askeleella on ratkaistava koko alueen yhtälöryhmä, vaikka
  muu olisi eksplisiittistä. Tämä on virtauslaskennan kallein osa.
- Vain paineen gradientti vaikuttaa. Paineen taso on mielivaltainen,
  ellei reunaehto kiinnitä sitä.

## Shakkilautaongelma

Luontevinta olisi tallentaa $u$, $v$ ja $p$ samoihin pisteisiin, ruutujen
keskelle, ja laskea painegradientti keskeisdifferenssillä. Silloin
ruudun oma paine ei vaikuta sen omaan gradienttiin lainkaan, vaan
gradientti näkee vain joka toisen ruudun.

```{.python tiedosto="esimerkit/06-shakkilauta.py" osa="kentta"}
```

```{.python tiedosto="esimerkit/06-shakkilauta.py" osa="gradientit"}
```

```{.tuloste tiedosto="esimerkit/06-shakkilauta.odotettu" rivit="1-3"}
```

Painekenttä, joka vaihtelee ruudusta toiseen välillä $-1 \dots 1$, on
samojen pisteiden gradientille näkymätön. Liikemäärän yhtälö ei tunne
sitä, joten se voi kasvaa ratkaisuun vapaasti. Sama näkyy
paineyhtälössä: lasketaan, kuinka monta erilaista painekenttää
diskreetti operaattori $\nabla\cdot\nabla$ kuvaa nollaksi.

```{.python tiedosto="esimerkit/06-shakkilauta.py" osa="nolla-avaruus"}
```

```{.tuloste tiedosto="esimerkit/06-shakkilauta.odotettu" rivit="4-5"}
```

Yksi näkymätön kenttä on aina: vakio, eli paineen taso. Samoissa
pisteissä niitä on neljä: vakio ja kolme shakkilautakuviota (raidat
kumpaankin suuntaan ja ruudukko). Ohjelma, joka on tehty näin,
tuottaa painekenttiä, joissa on sahalaitaa ilman fysikaalista syytä.

## Porrastettu hila

Ratkaisu on vuodelta 1965: tallennetaan muuttujat eri paikkoihin.
**Porrastetussa hilassa** (*staggered grid*) paine on ruutujen keskellä,
vaakanopeus $u$ ruutujen pystypinnoilla ja pystynopeus $v$
vaakapinnoilla.

![Porrastettu hila. Jokainen nopeus on kahden paineen puolivälissä, ja
jokaisen ruudun pinnoilla on juuri ne nopeudet, joita sen massatase
tarvitsee.](kuvat/hila.png){width=85%}

Järjestely on sama kuin luvun 3 kirjastossa, jossa pitoisuus oli
keskellä ja nopeudet pinnoilla. Siitä seuraa kaksi asiaa.

- Ruudun **divergenssi** lasketaan sen neljästä pintanopeudesta ilman
  mitään interpolointia: se on täsmälleen ruudun massatase.
- Nopeuden $u$ kohdalla **painegradientti** on kahden vierekkäisen
  paineen erotus. Shakkilautakuvio tuottaa suurimman mahdollisen
  gradientin, joten se ei voi piiloutua.

```{.python tiedosto="esimerkit/06-projektio.py" osa="operaattorit"}
```

Paineyhtälön matriisi on divergenssi gradientista, ja se on tuttu:
viiden pisteen kaava, jonka reunarivit kertovat, ettei seinän läpi ole
vuota. Näin rakennettuna diskreetti Laplacen operaattori on *täsmälleen*
diskreetti divergenssi diskreetistä gradientista. Tämä yhteensopivuus
on porrastetun hilan varsinainen etu, ja seuraava koe nojaa siihen.

## Projektio

Mikä tahansa nopeuskenttä voidaan jakaa kahteen osaan: lähteettömään
kenttään ja jonkin potentiaalin gradienttiin. Tämä on **Helmholtzin
hajotelma**. Lähteetön osa löydetään ratkaisemalla Poissonin yhtälö:

1. Lasketaan kentän $\mathbf u^*$ divergenssi.
2. Ratkaistaan $\nabla^2\varphi = \nabla\cdot\mathbf u^*$.
3. Vähennetään gradientti: $\mathbf u = \mathbf u^* - \nabla\varphi$.

Tulos on lähteetön, koska
$\nabla\cdot\mathbf u = \nabla\cdot\mathbf u^* - \nabla^2\varphi = 0$.
Operaatiota sanotaan **projektioksi**: kentästä poistetaan se osa, joka
rikkoo massan taseen, ja muu jätetään koskematta.

```{.python tiedosto="esimerkit/06-projektio.py" osa="projektio"}
```

Kokeessa rakennetaan kenttä, jonka hajotelma tunnetaan. Pyörre tehdään
virtafunktiosta, jolloin se on lähteetön jo hilalla, ja sen päälle
lisätään lähde–nielu-kenttä, joka on erään potentiaalin gradientti.

```{.python tiedosto="esimerkit/06-projektio.py" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/06-projektio.odotettu"}
```

![Projektio. Väri on divergenssi: ruskeissa ruuduissa neste lähtee,
sinisissä kasaantuu. Keskellä poistettu osa, oikealla jäljelle jäänyt
lähteetön pyörre.](kuvat/projektio.png){width=95%}

Projektio palauttaa alkuperäisen pyörteen pyöristystarkkuudella, ja
divergenssi on sen jälkeen nolla jokaisessa ruudussa. Tämä ei ole
likiarvo, joka paranisi hilaa tihentämällä: se on täsmällinen millä
tahansa hilalla, koska operaattorit sopivat yhteen.

Liike-energiat summautuvat kuin suorakulmaisen kolmion sivut. Lähteetön
osa ja gradienttiosa ovat siis toisiaan vastaan kohtisuorassa, ja
projektio on kohtisuora projektio myös geometrisessa mielessä: se
valitsee lähteettömistä kentistä sen, joka on lähinnä alkuperäistä.

Potentiaali on määrätty vain vakiota vaille, ja koodi kiinnittää
yhden ruudun arvon. Syy on sama kuin eristetyn kappaleen lämpötilassa:
kun yhtään reunaa ei ole kiinnitetty, matriisi on singulaarinen.
Yhtälöllä on ratkaisu vain, jos oikean puolen summa on nolla, ja
suljetussa laatikossa se on, koska seinien läpi ei virtaa mitään.

## Käytännössä

- **Paineyhtälö on laskennan hinta.** Tavallisessa
  kokoonpuristumattomassa laskussa suurin osa ajasta kuluu paineen
  ratkaisemiseen. Ratkaisijan valinta käsitellään luvussa 12.
- **Tarkista divergenssi.** Projektion jälkeen sen pitää olla
  ratkaisijan toleranssin luokkaa jokaisessa ruudussa. Suuri arvo
  jossain kertoo virheestä reunaehdossa tai liian löysästä
  toleranssista.
- **Paineen taso ei merkitse.** Suljetussa alueessa vain paine-erot
  ovat fysikaalisia. Kahta laskua verrattaessa paineet tasataan
  samaan vertailupisteeseen.
- **Sahalaitainen paine on diskretoinnin vika.** Jos painekentässä
  näkyy ruudun levyistä kuviota, paineen ja nopeuden kytkentä on
  rikki. Porrastetulla hilalla sitä ei synny.
- **Rakenteettomilla verkoilla muuttujat ovat samassa paikassa.**
  Porrastus ei yleisty mielivaltaisiin monitahokkaisiin, joten valmiit
  ohjelmat tallentavat kaiken ruutujen keskelle ja estävät
  shakkilaudan erityisellä pintanopeuden interpoloinnilla (luku 12).

## Itsearviointi

- Osaat selittää, miksi kokoonpuristumattomassa virtauksessa paineelle
  ei ole omaa kehitysyhtälöä ja mistä paine määräytyy.
- Osaat näyttää, miksi samoihin pisteisiin tallennetut paine ja nopeus
  päästävät shakkilautakuvion läpi.
- Osaat piirtää porrastetun hilan ja kirjoittaa ruudun divergenssin ja
  pinnan painegradientin.
- Osaat tehdä nopeuskentästä lähteettömän projektiolla ja tarkistaa
  tuloksen.
- Osaat selittää, miksi suljetun alueen paineyhtälö on singulaarinen
  ja miten se käsitellään.
