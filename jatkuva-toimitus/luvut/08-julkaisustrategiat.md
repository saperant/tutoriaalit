# Julkaisustrategiat

Putken läpäissyt artefakti on valmis tuotantoon. Jäljellä on kaksi
päätöstä: kuka päättää, että se viedään sinne, ja millä tavalla vanha
versio vaihdetaan uuteen. Tämä luku käsittelee molemmat ja vertaa
vaihtotapoja mallilla, joka laskee, kuinka moni käyttäjä kohtaa vian
ennen kuin se huomataan.

## Jatkuva toimitus ja jatkuva käyttöönotto

Jatkuvassa toimituksessa jokainen putken läpäissyt rungon tila
*voidaan* julkaista, ja julkaisu tapahtuu ihmisen päätöksestä.
Jatkuvassa käyttöönotossa päätöstä ei ole: putken läpäissyt muutos
menee tuotantoon itsestään.

| Asia | Jatkuva toimitus | Jatkuva käyttöönotto |
|------------------|-------------------------------|-------------------------------|
| viimeinen askel | ihminen käynnistää | automaattinen |
| julkaisutahti | liiketoiminnan valitsema | jokainen muutos |
| vaatii | luotettavan putken | lisäksi automaattisen seurannan ja perumisen |
| sopii, kun | julkaisulla on ulkoisia ehtoja | palvelu on oma, vika on halpa perua |

Jatkuva käyttöönotto ei ole jatkuvan toimituksen parempi versio. Se on
perusteltu, kun palvelu on täysin omassa hallinnassa ja luvun 7
liput erottavat käyttöönoton julkaisusta. Monella on hyvä syy
pysähtyä ihmisen päätökseen: asiakkaalle on ilmoitettava etukäteen,
laite vaatii huoltokatkon, sovelluskauppa tarkastaa version tai
viranomainen edellyttää hyväksyntää.

Olennaista on, mikä päätös on. Jatkuvassa toimituksessa se on
liiketoiminnan päätös ajankohdasta, eikä siihen liity teknistä
epävarmuutta, koska putki on jo vastannut kysymykseen, toimiiko versio.
Jos julkaisupäätös vaatii viikon käsin testaamista, kyse ei ole
jatkuvasta toimituksesta, vaikka käyttöönotto olisi automaattinen.
Julkaisutahti voi silti olla harva. Tavoite on, että julkaisu on
*mahdollinen* milloin tahansa.

## Neljä tapaa vaihtaa versio

Tutoriaali *Kontit ja pilvi-infrastruktuuri* esittelee
käyttöönottostrategiat Kubernetesin välinein. Tässä niitä tarkastellaan
periaatteina, jotka pätevät alustasta riippumatta.

| Strategia | Miten vaihto tapahtuu | Peruminen | Hinta |
|---------------|-------------------------------|--------------------|--------------------|
| kerralla | vanha pysäytetään ja uusi asennetaan tilalle | uusi asennus vanhasta | katko; vika osuu kaikkiin |
| rullaava | palvelimet päivitetään yksi tai muutama kerrallaan | sama kierros takaisin | versiot ajossa rinnan; hidas |
| sinivihreä | uusi versio käynnistetään vanhan rinnalle, ja liikenne käännetään kerralla | liikenne takaisin vanhaan | kaksinkertainen kapasiteetti vaihdon ajan |
| kanarialintu | pieni osa liikenteestä ohjataan uuteen, ja osuutta kasvatetaan mittareiden mukaan | osuus nollaan | liikenteen ohjaus ja mittarit rakennettava |

```{.dot otsikko="Sinivihreä käyttöönotto: reititin osoittaa yhteen ympäristöön kerrallaan, ja vaihto on yksi asetus"}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.5;
  k [label="käyttäjät"]; r [label="reititin tai\nkuormantasaaja"];
  s [label="sininen:\nversio 1.4"]; v [label="vihreä:\nversio 1.5"];
  d [label="tietokanta", shape=cylinder];
  k -> r;
  r -> s [label="nyt"];
  r -> v [style=dashed, label="vaihdon\njälkeen"];
  s -> d; v -> d;
}
```

Kuva näyttää myös sinivihreän käyttöönoton heikon kohdan: tietokanta on
yhteinen. Kaksi versiota käyttää samaa dataa, joten niiden on oltava
yhteensopivia sen kanssa (luku 9).

Kanarialintujulkaisun nimi tulee kaivosten kanarialinnuista, jotka
varoittivat kaasusta ennen kuin se ehti vahingoittaa ihmisiä. Pieni osa
liikenteestä kohtaa uuden version ensin.

## Strategiat mallina

Strategian voi kuvata kahdella luettelolla: uuden version osuus
liikenteestä askel askeleelta ja se, mitä perumisen aikana vielä
tapahtuu.

```{.python tiedosto="esimerkit/toimitus/julkaisu.py" osa="strategia"}
```

