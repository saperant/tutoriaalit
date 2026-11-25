# Sopimukset ja projektin päättäminen

Kun ohjelmisto tilataan toiselta organisaatiolta, sopimus määrää, kuka
kantaa epävarmuuden. Edellisissä luvuissa nähtiin, että työn määrää ei
tiedetä etukäteen. Sopimusmalli ei poista tätä epävarmuutta vaan jakaa
sen seuraukset tilaajan ja toimittajan kesken. Luvun toinen puolisko
käsittelee projektin päättämistä: luovutusta, siirtoa ylläpitoon ja
oppien keräämistä.

## Sopimusmallit

Kolme perusmallia eroavat siinä, mikä on kiinnitetty:

| Malli | Kiinnitetty | Riskin kantaa | Kannustin |
|----------------|--------------------|--------------------|--------------------------------|
| kiinteä hinta | laajuus ja hinta | toimittaja | toimittaja minimoi työn, tilaaja maksimoi laajuuden |
| tuntityö | tuntihinta | tilaaja | toimittajalla ei kannustinta tehokkuuteen |
| tavoitehinta | tavoite ja jakosääntö | molemmat | säästö ja ylitys jaetaan |

**Kiinteä hinta** tuntuu tilaajasta turvalliselta, koska lasku
tiedetään etukäteen. Sen hinta on kolmiosainen. Toimittaja hinnoittelee
riskin tarjoukseen. Laajuus on määriteltävä tarkasti ennen työn alkua,
jolloin palataan vaiheittaiseen malliin (luku 3). Ja jokainen muutos
on sopimusneuvottelu, jolloin osapuolten edut ovat vastakkaiset:
toimittaja tulkitsee määrittelyä suppeasti ja tilaaja laajasti.

**Tuntityö** (*time and materials*) on joustava: tilaaja voi muuttaa
suuntaa milloin tahansa ja maksaa tehdystä työstä. Riski on tilaajalla,
joten hänen on kyettävä ohjaamaan työtä ja arvioimaan sen tuloksia.
Malli sopii ketterään kehitykseen, kun tilaajalla on oma tuoteomistaja
ja työ näytetään usein.

**Tavoitehinnassa** sovitaan tavoitekustannus ja sääntö, jolla alitus
ja ylitys jaetaan, usein lisäksi kattohinta. Molemmat hyötyvät, jos työ
valmistuu tavoitetta halvemmalla, ja molemmat kärsivät ylityksestä.

Mallinnetaan riskinjako. Työn todellinen kustannus toimittajalle on
epävarma: mediaani on 100 000 euroa ja jakauma on vino. Toimittajan
katetavoite on 15 %.

```{.python tiedosto="esimerkit/10-sopimus.py" osa="mallit"}
```

```{.tuloste tiedosto="esimerkit/10-sopimus.odotettu"}
```

Samoista toteumista seuraa kolme erilaista lopputulosta:

- **Tuntityössä** tilaaja maksaa keskimäärin 122 000 euroa, mutta
  huonoimmassa kahdeskymmenesosassa tapauksista yli 200 000. Toimittaja
  ei koskaan tee tappiota.
- **Kiinteässä hinnassa** tilaaja maksaa aina 165 000 euroa, koska
  järkevä toimittaja hinnoittelee työn 85 %:n varmuustason mukaan.
  Varmuus maksaa tilaajalle keskimäärin 43 000 euroa enemmän kuin
  tuntityö. Toimittaja tekee silti tappiota seitsemässä tapauksessa
  sadasta. Jos kilpailu pakottaa tarjoamaan halvemmalla, tappion
  todennäköisyys kasvaa, ja tappiollinen toimittaja säästää siitä,
  mistä voi: laadusta.
- **Tavoitehinnassa** tilaajan keskimääräinen lasku on sama kuin
  tuntityössä, mutta pahimmat tapaukset ovat halvempia (95 %:n taso
  157 000 euroa), koska toimittaja kantaa puolet ylityksestä.

