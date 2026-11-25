# Kehyksen valinta ja elinkaari

Kun saman sovelluksen on nähnyt neljällä kehyksellä, on helppo huomata,
ettei valinta ratkea tekniikalla. Kaikilla neljällä saa tehtyä saman
sovelluksen suunnilleen samalla vaivalla. Erot ovat siinä, mitä kehys
tuo mukanaan, kuinka kauan se pysyy samana ja kuinka paljon sovelluksesta
sidotaan siihen. Tässä luvussa mitataan se, mikä on mitattavissa, ja
käydään läpi se, mikä ei ole.

## Mitä toteutuksista voi mitata

Työkalu `tyokalut/mitat.ts` laskee jokaisesta toteutuksesta lähdekoodin
rivit ja selaimeen ladattavan JavaScriptin koon:

```{.typescript tiedosto="esimerkit/tyokalut/mitat.ts" osa="mitat"}
```

```{.tuloste tiedosto="esimerkit/tulokset/mitat.txt"}
```

Luvut ovat näiden versioiden ja tämän sovelluksen lukuja, ja ne
vanhenevat jokaisen julkaisun myötä. Testi tarkistaa vain suuruusluokat.
Niistä voi silti lukea kolme pysyvämpää asiaa.

**Koodin määrä ei erota kehyksiä.** Rivimäärät ovat samaa
kokoluokkaa, ja kehyksetön toteutus asettuu niiden keskelle. Kehys ei vähennä kirjoitettavaa koodia pienessä
sovelluksessa; se muuttaa sen, mistä koodi koostuu (luku 2).

**Ajonaikaisen koodin määrä erottaa.** Kehyksetön toteutus lähettää
selaimeen muutaman kilotavun. React ja Angular lähettävät pakattunakin
kuutisenkymmentä kilotavua kehyksen omaa koodia ennen kuin sovelluksesta
on riviäkään, Vue ja Svelte alle puolet siitä. Syy on luvun 3 malleissa: virtuaalisen DOM:n
vertailija ja Angularin koneisto ovat ajonaikaista koodia, kun taas
kääntäjä siirtää työtä rakennusvaiheeseen. Ero on kiinteä lähtöhinta.
Sovelluksen kasvaessa oman koodin osuus kasvaa ja kehyksen osuus
pienenee, ja kääntäjän tuottama koodi kasvaa komponenttien mukana.

**Suurin osa sovelluksesta ei ole kehystä.** Viimeinen rivi on
moduuli, jota kaikki viisi toteutusta käyttävät. Siihen palataan alla.

Toinen työkalu laskee lukitustiedostosta, montako pakettia kukin kehys
tuo mukanaan:

```{.tuloste tiedosto="esimerkit/tyokalut/riippuvuudet.odotettu"}
```

Ajonaikaisia paketteja on vähän kaikilla. Vuen ja Svelten luvut ovat
suurempia kuin selaimeen päätyvä koodi antaisi olettaa, koska niiden
paketti sisältää myös kääntäjän riippuvuuksineen. Kehitystyökaluissa
ero on suuri: Angularin komentorivityökalu tuo mukanaan moninkertaisen
määrän paketteja muihin verrattuna. Se on "kaikki samassa paketissa"
-mallin hinta ja samalla sen lupaus, sillä nuo paketit on testattu
toimimaan yhdessä.

Jokainen paketti on riippuvuus, jonka päivityksiä ja haavoittuvuuksia
on seurattava (taito *Tietoturva kehitystyössä*). Luku ei kerro
laadusta, mutta se kertoo, kuinka suuren joukon varaan sovellus
rakennetaan.

## Mitä ei voi mitata

**Ekosysteemi.** Kehys on harvoin koko ratkaisu. Tarvitaan
komponenttikirjasto, lomakkeet, taulukot, kaaviot, kansainvälistys ja
testausvälineet. Reactilla valinnanvaraa on eniten, mikä tarkoittaa
sekä sitä, että kaikkeen löytyy jotain, että sitä, että jokainen
projekti on koottu eri osista. Angularissa suurin osa tulee kehyksen
mukana, ja kaksi Angular-projektia muistuttavat toisiaan. Vue ja
Svelte ovat näiden välissä.

**Ihmiset.** Kehys, jota tiimi osaa, on lähes aina parempi valinta
kuin kehys, joka olisi paperilla parempi. Rekrytoinnissa yleisyys
ratkaisee: yleisimmälle kehykselle löytyy tekijöitä helpoimmin. Tämän
tutoriaalin väite on kuitenkin, että kehyksen vaihtaminen on kokeneelle
kehittäjälle viikkojen, ei kuukausien asia, koska käsitteet ovat samat.

