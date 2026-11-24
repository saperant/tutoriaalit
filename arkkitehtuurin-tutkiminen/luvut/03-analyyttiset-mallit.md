# Analyyttiset suorituskykymallit

Analyyttinen malli on kaava, joka laskee suorituskyvyn muutamasta
parametrista. Se on epätarkka, mutta se on niin nopea, että koko
suunnittelutilan voi käydä läpi silmänräpäyksessä. Se myös näyttää
*miksi*: kaavasta näkee, mikä parametri rajoittaa ja kuinka paljon.
Paketti *Suorituskyvyn analyysi ja optimointi* käyttää Amdahlin lakia ja
roofline-mallia ohjelman optimointiin. Tässä luvussa samat mallit
mitoittavat laitteistoa: kuinka suuria ytimiä, kuinka paljon kaistaa ja
kuinka monta keskeneräistä muistipyyntöä.

## Amdahl ja Gustafson

Amdahlin laki antaa nopeutuksen, kun osuus $p$ ajosta nopeutuu
$s$-kertaiseksi, ja Gustafsonin laki skaalatun nopeutuksen, kun
rinnakkaisen työn määrä kasvaa ytimien mukana:

```{.python tiedosto="esimerkit/arkki/mallit.py" osa="amdahl"}
```

Laitteiston näkökulmasta Amdahlin laki sanoo, että sarjaosa ratkaisee:
jos 1 % työstä on sarjallista, mikään ytimien määrä ei anna yli
100-kertaista nopeutusta. Gustafsonin laki on optimistisempi, koska se
olettaa, että suurempi kone ajaa suuremman ongelman. Kumpi oletus
pätee, riippuu kuormasta, ja se on päätettävä ennen kuin malli kertoo
mitään.

## Hillin ja Martyn moniydinmallit

Hill ja Marty (2008) yhdistivät Amdahlin lain pinta-alarajoitteeseen.
Sirulla on $n$ *perusytimen* (*base core equivalent*, BCE) pinta-ala.
Ytimen, joka käyttää $r$ BCE:tä, yksisäikeinen suorituskyky on
$\text{perf}(r)$. Pollackin säännön mukaan suorituskyky kasvaa pinta-alan
neliöjuurena: kaksinkertainen ydin on noin 1,4 kertaa nopeampi. Kolme
rakennetta:

- **Symmetrinen**: $n/r$ samanlaista ydintä. Sarjaosa ajetaan yhdellä,
  rinnakkaisosa kaikilla.
- **Epäsymmetrinen**: yksi suuri $r$:n ydin ja $n - r$ pientä. Sarjaosa
  ajetaan suurella, rinnakkaisosa kaikilla yhtä aikaa.
- **Dynaaminen**: pienet ytimet yhdistyvät sarjaosan ajaksi yhdeksi
  suureksi. Tämä on ideaali, jota mikään todellinen suoritin ei
  täysin saavuta.

```{.python tiedosto="esimerkit/arkki/mallit.py" osa="hill-marty"}
```

Paras ydinkoko 64 BCE:n sirulla eri rinnakkaisuusosuuksilla $f$:

```{.python tiedosto="esimerkit/03-hill-marty.py" osa="paras"}
```

```{.tuloste tiedosto="esimerkit/03-hill-marty.odotettu"}
```

![Hillin ja Martyn mallit 64 BCE:n sirulle. Kun rinnakkaisuutta on
paljon, symmetrisellä sirulla kannattaa pienet ytimet; epäsymmetrinen
siru hyötyy yhdestä suuresta ytimestä.](kuvat/hill-marty.png){width=100%}

Mallista seuraa kolme johtopäätöstä, jotka ovat ohjanneet
moniydinsuorittimien suunnittelua:

1. **Symmetrisen sirun optimi riippuu kuormasta.** Kun $f = 0{,}9$,
   parhaat ovat 8 BCE:n ytimet, ja kun $f = 0{,}99$, yhden BCE:n ytimet.
   Yksi siru ei ole paras kaikille kuormille.
2. **Epäsymmetrisyys kannattaa aina.** Yksi suuri ydin sarjaosaa varten
   ja pieniä rinnakkaisosaa varten on vähintään yhtä hyvä kuin paras
   symmetrinen siru, ja usein paljon parempi. Tämä on Armin big.LITTLE-
   ja Intelin P- ja E-ytimien ajatus.
