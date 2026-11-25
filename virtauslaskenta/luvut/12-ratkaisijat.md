# Ratkaisijat ja suppeneminen

Tutoriaalin virtausratkaisija on tehty ymmärrettäväksi, ei nopeaksi.
Tässä luvussa katsotaan, missä sen aika kuluu, milloin lasku on valmis
ja mitä valmiit ohjelmat tekevät toisin: miten paineyhtälö ratkaistaan
miljoonille ruuduille, miten tasapainotila haetaan ilman pieniä
aika-askelia ja mikä muuttuu, kun hila ei enää ole suorakulmainen.
Tavoite on, että ohjelman asetusten nimet alkavat tarkoittaa jotain.

## Milloin lasku on valmis

Tasapainotilaa haettaessa lasku ei pääty itsestään, vaan se
lopetetaan, kun tulos ei enää muutu. Muutosta mitataan
**jäännöksellä**, joka kertoo, kuinka kaukana nykyinen kenttä on
yhtälöiden toteuttamisesta. Luvun 9 marssissa jäännös oli nopeuden
suurin muutosnopeus.

Jäännös ei kuitenkaan ole se suure, josta ollaan kiinnostuneita.
Esimerkki seuraa onkalolaskun aikana sekä jäännöstä että pääpyörteen
voimakkuutta.

```{.python tiedosto="esimerkit/12-suppeneminen.py" osa="seuranta"}
```

```{.tuloste tiedosto="esimerkit/12-suppeneminen.odotettu"}
```

![Jäännös ja seurattavan suureen ero lopulliseen arvoon. Molemmat
pienenevät samaa tahtia, mutta niiden suuruudet ovat eri
asioita.](kuvat/suppeneminen.png){width=70%}

Kun jäännös on pudonnut sadasosan tuntumaan, pyörteen voimakkuus on
vielä parin prosentin päässä lopullisesta. Kun jäännös on tuhannesosa
taulukon ensimmäisestä arvosta, virhe on kaksi sadasosaprosenttia.
Yleispätevää jäännöksen rajaa ei silti ole, koska suhde riippuu
tehtävästä, suureesta ja siitä, miten ohjelma jäännöksen skaalaa.
Varma tapa on seurata itse suuretta ja lopettaa, kun se on asettunut
tarvittavaan tarkkuuteen.

Tämä **iterointivirhe** on eri asia kuin luvun 9 diskretointivirhe, ja
se on saatava selvästi sitä pienemmäksi ennen hilavertailua. Muuten
kolmen hilan ero kertoo siitä, mihin kohtaan kukin lasku sattui
pysähtymään.

## Paineyhtälö suurella hilalla

Tutoriaalin ratkaisija hajottaa paineyhtälön matriisin tekijöihin
kerran ja käyttää hajotelmaa joka askeleella. Tasossa muutamalla
tuhannella ruudulla se on nopein tapa. Kolmessa ulottuvuudessa
hajotelma täyttyy niin, ettei miljoonan ruudun matriisi mahdu muistiin,
ja ratkaisijan on oltava iteratiivinen.

Esitiedoista tuttu liittogradienttimenetelmä tarvitsee kierroksia
suhteessa hilan sivun pituuteen ruutuina. Jacobin iteraatio, joka
korjaa jokaista pistettä naapuriensa perusteella, tarvitsee niitä
sivun pituuden neliöön verrannollisen määrän. Kumpikin hidastuu, kun
hila tihenee, ja syy on sama: tieto kulkee kierroksessa vain ruudun tai
muutaman verran, ja paineen on välitettävä tieto koko alueen poikki.

**Monihilamenetelmä** (*multigrid*) lähtee havainnosta, joka näkyy
kuvan vasemmassa paneelissa. Jacobin iteraatio poistaa virheen
nopeasti vaihtelevan osan muutamassa kierroksessa, mutta hitaasti
vaihteleva osa jää. Hitaasti vaihteleva virhe on kuitenkin sileä, joten
sen voi esittää karkeammalla hilalla, ja siellä sama virhe on ruutuihin
nähden nopeasti vaihtelevaa.

```{.python tiedosto="esimerkit/12-monihila.py" osa="perus"}
```

Menetelmä on rekursio: tasoita muutama kierros, siirrä jäännös
karkeammalle hilalle, ratkaise siellä virheen yhtälö samalla tavalla,
tuo korjaus takaisin ja tasoita vielä kerran. Karkein hila on niin
pieni, että se ratkeaa suoraan. Yhtä tällaista kierrosta sanotaan
V-kierrokseksi.

```{.python tiedosto="esimerkit/12-monihila.py" osa="monihila"}
```

```{.tuloste tiedosto="esimerkit/12-monihila.odotettu"}
```

![Vasemmalla virhe hilan keskirivillä Jacobin kierrosten jälkeen:
sahalaita häviää heti, kumpu jää. Oikealla jäännös kierrosten
funktiona.](kuvat/monihila.png){width=95%}

Jacobin kierrosmäärä nelinkertaistuu ja liittogradientin
kaksinkertaistuu, kun hila tihennetään kaksinkertaiseksi. Monihila
tarvitsee yksitoista tai kaksitoista kierrosta hilan koosta
riippumatta. Koska karkeampien hilojen työ on yhteensä vain kolmasosa
hienoimman hilan työstä, ratkaisun hinta on suoraan verrannollinen
tuntemattomien määrään, eikä sitä parempaa voi olla. Tästä syystä
monihila tai sen rakenteettomille verkoille sopiva algebrallinen
muunnelma on jokaisen suuren virtauslaskentaohjelman paineratkaisija,
usein liittogradienttimenetelmän esiehdostimena.

## Tasapainotila ilman aikamarssia

