# Konsistenssimallit

Konsistenssimalli on sopimus järjestelmän ja sen käyttäjän välillä: mitä
luku voi palauttaa, kun kirjoituksia tapahtuu samanaikaisesti ja tieto
on replikoitu. Vahva malli tekee hajautetusta järjestelmästä yhden koneen
näköisen, heikompi malli sallii poikkeamia mutta toimii nopeammin ja
verkon jakautuessa. Tämä luku määrittelee tärkeimmät mallit, rakentaa
tarkistimen linearisoituvuudelle ja käyttää sitä kolmen rekisterin
toteutuksen arvioimiseen.

## Mallien kirjo

| Malli | Takuu |
|-------|-------|
| linearisoituvuus | jokainen operaatio näyttää tapahtuvan yhdessä hetkessä alkunsa ja loppunsa välillä; valmis kirjoitus näkyy kaikille |
| sarjallistuvuus | transaktiot näyttävät tapahtuvan jossain sarjallisessa järjestyksessä, ei välttämättä reaaliajan mukaisessa |
| tiukka sarjallistuvuus | sarjallistuvuus ja reaaliajan järjestys; linearisoituvuus transaktioille |
| kausaalinen | jokainen näkee syy-seuraussuhteessa olevat kirjoitukset samassa järjestyksessä, samanaikaiset voivat näkyä eri järjestyksessä |
| istuntotakuut | yksittäinen asiakas näkee omat kirjoituksensa eikä aikaa taaksepäin |
| lopulta konsistentti | jos kirjoitukset loppuvat, replikat päätyvät ennen pitkää samaan tilaan |

Linearisoituvuus (Herlihy ja Wing 1990) koskee yksittäisiä olioita,
kuten rekisteriä tai jonoa, ja reaaliaikaa. Sarjallistuvuus koskee
usean olion transaktioita mutta ei reaaliaikaa: tietokanta saa
järjestää transaktiot miten tahansa, kunhan tulos vastaa jotakin
järjestystä (ks. eristystasot taidossa *SQL*). Nimet sekoittuvat usein,
mutta ne vastaavat eri kysymyksiin.

Kausaalinen konsistenssi on vahvin malli, joka säilyy käytettävänä
verkon jakautuessa. Istuntotakuut (Terry ym. 1994) ovat sen osia
yhden asiakkaan näkökulmasta: *lue omat kirjoituksesi*, *monotoniset
luvut* (aika ei kulje taaksepäin), *monotoniset kirjoitukset* ja
*kirjoitukset seuraavat lukuja*. Lopullinen konsistenssi on heikoin:
se ei kerro mitään siitä, mitä luku palauttaa ennen kuin kirjoitukset
loppuvat.

## Linearisoituvuuden tarkistin

Historia on joukko operaatioita, joilla on alku- ja loppuhetki. Historia
on linearisoituva, jos jokaiselle operaatiolle voidaan valita
*linearisointipiste* sen alun ja lopun väliltä niin, että operaatiot
pisteiden järjestyksessä suoritettuina antavat samat tulokset kuin yksi
rekisteri. Jos operaatio a päättyi ennen kuin b alkoi, a:n on oltava
ensin. Päällekkäiset operaatiot voivat olla kummassa järjestyksessä
tahansa.

```{.cpp tiedosto="esimerkit/yhteinen/historia.hpp" osa="operaatio"}
```

Tarkistus on hakua (Wing ja Gong 1993): valitaan operaatio, joka voi olla
seuraava (yksikään tekemätön operaatio ei päättynyt ennen sen alkua),
sovelletaan se rekisteriin ja jatketaan. Jos haara umpikujautuu,
palataan. Haku muistaa jo kokeillut tilat (tehdyt operaatiot ja
rekisterin arvo), mikä tekee siitä käytännössä nopean
historioille, joissa on kymmeniä operaatioita. Ongelma on yleisesti
NP-täydellinen, joten muisti on välttämätön. Kesken jääneen
kirjoituksen tulos on tuntematon: se on voinut tapahtua milloin tahansa
alkunsa jälkeen tai ei lainkaan:

