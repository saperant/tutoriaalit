# Verifiointisuunnitelma

Verifiointi alkaa samasta asiakirjasta kuin suunnittelu: määrittelystä.
Suunnittelija lukee sen ja kysyy, miten toiminto rakennetaan.
Verifioija lukee saman määrittelyn ja kysyy, mistä tiedetään, että
toiminto on valmis. Vastaukset kirjataan *verifiointisuunnitelmaan*
(verification plan, testplan), joka kertoo, mitä tarkistetaan, millä
menetelmällä ja milloin työ on tehty.

Suunnitelma kirjoitetaan määrittelyn rinnalla, ei suunnitelman
valmistuttua. Silloin verifioija ja suunnittelija tulkitsevat
määrittelyn toisistaan riippumatta, ja tulkintaerot paljastuvat
keskusteluissa jo ennen kuin niistä tulee vikoja. Kaksi riippumatonta
tulkintaa on verifioinnin perusidea: testipenkin referenssimalli on
toinen toteutus samasta määrittelystä.

## Vaatimuksista ominaisuuksiin

Määrittelyn lauseet muutetaan ensin tarkistettaviksi
*ominaisuuksiksi* (features). FIFOn määrittely voisi sanoa: "Jono
säilyttää neljä tavua. Kirjoitus täyteen jonoon ja luku tyhjästä
jonosta jätetään huomiotta." Siitä seuraa joukko ominaisuuksia:

- data luetaan samassa järjestyksessä kuin se kirjoitettiin;
- kirjoitus täyteen jonoon hylätään eikä se muuta sisältöä;
- luku tyhjästä jonosta hylätään;
- liput `tyhja` ja `taysi` vastaavat jonon määrää;
- samanaikainen kirjoitus ja luku säilyttää määrän;
- nollaus tyhjentää jonon missä tilassa tahansa.

Viimeiset kaksi eivät lue määrittelyssä suoraan. Ne ovat seurauksia,
joita lukija ei välttämättä huomaa, ja juuri niissä vikoja on
eniten: samanaikaiset tapahtumat, rajat ja nollaus kesken toiminnan.
Hyvä verifioija kysyy jokaisesta ominaisuudesta, mitä tapahtuu rajalla,
mitä tapahtuu kahden tapahtuman sattuessa yhtä aikaa ja mitä tapahtuu
nollauksessa.

Jokaiselle ominaisuudelle kirjataan kolme asiaa:

1. **Tarkistus:** mikä havaitsee virheen (referenssimalli, väite,
   formaali ominaisuus).
2. **Kattavuuskohde:** mikä osoittaa, että tilanne todella syntyi
   ajossa. Tarkistus, jonka ehto ei koskaan toteudu, ei tarkista
   mitään.
3. **Menetelmä:** simulointi, väite, formaali tarkistus tai niiden
   yhdistelmä.

## Menetelmän valinta

| Ominaisuus | Sopiva menetelmä | Peruste |
|------------|------------------|---------|
| datan järjestys ja eheys | simulointi ja referenssimalli | tarkistus vaatii mallin koko sisällöstä |
| liput ja rajat | väite ja formaali | paikallinen sääntö, kaikki tilat käytävissä läpi |
| kättelysäännöt | väite | tarkistetaan jokaisella jaksolla kaikissa testeissä |
| reiluus, ei lukkiutumista | formaali | "ei koskaan" on vaikea osoittaa simuloimalla |
| järjestelmän suorituskyky | simulointi | vaatii pitkiä ja realistisia ajoja |
| ohjelmiston ja laitteiston yhteistoiminta | simulointi, emulointi | vaatii koko järjestelmän |
| kellotusalueiden ylitykset | rakenteellinen CDC-analyysi | metastabiilius ei näy RTL-simulaatiossa (*RTL-suunnittelu SystemVerilogilla*) |
| nollauksen toiminta ja vapautus | simulointi nollauksella kesken toiminnan, nollausanalyysi | virhe näkyy vain tietyssä vaiheessa |
| synteesin tulos vastaa RTL:ää | ekvivalenssitarkistus, porttitason simulointi | työkaluvirheet ja ajoitus (*ASIC-toteutus*) |

