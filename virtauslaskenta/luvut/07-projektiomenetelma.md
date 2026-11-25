# Projektiomenetelmä

Edellisen luvun projektio teki annetusta kentästä lähteettömän. Kun se
tehdään jokaisen aika-askeleen lopuksi, saadaan **projektiomenetelmä**,
kokoonpuristumattoman virtauksen yksinkertaisin toimiva ratkaisutapa.
Tässä luvussa siitä rakennetaan kirjasto `virta`, tarkistetaan se
tehtävällä, jonka tarkka ratkaisu tunnetaan, ja selvitetään, kuinka
pitkän aika-askeleen se sietää.

## Aika-askel kolmessa vaiheessa

Menetelmä jakaa askeleen osiin sen mukaan, mikä termi on vaikea:

1. **Ennustus.** Liikemäärän yhtälö ratkaistaan ilman painetta:
   $\mathbf u^* = \mathbf u^n + \Delta t\,\bigl(-\nabla\cdot(\mathbf u\mathbf u)
   + \nu\nabla^2\mathbf u\bigr)$. Tulos $\mathbf u^*$ ei ole lähteetön.
2. **Paineyhtälö.** Ratkaistaan
   $\nabla^2 p = \nabla\cdot\mathbf u^*/\Delta t$.
3. **Korjaus.** $\mathbf u^{n+1} = \mathbf u^* - \Delta t\,\nabla p$.

Vaiheet 2 ja 3 ovat projektio, jossa potentiaali on
$\varphi = \Delta t\,p$. Paine on siis juuri se voima, joka aika-askeleen
aikana tarvitaan pitämään nopeus lähteettömänä.

```{.dot otsikko="Projektiomenetelmän aika-askel. Paineyhtälö on ainoa vaihe, jossa ratkaistaan yhtälöryhmä."}
digraph {
  rankdir=LR;
  node [shape=box];
  a [label="u(n)\nlähteetön"];
  b [label="ennustus:\nu* ilman\npainetta"];
  c [label="paineyhtälö:\nlap(p) =\ndiv(u*) / dt"];
  d [label="korjaus:\nu* - dt grad(p)"];
  e [label="u(n+1)\nlähteetön"];
  a -> b -> c -> d -> e;
}
```

## Kirjasto

Tehtävä kuvataan kolmella tietorakenteella: alueen reunat, itse tehtävä
ja ratkaisun tila. Reunaehdot käsitellään luvussa 8; tässä luvussa
kaikki reunat ovat symmetriatasoja.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="tehtava"}
```

Divergenssi on edellisestä luvusta. Funktio `vuo` laskee kuljetettavan
suureen vuon pinnan läpi ja sisältää luvun 5 sekoituksen: arvolla
$\gamma = 0$ pinnan arvo on keskiarvo, arvolla $\gamma = 1$ tulosuunnan
arvo.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="operaattorit"}
```

Ennustusvaiheen ydin on liikemäärän tase. Porrastetussa hilassa
nopeuden $u$ kontrollitilavuus on puoli ruutua sivussa painehilasta: sen
pystypinnat kulkevat ruutujen keskipisteiden ja vaakapinnat ruutujen
kulmien kautta. Vuo $uu$ lasketaan siksi ruutujen keskellä ja vuo $uv$
kulmissa. Kummassakin kuljettava nopeus on kahden lähimmän arvon
keskiarvo.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="kiihtyvyys"}
```

Koodi on pitkä mutta toistaa yhtä kaavaa neljästi: vuon erotus pintojen
välillä jaettuna ruudun koolla. Taulukoissa `ue` ja `ve` on haamurivit
alueen ulkopuolella reunaehtoja varten.

Projektio on luvun 6 funktio yleistettynä. Paineyhtälön matriisi ei
muutu askeleesta toiseen, joten se kootaan ja hajotetaan tekijöihin
kerran, ja jokainen askel on vain takaisinsijoitus.

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="projektio"}
```

```{.python tiedosto="esimerkit/07-virta/virta.py" osa="askel"}
```

## Tarkistus: Taylorin ja Greenin pyörre

Navier–Stokesin yhtälöille tunnetaan harvoja tarkkoja ratkaisuja, joissa
advektio, paine ja viskositeetti ovat kaikki mukana. **Taylorin ja
Greenin pyörre** on niistä käytetyin:

$$u = \sin x\,\cos y\;e^{-2\nu t}, \qquad
  v = -\cos x\,\sin y\;e^{-2\nu t}.$$

Pyörteen muoto säilyy ja viskositeetti vaimentaa sitä eksponentiaalisesti.
Neliössä $[0, \pi]^2$ nopeus on reunoilla reunan suuntainen eikä sen
suuntainen komponentti muutu reunaa vastaan kohtisuoraan, joten reunat
ovat symmetriatasoja.

```{.python tiedosto="esimerkit/07-virta/main.py" osa="tarkka"}
```

```{.python tiedosto="esimerkit/07-virta/main.py" osa="ajo"}
```

```{.tuloste tiedosto="esimerkit/07-virta.odotettu" rivit="1-8"}
```

![Vasemmalla pyörteen pyörteisyys ja virtaviivat. Keskellä liike-energian
vaimeneminen, oikealla virhe hilan tiheyden
funktiona.](kuvat/taylor-green.png){width=95%}

