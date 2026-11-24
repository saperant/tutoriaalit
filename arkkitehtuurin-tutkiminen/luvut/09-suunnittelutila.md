# Suunnittelutilan tutkiminen

Edelliset luvut antoivat malleja yksittäisille kysymyksille. Oikea
suunnittelupäätös koskee montaa parametria yhtä aikaa, ja ne vaikuttavat
toisiinsa. Suurempi välimuisti vie tilaa ytimiltä. Matalampi jännite
sallii useampia ytimiä samassa tehobudjetissa, mutta ne ovat hitaampia.
*Suunnittelutila* on kaikkien parametriyhdistelmien joukko, ja sen
tutkiminen on järjestelmällistä hakua siitä.

Tämä luku tutkii moniydinsirun suunnittelutilaa. Tavoite on suurin
suorituskyky 80 W:n tehobudjetissa ja 64 perusytimen (BCE) pinta-alalla.

## Malli

Sirumalli yhdistää aiemmat luvut. Ydinten koko $r$ ja yhteisen
välimuistin koko $c$ jakavat pinta-alan. Kunkin ytimen nopeus tulee
CPI-pinosta (luku 3): perus-CPI Pollackin säännöstä ja muistihudit
neliöjuurisäännöstä, kun välimuisti jaetaan ytimien kesken.
Rinnakkaisosan nopeutta rajaa muistin kaista (roofline). Koko kuorma
yhdistetään Amdahlin lailla, ja teho tulee luvun 8 piirimallista:

```{.python tiedosto="esimerkit/arkki/siru.py" osa="siru"}
```

Malli on yksinkertainen, ja sen kaikki oletukset ovat näkyvissä. Se on
tarkoituskin: suunnittelutilan tutkimisen alussa malli, jonka jokaisen
termin ymmärtää, on arvokkaampi kuin tarkka malli, jonka tulosta ei osaa
selittää.

## Täysi ruudukko

Kun parametreja on vähän ja malli on nopea, kaikki yhdistelmät voi
arvioida (*täysi faktorikoe*). Kolme parametria, 5 × 5 × 6 = 150
pistettä:

```{.python tiedosto="esimerkit/arkki/tutkimus.py" osa="naytteistys"}
```

```{.python tiedosto="esimerkit/09-ruudukko.py" osa="tila"}
```

```{.python tiedosto="esimerkit/09-ruudukko.py" osa="haku"}
```

Kun paras piste on löytynyt, on tarkistettava, onko se tilan reunalla.
Jos on, tila on ehkä rajattu liian tiukasti, ja optimi voi olla sen
ulkopuolella:

```{.python tiedosto="esimerkit/09-ruudukko.py" osa="reuna"}
```

```{.tuloste tiedosto="esimerkit/09-ruudukko.odotettu"}
```

Paras suunnitelma on 48 pientä ydintä, 16 MiB välimuistia ja 0,8 V.
Ydinkoko on tilan reunalla, mutta reuna on luonnollinen: perusydintä
pienempää ydintä ei ole määritelty. Välimuistin koko ei ole reunalla,
koska tila ulottuu 32 MiB:iin. Ensimmäisessä versiossa tila päättyi
16 MiB:iin, ja reunatarkistus osoitti, että sitä kannatti laajentaa.

Huomaa myös toiseksi paras: 32 ydintä, 32 MiB ja 0,9 V, vain 3 %
heikompi täysin eri rakenteella. Kun kaksi hyvin erilaista suunnitelmaa
ovat näin lähellä, mallin epätarkkuus ratkaisee niiden järjestyksen, ja
päätös vaatii tarkempaa mallia tai lisätietoa kuormista.

## Kun arviointeja on vähän

Jos yksi arviointi on syklitarkka simulointi, 150 pistettä on liikaa, ja
tiloissa on usein kymmeniä parametreja. Silloin arvioidaan otos. Kaksi
perusmenetelmää:

- **Satunnainen otanta** valitsee jokaisen parametrin tason
  riippumattomasti.