Simulaatiossa jokaisella askeleella saapuu tuhat pyyntöä. Uuden version
virheet lasketaan, ja julkaisu perutaan, kun uudelle versiolle on
kertynyt vähintään sata pyyntöä ja niistä yli kaksi prosenttia on
epäonnistunut.

```{.python tiedosto="esimerkit/toimitus/julkaisu.py" osa="simuloi"}
```

Malli ajetaan kolmelle versiolle: ehjälle, selvästi rikkinäiselle ja
sellaiselle, jossa vika on hienovarainen. Luvut ovat kolmensadan ajon
keskiarvoja.

```{.tuloste tiedosto="esimerkit/luku08/strategiat.odotettu"}
```

**Ehjä versio** näyttää strategian hinnan silloin, kun mikään ei mene
vikaan. Kerralla tehty ja sinivihreä vaihto ovat valmiita yhdessä
askeleessa, kanarialintu kuudessa ja rullaava kymmenessä. Varovaisuus
maksaa aikaa jokaisessa julkaisussa.

**Rikkinäinen versio** näyttää, mitä varovaisuudella saadaan. Jokainen
strategia havaitsee viiden prosentin virhetason ja peruu, mutta
käyttäjien kokema vahinko eroaa suuruusluokalla.

![Epäonnistuneiden pyyntöjen kertymä, kun uudessa versiossa viisi
prosenttia pyynnöistä epäonnistuu. Kerralla tehdyssä vaihdossa vahinko
kasvaa koko perumisen ajan.](kuvat/julkaisu.png){width=64%}

Kerralla tehdyssä vaihdossa vika osuu kaikkiin ja jatkuu niin kauan
kuin vanhan version asentaminen takaisin kestää. Sinivihreässä vika
osuu myös kaikkiin, mutta peruminen on välitön, koska vanha ympäristö
on yhä käynnissä. Rullaava ja kanarialintu rajaavat vian pieneen
osaan liikenteestä. Kanarialintu jää noin kuuteen epäonnistuneeseen
pyyntöön, kerralla tehty vaihto noin kahteensataan.

Strategiat eroavat siis kahdella akselilla: kuinka suuri osa
käyttäjistä altistuu ennen havaintoa ja kuinka kauan peruminen kestää.

## Hienovarainen vika

Kolmas ajo on opettavaisin. Kun uuden version virhetaso on 0,6
prosenttia, kuusinkertainen ehjään verrattuna, juuri mikään strategia
ei huomaa mitään. Peruutusraja oli kaksi prosenttia, ja vika jää sen
alle. Kanarialintu ei suojaa vialta, jota sen mittari ei näe.

Tästä seuraa kanarialintujulkaisun todelliset vaatimukset.

- **Mittari on valittava niin, että se näkee vian.** Virhetaso on
  ilmeinen valinta, mutta vika voi olla hitautta, vääriä tuloksia tai
  liiketoiminnan mittarin lasku, joka ei näy virheenä lainkaan.
- **Vertailukohta on vanha versio samaan aikaan.** Kiinteä raja on
  karkea. Tarkempi tapa on verrata kanarialinnun mittareita vanhan
  version mittareihin samalla hetkellä, jolloin vuorokaudenaika ja
  kuorma eivät sotke vertailua.
- **Näytteen on oltava riittävä.** Pieni ero vaatii paljon liikennettä
  erottuakseen satunnaisvaihtelusta. Viiden prosentin osuus
  vähäliikenteisestä palvelusta on muutama pyyntö minuutissa, eikä
  siitä voi päätellä mitään. Vähäliikenteisessä palvelussa
  kanarialintu on usein näennäinen, ja sinivihreä vaihto hyvillä
  savutesteillä on rehellisempi valinta.
- **Aikaa on annettava.** Muistivuoto tai hitaasti täyttyvä jono
  näkyy vasta tuntien päästä.

Mittareiden valintaa, palvelutasotavoitteita ja virhebudjettia
käsittelee *Skaalautuvien järjestelmien suunnittelu*. Virhebudjetti
sopii julkaisupäätöksen pohjaksi: kun budjettia on jäljellä, julkaistaan
normaalisti, ja kun se on käytetty, julkaisuja hidastetaan ja
korjataan luotettavuutta.

## Mitä asteittainen julkaisu edellyttää

Kaikissa muissa strategioissa kuin kerralla tehdyssä vaihdossa vanha ja
uusi versio ovat ajossa yhtä aikaa. Siitä seuraa vaatimuksia, jotka on
otettava huomioon jo suunnittelussa.

- **Versiot ovat keskenään yhteensopivia.** Uuden version kirjoittama
  tieto on vanhan luettavissa ja päinvastoin. Sama koskee palvelujen
  välisiä rajapintoja ja viestejä (ks. *Palveluarkkitehtuurit*,
  sopimustestaus).
- **Tila ei ole palvelimen muistissa.** Käyttäjän peräkkäiset pyynnöt
  voivat osua eri versioihin, joten istunnot ja välitulokset ovat
  yhteisessä varastossa.
