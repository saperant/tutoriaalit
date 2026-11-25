# DevOps, SRE ja vastuunjako

Edellinen luku päätyi siihen, että omistajuus sisältää tuotannon.
Historiallisesti näin ei ole ollut: kehitys ja ylläpito olivat eri
osastoja. Tämä luku käy läpi, miksi jako tuotti ongelmia, mitä DevOps
ja SRE sille tekivät ja miten päivystys ja virheistä oppiminen
järjestetään.

## Kehityksen ja ylläpidon muuri

Perinteisessä mallissa kehitysosasto kirjoitti ohjelman ja luovutti sen
ylläpidolle, joka asensi ja ajoi sitä. Osastoilla oli vastakkaiset
tavoitteet: kehitystä mitattiin toimitetuilla muutoksilla, ylläpitoa
häiriöttömyydellä. Koska muutokset aiheuttavat häiriöitä, ylläpidon
järkevä vastaus oli hidastaa muutoksia: julkaisuikkunat, hyväksyntälautakunnat
ja pitkät tarkistuslistat. Kehitys vastasi kasvattamalla julkaisuja,
ja suuret julkaisut epäonnistuivat useammin. Kumpikin toimi omien
mittariensa mukaan oikein, ja kokonaisuus huononi.

Tämä on luvun 3 siilo puhtaimmillaan, ja sen hinta on juuri
luovutuksen odotus ja katoava tieto.

## DevOps

Sana **DevOps** syntyi vuonna 2009, kun Patrick Debois järjesti
Gentissä ensimmäisen DevOpsDays-tapahtuman. Samana vuonna John Allspaw
ja Paul Hammond kertoivat, miten Flickrissä kehitys ja ylläpito
tekivät yhdessä yli kymmenen tuotantojulkaisua päivässä. DevOps ei ole
työkalu, rooli eikä tiimi vaan tapa toimia: kehitys ja ylläpito
jakavat tavoitteet, vastuun ja työkalut. Sen sisältöä tiivistetään
usein kirjaimin CALMS: kulttuuri, automaatio, lean-ajattelu, mittaaminen
ja jakaminen.

Forsgrenin, Humblen ja Kimin *Accelerate* (2018) kokosi usean vuoden
kyselytutkimuksen tulokset. Keskeinen havainto on, että nopeus ja
vakaus eivät ole vaihtokauppa: organisaatiot, jotka julkaisevat usein
ja pienin erin, myös toipuvat häiriöistä nopeammin ja epäonnistuvat
harvemmin. Mittarit ja käytännöt käsitellään taidossa *Jatkuva
integraatio ja toimitus*.

## Vastuunjaon mallit ja niiden vääristymät

Matthew Skelton kokosi vuonna 2013 luettelon tavoista järjestää
kehityksen ja ylläpidon suhde (*DevOps Topologies*). Hyödyllisimpiä
ovat vääristymät, koska ne ovat tunnistettavia:

| Vääristymä | Mitä tapahtuu |
|------------------------|---------------------------------------------|
| kehitys ja ylläpito siiloissa | muutos heitetään muurin yli, vika palautetaan takaisin |
| erillinen DevOps-tiimi | kolmas siilo kahden väliin: ”DevOps hoitaa putken” |
| ylläpito nimetty uudelleen | sama tikettijono, uusi nimi (SRE, alusta) |
| kehitys ilman ylläpito-osaamista | ”pilvi hoitaa”; kukaan ei osaa kapasiteettia, varmistuksia tai verkkoa |

Toimivia malleja on useita, ja ne vastaavat luvun 4 tyyppejä:
virtatiimi omistaa palvelunsa tuotannossa ja käyttää alustaa palveluna,
ja mahdollistava tiimi tai SRE-ryhmä tukee tarvittaessa. Yhteistä
niille on, että sama tiimi kantaa sekä muutoksen hyödyn että sen
riskin.