3. **Sarjaosan nopeuttaminen on arvokasta.** Dynaamisen sirun etu
   epäsymmetriseen on sarjaosan nopeus, ja se kasvaa, kun $f$ kasvaa.

Testit varmistavat mallien perusominaisuudet: yhden BCE:n ytimillä
kaikki rakenteet palautuvat Amdahlin lakiin, ja dynaaminen on aina
paras:

```{.python tiedosto="esimerkit/testit/test_mallit.py" osa="hill-marty"}
```

Malli jättää huomiotta muistin, tehon ja ytimien välisen viestinnän.
Luvussa 9 se yhdistetään muisti- ja tehomalleihin, ja silloin optimi
muuttuu.

## Roofline usealla muistitasolla

Roofline-malli rajaa suorituskyvyn ylhäältä: ydin ei voi laskea
nopeammin kuin huipputeho $P$ eikä nopeammin kuin muisti tuo dataa,
$B \cdot I$, missä $I$ on laskentaintensiteetti (FLOP/B). *Hierarkkinen
roofline* laskee intensiteetin erikseen jokaiselle muistitasolle sen
läpi kulkevasta liikenteestä. Matalin katto rajoittaa:

```{.python tiedosto="esimerkit/arkki/mallit.py" osa="roofline"}
```

Liikenne kullakin tasolla saadaan luvun 2 hutikäyristä. L1:n läpi
kulkevat kaikki viittaukset, L2:n läpi L1:n hudit ja muistiin L2:n
hudit, kukin 64 tavun rivinä. Välimuistit on pienennetty samassa
suhteessa kuin ytimet, jotta pienet ytimet käyttäytyvät kuten suuret
oikealla koneella:

```{.python tiedosto="esimerkit/03-roofline.py" osa="kone"}
```

```{.python tiedosto="esimerkit/03-roofline.py" osa="intensiteetit"}
```

```{.tuloste tiedosto="esimerkit/03-roofline.odotettu"}
```

![Roofline: muistikatto ja ytimien muistitason intensiteetit. Lohkottu
matriisitulo on lähellä harjannetta, lista ja virta kaukana sen
vasemmalla puolella.](kuvat/roofline.png){width=100%}

Hierarkkinen roofline paljastaa sen, minkä luvun 2 L1-intensiteetti
peitti. Naiivi ja lohkottu matriisitulo ovat L1-tasolla yhtä
intensiivisiä, mutta naiivin L1-hudit tekevät L2:sta pullonkaulan
(0,03 FLOP/B). Lohkottu nostaa L2:n intensiteetin 0,67:ään ja
muistin 1,33:een, ja rajoittavaksi jää L1:n kaista. Virta ja lista ovat
muistirajoitteisia millä tahansa välimuistilla: niiden intensiteettiä
nostaa vain algoritmin muutos.

Arkkitehdille roofline kertoo, mihin pinta-ala kannattaa käyttää. Jos
tärkeät kuormat ovat muistirajoitteisia, laskentayksiköiden lisääminen
ei auta, mutta kaista ja välimuisti auttavat. Jos ne ovat
laskentarajoitteisia, päinvastoin.

## Kaista ja Littlen laki

Muistikanavan kaista on teoreettinen yläraja. Siihen päästään vain, jos
pyyntöjä on tarpeeksi monta yhtä aikaa kesken. *Littlen laki* (luku 4)
yhdistää kolme suuretta: keskimäärin kesken olevien pyyntöjen määrä $L$
on läpäisy $\lambda$ kertaa viive $W$. Muistille $\lambda$ on
kaista riveinä sekunnissa:

$$\text{kaista} = \frac{L \cdot \text{rivikoko}}{W}.$$

```{.python tiedosto="esimerkit/arkki/mallit.py" osa="kaista"}
```

```{.python tiedosto="esimerkit/03-kaista.py" osa="taulukko"}
```

```{.python tiedosto="esimerkit/03-kaista.py" osa="ytimet"}
```

```{.tuloste tiedosto="esimerkit/03-kaista.odotettu"}
```