- **Palvelu kertoo, onko se valmis.** Kuormantasaaja ohjaa liikennettä
  vain kopioille, jotka ilmoittavat olevansa valmiita, ja sammuva
  kopio käsittelee keskeneräiset pyyntönsä loppuun. Terveystarkistukset
  ja siistin sammutuksen käsittelee *Skaalautuvien järjestelmien
  suunnittelu*.
- **Käyttöönotto on automaattinen.** Kymmenen askeleen julkaisua ei
  tehdä käsin.

## Peruminen ja korjaus eteenpäin

Kun julkaisu osoittautuu vialliseksi, vaihtoehtoja on kaksi: palataan
edelliseen versioon tai julkaistaan korjaus.

**Peruminen** on nopea ja turvallinen, jos edellinen artefakti on
tallessa ja tiedon muoto ei ole muuttunut. Se ei vaadi vian
ymmärtämistä, joten se on oikea ensimmäinen toimi, kun käyttäjät
kärsivät.

**Korjaus eteenpäin** (*roll forward*) on ainoa vaihtoehto, kun
paluuta ei ole: tietokanta on muuttunut peruuttamattomasti, viestejä on
lähetetty tai asiakkaat ovat jo ladanneet version. Se on myös
luonteva, kun putki on nopea ja vika pieni.

Peruminen on käyttöönotto, ja sitä koskee sama sääntö kuin muitakin:
jos sitä ei ole harjoiteltu, se ei toimi. Perumista kannattaa kokeilla
säännöllisesti tavallisena päivänä, ei ensimmäistä kertaa häiriön
aikana.

Kaikkea ei voi perua. Mobiilisovelluksen, työpöytäohjelman tai
laiteohjelmiston julkaisu on käyttäjän laitteessa, eikä sitä saa
takaisin. Näissä ympäristöissä korostuvat sovelluskaupan vaiheittainen
jakelu, palvelimelta ohjattavat liput ja se, että uuden version on
toimittava vanhan palvelinrajapinnan kanssa ja päinvastoin.

## Julkaisun jälkeen

Julkaisu ei pääty siihen, että uusi versio on käynnissä. Se päättyy,
kun on varmistettu, että versio toimii.

- **Savutesti tuotannossa.** Käyttöönoton jälkeen ajetaan muutama
  tarkistus, jotka käyttävät järjestelmää ulkoa päin.
- **Julkaisu näkyy mittareissa.** Käyttöönoton hetki merkitään
  valvonnan kuvaajiin. Kun virhetaso nousee, ensimmäinen kysymys on,
  mitä juuri muuttui.
- **Julkaisija seuraa.** Muutoksen tekijä katsoo mittareita
  käyttöönoton jälkeen eikä siirry heti seuraavaan työhön.
- **Portit ovat automaattisia, kun mahdollista.** Asteittainen
  julkaisu etenee seuraavaan portaaseen vain, jos mittarit ovat
  rajoissa, ja peruu itse, jos eivät ole.

Julkaisuajankohdalla on merkitystä vain, jos julkaisut ovat suuria ja
riskialttiita. Perjantai-iltapäivän julkaisukielto kertoo, että
julkaisuun ei luoteta. Kun julkaisut ovat pieniä ja peruminen nopeaa,
ajankohdan valinta menettää merkityksensä, mutta kiellon poistaminen
on seuraus luottamuksesta, ei keino saavuttaa sitä.

## Käytännössä

- Päätä erikseen, kuka käynnistää julkaisun ja millä strategialla
  versio vaihdetaan.
- Valitse strategia liikenteen määrän ja perumisen hinnan mukaan.
  Vähäliikenteiselle palvelulle sinivihreä ja savutestit, vilkkaalle
  kanarialintu.
- Määritä kanarialinnulle mittarit, vertailukohta, vähimmäisnäyte ja
  vähimmäisaika ennen kuin otat sen käyttöön.
- Pidä kaksi peräkkäistä versiota aina keskenään yhteensopivina.
- Harjoittele peruminen. Kirjaa, mitä ei voi perua.
- Merkitse julkaisut valvonnan kuvaajiin.

## Itsearviointi

- Osaat erottaa jatkuvan toimituksen ja jatkuvan käyttöönoton ja
  perustella, milloin ihmisen päätös on paikallaan.
- Osaat verrata neljää julkaisustrategiaa altistuvien käyttäjien
  määrän ja perumisen keston mukaan.
- Osaat selittää, miksi kanarialintujulkaisu ei havaitse vikaa, joka
  jää sen mittarin tai rajan alle, ja mitä vähäinen liikenne siitä
  seuraa.
- Osaat luetella, mitä kahden version ajaminen rinnan vaatii
  sovellukselta.
- Osaat valita perumisen ja eteenpäin korjaamisen välillä ja kertoa,
  mikä estää perumisen.
