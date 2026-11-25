# Toimitusputki

Toimitusputki (*deployment pipeline*) on automatisoitu reitti, jota
pitkin jokainen muutos kulkee versionhallinnasta tuotantoon. Käsite on
peräisin Jez Humblen ja David Farleyn kirjasta *Continuous Delivery*
(2010), ja sen perusajatus on, että **jokainen runkoon yhdistetty
muutos on julkaisuehdokas**. Putken tehtävä on yrittää osoittaa, että
ehdokas ei kelpaa. Jos mikään vaihe ei siinä onnistu, ehdokas voidaan
julkaista.

Näkökulma on eri kuin perinteisessä laadunvarmistuksessa, jossa
julkaisu kootaan ensin ja testataan sitten. Putkessa erillistä
kokoamisvaihetta ei ole. Julkaisu on mikä tahansa putken läpäissyt
rungon tila.

## Vaiheet

Putki jakautuu vaiheisiin, jotka etenevät nopeista ja halvoista
tarkistuksista hitaisiin ja kalliisiin.

```{.dot otsikko="Toimitusputken vaiheet: artefakti rakennetaan kerran, ja sama artefakti etenee vaiheesta toiseen"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.35;
  { node [group=p]; r [label="runko"]; c [label="commit-vaihe\n(minuutteja)"];
    h [label="hyväksymis-\nvaihe"]; e [label="muut\ntarkistukset"];
    t [label="tuotanto"]; }
  v [label="artefakti-\nvarasto", shape=cylinder];
  r -> c -> h -> e -> t;
  c -> v [label="tallenna"];
  v -> h [style=dashed, constraint=false];
  v -> e [style=dashed, constraint=false];
  v -> t [style=dashed, constraint=false, label="sama artefakti"];
  { rank=same; h; v; }
}
```

| Vaihe | Mitä tehdään | Kysymys, johon vastataan |
|-----------------|---------------------------------|--------------------------|
| commit-vaihe | käännös, yksikkötestit, staattinen analyysi, paketointi | onko muutos teknisesti ehjä? |
| hyväksymisvaihe | artefakti otetaan käyttöön tuotannon kaltaiseen ympäristöön ja ajetaan automaattiset hyväksymistestit | tekeekö järjestelmä sen, mitä käyttäjä tarvitsee? |
| muut tarkistukset | suorituskyky- ja kuormitustestit, tietoturvatarkistukset, tutkiva testaus | kestääkö se kuormaa ja väärinkäyttöä? |
| käyttöönotto | artefakti viedään tuotantoon ja julkaisua seurataan | toimiiko se oikeilla käyttäjillä? |

**Commit-vaihe** on putken tärkein, koska se ajetaan useimmin ja sen
tulosta odotetaan. Humblen ja Farleyn ohje on, että sen pitäisi
valmistua mieluiten alle viidessä ja enintään noin kymmenessä
minuutissa. Sama kymmenen minuutin raja on Extreme Programmingin
käytännöissä. Raja ei ole mielivaltainen: sitä pidemmän odotuksen
aikana kehittäjä siirtyy muuhun työhön, ja palaaminen maksaa
asiayhteyden vaihdon.

**Hyväksymisvaihe** testaa valmista artefaktia ulkoa päin. Testit on
kirjoitettu käyttäjän kielellä, ja ne ovat sama asia kuin tutoriaalin
*Testivetoinen kehitys ja testisuunnittelu* suoritettavat määrittelyt.
Vaihe on hitaampi, koska se tarvitsee käynnissä olevan järjestelmän
riippuvuuksineen (ks. *Integraatiotestaus ja Testcontainers*).

Loput vaiheet vaihtelevat. Kaikkea ei voi automatisoida: tutkiva
testaus ja käytettävyyden arviointi vaativat ihmisen. Putki tukee
niitä tarjoamalla napin painalluksella ympäristön, jossa on tietty
julkaisuehdokas.

## Putki mallina

Putki on suunnattu verkko: vaiheilla on riippuvuuksia, ja toisistaan
riippumattomat vaiheet voi ajaa rinnakkain. Seuraava malli on
toimitusputken ydin muutamalla kymmenellä rivillä. Vaihe on nimi,
toiminto ja luettelo vaiheista, joiden on onnistuttava ensin.

```{.python tiedosto="esimerkit/toimitus/putki.py" osa="vaihe"}
```

Ajaja järjestää vaiheet topologisesti ja suorittaa ne aalto
kerrallaan. Aallon vaiheet ajetaan rinnakkain. Jos vaiheen edeltäjä
epäonnistui, vaihe ohitetaan.

```{.python tiedosto="esimerkit/toimitus/putki.py" osa="aja"}
```

Esimerkkisovelluksen putkessa on viisi vaihetta. Kolme ensimmäistä
ovat commit-vaiheen tarkistukset ja ajavat oikeat työkalut. Paketointi
riippuu niistä kaikista, ja savutesti purkaa valmiin paketin ja ajaa
sen.

