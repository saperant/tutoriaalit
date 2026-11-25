# Suoritettavat määrittelyt ja BDD

Edellisten lukujen testit vastasivat kysymykseen "toimiiko koodi niin
kuin ohjelmoija tarkoitti". Kalleimmat virheet syntyvät aiemmin: koodi
tekee tarkalleen sen, mitä ohjelmoija tarkoitti, mutta tilaaja tarkoitti
muuta. **Käyttäytymisvetoinen kehitys** (*behaviour-driven development*,
BDD) tarttuu tähän. Sen ydin ei ole työkalu vaan tapa: vaatimuksesta
keskustellaan konkreettisin esimerkein ennen toteutusta, ja esimerkit
kirjoitetaan kielellä, jota liiketoiminnan edustaja, testaaja ja
ohjelmoija kaikki lukevat. Kun sama teksti lisäksi ajetaan testinä, siitä
tulee **suoritettava määrittely**: dokumentaatio, joka ei voi vanheta
huomaamatta.

## Esimerkit ennen ratkaisua

Vaatimus "vähintään 50 euron tilaukset toimitetaan ilmaiseksi" kuulostaa
valmiilta. Kun siitä pyydetään esimerkkejä, se alkaa vuotaa:

| Sääntö | Esimerkki | Avoin kysymys |
|----------------------|----------------------------|---------------------------|
| alle 50 e maksaa toimituksen | 20,00 e ja 1,5 kg: 5,90 e | |
| 50 e tai yli on ilmainen | 49,99 e maksaa, 50,00 e ei | lasketaanko raja ennen alennuksia vai niiden jälkeen? |
| raskas tilaus ei ole ilmainen | 120 e ja 14 kg: 19,90 e | onko rahdin raja 10 kg kaikille? |
| yli 30 kg ei toimiteta | 31 kg: virheilmoitus | näytetäänkö vaihtoehtona nouto? |

Tätä kutsutaan **esimerkkikartoitukseksi** (*example mapping*).
Tavallinen kokoonpano on kolme näkökulmaa: joku, joka tuntee tarpeen,
joku, joka toteuttaa, ja joku, joka etsii aukkoja. Puoli tuntia riittää
yhdelle ominaisuudelle. Jos avoimia kysymyksiä kertyy enemmän kuin
esimerkkejä, ominaisuus ei ole valmis toteutettavaksi, ja se on
hyödyllinen tieto ennen kuin riviäkään koodia on kirjoitettu.

Esimerkit ovat samoja, joita luvun 4 tekniikat tuottavat: 49,99 ja
50,00 euroa ovat raja-arvoja. Ero on yleisössä. Parametroidun
pytest-taulukon lukee ohjelmoija, esimerkkitaulun kuka tahansa.

## Gherkin

Esimerkit kirjoitetaan **Gherkin**-kielellä. Tapaus (*scenario*) kuvaa
yhden esimerkin kolmessa osassa: alkutilanne (*Given*, suomeksi
*Oletetaan*), tapahtuma (*When*, *Kun*) ja odotettu seuraus (*Then*,
*Niin*). Rakenne on sama kuin testin alkutilanne, toiminto ja väite.
Gherkinin avainsanat on käännetty kymmenille kielille; tiedoston
ensimmäinen rivi valitsee kielen.

```{.default tiedosto="esimerkit/06-bdd/ominaisuudet/toimitus.feature"}
```

**Tapausaihio** (*scenario outline*) ajetaan kerran jokaista
*Tapaukset*-taulun riviä kohden. Se sopii rajojen kuvaamiseen: taulusta
näkee yhdellä silmäyksellä, missä raja kulkee.

## Askeleet ovat ohut liima

Määrittely muuttuu testiksi **askelmäärittelyillä**, jotka liittävät
lauseen koodiin. Pythonissa tavallisimmat työkalut ovat pytest-bdd ja
behave; tässä käytetään pytest-bdd:tä, koska se toimii pytestin
liitännäisenä ja askeleet voivat käyttää fixtureita.

```{.python tiedosto="esimerkit/06-bdd/test_toimitus.py" osa="askeleet"}
```

Askeleet jakavat tilan fixturen `kassa` kautta: *Oletetaan*-askeleet
täyttävät sen, *Kun*-askel kutsuu sovellusta ja *Niin*-askeleet
tarkistavat tuloksen. Jokainen askel on muutaman rivin mittainen. Jos
askelmäärittelyyn alkaa kertyä logiikkaa, se kuuluu sovellukseen tai
testin apukirjastoon.

Rivi `scenarios(...)` tiedoston alussa tekee jokaisesta tapauksesta
pytest-testin, ja tapausaihion rivit näkyvät parametreina:

```{.tuloste tiedosto="esimerkit/06-bdd/odotettu"}
```

Tässä askeleet kutsuvat funktiota `toimitusmaksu` suoraan. Samat
tapaukset voisi ajaa HTTP-rajapinnan tai selaimen kautta vaihtamalla
vain askelmäärittelyt, koska määrittely ei mainitse kumpaakaan. Mitä
alempaa tasoa vasten tapaukset ajetaan, sitä nopeampia ja vakaampia ne
ovat.

## Hyvä ja huono tapaus

Sama asia voidaan kirjoittaa myös näin:

```{.default tiedosto="esimerkit/06-bdd/ominaisuudet/huono.feature"}
```

Tämä on käyttöliittymätestin skripti Gherkinin syntaksilla. Sen ongelmat
ovat tyypillisiä:

