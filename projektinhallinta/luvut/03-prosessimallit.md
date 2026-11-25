# Prosessimallit

Prosessimalli kertoo, missä järjestyksessä työ tehdään ja milloin
päätökset lyödään lukkoon. Mallien erot palautuvat yhteen kysymykseen:
kuinka kauan tehdään työtä ennen kuin saadaan palautetta siitä, oliko
työ oikeaa. Tämä luku käy läpi vaiheittaisen mallin, iteratiivisen
kehityksen ja ketterien menetelmien periaatteet. Scrum ja Kanban, joita
useimmat tiimit käytännössä käyttävät, ovat luvussa 4.

## Vaiheittainen malli eli vesiputous

Vaiheittaisessa mallissa työ etenee vaiheesta toiseen: vaatimukset,
suunnittelu, toteutus, testaus ja käyttöönotto. Jokainen vaihe tuottaa
dokumentin, joka hyväksytään ennen seuraavan alkua.

```{.dot otsikko="Vaiheittainen malli: palaute käyttäjältä tulee vasta lopussa"}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.35;
  v [label="vaatimukset"]; s [label="suunnittelu"]; t [label="toteutus"];
  te [label="testaus"]; k [label="käyttöönotto"];
  v -> s -> t -> te -> k;
  k -> v [style=dashed, constraint=false, label="palaute"];
}
```

Mallin nimi yhdistetään Winston Roycen artikkeliin vuodelta 1970.
Artikkeli on luettu huonosti. Royce esittää vaiheittaisen kaavion,
mutta toteaa heti perään, että sellaisenaan toteutettuna se on
riskialtis: testaus on ensimmäinen hetki, jolloin suunnitelmaa
verrataan todellisuuteen, ja silloin havaitut ongelmat pakottavat
palaamaan suunnitteluun asti. Loppuosa artikkelista ehdottaa korjauksia,
muun muassa koeversion tekemistä ensin (”tee se kahdesti”) ja asiakkaan
ottamista mukaan työhön. Sana vesiputous ei esiinny artikkelissa; nimi
vakiintui myöhemmin.

Mallin vahvuus on selkeys. Sopimus, budjetti ja aikataulu on helppo
sitoa vaiheisiin, ja jokaisella vaiheella on tarkistettava tulos. Se
toimii, kun vaatimukset tunnetaan hyvin eivätkä muutu, kuten vanhan
järjestelmän siirrossa uudelle alustalle. Sen heikkous on oletus, että
vaatimukset voidaan tietää etukäteen. Kun oletus ei päde, virhe
paljastuu vasta käyttöönotossa, kun kaikki raha on käytetty.

## V-malli

**V-malli** on vaiheittaisen mallin muunnelma, jossa jokaista
määrittelyvaihetta vastaa testausvaihe: vaatimuksia hyväksymistestaus,
järjestelmäsuunnittelua järjestelmätestaus, yksityiskohtaista
suunnittelua integraatio- ja yksikkötestaus. Testit suunnitellaan
määrittelyn rinnalla.

V-malli on vallitseva turvallisuuskriittisillä ja säädellyillä aloilla,
kuten auto-, lääkintälaite-, ilmailu- ja raideliikenneohjelmistoissa.
Syy on jäljitettävyys: viranomaiselle on osoitettava, että jokainen
vaatimus on toteutettu ja testattu. Mallin sisällä voidaan silti
työskennellä iteratiivisesti, ja näin nykyään tehdäänkin. V kuvaa
tällöin todistusaineiston rakennetta eikä työn järjestystä.

## Iteratiivinen ja inkrementaalinen kehitys

Iteratiivisessa kehityksessä työ tehdään kierroksina, ja jokaisessa on
kaikki vaiheet pienenä.

- **Inkrementaalinen**: järjestelmä kasvaa käyttökelpoinen pala
  kerrallaan.
- **Iteratiivinen**: jo tehtyä parannetaan palautteen perusteella.

```{.dot otsikko="Iteratiivinen kehitys: jokainen kierros tuottaa palautetta"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.4;
  s [label="suunnittele\npieni osa"]; t [label="toteuta\nja testaa"];
  n [label="näytä tai\njulkaise"]; o [label="opi ja\nsäädä suuntaa"];
  s -> t -> n -> o;
  o -> s [constraint=false];
}
```

Ajatus ei ole uusi. Larman ja Basili ovat koonneet esimerkkejä
iteratiivisesta kehityksestä 1950-luvulta alkaen, ja Barry Boehmin
spiraalimalli (1988) teki siitä riskienhallinnan välineen: jokaisella
kierroksella ratkaistaan ensin suurin jäljellä oleva riski.
Vaiheittaista mallia ei siis koskaan pidetty tutkimuksessa ainoana
tapana, vaikka sopimuskäytännöt pitkään olettivat sen.