```{.dot otsikko="Kaksi vastuunjakoa: muuri kehityksen ja ylläpidon välillä sekä tiimi, joka omistaa palvelunsa ja käyttää alustaa"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  subgraph cluster_a { label="siilot"; style=dashed;
    dev [label="kehitys\ntavoite: muutokset"];
    ops [label="ylläpito\ntavoite: vakaus"];
    dev -> ops [label="julkaisu"]; ops -> dev [label="vikatiketti"]; }
  subgraph cluster_b { label="omistava tiimi"; style=dashed;
    tiimi [label="virtatiimi\nkehittää, julkaisee,\npäivystää"];
    alusta [label="alusta\nitsepalveluna"];
    tiimi -> alusta [label="käyttää"]; }
}
```

## SRE

**Site Reliability Engineering** syntyi Googlessa 2000-luvun alussa.
Ben Treynor Sloss kuvasi sen sanomalla, että SRE on se, mitä tapahtuu,
kun ohjelmistokehittäjää pyydetään suunnittelemaan ylläpito-organisaatio.
Kirja *Site Reliability Engineering* (2016) kuvaa käytännöt. Tämän
tutoriaalin kannalta olennaisimmat ovat ne, jotka koskevat vastuunjakoa.

- **Virhebudjetti.** Palvelulle sovitaan luotettavuustavoite, ja
  tavoitteen ja sadan prosentin erotus on budjetti, jonka saa käyttää
  muutosten riskiin. Kun budjetti on käytetty, uudet ominaisuudet
  odottavat ja työ kohdistetaan luotettavuuteen. Budjetti tekee
  kehityksen ja ylläpidon ristiriidasta yhteisen luvun. Laskenta
  käsitellään taidossa *Skaalautuvien järjestelmien suunnittelu*.
- **Raadannan raja.** Raadanta (*toil*) on käsin tehtävää, toistuvaa
  ja automatisoitavissa olevaa ylläpitotyötä, joka kasvaa palvelun
  mukana. SRE-tiimin ajasta enintään puolet saa mennä ylläpitotyöhön;
  loppu käytetään kehitystyöhön, joka vähentää raadantaa. Jos raja
  ylittyy, ylimenevä työ palautetaan kehitystiimille.
- **Palvelun palauttaminen.** SRE-tiimi voi kieltäytyä tukemasta
  palvelua, joka ei täytä sovittuja ehtoja. Tuki on ansaittava.

Googlen malli olettaa suuren mittakaavan ja erillisen SRE-organisaation.
Pienemmässä yrityksessä käytännöt (tavoitteet, virhebudjetti,
jälkiselvitykset, raadannan mittaaminen) ovat käyttökelpoisia ilman
erillistä tiimiä.

## Päivystys

Tuotantovastuu tarkoittaa päivystystä, ja päivystys on ihmisille
raskasta. SRE-kirja antaa kaksi mitoitussääntöä: päivystystä saa olla
enintään neljännes insinöörin ajasta, ja vuorossa on kerrallaan
ensisijainen ja varalla oleva päivystäjä. Näistä seuraa ringin
vähimmäiskoko:

```{.python tiedosto="esimerkit/07-paivystys.py" osa="rinki"}
```

Toinen sääntö koskee kuormaa vuoron aikana. Kirjan mukaan yhden
häiriön käsittely selvityksineen ja jälkiselvityksineen vie
keskimäärin kuusi tuntia:

```{.python tiedosto="esimerkit/07-paivystys.py" osa="kuorma"}
```

```{.tuloste tiedosto="esimerkit/07-paivystys.odotettu"}
```

Kahden päivystäjän rinki on kestävä vasta kahdeksalla hengellä.
Kolmen hengen tiimi, joka päivystää yksin omaa palveluaan, on vuorossa
kaksi viikkoa kolmesta. Tämä on käytännön vastaväite periaatteelle
”tee se, aja se”: pieni tiimi ei pysty päivystämään kestävästi.
Ratkaisuja ovat yhteinen rinki usean tiimin kesken (mikä vaatii hyvät
toimintaohjeet), päivystys vain työaikana palveluille, jotka sen
kestävät, ja ennen kaikkea häiriöiden vähentäminen. Jos häiriöitä on
neljä viikossa, ensisijaisen päivystäjän työajasta kaksi kolmasosaa
menee niihin, eikä hän tee muuta.