Luvun 9 onkalolasku otti tuhansia aika-askelia, koska eksplisiittisen
askeleen pituutta rajoittivat diffuusio ja advektio. Valmiit ohjelmat
välttävät rajat käsittelemällä liikemäärän yhtälön implisiittisesti:
uusi nopeus ratkaistaan yhtälöryhmästä kuten lämpöyhtälön
implisiittisessä menetelmässä.

Tasapainotilan vakiomenetelmä on **SIMPLE**. Sen kierros on
projektiomenetelmän sukulainen:

1. Ratkaistaan liikemäärän yhtälö implisiittisesti käyttäen edellisen
   kierroksen painetta.
2. Ratkaistaan painekorjaus, joka tekee nopeudesta lähteettömän.
3. Korjataan paine ja nopeus, mutta vain osittain.

Kolmannen kohdan osittaista korjausta sanotaan **alirelaksaatioksi**.
Ilman sitä kierros hajoaa, koska yhtälöt ovat epälineaariset ja
kytketyt. Alirelaksaatiokertoimet (tyypillisesti 0,3 paineelle ja 0,7
nopeudelle) ovat menetelmän aika-askeleen vastine: pienet arvot ovat
varmoja ja hitaita.

Ajasta riippuvissa laskuissa käytetään muunnelmaa **PISO**, joka tekee
painekorjauksen kahdesti tai useammin askelta kohden ja pysyy tarkkana
ilman alirelaksaatiota. Implisiittinen aika-askel poistaa
stabiilisuusrajan, ei tarkkuusvaatimusta: pyörrerata, jonka jaksoon
mahtuu viisi aika-askelta, lasketaan väärin, vaikka lasku pysyy
pystyssä.

## Rakenteeton verkko

Auton tai venttiilin ympärille ei saa suorakulmaista hilaa. Oikeat
ohjelmat käyttävät **rakenteettomia verkkoja**, joiden ruudut ovat
mielivaltaisia monitahokkaita. Kontrollitilavuusmenetelmä yleistyy
niihin suoraan, koska tase tarvitsee vain pinnat ja niiden vuot, mutta
kolme asiaa muuttuu.

- **Muuttujat ovat samassa paikassa.** Porrastus ei onnistu
  mielivaltaisilla ruuduilla, joten paine ja nopeus tallennetaan
  ruutujen keskelle. Luvun 6 shakkilautaongelma torjutaan laskemalla
  pinnan nopeus erityisellä interpoloinnilla, joka ottaa mukaan
  pinnan yli vaikuttavan paine-eron. Menetelmä tunnetaan keksijöidensä
  mukaan Rhien ja Chow'n interpolointina.
- **Pinnan vuo vaatii korjauksia.** Kun ruutujen keskipisteitä
  yhdistävä jana ei ole kohtisuorassa pintaa vastaan tai ei kulje
  pinnan keskipisteen kautta, yksinkertainen erotusosamäärä ei enää
  ole toista kertalukua. Ohjelma korjaa vuota, mutta huonolla
  verkolla korjaus on suuri ja epätarkka.
- **Verkon laatu on osa tarkkuutta.** Ohjelmat mittaavat verkosta
  pintojen vinoutta (*non-orthogonality*, *skewness*), ruutujen
  sivusuhdetta ja koon muutosta naapurista toiseen. Raja-arvot
  ylittävä verkko hidastaa suppenemista tai kaataa laskun.

Seinien viereen tehdään ohuista särmiöistä kerroksia, jotta rajakerros
saadaan erotetuksi luvun 11 vaatimalla tarkkuudella, ja muu tilavuus
täytetään suuremmilla ruuduilla. Verkon tekeminen on usein koko
laskentaprojektin työläin vaihe.

## Käytännössä

- **Seuraa suuretta, älä vain jäännöstä.** Lisää laskuun mittari
  kiinnostavalle suureelle (voima, painehäviö, lämpötila) ja katso sen
  historia. Jäännös kertoo suunnan, mittari kertoo, milloin on valmista.
- **Pudota iterointivirhe diskretointivirheen alle.** Hilavertailu on
  mieletön, jos laskut on lopetettu löysällä rajalla.
- **Jäännös, joka ei pienene, on viesti.** Syy voi olla huono verkko,
  liian suuri alirelaksaatiokerroin tai virtaus, joka ei ole
  ajasta riippumaton.
- **Paineratkaisija määrää nopeuden.** Jos lasku on hidas, katso ensin,
  montako kierrosta paineyhtälö vie askelta kohden. Monihilan pitäisi
  selvitä kymmenellä tai kahdellakymmenellä.
- **Tarkista verkon laatu ennen laskua.** Ohjelman oma
  verkkotarkistus on halvin koko työnkulun vaihe ja ehkäisee
  kalleimmat virheet.
- **Implisiittinen ei tarkoita tarkkaa.** Suuri aika-askel pysyy
  vakaana mutta tasoittaa ajasta riippuvat ilmiöt pois.

## Itsearviointi

- Osaat erottaa iterointivirheen ja diskretointivirheen ja kertoa,
  miksi jäännöksen raja ei yksin riitä lopetusehdoksi.
- Osaat selittää, miksi Jacobin iteraatio ja liittogradientti
  hidastuvat hilaa tihennettäessä ja miten monihila välttää sen.
- Osaat kuvata V-kierroksen vaiheet.
- Osaat kertoa, miten SIMPLE ja PISO liittyvät projektiomenetelmään ja
  mitä alirelaksaatio tekee.
- Osaat nimetä, mikä muuttuu, kun suorakulmaisesta hilasta siirrytään
  rakenteettomaan verkkoon, ja mitä verkon laatumittarit kertovat.