## Ketterä kehitys

Vuonna 2001 seitsemäntoista kevyiden menetelmien kehittäjää kirjoitti
**ketterän ohjelmistokehityksen julistuksen**. Sen neljä arvoa
asettavat kaksi hyvää asiaa vastakkain:

| Arvostamme enemmän | kuin |
|------------------------------------|------------------------------------|
| yksilöitä ja vuorovaikutusta | prosesseja ja työkaluja |
| toimivaa ohjelmistoa | kattavaa dokumentaatiota |
| yhteistyötä asiakkaan kanssa | sopimusneuvotteluja |
| muutokseen vastaamista | suunnitelman noudattamista |

Julistus toteaa erikseen, että myös oikeanpuoleisilla asioilla on
arvoa. Tämä lause unohtuu usein: ketteryys ei tarkoita, ettei
suunnitella tai dokumentoida.

Arvoja täsmentää kaksitoista periaatetta. Projektinhallinnan kannalta
keskeisimmät ovat: toimivaa ohjelmistoa toimitetaan usein, parista
viikosta pariin kuukauteen; muuttuvat vaatimukset ovat tervetulleita
myöhäänkin; liiketoiminnan edustajat ja kehittäjät työskentelevät
yhdessä päivittäin; toimiva ohjelmisto on edistymisen ensisijainen
mittari; työtahti on kestävä; ja tiimi tarkastelee säännöllisesti
toimintaansa ja säätää sitä.

Julistus ei ole menetelmä. Se ei kerro, mitä maanantaina tehdään.
Menetelmiä ovat esimerkiksi Scrum ja Kanban (luku 4) sekä XP.

### Extreme Programming

Kent Beckin **Extreme Programming** (XP) on ketteristä menetelmistä
teknisin. Sen käytännöt ovat levinneet laajalle myös tiimeihin, jotka
eivät ole XP:stä kuulleetkaan: testivetoinen kehitys, jatkuva
integraatio, refaktorointi, pariohjelmointi, pienet julkaisut, koodin
yhteisomistus, yksinkertainen suunnittelu ja kestävä työtahti. XP:n
havainto on, että lyhyet kierrokset edellyttävät teknistä kurinalaisuutta.
Ilman automaattisia testejä ja jatkuvaa integraatiota jokainen kierros
jättää jälkeensä vähän lisää rikkinäistä, ja kymmenennen kierroksen
kohdalla muuttaminen on yhtä kallista kuin vaiheittaisessa mallissa.
Käytännöt käsitellään taidoissa *Testivetoinen kehitys ja
testisuunnittelu* ja *Jatkuva integraatio ja toimitus*.

### Lean

**Lean**-ajattelu tulee Toyotan tuotantotavasta. Mary ja Tom
Poppendieck sovittivat sen ohjelmistokehitykseen seitsemäksi
periaatteeksi: poista hukka, vahvista oppimista, päätä mahdollisimman
myöhään, toimita mahdollisimman nopeasti, anna tiimille valta, rakenna
laatu sisään ja katso kokonaisuutta. Ohjelmistotyön hukkaa ovat
esimerkiksi keskeneräinen työ, ominaisuudet joita kukaan ei käytä,
tehtävien vaihtelu ja odottaminen. Leanin perintö näkyy erityisesti
virtauksen mittaamisessa (luku 7).

## Palautesilmukan pituus laskettuna

Mallien ero on palautteen tiheys, ja sen vaikutusta voi arvioida
laskemalla. Projektissa on 40 ominaisuutta, joista jokainen vie viisi
päivää. Neljännes on ymmärretty väärin, mutta se selviää vasta, kun
asiakas näkee tuloksen. Jos virhe huomataan heti, korjaus vie kaksi
päivää. Jokainen ominaisuus, joka on ehditty rakentaa väärän oletuksen
päälle, lisää korjaukseen puoli päivää.

```{.python tiedosto="esimerkit/03-palaute.py" osa="malli"}
```

Palaute ei ole ilmaista. Jokainen kierros vaatii julkaisun, esittelyn
ja läpikäynnin. Esimerkki laskee kokonaistyön kahdella kierroksen
hinnalla, kahdella päivällä ja puolella päivällä, ja tarkistaa kaavan
simuloimalla (funktio `simuloi` arpoo, mitkä ominaisuudet menivät
väärin).

```{.tuloste tiedosto="esimerkit/03-palaute.odotettu"}
```

![Erän koon U-käyrä. Suuri erä maksaa uudelleentyönä, pieni erä
palautekierrosten hintana. Kun kierros halpenee, paras erä
pienenee.](kuvat/palaute.png){width=62%}

Kolme havaintoa:

1. Yksi suuri erä (koko projekti kerralla) on selvästi kallein: 320
   päivää, josta uudelleentyötä on 118.