```{.cpp tiedosto="esimerkit/yhteinen/historia.hpp" osa="tarkistin"}
```

Tarkistinta kannattaa testata käsin kirjoitetuilla historioilla, joiden
vastaus tiedetään:

```{.cpp tiedosto="esimerkit/06-tarkistin.cpp" osa="historiat"}
```

```{.tuloste tiedosto="esimerkit/06-tarkistin.odotettu"}
```

Kolmas historia on tärkein: luku näki uuden arvon 1, ja sen jälkeen
alkanut luku näki vanhan arvon 0, vaikka kirjoitus oli yhä kesken.
Kumpikin luku on erikseen mahdollinen, mutta yhdessä ne eivät ole,
koska linearisointipisteen jälkeen kaikki näkevät uuden arvon. Tämä
*uusi ja sitten vanha* -rike on replikoitujen rekisterien tyypillinen
virhe. Viimeinen historia näyttää, että tarkistin löytää myös
järjestyksen, joka poikkeaa alkuhetkien järjestyksestä: kirjoitus 2
linearisoituu ennen kirjoitusta 1, vaikka se alkoi myöhemmin.

Jepsen ja sen Knossos- ja Elle-tarkistimet tekevät saman oikeille
tietokannoille: asiakkaat kirjaavat jokaisen operaation alun ja lopun,
testi aiheuttaa vikoja, ja tarkistin etsii historiasta rikkeen.

## Kolme rekisteriä

Seuraavaksi sama rekisteri toteutetaan kolmella tavalla, ja jokaisesta
ajetaan 200 simulaatiota, joissa kolme asiakasta lukee ja kirjoittaa
samanaikaisesti. Viidesosa viesteistä katoaa, ja asiakas luopuu
operaatiosta 300 ms:n jälkeen, jolloin kirjoituksen tulos jää
tuntemattomaksi. Replika säilyttää arvon, jolla on suurin leima
(versio, asiakas):

```{.cpp tiedosto="esimerkit/06-rekisteri.cpp" osa="replika"}
```

Asiakas tekee operaation kahdessa vaiheessa. Ensin se kysyy kvoorumilta
suurimman leiman. Kirjoitus kirjoittaa sitten arvon leimalla, joka on
suurempi kuin mikään nähty. ABD-algoritmin (Attiya, Bar-Noy ja Dolev
1995) luku kirjoittaa näkemänsä arvon takaisin kvoorumille ennen kuin
palauttaa sen. Ilman takaisinkirjoitusta luku palaa heti ensimmäisen
vaiheen jälkeen:

```{.cpp tiedosto="esimerkit/06-rekisteri.cpp" osa="asiakas"}
```

```{.cpp tiedosto="esimerkit/06-rekisteri.cpp" osa="koe"}
```

```{.tuloste tiedosto="esimerkit/06-rekisteri.odotettu"}
```

Yksi kopio on linearisoituva, mutta se ei siedä yhtään vikaa.
Kvoorumi ilman takaisinkirjoitusta tuotti ei-linearisoituvan historian
joka kahdeskymmenes ajo: kirjoitus oli ehtinyt yhdelle replikalle ja
jäänyt kesken, ensimmäinen luku osui siihen replikaan ja näki uuden arvon,
ja myöhempi luku osui kahteen muuhun ja näki vanhan. ABD:ssa
ensimmäinen luku olisi kirjoittanut uuden arvon kvoorumille ennen
vastaamista, joten myöhemmän luvun kvoorumi leikkaa sen. Takaisinkirjoitus
maksaa toisen kierroksen jokaisessa luvussa, mikä on linearisoituvuuden
hinta tässä mallissa.

Taulukko kertoo myös simulointitestauksesta jotain tärkeää: rike
näkyi vain joka kahdennessakymmenennessä ajossa ja vasta, kun viestejä
katosi ja operaatioita jäi kesken. Yksi tai kaksi onnistunutta ajoa ei
todista mitään. Ensimmäinen kaatuva siemen, 7, on toistettava
testitapaus, jonka historian voi tutkia rivi riviltä.

