# Vikamallit ja simulaattori

Algoritmi on oikein vain jonkin *vikamallin* suhteen: oletuksen siitä,
mitä solmut ja verkko voivat tehdä väärin. Sama algoritmi voi olla
oikein, kun solmut kaatuvat siististi, ja väärin, kun ne palaavat
kaatumisen jälkeen vanhalla tilalla. Tämä luku käy läpi tavalliset
vikamallit, rakentaa simulaattorin, joka tuottaa niitä hallitusti, ja
näyttää kolme ilmiötä, jotka toistuvat koko tutoriaalin ajan:
uudelleenlähetys, vikailmaisimen epävarmuus ja pysyvän tilan
merkitys.

## Solmujen viat

**Kaatuminen ja pysähtyminen** (*crash-stop*). Solmu lakkaa toimimasta
eikä palaa. Malli on yksinkertainen ja usein liian optimistinen:
oikeat koneet käynnistyvät uudelleen.

**Kaatuminen ja palautuminen** (*crash-recovery*). Solmu kaatuu,
menettää muistinsa ja käynnistyy myöhemmin uudelleen. Levylle
kirjoitettu tila säilyy, muistissa ollut katoaa. Tämä on tavallisin
malli käytännön järjestelmille, ja se tekee kirjoitusjärjestyksestä
tärkeän: jos solmu lupaa jotain ennen kuin lupaus on levyllä, kaatuminen
voi rikkoa lupauksen.

**Puutteellinen toiminta** (*omission*). Solmu jättää viestejä
lähettämättä tai vastaanottamatta, esimerkiksi täyden puskurin vuoksi.
Ulospäin se näyttää samalta kuin häviävä verkko.

**Bysanttilainen vika.** Solmu voi tehdä mitä tahansa: valehdella,
lähettää ristiriitaisia viestejä eri solmuille tai olla hyökkääjän
hallussa. Bysanttilaisen vian sietäminen vaatii yli kaksi kolmasosaa
kunnollisia solmuja ja on kallista; sitä tarvitaan lohkoketjuissa ja
joissakin ilmailun ja avaruustekniikan järjestelmissä. Tämä tutoriaali
olettaa, että solmut eivät valehtele.

## Verkon viat ja ajoitusmallit

Verkko voi kadottaa viestin, viivästyttää sitä mielivaltaisesti,
monistaa sen (uudelleenlähetys alemmalla tasolla) ja toimittaa viestit
eri järjestyksessä kuin ne lähetettiin. TCP piilottaa katoamisen,
monistumisen ja järjestyksen yhden yhteyden sisällä, mutta yhteys voi
katketa, ja uuden yhteyden yli lähetetty viesti voi ohittaa vanhan.
Viesti voi myös jäädä kulkematta vain toiseen suuntaan, tai verkko
voi *jakautua* (*partition*) kahteen tai useampaan osaan, joiden
välillä mikään ei kulje.

Ajoituksen suhteen järjestelmät jaetaan kolmeen malliin:

| Malli | Oletus | Seuraus |
|-------|--------|---------|
| synkroninen | viestin viiveellä ja laskennan nopeudella on tunnettu yläraja | aikakatkaisu kertoo varmasti, että solmu on kaatunut |
| asynkroninen | ei mitään ylärajaa | hidasta solmua ei voi erottaa kaatuneesta |
| osittain synkroninen | yläraja on olemassa, mutta vain jonkin tuntemattoman hetken jälkeen | algoritmi on aina turvallinen ja etenee, kun verkko rauhoittuu |

Synkroninen malli ei kuvaa oikeita verkkoja: ruuhka, roskienkeruu tai
virtuaalikoneen siirto voi pysäyttää prosessin sekunneiksi. Puhtaasti
asynkronisessa mallissa taas Fischerin, Lynchin ja Patersonin tulos
(FLP, 1985) osoittaa, ettei mikään deterministinen konsensusalgoritmi
voi taata päätöstä, jos yksikin solmu voi kaatua. Käytännön algoritmit,
kuten Raft, olettavat siksi osittaisen synkronisuuden: ne eivät koskaan
tee väärää päätöstä, mutta etenevät vain, kun viiveet pysyvät
kohtuullisina riittävän kauan.