- **Se kuvaa toteutusta, ei käytöstä.** Kenttien nimet ja napit vaihtuvat
  joka uudistuksessa, ja jokainen muutos rikkoo tapauksen, vaikka
  sääntö pysyy.
- **Säännöstä ei saa selvää.** Lukijan pitää päätellä luvuista 2000 ja
  5000, että kyse on 50 euron rajasta.
- **Yhdessä tapauksessa on kaksi tapausta.** Toinen *Kun* aloittaa uuden
  esimerkin, ja jos ensimmäinen epäonnistuu, toista ei ajeta.
- **Nimi ei kerro mitään.** "Testaa toimitusmaksu" ei kerro, mikä
  sääntö on rikki, kun tapaus epäonnistuu.

Hyvä tapaus on **deklaratiivinen**: se kertoo, mitä asiakas saa, ei
mitä hän klikkaa. Nyrkkisääntö: jos käyttöliittymä vaihtuisi
puhelinsovellukseen, pitäisikö tapaus kirjoittaa uudelleen? Jos
pitäisi, se on liian lähellä toteutusta.

## Kaksi silmukkaa

Suoritettava määrittely ja TDD täydentävät toisiaan. Määrittelyn tapaus
on **hyväksymistesti**: se kertoo, milloin ominaisuus on valmis.
Yksikkötestit kertovat, miten sinne päästään.

```{.dot otsikko="Hyväksymistesti pysyy punaisena, kunnes sisempi TDD-silmukka on tuottanut ominaisuuden"}
digraph {
  ranksep=0.35; nodesep=0.5;
  a [label="Tapaus epäonnistuu", fillcolor="#F4C7C3"];
  subgraph cluster_tdd {
    label="TDD-kierroksia"; labelloc=b; color="#5B6B70"; fontsize=9;
    { rank=same;
      p [label="Yksikkötesti\nepäonnistuu", fillcolor="#F4C7C3"];
      v [label="Yksikkötesti\nmenee läpi", fillcolor="#CDE8C5"];
      r [label="Refaktorointi"];
    }
    p -> v -> r;
    r -> p [constraint=false];
  }
  ok [label="Tapaus menee läpi", fillcolor="#CDE8C5"];
  a -> p;
  r -> ok;
}
```

Ulompi silmukka kestää tunteja tai päiviä, sisempi minuutteja.
Hyväksymistestejä on vähän, koska ne ovat hitaampia kirjoittaa ja
ylläpitää: muutama tapaus sääntöä kohden, ei jokaista reunatapausta.
Reunatapaukset kuuluvat yksikkötesteihin, joissa ne ovat halpoja.

## Milloin BDD kannattaa

BDD:n hyöty tulee keskustelusta. Jos tapaukset kirjoittaa ohjelmoija
yksin toteutuksen jälkeen eikä kukaan muu lue niitä, Gherkin on vain
hidas tapa kirjoittaa testejä: jokainen lause tarvitsee
askelmäärittelyn, säännöllisen lausekkeen ja ylläpitoa.

Menetelmä sopii, kun

- säännöt tulevat liiketoiminnasta ja niistä on eri käsityksiä
  (hinnoittelu, oikeudet, laskutus, viranomaissäännöt)
- joku muu kuin ohjelmoija todella lukee tai kirjoittaa esimerkkejä
- määrittelyn halutaan pysyvän ajan tasalla ilman erillistä dokumenttia.

Se ei sovi teknisiin kirjastoihin, algoritmeihin tai sisäisiin
rajapintoihin, joiden ainoa lukija on toinen ohjelmoija. Niissä hyvin
nimetty pytest-testi on parempi määrittely. Esimerkkikartoituksesta on
silti hyötyä myös ilman Gherkiniä: esimerkit voi kirjata suoraan
taulukkotesteiksi.

## Käytännössä

- **Kirjoita tapaukset yhdessä ennen toteutusta.** Jälkikäteen
  kirjoitettu tapaus kuvaa sen, mitä koodi tekee, ei sitä, mitä
  tarvittiin.
- **Yksi tapaus, yksi sääntö.** Yksi *Kun* ja sen seuraukset. Nimi
  kertoo säännön.
- **Käytä alan omia sanoja johdonmukaisesti.** Jos kauppa puhuu
  "korista", älä kirjoita "ostoslistaa". Sanasto, jonka sekä tapaukset
  että koodi jakavat, on BDD:n pysyvin hyöty.
- **Pidä askelkirjasto pienenä.** Kymmenen hyvin valittua askelta on
  parempi kuin sata lähes samanlaista. Sama asia sanotaan aina samoin.
- **Aja tapaukset sovelluslogiikkaa vasten, vain muutama käyttöliittymän
  läpi.** Käyttöliittymän kautta ajetut tapaukset ovat hitaita ja
  hajoavat helposti (taito *Web-sovellukset*).
- **Poista tapaus, jota kukaan ei lue.** Määrittely, joka ei enää vastaa
  kenenkään kysymykseen, on pelkkää ylläpitokuormaa.

## Itsearviointi

- Osaat purkaa vaatimuksen säännöiksi, esimerkeiksi ja avoimiksi
  kysymyksiksi.
- Osaat kirjoittaa Gherkin-tapauksen ja tapausaihion sekä niille
  askelmäärittelyt.
- Osaat erottaa deklaratiivisen tapauksen käyttöliittymäskriptistä ja
  korjata jälkimmäisen.
- Osaat selittää, miten hyväksymistesti ja TDD:n yksikkötestit liittyvät
  toisiinsa.
- Osaat arvioida, kannattaako Gherkinin käyttö tietyssä projektissa.