Formaali tarkistus on vahvin, kun lohko on pieni ja ominaisuus
paikallinen. Simulointi on ainoa vaihtoehto, kun tarvitaan koko
järjestelmä tai miljoonia jaksoja. Väitteet ovat halpoja ja sopivat
molempiin, joten niitä kirjoitetaan kaikkialle.

## Verifioinnin tasot

Verifiointi tehdään kerroksittain. *Lohkotasolla* (unit, block) yksi
moduuli testataan omassa testipenkissään, jossa kaikki sen tulot ovat
hallittavissa ja kulmatapaukset helppo tuottaa. *Alijärjestelmätasolla*
lohkot kootaan yhteen ja testataan niiden rajapintoja. *Järjestelmätasolla*
ajetaan koko piiriä usein oikealla ohjelmistolla. Vika kannattaa löytää
alimmalla tasolla, jolla se on näkyvissä: lohkotason testi ajaa
sekunneissa ja osoittaa suoraan vian paikan, järjestelmätason testi
ajaa tunteja ja osoittaa vain, että jokin meni pieleen.

Tasot vaikuttavat myös siihen, miten lohkoa katsotaan. *Mustan
laatikon* (black box) testi näkee vain liitännän ja toimii, vaikka
toteutus vaihtuisi. *Valkoisen laatikon* (white box) tarkistus katsoo
sisäisiä signaaleja, kuten osoittimia, ja löytää vian lähempää sen
syytä. Väitteet ovat tyypillisesti valkoisen laatikon tarkistuksia,
testipenkin tulostaulu mustan laatikon.

## Valmiuskriteerit

Verifiointi ei lopu koskaan itsestään: aina voisi ajaa vielä yhden
siemenen. Siksi suunnitelmassa sovitaan etukäteen, milloin lohko on
valmis (sign-off). Tavallisia kriteerejä ovat:

- jokaisella ominaisuudella on tarkistus ja kattavuuskohde, ja kaikki
  kattavuuskohteet on saavutettu tai perusteltu saavuttamattomiksi;
- koodikattavuus on sovitulla tasolla, ja kattamattomat rivit on
  käyty läpi;
- formaalit ominaisuudet on todistettu tai tarkistettu sovittuun
  syvyyteen;
- regressio on ollut vihreä sovitun ajan, ja uusia vikoja löytyy enää
  harvoin;
- kaikki löydetyt viat on korjattu tai hyväksytty tiedossa oleviksi.

Vikojen löytymistahti on hyödyllinen mittari: kun uusia vikoja löytyy
viikossa yhä vähemmän, menetelmät ovat tehneet tehtävänsä. Se ei
kuitenkaan erota valmista lohkoa testipenkistä, joka ei enää löydä
mitään. Siksi tarvitaan kattavuus (luku 6).

## Suunnitelma tiedostona

Suunnitelma on usein taulukko tai asiakirja, joka vanhenee heti, kun
testejä nimetään uudelleen. Kun se kirjoitetaan koneluettavaan
muotoon ja tarkistetaan jokaisessa regressiossa, se pysyy totena.
Esimerkkien FIFOn suunnitelma on TOML-tiedosto, jossa viittaukset ovat
muotoa `tiedosto#teksti`:

```{.toml tiedosto="esimerkit/suunnitelma/fifo.toml"}
```

Työkalu tarkistaa, että jokainen viitattu teksti löytyy tiedostosta:

```{.python tiedosto="esimerkit/tyokalut/suunnitelma.py" osa="viite"}
```

Raportti näyttää, että viimeisellä vaatimuksella ei ole tarkistusta
eikä kattavuuskohdetta. Se on *aukko*, ja se jätettiin esimerkkiin
tarkoituksella: yksikään tämän tutoriaalin testeistä ei nollaa FIFOa
kesken käytön.

