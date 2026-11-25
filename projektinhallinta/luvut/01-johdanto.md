# Johdanto {.runko-johdanto}

Ohjelmistoprojektin hallinta on päätöksentekoa epävarmuudessa: mitä
tehdään, missä järjestyksessä, kuka tekee, milloin on valmista ja mitä
jätetään tekemättä. Koodin kirjoittaminen on harvoin se, mihin projekti
kaatuu. Tavallisemmin tehdään väärää asiaa, luvataan liikaa, aloitetaan
liian monta työtä kerralla tai huomataan ongelma niin myöhään, että
korjaaminen on kallista.

Tämä tutoriaali käy läpi alan vakiintuneet käsitteet ja menetelmät:
vaatimukset, prosessimallit vesiputouksesta ketteriin, arvioinnin ja
ennustamisen, työn virtauksen, riskit ja teknisen velan sekä ihmisten
välisen työn. Tavoite on yleiskuva, jonka varaan voi rakentaa missä
tahansa organisaatiossa. Mitään menetelmää ei esitetä ratkaisuna
kaikkeen: jokaisesta kerrotaan, mihin ongelmaan se syntyi, mihin se
perustuu ja missä sen rajat ovat.

## Miksi ohjelmistoprojekti on vaikea

Talon rakentaja tietää, montako tiiltä seinään tarvitaan, ja näkee,
kuinka korkealla seinä on. Ohjelmistossa kumpikaan ei päde.

- **Työ on suunnittelua, ei valmistusta.** Kun sama asia on tehty
  kerran, sitä ei tehdä uudestaan vaan se kopioidaan. Jokainen projekti
  tekee siis jotain, mitä tekijät eivät ole ennen tehneet juuri tässä
  muodossa, ja siksi työn määrä tiedetään vasta, kun se on tehty.
- **Edistyminen ei näy.** Puolivalmis ohjelma voi näyttää valmiilta tai
  olla näkymätön. ”90 % valmis” on projektien tunnetuin tila, koska
  viimeinen kymmenes sisältää kaiken, mitä ei osattu ennakoida.
- **Vaatimukset muuttuvat.** Tilaaja oppii, mitä haluaa, vasta
  nähdessään jotain toimivaa. Lisäksi maailma muuttuu projektin aikana.
- **Osat riippuvat toisistaan.** Pieni muutos yhdessä paikassa voi
  rikkoa toisen, ja työn jakaminen useammalle tekijälle lisää
  yhteensovittamisen tarvetta (luku 9).
- **Kestot ovat vinoja.** Tehtävä voi valmistua vähän arvioitua
  nopeammin mutta paljon hitaammin. Ylitykset eivät kumoa alituksia.

Viimeinen kohta on helppo näyttää laskemalla. Projektissa on kymmenen
tehtävää. Jokainen kestää nopeimmillaan 3, todennäköisimmin 5 ja
hitaimmillaan 15 päivää. Suunnitelmaan kirjataan todennäköisin arvo,
jolloin projektin kestoksi tulee 50 päivää. Simuloidaan projekti 20 000
kertaa arpomalla jokaiselle tehtävälle kesto:

```{.python tiedosto="esimerkit/01-summa.py" osa="simulointi"}
```

```{.tuloste tiedosto="esimerkit/01-summa.odotettu"}
```

Suunnitelma ei toteudu kertaakaan. Syy ei ole huono onni vaan
laskutapa: jokaisen tehtävän todennäköisin kesto on jakauman huippu,
mutta vinon jakauman odotusarvo on huippua suurempi (tässä 7,7 päivää),
ja summan odotusarvo on odotusarvojen summa. Kuvassa näkyy, kuinka
kaukana suunnitelma on koko jakaumasta.

![Kymmenen tehtävän projektin keston jakauma. Todennäköisimpien kestojen
summa (50 pv) jää jakauman ulkopuolelle; 85 %:n varmuuteen tarvitaan 85
päivää.](kuvat/summa.png){width=62%}

Esimerkki sisältää tutoriaalin keskeisen ajatuksen. Arvio on jakauma,
ei luku, ja lupaus on päätös siitä, mihin kohtaan jakaumaa sitoudutaan.
Luvut 5 ja 6 palaavat tähän.

## Projekti, tuote ja niiden rajoitteet

**Projekti** on määräaikainen ponnistus, jolla on tavoite, aikataulu ja
budjetti: uuden järjestelmän käyttöönotto, vanhan korvaaminen tai
asiakkaalle tehtävä toimitus. **Tuote** elää niin kauan kuin sillä on
käyttäjiä, ja sitä kehittää pysyvä tiimi. Ero vaikuttaa siihen, mitä
optimoidaan. Projektissa kysytään, valmistuuko sovittu sisältö ajallaan
ja budjetissa. Tuotekehityksessä kysytään, mitä kannattaa tehdä
seuraavaksi, ja ohjelmiston ylläpito kuuluu samalle tiimille.