Divergenssi on pyöristysvirheen tasolla, energia vaimenee oikeaa tahtia,
ja virhe pienenee neljäsosaan, kun hila tihennetään kaksinkertaiseksi.
Paikan diskretointi on siis toista kertalukua, kuten keskeisdifferenssiltä
odotetaan. Yksi tehtävä tarkistaa kerralla advektion, diffuusion,
paineen ja niiden yhteispelin; jos yhdessäkin vuossa olisi väärä
indeksi, kertaluku putoaisi.

## Aika-askel: Euler ja Adams–Bashforth

Ennustusvaiheen voi ottaa Eulerin menetelmällä, jolloin kiihtyvyys
lasketaan nykyisestä nopeudesta. Toinen vaihtoehto on **toisen
kertaluvun Adams–Bashforth** (AB2), joka käyttää myös edellisen
askeleen kiihtyvyyttä:

$$\mathbf u^* = \mathbf u^n + \Delta t\left(\tfrac32\,\mathbf a^n
  - \tfrac12\,\mathbf a^{n-1}\right).$$

Se maksaa yhden tallennetun kentän eikä yhtään lisälaskentaa.

```{.tuloste tiedosto="esimerkit/07-virta.odotettu" alkaen="ajan kertaluku"}
```

Euler on ensimmäistä ja AB2 toista kertalukua ajassa, ja samalla
askelmäärällä AB2:n virhe on vähintään parikymmentä kertaa pienempi.

Tärkeämpi ero on stabiilisuus. Luvussa 4 nähtiin, että keskeisdifferenssi
ja Euler yhdessä ovat puhtaalle advektiolle aina epästabiili pari.
Viskositeetti pelastaa tilanteen vain, jos

$$\Delta t \le \frac{2\nu}{U^2},$$

ja ehto kiristyy nopeasti, kun viskositeetti pienenee. AB2:n
stabiilisuusalue ulottuu lähemmäs puhdasta advektiota, ja sille riittää
käytännössä tavallinen Courantin luvun ehto. Koe on kaksi sisäkkäistä
pyörrettä lähes kitkattomassa nesteessä. Liike-energia voi fysikaalisesti
vain pienentyä.

```{.python tiedosto="esimerkit/07-aika.py" osa="tehtava"}
```

```{.tuloste tiedosto="esimerkit/07-aika.odotettu"}
```

![Liike-energia ajan funktiona. Eulerin menetelmällä energia alkaa
kasvaa, ensin huomaamatta ja sitten räjähtäen. AB2 seuraa oikeaa
vaimenemista samalla askeleella, jolla Euler
hajoaa.](kuvat/aika.png){width=70%}

Eulerin menetelmällä tulos huononee jo ennen kuin lasku hajoaa: askeleella
0,01 energia on lopussa suurempi kuin viitearvo, eli kaavio tuottaa
energiaa. AB2 antaa oikean tuloksen askeleella 0,04, joka on sata kertaa
Eulerin rajaa pidempi, ja hajoaa vasta, kun Courantin luku lähestyy
yhtä. Kirjaston apufunktio `vakaa_askel` valitsee askeleen näistä
rajoista: AB2:lle Courantin luku 0,3 ja diffuusion raja $h^2/(8\nu)$
varmuusvaralla.

Projektiomenetelmällä on myös oma aikavirheensä: paine saadaan
tarkasti vain ensimmäisessä kertaluvussa, koska ennustus tehdään kokonaan
ilman sitä. Nopeuden tarkkuuteen se ei tässä vaikuta, kuten mittaus
näyttää. Tuotantokoodeissa käytetään muunnelmia, joissa ennustus
käyttää edellisen askeleen painetta ja korjaus ratkaisee vain paineen
muutoksen.

## Käytännössä

- **Ennustus, paine, korjaus** on kaikkien kokoonpuristumattomien
  ratkaisijoiden runko. Nimet vaihtelevat (projektio, painekorjaus,
  PISO, SIMPLE), mutta jokaisessa on vaihe, joka tekee nopeudesta
  lähteettömän ratkaisemalla Poissonin tyyppisen yhtälön.
- **Tarkista uusi koodi Taylorin ja Greenin pyörteellä.** Se on
  halpa, ja sen kertaluku paljastaa virheet, joita silmä ei kuvasta
  näe.
- **Älä käytä Eulerin aika-askelta keskeisdifferenssin kanssa**, ellei
  viskositeetti ole suuri. Monivaiheinen tai Runge–Kutta-tyyppinen
  kaavio maksaa vähän ja sallii moninkertaisen askeleen.
- **Epästabiilius ei aina näy heti.** Energian hidas kasvu on
  varoitusmerkki. Suljetussa, kitkallisessa virtauksessa ilman
  ulkoista voimaa liike-energia ei saa kasvaa.
- **Aika-askel seuraa nopeutta.** Kun virtaus kiihtyy laskun aikana,
  alussa turvallinen askel voi myöhemmin olla liian pitkä. Valmiit
  ohjelmat säätävät askelta Courantin luvun mukaan.

## Itsearviointi

- Osaat kuvata projektiomenetelmän kolme vaihetta ja kertoa, mitä
  kukin tekee.
- Osaat selittää, missä porrastetun hilan liikemäärän vuot lasketaan
  ja miksi.
- Osaat tarkistaa virtausratkaisijan Taylorin ja Greenin pyörteellä:
  divergenssi, energian vaimeneminen ja kertaluku.
- Osaat kertoa, mikä rajoittaa aika-askelta Eulerin ja
  Adams–Bashforthin menetelmässä.
- Osaat tunnistaa numeerisen epästabiiliuden liike-energian
  kehityksestä.