```{.tuloste tiedosto="esimerkit/odotetut/suunnitelma.odotettu"}
```

Tekstihaku on karkea tapa linkittää vaatimus tarkistukseen, mutta se
riittää havaitsemaan, kun testi tai väite poistetaan tai nimetään
uudelleen ja suunnitelma unohdetaan päivittää. Kaupallisissa
työkaluissa suunnitelma yhdistetään kattavuustietokantaan
(*executable verification plan*), jolloin raportti kertoo myös,
mitkä kattavuuskohteet regressio on saavuttanut.

## Istutetut viat

Miten tiedetään, että testipenkki löytää vikoja? Kokeilemalla:
suunnitelmaan istutetaan tunnettu vika ja katsotaan, epäonnistuuko
testi. Menetelmä on ohjelmistotestauksen *mutaatiotestaus*. Laitteiston
verifioinnissa sitä käytetään kahdella tavalla:

1. **Käsin istutetut viat** kuten tämän tutoriaalin `BUGI_*`-makrot.
   Ne edustavat tunnettuja virhetyyppejä, ja jokaiselle kirjoitetaan
   testi, jonka on epäonnistuttava. Se on samalla regressiotesti
   testipenkille itselleen: jos joku heikentää tarkistusta, istutettu
   vika lakkaa löytymästä.
2. **Automaattinen mutaatio.** Työkalu muuttaa RTL:ää järjestelmällisesti
   (vaihtaa `&&`:n `||`:ksi, vakion toiseksi, poistaa ehdon) ja ajaa
   regression jokaiselle mutantille. Eloon jäänyt mutantti osoittaa
   kohdan, jota mikään testi ei tarkista. Avoimista työkaluista
   mutaatioita tukee esimerkiksi Yosysin `mutate`-komento.

Istutettu vika ei korvaa kattavuutta, mutta se mittaa asiaa, jota
kattavuus ei mittaa: tarkistusten voimaa. Kattavuus kertoo, että
tilanne syntyi; istutettu vika kertoo, että tilanteen virhe myös
huomattiin.

## Käytännössä

- **Suunnitelma ennen testipenkkiä.** Ominaisuuslista ja
  kattavuustavoitteet ovat halvin vaihe löytää määrittelyn
  aukkoja. Ne katselmoidaan suunnittelijan kanssa.
- **Verifioija ei lue RTL:ää mallin pohjaksi.** Referenssimalli
  kirjoitetaan määrittelystä. Jos malli kopioi RTL:n rakenteen, se
  kopioi myös sen virheet.
- **Rajat, samanaikaisuus ja nollaus.** Jokaiselle ominaisuudelle
  kirjataan nämä kolme kulmaa erikseen; niissä vikoja on eniten.
- **Suunnitelma on elävä.** Kun vika löytyy, kysytään, miksi mikään
  olemassa oleva tarkistus ei löytänyt sitä aiemmin, ja lisätään
  puuttuva ominaisuus tai kattavuuskohde.
- **Konekielinen suunnitelma tarkistetaan regressiossa.** Muuten se
  vanhenee, eikä kukaan huomaa sitä ennen sign-off-katselmusta.
- **Istuta vika jokaiselle tarkistukselle.** Tarkistus, jota ei ole
  koskaan nähty epäonnistuvan, voi olla väärin kytketty tai aina tosi.

## Itsearviointi

- Osaat muuttaa määrittelyn lauseet tarkistettaviksi ominaisuuksiksi
  ja tunnistaa niistä rajat, samanaikaiset tapahtumat ja nollauksen.
- Osaat valita ominaisuudelle menetelmän (simulointi, väite,
  formaali) ja perustella valinnan.
- Osaat kirjata ominaisuudelle sekä tarkistuksen että kattavuuskohteen
  ja selittää, miksi molemmat tarvitaan.
- Osaat määritellä lohkolle valmiuskriteerit.
- Osaat käyttää istutettuja vikoja testipenkin voiman mittaamiseen.