Useimmat käsitteet pätevät molempiin, ja tutoriaali käyttää sanaa
projekti väljästi. Luvussa 10 palataan siihen, miksi projektin
päättyminen on ohjelmistolle riski.

Projektin perinteiset rajoitteet ovat **laajuus**, **aika** ja
**kustannus**. Niitä kutsutaan rautakolmioksi, koska kahta voi
kiinnittää mutta kolmas joustaa. Neljäs muuttuja on **laatu**, ja se
joustaa huomaamatta, jos kolme muuta on lyöty lukkoon: testaus jää
vähemmälle ja oikoteitä otetaan (luku 8). Ketterien menetelmien
keskeinen valinta on kiinnittää aika ja kustannus ja antaa laajuuden
joustaa, kun taas kiinteähintainen toimitusprojekti kiinnittää
laajuuden (luku 10).

## Esitiedot ja rajaus

Esitietona on taito *Versionhallinta (Git)*, koska esimerkkiprojektit
ovat ohjelmistoprojekteja ja luvussa 9 mittareita lasketaan
versiohistoriasta. Esimerkit ovat lyhyitä Python-ohjelmia, joiden
lukemiseen riittää *Ohjelmoinnin perusteet (Python)*. Simulaatioissa käytetään
satunnaislukuja ja persentiilejä; niiden taustan antaa taito
*Todennäköisyys ja tilastot*, mutta se ei ole välttämätön.

Naapuritaidot käsittelevät aiheita, joita tässä vain sivutaan:

| Aihe | Taito |
|----------------------------------|----------------------------------------|
| testit suunnittelun välineenä, hyväksymistestit | *Testivetoinen kehitys ja testisuunnittelu* |
| toimitusputki, julkaisut ja toimituskyvyn mittarit | *Jatkuva integraatio ja toimitus* |
| tiimirakenteet, Conwayn laki, skaalausmallit | *Tiimit ja organisaatiomallit* |
| dokumentit, arkkitehtuurikuvaukset ja päätöslokit | *Tekninen dokumentaatio* |
| haarat ja katselmointi | *Versionhallinta (Git)* |
| turvallisuus kehitysprosessissa | *Tietoturva kehitystyössä* |

Henkilöstöjohtaminen, budjetointi ja laskentatoimi sekä yksittäiset
työkalut (tehtävienhallinta- ja tikettijärjestelmät) jäävät pois.
Työkalut vaihtuvat, käsitteet eivät.

## Simulaatiot ovat malleja

Projektinhallinnan väitteet esitetään usein sääntöinä: rajaa
keskeneräistä työtä, pienennä erää, älä lisää väkeä myöhässä olevaan
projektiin. Tässä tutoriaalissa jokaisen säännön taustalla oleva
mekanismi rakennetaan pieneksi Python-malliksi, jonka lukija voi ajaa
ja jonka oletuksia voi muuttaa. Esimerkit ovat hakemistossa
`esimerkit/`, ja ne ajetaan komennolla

```text
python3 esimerkit/01-summa.py
```

Satunnaislukujen siemen on kiinteä, joten tulos on sama joka kerta, ja
`make testaa` vertaa tulosteita tallennettuihin.

Malli ei ole todiste. Se näyttää, mitä valituista oletuksista seuraa:
jos kestot ovat vinoja, summa käyttäytyy näin. Oikean projektin luvut
ovat toiset, ja mallin parametrit (esimerkiksi kuinka paljon
samanaikaiset työt hidastavat) on valittu havainnollisiksi, ei
mitatuiksi. Mallin arvo on siinä, että se pakottaa sanomaan oletukset
ääneen ja näyttää ilmiön suunnan ja suuruusluokan. Kun oma kokemus on
ristiriidassa mallin kanssa, kannattaa selvittää, mikä oletus ei päde.

## Tutoriaalin rakenne

Luvut 2–4 käsittelevät sitä, mitä tehdään ja millä tavalla työ
järjestetään: vaatimukset, prosessimallit sekä Scrum ja Kanban. Luvut
5–7 käsittelevät lukuja: arviointia, ennustamista ja virtausta. Luku 8
käsittelee riskejä, teknistä velkaa ja laatua, luku 9 ihmisiä ja
viestintää ja luku 10 sopimuksia ja projektin päättämistä. Jokainen
luku päättyy osioihin *Käytännössä* ja *Itsearviointi*; kokenut lukija
voi lukea itsearvioinnin ensin ja ohittaa luvun, jos väitteet ovat
tuttuja.