- **Latinalainen hyperkuutio** (McKay ym. 1979) jakaa kunkin parametrin
  vaihteluvälin $n$ osaan ja varmistaa, että jokaisesta osasta tulee
  täsmälleen yksi piste. Otos kattaa jokaisen parametrin tasaisesti,
  vaikka pisteitä on vähän.

Testi varmistaa hyperkuution ominaisuuden: kun tasoja on yhtä monta kuin
pisteitä, jokainen taso esiintyy kerran.

```{.python tiedosto="esimerkit/testit/test_muut.py" osa="hyperkuutio"}
```

Kumpaakin menetelmää toistetaan 200 siemenellä, ja parasta löydettyä
verrataan ruudukon optimiin. Tavoite on nopeutus, jos tehoraja täyttyy:

```{.python tiedosto="esimerkit/09-naytteistys.py" osa="arvo"}
```

```{.python tiedosto="esimerkit/09-naytteistys.py" osa="toistot"}
```

```{.tuloste tiedosto="esimerkit/09-naytteistys.odotettu"}
```

Kymmenen satunnaista pistettä jää keskimäärin neljänneksen optimista,
ja pahimmillaan kaksi kolmasosaa. Hyperkuutio on hieman parempi
keskimäärin, mutta ero on pieni: kolmen parametrin diskreetissä tilassa
satunnainenkin otos kattaa tasot kohtuullisesti. Hyperkuution etu kasvaa
ulottuvuuksien mukana. Neljälläkymmenellä pisteellä kumpikin löytää
optimin vain noin joka viidennellä kerralla.

Tästä seuraa, että pelkkä otanta ei riitä kalliille arvioinneille. Oikeat
työkalut käyttävät otosta lähtökohtana ja ohjaavat hakua:

- **Korvikemalli** (*surrogate model*) sovitetaan arvioituihin pisteisiin
  (regressio, Gaussin prosessi tai neuroverkko), ja sitä käytetään
  halpana mallina. Bayesilainen optimointi valitsee seuraavan arvioitavan
  pisteen sen perusteella, missä korvike on epävarmin tai lupaavin.
- **Evoluutioalgoritmit**, kuten NSGA-II, kehittävät joukkoa pisteitä
  kohti Pareto-rintamaa. Ne sopivat moneen tavoitteeseen yhtä aikaa.
- **Hierarkkinen tutkiminen** käy koko tilan läpi analyyttisellä mallilla
  ja simuloi vain sen parhaat pisteet. Tämä on yksinkertaisin ja usein
  tehokkain tapa, ja se on syy siihen, että analyyttisiä malleja
  ylipäätään tarvitaan.

## Pareto-rintama

Tehoraja on päätös, ja se voi muuttua. Pareto-rintama näyttää kaikki
suunnitelmat, joita mikään muu ei voita kummassakaan tavoitteessa:
mikään muu ei ole yhtä nopea pienemmällä teholla.

```{.python tiedosto="esimerkit/arkki/tutkimus.py" osa="pareto"}
```

```{.python tiedosto="esimerkit/09-pareto.py" osa="rintama"}
```

```{.tuloste tiedosto="esimerkit/09-pareto.odotettu"}
```

![Suunnittelutila ja Pareto-rintama. Tehorajan siirtäminen siirtää
valinnan rintamaa pitkin.](kuvat/pareto.png){width=100%}

Rintamalla on 17 pistettä 150:stä. Muut 133 voi unohtaa: jokaiselle
niistä on parempi vaihtoehto. Rintaman muoto kertoo kaupan hinnan.
30 W:iin asti nopeutus kasvaa jyrkästi pienillä ytimillä ja kasvavalla
välimuistilla, ja nopeutus wattia kohden on paras 29 W:n kohdalla.
Sen jälkeen jokainen lisänopeutus maksaa yhä enemmän: nopeutuksen
nostaminen 25,7:stä 31:een vaatii 2,5-kertaisen tehon. Suunnitelmat, joissa on suuria ytimiä,
ovat rintamalla vain pienimmillä tehoilla, joilla ne ovat ainoita
vaihtoehtoja.