Näistä seuraa hajautettujen järjestelmien keskeinen erottelu:
**turvallisuus** (*safety*) tarkoittaa, ettei mitään pahaa tapahdu
koskaan, ja **eteneminen** (*liveness*), että jotain hyvää tapahtuu
lopulta. Turvallisuuden rike näkyy äärellisessä historiassa (kaksi
johtajaa samalla termillä), etenemisen rike ei (ehkä johtaja valitaan
seuraavalla sekunnilla). Hyvä algoritmi luopuu tarvittaessa
etenemisestä, ei koskaan turvallisuudesta.

## Simulaattorin rakenne

Simulaattorissa solmu on tilakone, joka reagoi kolmeen asiaan:
käynnistymiseen, viestiin ja ajastimeen. Solmu ei näe muuta maailmaa
kuin rajapinnan `Yhteys`: oman tunnisteensa, paikallisen kellonsa,
viestien lähetyksen, ajastimet ja oman satunnaislukuvirtansa.

```{.cpp tiedosto="esimerkit/yhteinen/simulaattori.hpp" osa="rajapinta"}
```

Rajapinta on tarkoituksella sama, jonka oikea verkkopalvelin näkisi
tapahtumasilmukastaan (ks. *Verkko-ohjelmointi*): solmun koodi ei tiedä
ajavansa simulaattorissa. Tuotantojärjestelmät, jotka testataan
simuloimalla, erottavat juuri näin protokollan logiikan verkosta,
kellosta ja levystä, ja vaihtavat testeissä nämä simuloituihin.

Simulaattori pitää prioriteettijonoa tapahtumista, jotka on
järjestetty ajan ja lisäysjärjestyksen mukaan. Saman hetken
tapahtumat käsitellään siinä järjestyksessä, jossa ne lisättiin, joten
järjestys ei riipu jonon toteutuksesta:

```{.cpp tiedosto="esimerkit/yhteinen/simulaattori.hpp" osa="ajo"}
```

Verkon käyttäytymisen määräävät asetukset:

```{.cpp tiedosto="esimerkit/yhteinen/simulaattori.hpp" osa="asetukset"}
```

Lähetys arpoo viestin kohtalon. Jokainen arvonta on omassa
lauseessaan, jotta järjestys on sama kaikilla kääntäjillä:

```{.cpp tiedosto="esimerkit/yhteinen/simulaattori.hpp" osa="laheta"}
```

Uudelleenjärjestys syntyy itsestään: kaksi peräkkäin lähetettyä
viestiä saa eri viiveen, ja myöhemmin lähetetty voi saapua ensin.
Vikoja ohjataan testistä käsin:

```{.cpp tiedosto="esimerkit/yhteinen/simulaattori.hpp" osa="viat"}
```

Kaatuminen tuhoaa solmun olion. Siksi kaikki tila, jota ei ole
erikseen tallennettu pysyvään tilaan (`P`, "levy"), todella katoaa, eikä
kaatumista voi vahingossa simuloida vain osittain. Uudelleenkäynnistys
luo uuden olion tehdasfunktiolla ja antaa sille saman levyn. Vanhat
ajastimet mitätöityvät aikakauden avulla, ja kaatuneelle solmulle
saapuvat viestit katoavat. Verkon jako tarkistetaan viestin
saapumishetkellä: viesti katoaa, jos lähettäjä ja vastaanottaja ovat
silloin eri puolilla.

Satunnaisuus tulee PCG32-generaattorista. Verkolla on oma virtansa ja
jokaisella solmulla omansa, joten solmun satunnaiset päätökset eivät
muuta verkon arvontoja:

```{.cpp tiedosto="esimerkit/yhteinen/satunnainen.hpp" osa="muunnos"}
```

Välin muunnos hylkää liian suuret luvut eikä käytä pelkkää jakojäännöstä,
joka suosisi pieniä arvoja.

## Pyyntö ja vastaus häviävän verkon yli

Ensimmäinen esimerkki on tuttu verkko-ohjelmoinnista: asiakas lähettää
pyynnön ja odottaa vastausta, ja lähettää pyynnön uudelleen, jos
vastausta ei kuulu. Viesti on tavallinen tietue:

```{.cpp tiedosto="esimerkit/02-viestit.cpp" osa="viesti"}
```

Asiakas on tilakone, jonka tila on käsiteltävän pyynnön numero.
Ajastimen tunnisteena on pyynnön numero, joten vanhan pyynnön
aikakatkaisu ei sotke uutta:

```{.cpp tiedosto="esimerkit/02-viestit.cpp" osa="asiakas"}
```

Palvelin vastaa jokaiseen pyyntöön ja laskee, montako se käsitteli.
Testi rakentaa simulaattorin, jossa 30 % viesteistä katoaa ja 10 %
monistuu, ja ajaa sitä 10 ms kerrallaan, kunnes asiakas on valmis:

```{.cpp tiedosto="esimerkit/02-viestit.cpp" osa="aja"}
```

Pääohjelma ajaa ensin siemenen 7 lokin kanssa ja sitten viisi ajoa
ilman lokia, joista kaksi samalla siemenellä:

```{.tuloste tiedosto="esimerkit/02-viestit.odotettu"}
```

Ensimmäinen ajo tulostaa solmujen lokirivit simuloidun ajan kanssa.
Sama siemen 7 tuottaa taulukossa täsmälleen saman rivin kahdesti, ja
eri siemenet tuottavat eri suoritukset. Taulukosta näkyy myös luvun
*Hajautetut transaktiot* aihe: palvelin käsitteli pyyntöjä useammin kuin
asiakas lähetti eri pyyntöjä, koska uudelleenlähetykset ja verkon
monistamat viestit tulivat perille. Jos pyyntö muuttaisi tilaa,
esimerkiksi siirtäisi rahaa, se tehtäisiin useasti.

## Vikailmaisin

Solmu ei voi tietää, onko toinen solmu kaatunut. Se voi vain epäillä:
jos sykettä (*heartbeat*) ei ole kuulunut aikarajan sisällä, toinen on
ehkä kaatunut, tai ehkä verkko on vain hidas. Tällainen *vikailmaisin*
on epätäydellinen kahdella tavalla. Se voi epäillä toimivaa solmua
(*väärä epäily*), ja se huomaa kaatumisen vasta aikarajan jälkeen.

Lähettäjä lähettää sykkeen 20 ms välein, ja ilmaisin tarkistaa 5 ms
välein, milloin syke viimeksi kuului:

```{.cpp tiedosto="esimerkit/02-vikailmaisin.cpp" osa="ilmaisin"}
```

Kokeessa verkko on ensin nopea, sitten sekunnin ajan ruuhkainen
(viive 5–120 ms ja 5 % katoaa) ja taas nopea. Lähettäjä kaatuu
hetkellä 3000, ja koe toistetaan 50 siemenellä kullakin aikarajalla:

```{.tuloste tiedosto="esimerkit/02-vikailmaisin.odotettu"}
```

Lyhyt aikaraja tunnistaa kaatumisen nopeasti mutta epäilee ruuhkan
aikana kymmenkunta kertaa turhaan. Pitkä aikaraja ei epäile turhaan,
mutta kaatumisen huomaaminen kestää lähes yhtä kauan kuin aikaraja. Valinta on
aina kompromissi, ja se näkyy kaikissa johtajaa käyttävissä
järjestelmissä: liian herkkä vikailmaisin vaihtaa johtajaa turhaan
ja pysäyttää palvelun vaalin ajaksi, liian hidas jättää palvelun
pysähdyksiin johtajan kaaduttua. Käytännön ilmaisimet sopeuttavat
aikarajaa havaittuihin viiveisiin; esimerkiksi Cassandran ja Akkan
käyttämä φ-kertymäilmaisin (*phi accrual*) arvioi viiveiden jakaumaa
ja ilmoittaa epäilyn todennäköisyytenä.

## Kaatuminen ja pysyvä tila

Viimeinen esimerkki näyttää, miksi kaatumisen ja palautumisen malli
tekee kirjoitusjärjestyksestä tärkeän. Palvelin pitää laskuria ja
kuittaa jokaisen kasvatuksen. Levyn tila säilyy kaatumisen yli:

```{.cpp tiedosto="esimerkit/02-kaatuminen.cpp" osa="levy"}
```

Palvelimella on neljä tapaa käsitellä pysyvää tilaa. *Haihtuva* pitää
laskurin vain muistissa. *Pysyvä* kirjoittaa levylle ennen jokaista
kuittausta. *Ryhmä* kerää muutokset ja kirjoittaa ne 50 ms välein
kerralla (*group commit*), ja kuittaa vasta kirjoituksen jälkeen.
*Ryhmä-heti* kerää samoin mutta kuittaa heti:

```{.cpp tiedosto="esimerkit/02-kaatuminen.cpp" osa="palvelin"}
```

Palvelin kaatuu hetkellä 1234 ja käynnistyy hetkellä 1300, ja asiakas
lähettää kasvatuksen 10 ms välein:

```{.tuloste tiedosto="esimerkit/02-kaatuminen.odotettu"}
```

Haihtuva palvelin menetti kaiken kaatumista edeltäneen. Pysyvä
menetti ei mitään, mutta kirjoitti levylle jokaisen pyynnön kohdalla.
Ryhmäkirjoitus vähensi kirjoitukset neljäsosaan ilman menetyksiä,
mutta viive kasvoi, koska kuittaus odottaa seuraavaa kirjoitusta.
Ryhmä-heti näyttää yhtä nopealta kuin haihtuva, mutta se menetti
neljä kuitattua kasvatusta: asiakkaalle luvattu tieto katosi. Tämä on
tavallinen virhe, kun suorituskykyä parannetaan siirtämällä `fsync`
taustalle, ja juuri sellainen, jota ei huomaa ilman kaatumistestejä.

Oikea levy on vielä tätäkin hankalampi. `write` ilman `fsync`iä jää
käyttöjärjestelmän välimuistiin, levyohjain voi valehdella
kirjoittaneensa, ja kesken jäänyt kirjoitus voi jättää lohkon
puoliksi vanhaksi. Simulaattorin levy on idealisoitu: kirjoitus on
välitön ja atominen.

## Käytännössä

- **Kirjoita vikamalli auki.** Suunnitteludokumentissa kannattaa
  sanoa, kaatuvatko solmut pysyvästi vai palautuen, voiko viesti
  monistua ja voiko verkko jakautua. Moni kiistelty virhe on
  todellisuudessa eri vikamallien oletus.
- **Erota logiikka ympäristöstä.** Kun protokolla näkee verkon,
  kellon ja levyn rajapinnan kautta, sen voi ajaa simulaattorissa ja
  tuotannossa samana koodina. Jälkikäteen erottelu on työlästä.
- **Aikakatkaisu on arvaus.** Aikakatkaisu kertoo vain, ettei vastausta
  tullut. Pyyntö on ehkä käsitelty, joten uudelleenlähetyksen on
  oltava vaaraton (ks. *Hajautetut transaktiot*).
- **Kuittaa vasta, kun lupaus on pysyvä.** Ryhmäkirjoitus on hyvä
  tapa saada pysyvyys halvalla, kunhan kuittaus odottaa kirjoitusta.
- **Testaa kaatumisia.** Kaatumisen ja palautumisen virheet näkyvät
  vain, jos testi todella kaataa solmuja kiinnostavissa kohdissa.

## Itsearviointi

- Osaat erottaa kaatumisen ja pysähtymisen, kaatumisen ja palautumisen,
  puutteellisen toiminnan ja bysanttilaisen vian.
- Osaat kuvata synkronisen, asynkronisen ja osittain synkronisen
  ajoitusmallin ja kertoa, mitä FLP-tulos sanoo.
- Osaat erottaa turvallisuuden ja etenemisen ja perustella, kumpi
  algoritmin pitää säilyttää kaikissa oloissa.
- Osaat kirjoittaa protokollan tilakoneena deterministiseen
  simulaattoriin ja toistaa suorituksen siemenestä.
- Osaat selittää vikailmaisimen aikarajan kompromissin ja sen, miksi
  kuittaus ennen pysyvää kirjoitusta on virhe.