**Elinkaari.** Kehyksen ikä ei kerro sen vakaudesta. Jokainen neljästä
on tehnyt ainakin yhden suuren suunnanmuutoksen:

| Kehys | Suunnanmuutos | Mitä siitä seurasi |
|-------|---------------|--------------------|
| Angular | AngularJS:stä Angulariin 2016 | uudelleenkirjoitus: vanha koodi ei siirtynyt |
| React | luokista hookeihin 2019 | vanha tapa toimii yhä, uusi koodi kirjoitetaan toisin |
| Vue | versiosta 2 versioon 3 | rikkovia muutoksia; siirtymä kesti ekosysteemiltä vuosia |
| Svelte | versiosta 4 versioon 5 | uusi reaktiivisuus; vanha syntaksi toimii rinnalla |
| Angular | muutostentunnistuksesta signaaleihin | vaiheittainen: molemmat toimivat rinnakkain |

Luettelosta näkyy myös oppiminen. Kaksi ensimmäistä suurta muutosta
rikkoivat vanhan koodin, uudemmat on tehty vaiheittain ja
siirtymätyökaluilla. Arvioinnissa kannattaa katsoa, miten kehys on
hoitanut edellisen muutoksensa: julkaistaanko versiot ennustettavasti,
kuinka kauan vanhoja tuetaan ja tarjotaanko automaattisia
siirtymätyökaluja. Angularilla on kiinteä julkaisurytmi ja ilmoitettu
tukiaika jokaiselle pääversiolle; muilla käytäntö on väljempi.

## Lukkiutuminen ja sen rajaaminen

Kehyksen vaihtaminen valmiissa sovelluksessa on kallista, ja juuri
siksi sitä tehdään harvoin. Hintaan voi vaikuttaa etukäteen yhdellä
tavalla: pitämällä kehykseen sidotun koodin osuuden pienenä.