Malli jättää pois sen, mikä käytännössä usein ratkaisee: kannustimet
muuttavat käyttäytymistä. Kiinteä hinta palkitsee toimittajaa vähimmän
kelpaavan tuloksen toimittamisesta, ja tuntityö ilman ohjausta palkitsee
työn venymisestä. Mikään sopimus ei korvaa luottamusta ja sitä, että
tilaaja näkee toimivan ohjelmiston usein.

## Ketterä työ ja sopimukset

Ketterä kehitys ja kiinteä laajuus sopivat huonosti yhteen, koska
ketteryyden koko ajatus on antaa laajuuden joustaa. Käytännön
ratkaisuja on useita:

- **Kiinteä budjetti, joustava laajuus.** Sovitaan tavoite, tiimi ja
  aika. Tilaajan tuoteomistaja priorisoi, ja tärkeimmät asiat tehdään
  ensin. Rahan loppuessa käytössä on toimiva järjestelmä, josta puuttuvat
  vähiten tärkeät osat.
- **Vaiheistus.** Lyhyt esiselvitys tuntityönä kaventaa
  epävarmuuskartiota (luku 5), ja varsinainen toteutus hinnoitellaan
  vasta sen jälkeen.
- **Vaihtokauppa.** Laajuus on kiinnitetty kokonaismäärältään, mutta
  sisältöä saa vaihtaa: uusi vaatimus sisään, samankokoinen ulos ilman
  muutosneuvottelua.
- **Irtautumisoikeus.** Tilaaja voi lopettaa jokaisen jakson jälkeen.
  Tämä pitää toimittajan kiinnostuneena jokaisen jakson arvosta ja
  rajaa tilaajan riskin.

Suomessa IT-hankinnoissa käytetään usein valmiita yleisiä
sopimusehtoja: julkishallinnossa JIT-ehtoja (julkisen hallinnon
IT-hankintojen yleiset sopimusehdot) ja yritysten välillä IT-alan
yleisiä sopimusehtoja. Kummastakin on erityisehdot myös ketterille
menetelmille. Ehtoja päivitetään ajoittain, joten voimassa oleva versio
on tarkistettava. Julkisia hankintoja sääntelee lisäksi hankintalaki,
joka edellyttää kilpailutusta ja vaikuttaa siihen, miten vaatimukset ja
vertailuperusteet on kuvattava etukäteen. Sopimusten laatiminen on
juristin työtä; kehittäjän ja projektipäällikön on ymmärrettävä, mitä
malli tekee kannustimille.

Yksi riski koskee kaikkia malleja: **toimittajaloukku**. Jos vain
toimittaja ymmärtää järjestelmää, tilaaja ei voi vaihtaa toimittajaa
eikä neuvotella. Suoja on sopimuksessa (oikeudet lähdekoodiin ja
dokumentaatioon) ja käytännössä (koodi tilaajan versionhallinnassa,
automaattinen rakennus ja testit, ajantasainen dokumentaatio).

## Projektin päättäminen

Projekti päättyy, ohjelmisto ei. Suurin osa ohjelmiston elinkaaren
kustannuksista syntyy käyttöönoton jälkeen, ja projektin päätös on
hetki, jolloin tieto on vaarassa kadota: tiimi hajoaa ja siirtyy
seuraavaan hankkeeseen.

Päättämiseen kuuluu vähintään:

- **Hyväksyntä.** Tilaaja toteaa, että sovittu on toimitettu. Jos
  hyväksymiskriteerit on kirjattu ja testattu matkan varrella (luku 2),
  tämä on muodollisuus. Jos ei, tämä on riita.
- **Siirto ylläpitoon.** Kuka vastaa häiriöihin, kuka korjaa virheet,
  miten julkaisu tehdään ja missä ohjeet ovat. Ylläpitäjän on voitava
  rakentaa, testata ja julkaista järjestelmä ilman alkuperäistä tiimiä.
- **Dokumentaatio.** Arkkitehtuurin kuvaus, päätösten perustelut ja
  käyttöohjeet (*Tekninen dokumentaatio*). Projektin aikana kertynyt
  hiljainen tieto on kirjattava ennen kuin sen haltijat lähtevät.
- **Avoimet asiat.** Tunnettu tekninen velka (luku 8), tekemättä
  jääneet tarinat ja tiedossa olevat puutteet luovutetaan listana,
  ei yllätyksenä.