## Jälkiselvitys ilman syyllistämistä

Häiriön jälkeen tehdään **jälkiselvitys** (*postmortem*): mitä
tapahtui, miten se havaittiin, miten toivuttiin ja mitä muutetaan.
John Allspaw kuvasi vuonna 2012 Etsyn käytännön, jossa selvitys
tehdään syyllistämättä (*blameless*). Ajatus tulee turvallisuuskriittisiltä
aloilta, erityisesti Sidney Dekkerin työstä: ihminen toimi tavalla,
joka oli hänen silloisten tietojensa valossa järkevä, joten kysytään,
miksi järjestelmä teki virheen mahdolliseksi ja vaikeaksi huomata.

Syyllistämättömyys ei ole kiltteyttä vaan tiedonhankintaa. Jos virheen
tekijää rangaistaan, seuraava virhe piilotetaan, ja organisaatio
menettää tiedon, jota se tarvitsisi. *Ohjelmistoprojektin hallinta*
käsitteli samaa psykologisen turvallisuuden nimellä.

## Kulttuuri ja tiedon kulku

Ron Westrum luokitteli organisaatiokulttuurit sen mukaan, miten tieto
niissä kulkee:

| Kulttuuri | Suhde tietoon | Huonon uutisen tuoja | Epäonnistuminen |
|-------------------|------------------|-------------------|--------------------|
| patologinen (valta) | tieto on vallan väline | vaiennetaan | etsitään syyllinen |
| byrokraattinen (säännöt) | tieto kulkee virallisia kanavia | jätetään huomiotta | etsitään vastuullinen |
| generatiivinen (tulos) | tietoa haetaan aktiivisesti | koulutetaan | selvitetään syy |

*Accelerate*-tutkimuksessa generatiivinen kulttuuri ennusti sekä
parempaa toimituskykyä että parempaa työhyvinvointia. Kulttuuria ei
voi määrätä, mutta sitä muovaavat teot: miten esihenkilö reagoi
huonoon uutiseen, mitä jälkiselvityksestä seuraa ja saako toisen
tiimin koodia lukea.

## Käytännössä

- **Älä perusta DevOps-tiimiä muuriksi.** Jos tarvitaan tiimi, se on
  alustatiimi, jolla on käyttäjät, tai mahdollistava tiimi, jolla on
  päättymispäivä.
- **Anna sama tavoite molemmille.** Yhteinen luotettavuustavoite ja
  virhebudjetti korvaavat kiistan siitä, saako julkaista.
- **Mitoita päivystys ihmisten mukaan.** Laske ringin koko ja
  häiriöiden kuorma. Jos luvut eivät täsmää, vähennä häiriöitä tai
  yhdistä rinkejä; älä oleta, että ihmiset venyvät.
- **Mittaa raadanta.** Kirjaa viikon ajan, mihin ylläpitoaika menee.
  Toistuvin käsityö on ensimmäinen automatisoitava.
- **Tee jälkiselvitys jokaisesta merkittävästä häiriöstä** ja seuraa,
  toteutuvatko sovitut korjaukset. Selvitys ilman muutoksia on
  rituaali.

## Itsearviointi

- Osaat selittää, miksi kehityksen ja ylläpidon erilliset tavoitteet
  hidastavat ja heikentävät kokonaisuutta.
- Osaat kuvata DevOpsin toimintatapana ja tunnistaa sen tavalliset
  vääristymät.
- Osaat kertoa, miten virhebudjetti ja raadannan raja jakavat vastuun
  kehityksen ja SRE:n välillä.
- Osaat laskea päivystysringin vähimmäiskoon ja arvioida häiriöiden
  kuorman.
- Osaat perustella syyllistämättömän jälkiselvityksen ja kuvata
  Westrumin kolme kulttuurityyppiä.