Yksi DDR4-kanava 90 ns:n viiveellä vaatii 36 keskeneräistä pyyntöä.
Ytimellä on rajallinen määrä *hutirekisterejä* (*miss status holding
registers*, MSHR), joihin keskeneräiset hudit kirjataan; kymmenellä
yksi ydin saa vain 28 % kanavan kaistasta. Tästä seuraa
mitoitussääntö: MSHR:ien määrä, esihakijan syvyys ja ytimien määrä on
mitoitettava viiveen ja kaistan tulon mukaan, ei pelkän kaistan.
Luvussa 5 nähdään, että kuormitettuna viive kasvaa, jolloin tarvitaan
vielä enemmän rinnakkaisuutta.

## CPI-pino

CPI-pino jakaa käskyä kohden kuluvat jaksot syihin: perus-CPI, kun
kaikki osuu, ja kunkin hutityypin osuus. Hutien määrä annetaan tuhatta
käskyä kohden (*misses per kilo-instruction*, MPKI):

```{.python tiedosto="esimerkit/arkki/mallit.py" osa="cpi"}
```

Luvun 2 ytimet kahden tason välimuistilla (1 KiB ja 8 KiB, kuten
roofline-esimerkissä), L2-osuma 12 jaksoa ja muisti 200 jaksoa. Hutien
määrät tulevat hutikäyristä ja käskyjen määrät operaatiolaskureista:

```{.python tiedosto="esimerkit/03-cpi-pino.py" osa="parametrit"}
```

```{.python tiedosto="esimerkit/03-cpi-pino.py" osa="pino"}
```

```{.tuloste tiedosto="esimerkit/03-cpi-pino.odotettu"}
```

Pino näyttää heti, mitä kannattaa parantaa. Lohkotulla matriisitulolla
muisti vie yli puolet ajasta, mutta kokonais-CPI on jo 1,3. Virralla ja
listalla muisti on yli 90 % ajasta, ja 200 jakson sakon puolittaminen
lähes puolittaisi ajon. Naiivilla sekä L2-osumat (2,28) että
muistihudit (4,36) ovat merkittäviä. 4 KiB:n L1 poistaisi ensimmäisen
lähes kokonaan (luku 2), ja lohkominen poistaa molemmat.

Pino olettaa, että hudit eivät limity: jokainen maksaa koko sakon.
Epäjärjestyksessä suorittava ydin piilottaa osan viiveestä, ja
riippumattomat hudit voivat olla kesken yhtä aikaa. Virralla, jonka
hudit ovat riippumattomia, todellinen CPI on paljon pienempi; listalla,
jossa jokainen lataus odottaa edellistä, pino on lähes oikeassa.
Luvussa 6 tämä ero mallinnetaan.

## Käytännössä

- **Mallin oletukset ovat sen tulos.** Hillin ja Martyn malli olettaa
  Pollackin säännön ja täydellisen rinnakkaisuuden. Kun oletus muuttuu,
  optimi muuttuu. Kirjoita oletukset näkyviin ja testaa niiden
  herkkyys (luku 9).
- **Yläraja, ei ennuste.** Roofline ja Littlen laki antavat rajoja.
  Jos mitattu tulos on kaukana rajasta, jokin muu rajoittaa: viive,
  riippuvuudet tai kilpailu.
- **Laske intensiteetti jokaiselle tasolle.** Yhden tason intensiteetti
  piilottaa pullonkaulan. Hutikäyrä antaa liikenteen kaikille tasoille
  yhdellä läpikäynnillä.
- **Mitoita rinnakkaisuus viiveen mukaan.** Kaista ilman riittävää
  määrää keskeneräisiä pyyntöjä jää käyttämättä. Littlen laki kertoo
  tarvittavan määrän.
- **Aloita CPI-pinosta.** Se on yksinkertaisin malli, joka kertoo,
  mihin aika kuluu, ja jokainen hienompi malli on sen korjaus.

## Itsearviointi

- Osaat laskea Hillin ja Martyn mallilla parhaan ydinkoon symmetriselle,
  epäsymmetriselle ja dynaamiselle sirulle ja selittää, miksi
  epäsymmetrinen siru on vähintään yhtä hyvä kuin symmetrinen.
- Osaat laskea hierarkkisen rooflinen intensiteetit hutikäyristä ja
  päätellä, mikä muistitaso rajoittaa ydintä.
- Osaat mitoittaa keskeneräisten muistipyyntöjen määrän Littlen lailla.
- Osaat koota CPI-pinon hutimääristä ja sakoista ja kertoa, milloin
  pinon oletus hutien limittymättömyydestä pätee.