- **Resurssien vapautus.** Ympäristöt, käyttöoikeudet, lisenssit ja
  tunnukset suljetaan tai siirretään.

Projektimallin heikkous näkyy juuri tässä. Tiimi, joka rakensi
järjestelmän, ei vastaa sen käytöstä eikä näe valintojensa seurauksia.
Tuotemalli, jossa sama tiimi sekä kehittää että ylläpitää, poistaa
luovutuksen kokonaan (luku 1). Aihetta jatkaa taito *Tiimit ja
organisaatiomallit*.

## Jälkiarviointi

Projektin lopuksi pidetään koko hankkeen retrospektiivi. Sen kysymykset
ovat samat kuin tiimin säännöllisissä retrospektiiveissä (luku 9), mutta
aikajänne on koko projekti ja yleisönä myös organisaatio:

- Mitä luvattiin ja mitä toimitettiin? Arvio, ennuste ja toteuma
  rinnakkain ovat seuraavan projektin vertailuluokka (luku 5).
- Mitkä riskit toteutuivat? Mitkä yllätykset eivät olleet
  riskirekisterissä?
- Mitkä päätökset tehtäisiin nyt toisin, ja mitä tietoa silloin
  puuttui?
- Mitä käytäntöjä kannattaa viedä seuraavaan projektiin?

Jälkiarvioinnin arvo riippuu kahdesta asiasta. Sen on oltava
syyllistämätön, muuten ihmiset puolustautuvat eivätkä kerro. Ja sen
tulosten on päädyttävä jonnekin, missä seuraava projekti ne näkee:
tarkistuslistoihin, arviointipohjiin ja organisaation ohjeisiin.
Raportti, jota kukaan ei lue, on vain rituaali.

Myös epäonnistunut tai keskeytetty projekti päätetään kunnolla.
Hankkeen lopettaminen ajoissa, kun sen perusteet ovat kadonneet, on
onnistunut päätös eikä epäonnistuminen. Jo käytetty raha on
**uponnut kustannus**: se ei palaa, jatkettiin tai ei, joten päätös
tehdään vain jäljellä olevan työn ja odotettavan hyödyn perusteella.

## Käytännössä

- **Kysy, kuka kantaa riskin ja mihin malli kannustaa.** Jos vastaus
  on ”toimittaja kantaa kaiken”, riski on hinnassa tai palaa
  laatuongelmina.
- **Älä kiinnitä laajuutta, jota et tunne.** Tee esiselvitys ensin ja
  hinnoittele vasta, kun kartio on kaventunut.
- **Vaadi toimiva ohjelmisto nähtäväksi usein mallista riippumatta.**
  Se on tilaajan paras suoja kaikissa sopimusmalleissa.
- **Pidä koodi, rakennus ja dokumentaatio tilaajan hallussa alusta
  asti.** Toimittajaloukku syntyy huomaamatta ja puretaan kalliisti.
- **Suunnittele luovutus projektin alussa.** Ylläpitäjä mukaan ennen
  käyttöönottoa, ei sen jälkeen.
- **Kerää arvio ja toteuma talteen.** Ne ovat organisaation arvokkain
  arviointiaineisto, ja ne katoavat ensimmäisenä.
- **Lopeta projekti, jonka perusteet ovat poissa.** Uponneet
  kustannukset eivät ole syy jatkaa.

## Itsearviointi

- Osaat vertailla kiinteää hintaa, tuntityötä ja tavoitehintaa sen
  perusteella, kuka kantaa riskin ja mihin malli kannustaa.
- Osaat selittää, miksi kiinteä hinta on tilaajalle keskimäärin kalliimpi
  ja miksi kiinteä laajuus sopii huonosti ketterään kehitykseen.
- Osaat kuvata sopimusratkaisuja, joilla laajuus saa joustaa.
- Osaat luetella, mitä projektin päättämiseen ja ylläpitoon siirtoon
  kuuluu.
- Osaat suunnitella jälkiarvioinnin ja selittää uponneen kustannuksen
  merkityksen jatkamispäätöksessä.