## Istuntotakuut

Monessa sovelluksessa linearisoituvuus on tarpeeton, mutta käyttäjä
hämmentyy, jos hänen juuri tallentamansa muutos katoaa näkyvistä
seuraavalla sivulatauksella. Esimerkissä johtaja replikoi seuraajille
50 ms välein. Asiakas kirjoittaa johtajalle ja lukee sitten kolme kertaa
satunnaiselta seuraajalta. Seuraaja kieltäytyy, jos se on jäljessä
asiakkaan vaatimasta versiosta:

```{.cpp tiedosto="esimerkit/06-istunto.cpp" osa="replikat"}
```

Istuntotunniste on pienin versio, jonka asiakas hyväksyy: suurin, minkä
istunto on kirjoittanut tai lukenut. Jäljessä olevan seuraajan
kieltäytyessä asiakas lukee johtajalta. Ilman tunnistetta asiakas
vaatii versiota 0, eli mikä tahansa vastaus kelpaa:

```{.tuloste tiedosto="esimerkit/06-istunto.odotettu"}
```

Ilman takuita 40 % luvuista ei nähnyt asiakkaan omaa juuri tekemää
kirjoitusta, ja kerran aika kulki taaksepäin, kun luku osui
jäljessä olevaan seuraajaan tuoreemman jälkeen. Tunnisteella kumpikaan
ei toteudu, ja hinta näkyy viimeisestä sarakkeesta: vajaa kolmannes
luvuista siirtyi johtajalle. Samaa tekniikkaa käyttävät MongoDB:n
kausaaliset istunnot ja monet sovelluskerroksen välimuistit, joissa
asiakas kantaa viimeisimmän näkemänsä version evästeessä tai
otsakkeessa.

## Käytännössä

- **Selvitä, mitä järjestelmä oikeasti lupaa.** Dokumentaatio puhuu
  usein "vahvasta konsistenssista" määrittelemättä sitä. Jepsenin
  analyysit ovat löytäneet rikkeitä lähes jokaisesta testaamastaan
  tietokannasta.
- **Linearisoituvuutta tarvitaan lukoille, johtajuudelle ja
  yksilöllisyydelle.** Käyttäjänimen varaus, kassasaldo ja johtajan
  valinta vaativat, että kaikki näkevät saman järjestyksen.
- **Istuntotakuut riittävät käyttöliittymille.** Lue omat
  kirjoituksesi -takuu poistaa suurimman osan käyttäjien näkemistä
  oudoista ilmiöistä halvemmalla kuin linearisoituvuus.
- **Kirjaa historia testeissä.** Kun asiakas kirjaa jokaisen
  operaation alun, lopun ja tuloksen, tarkistin voi arvioida
  konsistenssin jälkikäteen, eikä testin tarvitse tietää oikeaa
  vastausta etukäteen.
- **Kesken jääneen operaation tulos on tuntematon.** Tarkistimen on
  sallittava se, tai testi antaa vääriä hälytyksiä aikakatkaisuista.

## Itsearviointi

- Osaat määritellä linearisoituvuuden, sarjallistuvuuden, kausaalisen
  konsistenssin, istuntotakuut ja lopullisen konsistenssin ja erottaa
  ne toisistaan.
- Osaat tarkistaa käsin, onko lyhyt historia linearisoituva, ja
  tunnistaa uusi ja sitten vanha -rikkeen.
- Osaat toteuttaa linearisoituvuuden tarkistimen haulla ja muistilla ja
  käsitellä kesken jääneet operaatiot.
- Osaat selittää, miksi kvoorumirekisteri tarvitsee
  takaisinkirjoituksen ollakseen linearisoituva.
- Osaat toteuttaa lue omat kirjoituksesi- ja monotoniset luvut
  -takuut versiotunnisteella.