```{.python tiedosto="esimerkit/luku04/putki_ajo.py" osa="vaiheet"}
```

Putki ajetaan kahdesti: ensin muuttumattomalle sovellukselle ja sitten
muutokselle, joka vaihtaa yhden tarkistelaskennan kertoimen.

```{.tuloste tiedosto="esimerkit/luku04/putki_ajo.odotettu"}
```

Tulosteessa näkyy kolme putken ominaisuutta. Ensinnäkin rinnakkaisuus:
tyyli, tyypit ja testit ajetaan samassa aallossa, joten vaiheen kesto
on hitaimman tarkistuksen kesto eikä niiden summa. Toiseksi
pysähtyminen: kun testit epäonnistuvat, pakettia ei rakenneta, joten
rikkinäisestä muutoksesta ei synny artefaktia, jonka joku voisi
vahingossa ottaa käyttöön. Kolmanneksi savutesti kohdistuu pakettiin
eikä lähdekoodiin. Yksikkötestit ajettiin työhakemistossa, mutta
käyttäjälle menee paketti, ja paketointi voi mennä pieleen omalla
tavallaan: tiedosto puuttuu, riippuvuus jää pois.

Oikeat putkijärjestelmät (GitHub Actions, GitLab CI, Jenkins ja muut)
ovat sama malli, johon on lisätty ajokoneiden hallinta, lokit,
salaisuudet, välimuistit ja käyttöliittymä. Luku 6 näyttää saman putken
yhden järjestelmän kuvauskielellä.

## Nopea palaute

Putken arvo on palautteen nopeudessa, ja nopeus on suunnittelukysymys.

**Järjestä halvimman mukaan.** Tarkistus, joka kestää sekunteja ja
löytää usein virheitä, ajetaan ensin. Tyylin ja tyyppien tarkistus
ennen testejä, yksikkötestit ennen integraatiotestejä.

**Rinnakkaista.** Riippumattomat tarkistukset ajetaan yhtä aikaa, ja
suuri testijoukko jaetaan usealle koneelle. Rinnakkaistaminen
edellyttää, että testit eivät riipu toisistaan eivätkä jaetusta
tilasta.

**Siirrä hidas myöhemmäksi.** Commit-vaiheeseen kuuluu se, mikä
mahtuu kymmeneen minuuttiin. Tuntien kuormitustesti ajetaan omassa
vaiheessaan tai öisin. Tämä on kauppa: myöhemmin ajettu tarkistus
löytää vian myöhemmin. Kun myöhempi vaihe löytää vian, kannattaa
kysyä, olisiko nopeampi testi voinut löytää sen aiemmin.

**Älä tee samaa työtä kahdesti.** Välimuistit ja muutoksiin
perustuva testaus säästävät työtä, jonka tulos tiedetään jo.
Luku 6 käsittelee ne.

**Pidä testipyramidi kunnossa.** Jos suurin osa testeistä kulkee
käyttöliittymän läpi, mikään edellisistä ei tee putkesta nopeaa.
Testien jako tasoille on käsitelty tutoriaaleissa
*Testivetoinen kehitys ja testisuunnittelu* ja *Integraatiotestaus ja
Testcontainers*.

Putken kestoa kannattaa seurata kuten mitä tahansa suorituskykylukua.
Se kasvaa huomaamatta, testi kerrallaan, ja kymmenen minuutin putki on
vuodessa neljänkymmenen minuutin putki, ellei kukaan vahdi sitä.

## Epävakaat testit

Putki on hyödyllinen vain, jos sen tulokseen luotetaan. Punaisen pitää
tarkoittaa vikaa ja vihreän sen puuttumista. Epävakaa testi
(*flaky test*) rikkoo tämän: se epäonnistuu joskus, vaikka koodissa ei
ole vikaa.

Yksittäisen testin häiriö vaikuttaa pieneltä, mutta putki vaatii, että
*kaikki* testit menevät läpi, joten häiriöt kertautuvat.

```{.python tiedosto="esimerkit/luku04/epavakaa.py" osa="lapi"}
```

```{.tuloste tiedosto="esimerkit/luku04/epavakaa.odotettu"}
```

![Ehjän muutoksen läpimenon todennäköisyys epävakaiden testien määrän
mukaan. Sata testiä, joista kukin pettää kerran kahdessasadassa ajossa,
kaataa putken neljässä ajossa kymmenestä.](kuvat/epavakaa.png){width=62%}

Kun putki on punainen neljä kertaa kymmenestä ilman syytä, tiimi oppii
ajamaan sen uudelleen katsomatta, mikä hajosi. Sen jälkeen punainen ei
tarkoita mitään, ja oikeat viat pääsevät läpi samalla
uudelleenajolla.