2. Pienin mahdollinen erä ei ole automaattisesti paras. Kun kierros
   maksaa kaksi päivää, palaute jokaisesta ominaisuudesta erikseen
   maksaa enemmän kuin se säästää. Käyrä on U:n muotoinen, ja optimi on
   tässä viiden ominaisuuden kohdalla.
3. Kun palautekierroksen hinta laskee puoleen päivään, optimi siirtyy
   kahteen ominaisuuteen ja koko käyrä laskee.

Kolmas havainto selittää, miksi ketterät menetelmät ja julkaisun
automatisointi kulkevat yhdessä. Jos julkaisu on päivän käsityö, tiheä
palaute ei kannata, ja tiimi ajautuu suuriin eriin. Automaattinen
testaus ja toimitusputki laskevat kierroksen hintaa, ja vasta se tekee
pienistä eristä taloudellisia. Reinertsen esittää saman U-käyrän
yleisenä periaatteena: erän koko on taloudellinen valinta
siirtokustannuksen ja viivästymisen hinnan välillä.

Malli on karkea. Todellisuudessa väärinymmärrysten osuus ja korjauksen
hinta vaihtelevat, eikä kaikkea voi näyttää asiakkaalle yhtä helposti.
Suunta ja muoto ovat kuitenkin yleisiä: myöhään löytyvä virhe on
kalliimpi, ja palautteen hinta määrää, kuinka usein sitä kannattaa
hakea.

## Mallin valinta

Malli valitaan tilanteen mukaan, ei muodin:

| Tilanne | Sopiva lähtökohta |
|------------------------------------|------------------------------------------|
| vaatimukset vakaat ja tunnetut, tekniikka tuttu | vaiheittainen eteneminen riittää |
| vaatimukset epävarmat, käyttäjä saatavilla | lyhyet kierrokset ja tiheät julkaisut |
| tekninen riski suuri | prototyyppi tai kokeilu ensin (spiraali) |
| virhe hengenvaarallinen tai viranomaisvalvottu | V-malli todisteluun, iteratiivinen työ sen sisällä |
| jatkuva ylläpito ja pienet muutokset | virtaukseen perustuva malli (Kanban) |

Useimmat organisaatiot käyttävät yhdistelmää. Budjetti ja suuret
päätökset tehdään vuosi- tai neljännesrytmissä, laitteisto ja
viranomaishyväksynnät etenevät vaiheittain, ja ohjelmisto tehdään
kierroksina. Yhdistelmässä ei ole mitään vikaa, kunhan tiedetään, mitkä
päätökset on lyöty lukkoon ja mitkä saavat muuttua.

## Käytännössä

- **Kysy, milloin ensimmäinen oikea käyttäjä näkee toimivan version.**
  Vastaus kertoo prosessista enemmän kuin sen nimi. Jos vastaus on
  ”käyttöönotossa”, malli on vaiheittainen, vaikka työ tehtäisiin
  sprinteissä.
- **Laske palautekierroksen hinta ja pienennä sitä.** Asennus,
  testiympäristö ja esittely ovat kierroksen kustannuksia. Niihin
  sijoittaminen maksaa itsensä takaisin jokaisella kierroksella.
- **Suurin riski ensin.** Aloita siitä osasta, jonka epäonnistuminen
  kaataisi hankkeen: tuntematon rajapinta, suorituskykyvaatimus tai
  epäselvä tarve. Helpoista osista aloittaminen tuottaa hyvännäköistä
  edistymistä ja siirtää huonot uutiset loppuun.
- **Älä sekoita rituaaleja ja periaatteita.** Päivittäinen palaveri ja
  kahden viikon sprintti eivät tee prosessista ketterää, jos laajuus,
  aikataulu ja toteutustapa on kiinnitetty etukäteen.
- **Dokumentoi se, mikä auttaa.** Julistus arvostaa toimivaa
  ohjelmistoa enemmän kuin kattavaa dokumentaatiota, ei sen sijaan.
  Arkkitehtuuripäätökset, rajapinnat ja käyttöohjeet tarvitaan
  mallista riippumatta (*Tekninen dokumentaatio*).

## Itsearviointi

- Osaat kuvata vaiheittaisen mallin ja V-mallin sekä kertoa, mitä Royce
  artikkelissaan varsinaisesti suositteli.
- Osaat erottaa iteratiivisen ja inkrementaalisen kehityksen.
- Osaat luetella ketterän julistuksen neljä arvoa ja selittää, miksi
  julistus ei ole menetelmä.
- Osaat selittää erän koon U-käyrän ja sen, miksi palautekierroksen
  halpeneminen pienentää parasta erää.
- Osaat valita prosessimallin lähtökohdan vaatimusten vakauden, riskin
  ja sääntelyn perusteella.