Tehtävälistassa säännöt ovat moduulissa, jossa ei ole yhtään
kehyksen tuontia. Sen testit ajetaan Nodella ilman selainta:

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.test.ts" osa="muutokset"}
```

Mittaustaulukon mukaan tässä moduulissa on noin puolet siitä koodista,
mitä yksittäinen toteutus sen lisäksi tarvitsee. Jos sovellus pitäisi
siirtää kehyksestä toiseen, tämä osa ja selaintestit siirtyisivät
sellaisinaan. Uudelleen kirjoitettavaksi jäisi komponenttien ohut
kerros, ja sen oikeellisuuden varmistaisi sama testisarja.

Oikeassa sovelluksessa kehyksestä riippumattomaksi kannattaa tehdä
ainakin nämä:

- **Sovellusalueen säännöt**: laskenta, validointi, tilasiirtymät.
- **Tietotyypit ja rajapinta-asiakas**: mitä palvelimelta tulee ja
  miten sitä kutsutaan.
- **Muotoilu ja kielikohtaiset asiat**: päivämäärät, rahasummat, tekstit.
- **Testit ylimmällä tasolla**: selaintestit, jotka eivät tunne kehystä.

Kehykseen jää se, mikä sille kuuluu: komponentit, sidokset ja tilan
kytkeminen näkymään. Rajan vetäminen ei ole ilmaista. Jaettu moduuli
palauttaa aina uuden taulukon, koska se on ainoa tapa, joka sopii
kaikille kehyksille, ja yhden kehyksen sovelluksessa samasta tiukkuudesta
voi tinkiä. Periaate on silti sama: kehyksen tuonti tiedoston alussa on
päätös, ja sen pitää näkyä vain tiedostoissa, joissa sille on syy.

## Muut kehykset

Neljän suuren lisäksi on kymmeniä muita. Niitä ei tarvitse osata,
mutta ne on hyvä osata sijoittaa. Kaksi kysymystä riittää: missä HTML
syntyy ja miten muutos viedään DOM:iin.

| Kehys | Missä HTML syntyy | Malli | Lähin sukulainen |
|----|-------|-----------|---------|
| Preact | selain | virtuaalinen DOM, sama rajapinta pienempänä | React |
| Solid | selain | signaalit ja käännetty JSX, ei virtuaalista DOM:ia | Reactin syntaksi, Svelten malli |
| Lit | selain | selaimen omat Web Components -rajapinnat | kehyksetön |
| Alpine | palvelin; selain elävöittää | direktiivit HTML:n attribuutteina | Vuen mallipohjat ilman rakennusvaihetta |
| htmx | palvelin | palvelin palauttaa HTML-paloja, jotka vaihdetaan sivulle | monisivuinen sovellus |
| Astro | palvelin tai käännös | staattinen HTML ja saarekkeet millä tahansa kehyksellä | staattinen sivusto |
| Qwik | palvelin | jatkettavuus: ei hydraatiota | Reactin syntaksi |

Taulukon alaosa muistuttaa, että "mikä kehys" ei ole ensimmäinen
kysymys. Sisältösivusto, jolla on vähän vuorovaikutusta, on parempi
tehdä palvelimella ja elävöittää kevyesti. Sovelluskehystä tarvitaan,
kun näkymässä on paljon tilaa, joka muuttuu selaimessa.

## Valintakysymykset

Kun kehystä valitaan uuteen projektiin, nämä kysymykset ratkaisevat
useammin kuin tekniset erot:

1. **Tarvitaanko sovelluskehystä?** Mikä osa sivuista on aidosti
   vuorovaikutteista sovellusta ja mikä sisältöä?
2. **Mitä tiimi osaa, ja ketä voidaan palkata?**
3. **Kuinka kauan sovellus elää?** Kymmenen vuoden sovellukselle
   ennustettava tukiaika ja siirtymäpolut painavat enemmän kuin
   kolmen kuukauden kampanjasivulle.
4. **Halutaanko valmis kokonaisuus vai kootaanko osista?** Suuri
   organisaatio, jossa on monta tiimiä, hyötyy siitä, että kehys päättää
   rakenteen. Pieni tiimi voi arvostaa vapautta.
5. **Missä sovellus renderöidään?** Jos tarvitaan palvelinrenderöintiä,
   valitaan käytännössä metakehys (luku 9).
6. **Mitä organisaatiossa jo käytetään?** Toinen kehys samaan taloon
   kaksinkertaistaa komponenttikirjastot, työkalut ja osaamisen.

Jos vastaukset eivät erota ehdokkaita, valinta on turvallinen: mikä
tahansa neljästä kelpaa, ja aika kannattaa käyttää sovellukseen.

## Käytännössä

- **Valitse tylsästi.** Vakiintunut kehys, jota tiimi osaa ja jota
  ylläpidetään aktiivisesti, on oikea valinta useammin kuin uusin ja
  nopein. Uutuudet ehtii ottaa käyttöön, kun ne ovat selvinneet
  ensimmäisestä suunnanmuutoksestaan.
- **Lukitse versiot ja päivitä säännöllisesti.** Lukitustiedosto
  tekee rakennuksesta toistettavan. Pienet päivitykset usein ovat
  halvempia kuin yksi suuri harppaus kolmen vuoden välein.
- **Seuraa, kuinka suuri osa koodista tuo kehyksen.** Jos jokainen
  tiedosto alkaa kehyksen tuonnilla, myös säännöt ovat sidottuja
  kehykseen.
- **Älä sekoita kehyksiä samassa näkymässä ilman pakkoa.** Jokainen
  kehys tuo oman ajonaikaisen koodinsa ja oman tilamallinsa. Vaiheittainen
  siirtymä on poikkeus, ja silloinkin raja vedetään reittien väliin.
- **Lue kehyksen oma dokumentaatio, kun tarvitset yksityiskohtia.**
  Se on ajan tasalla; opetusvideot ja vanhat vastaukset eivät
  välttämättä ole. Tämän tutoriaalin käsitteillä tiedät, mitä etsiä.

## Itsearviointi

- Osaat selittää, miksi kehysten ajonaikaisen koodin määrä vaihtelee,
  renderöintimallien avulla.
- Osaat arvioida kehyksen elinkaarta: julkaisurytmiä, tukiaikoja ja
  sitä, miten se on hoitanut aiemmat suuret muutoksensa.
- Osaat rajata sovelluksesta osat, jotka kannattaa pitää kehyksestä
  riippumattomina, ja perustella rajauksen.
- Osaat sijoittaa itsellesi uuden kehyksen kahdella kysymyksellä: missä
  HTML syntyy ja miten muutos viedään DOM:iin.
- Osaat esittää kysymykset, joilla kehys valitaan projektiin, ja
  tunnistaa tilanteen, jossa sovelluskehystä ei tarvita.