Tavallinen lääke on automaattinen uudelleenajo: testi hyväksytään, jos
se menee läpi jollakin kolmesta yrityksestä. Tulosteen loppuosa näyttää,
mitä se tekee.

```{.python tiedosto="esimerkit/luku04/epavakaa.py" osa="uusinta"}
```

Häiriö katoaa näkyvistä, mutta samalla katoaa oikea vika, joka ilmenee
vain osassa ajoista. Kilpatilanne, joka kaataa testin kolmessa ajossa
kymmenestä, pääsee kolmen yrityksen läpi 97 prosentin
todennäköisyydellä. Ajoittain epäonnistuva testi on usein oikeassa:
se on löytänyt kilpatilanteen, aikakatkaisun tai järjestysriippuvuuden,
joka on olemassa myös tuotannossa.

Parempi menettely on kolmiosainen.

1. **Tunnista.** Putki kirjaa testit, jotka menivät läpi vasta
   uudelleenajolla, tai testejä ajetaan toistuvasti muuttumattomalle
   koodille.
2. **Eristä.** Epävakaaksi todettu testi siirretään karanteeniin: se
   ajetaan edelleen ja tulos kirjataan, mutta se ei kaada putkea.
   Karanteenilla on omistaja ja määräaika.
3. **Korjaa tai poista.** Testi korjataan, tai jos se ei ole
   korjaamisen arvoinen, poistetaan. Pysyvä karanteeni on poistettu
   testi, jota ylläpidetään silti.

Tavallisimmat syyt ovat testien välinen jaettu tila, riippuvuus
kellonajasta tai suoritusjärjestyksestä, kiinteät odotusajat,
verkkoyhteydet ulkoisiin palveluihin ja aidot rinnakkaisuusvirheet.

## Yksi tie tuotantoon

Putki on hyödyllinen vain, jos se on *ainoa* reitti tuotantoon. Jos
kiireellinen korjaus viedään käsin putken ohi, tuotannossa on
versio, jota ei ole testattu, jota ei voi rakentaa uudelleen ja jonka
seuraava putken läpi kulkeva julkaisu pyyhkii pois.

Tästä seuraa vaatimus putkelle itselleen: sen on oltava niin nopea,
että hätäkorjauskin ehtii sen läpi. Jos näin ei ole, ohitus on
ymmärrettävä reaktio, ja korjattava asia on putken kesto.

Yksi reitti on myös hallinnon kannalta käytännöllinen. Putki tallentaa
jokaisesta käyttöönotosta, mikä commit vietiin, kuka sen hyväksyi ja
mitkä testit ajettiin. Moni sääntelyn vaatima todiste syntyy näin
sivutuotteena, eikä erillistä muutoshallinnan kirjanpitoa tarvita
jokaista rutiinimuutosta varten.

## Rajat

Putki testaa sen, mitä siihen on kirjoitettu. Vihreä putki tarkoittaa,
että tunnetut tarkistukset menivät läpi, eikä sitä, että ohjelma on
virheetön. Kaksi rajaa kannattaa tuntea.

- **Putki ei korvaa tuotannon seurantaa.** Testiympäristö eroaa
  tuotannosta aina jotenkin: datan määrä, liikenteen muoto,
  riippuvuuksien käytös. Siksi luvut 7 ja 8 käsittelevät julkaisemista
  niin, että vika havaitaan tuotannossa pienellä käyttäjäjoukolla.
- **Automaatio on koodia.** Putken skriptit vanhenevat, rikkoutuvat ja
  vaativat ylläpitoa. Putki, jota kukaan ei omista, rapautuu.

## Käytännössä

- Mittaa commit-vaiheen kesto ja pidä se kymmenessä minuutissa.
  Siirrä hitaat testit myöhempään vaiheeseen ennen kuin poistat ne.
- Testaa valmis artefakti, älä vain lähdekoodia.
- Pysäytä putki ensimmäiseen virheeseen niin, ettei rikkinäisestä
  muutoksesta synny käyttöönotettavaa pakettia.
- Kirjaa epävakaat testit ja anna jokaiselle omistaja. Älä piilota
  niitä automaattisella uudelleenajolla.
- Älä salli reittiä putken ohi. Jos sellaista tarvitaan, putki on
  liian hidas.

## Itsearviointi

- Osaat kuvata toimitusputken vaiheet ja kertoa, mihin kysymykseen
  kukin vastaa.
- Osaat perustella, miksi commit-vaiheen kestolle on raja ja mitä
  siihen kuuluu.
- Osaat esittää putken riippuvuusverkkona ja selittää, mitkä vaiheet
  voi ajaa rinnakkain.
- Osaat laskea, kuinka usein putki kaatuu epävakaiden testien vuoksi,
  ja perustella, miksi automaattinen uudelleenajo piilottaa oikeita
  vikoja.
- Osaat selittää, miksi putken on oltava ainoa reitti tuotantoon.