## Herkkyysanalyysi

Mallin tulos riippuu kuormaa koskevista oletuksista: sarjaosuus,
hutimäärä, muistiviive ja kaista. Ne ovat arvioita, ja ne voivat olla
väärin. Herkkyysanalyysi kysyy kaksi asiaa: kuinka paljon tulos muuttuu,
kun oletus muuttuu, ja muuttuuko päätös.

*Jousto* on tuloksen suhteellinen muutos jaettuna oletuksen
suhteellisella muutoksella. Jousto −0,4 tarkoittaa, että oletuksen
kasvu 10 %:lla laskee tulosta 4 %:

```{.python tiedosto="esimerkit/arkki/tutkimus.py" osa="herkkyys"}
```

```{.python tiedosto="esimerkit/09-herkkyys.py" osa="joustot"}
```

Joustoa tärkeämpää on, muuttuuko valinta. Jokainen oletus puolitetaan ja
kaksinkertaistetaan, optimi haetaan uudelleen, ja *katumus* kertoo,
kuinka paljon alkuperäinen valinta häviää uudelle optimille:

```{.python tiedosto="esimerkit/09-herkkyys.py" osa="optimi"}
```

```{.tuloste tiedosto="esimerkit/09-herkkyys.odotettu"}
```

Suorituskyky reagoi eniten hutimäärään ja viiveeseen, mutta valittu
suunnitelma on silti vakaa: useimmissa tapauksissa se pysyy optimina,
ja muutamassa sen häviö uudelle optimille on alle 3 %. Poikkeus on
kaista. Valitussa pisteessä kaista ei rajoita, joten sen jousto on nolla,
mutta kun kaista puolitetaan, 48 ytimen muistiliikenne ylittää sen, ja
valittu suunnitelma häviää 26 %. Uusi optimi on 32 ydintä ja 32 MiB:n
välimuisti, joka vähentää muistiliikennettä. Jousto mittaa vain
paikallista herkkyyttä; rajoitteen aktivoituminen näkyy vasta, kun
oletusta muutetaan tarpeeksi.

Päätöksentekijälle tämä on tärkein tulos: valinta on hyvä, *jos*
muistin kaista on vähintään oletettu 25 GB/s. Kaistan arvio on
siksi tarkistettava ennen kuin suunnitelma lyödään lukkoon.

## Käytännössä

- **Tarkista reunat.** Optimi tilan keinotekoisella reunalla tarkoittaa,
  että tilaa on laajennettava. Luonnollinen reuna (fyysinen raja) on
  eri asia.
- **Lähes yhtä hyvät vaihtoehdot ovat tieto.** Jos kaksi erilaista
  suunnitelmaa on muutaman prosentin päässä toisistaan, malli ei pysty
  valitsemaan niiden välillä. Raportoi molemmat.
- **Rintama ennen valintaa.** Pareto-rintama erottaa tekniset faktat
  (mitä on mahdollista) liiketoiminnan päätöksistä (mikä teho on
  hyväksyttävä).
- **Kysy, muuttuuko päätös.** Herkkyysanalyysin tarkoitus ei ole
  tuottaa lukuja vaan löytää ne oletukset, joista päätös riippuu.
  Niiden tarkentamiseen kannattaa käyttää aikaa.
- **Hierarkkisesti.** Analyyttinen malli koko tilaan, simulointi
  parhaisiin, RTL tai prototyyppi lopulliseen.

## Itsearviointi

- Osaat rakentaa suunnittelutilan parametreista ja tasoista ja käydä
  sen läpi täytenä ruudukkona.
- Osaat verrata satunnaista otantaa ja latinalaista hyperkuutiota ja
  selittää, milloin otanta ei riitä.
- Osaat laskea Pareto-rintaman ja tulkita sen muodon.
- Osaat laskea joustot ja tutkia, muuttaako oletuksen virhe optimaalista
  suunnitelmaa.
