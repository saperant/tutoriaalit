# Vaatimukset ja toleranssit

Suotimen suunnittelu alkaa vaatimuksista ja päättyy tarkistukseen,
joka kertoo, täyttyvätkö ne. Toteutuksen testaus vaatii lisäksi
tiedon siitä, kuinka paljon kahden oikean toteutuksen tulokset saavat
erota. Tämä luku käsittelee molemmat. Niitä käytetään kaikissa
myöhemmissä luvuissa.

## Alipäästön vaatimukset

Alipäästösuotimen vaatimus annetaan neljällä luvulla ja näytetaajuudella:

| Suure | Merkintä | Merkitys |
|--------------------|----------|----------------------------------------|
| päästökaistan raja | $f_p$ | tähän asti signaalin on säilyttävä |
| estokaistan raja | $f_s'$ | tästä ylöspäin on vaimennettava |
| aaltoilu | $R_p$ (dB) | päästökaistan vahvistuksen suurin vaihtelu |
| vaimennus | $A_s$ (dB) | estokaistan pienin vaimennus |

Väli $f_p \ldots f_s'$ on siirtymäkaista. Siellä vahvistus saa olla mitä
tahansa, ja juuri sen leveys määrää suotimen hinnan: puolet kapeampi
siirtymäkaista tarkoittaa FIR-suotimessa kaksinkertaista kertoimien
määrää. Vaimennuksen hinta kasvaa hitaammin, suunnilleen lineaarisesti
desibeleissä.

Desibelivaatimukset muunnetaan lineaarisiksi poikkeamiksi, kun
suunnittelumenetelmä niin vaatii. Päästökaistan suhteellinen poikkeama
$\delta_p$ ja estokaistan poikkeama $\delta_s$ ovat

$$\delta_p = \frac{10^{R_p/20} - 1}{10^{R_p/20} + 1}, \qquad
\delta_s = 10^{-A_s/20}.$$

Esimerkiksi 0,1 dB:n aaltoilu on $\pm 0{,}58$ % ja 60 dB:n vaimennus
kerroin 0,001.

## Vaatimus tietona

Vaatimus kannattaa kirjoittaa tietorakenteeksi eikä hajallaan oleviksi
vakioiksi. Silloin sama vaatimus kulkee suunnittelusta testiin, ja sen
ristiriidat havaitaan heti, kun olio luodaan.

```{.python tiedosto="esimerkit/02-vaatimukset.py" osa="vaatimus"}
```

Tarkistusfunktio laskee taajuusvasteen tiheällä hilalla ja palauttaa
listan rikotuista vaatimuksista. Tyhjä lista tarkoittaa, että suodin on
kunnossa. Lista on parempi kuin totuusarvo, koska epäonnistuneen testin
viesti kertoo, mikä vaatimus ja kuinka paljon jäi vajaaksi.

```{.python tiedosto="esimerkit/02-vaatimukset.py" osa="tarkista"}
```

Tiheä hila on tarpeen, koska kapea huippu voi osua hilapisteiden
väliin. 32 768 pistettä 4 kHz:n kaistalla on noin 0,12 Hz:n välein,
mikä riittää tämän tutoriaalin suotimille. Estokaistan tarkistus alkaa
tasan rajasta $f_s'$, koska vahvistus on siirtymäkaistan reunalla
suurimmillaan.

```{.python tiedosto="esimerkit/02-vaatimukset.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-vaatimukset.odotettu"}
```

Lyhyt suodin rikkoo molemmat vaatimukset, ja virheellinen vaatimus
hylätään ennen kuin sillä suunnitellaan mitään.

## Miksi C ja Python eroavat

Kun sama suodin lasketaan C:llä ja SciPyllä, tulokset eroavat yleensä
viimeisissä biteissä, vaikka molemmat toteutukset ovat oikein.
Liukulukujen yhteenlasku ei ole liitännäinen: $(a + b) + c$ ja
$a + (b + c)$ pyöristyvät eri tavoin. Eroja syntyy kolmesta syystä:

- **Laskujärjestys.** Yksinkertainen C-silmukka summaa järjestyksessä,
  BLAS ja NumPy lohkoissa ja vektorirekistereissä rinnakkain.
- **Yhdistetty kertolasku–yhteenlasku (FMA).** Kääntäjä voi laskea
  $a b + c$ yhdellä pyöristyksellä, jos prosessori tukee sitä ja
  optimointiasetukset sallivat.
- **Matematiikkakirjasto.** `sin`, `cos` ja `exp` voivat erota
  viimeisessä bitissä kirjastoversioiden ja vektoritoteutusten välillä.

```{.python tiedosto="esimerkit/02-toleranssi.py" osa="jarjestys"}
```

**ULP** (*unit in the last place*) on kahden vierekkäisen liukuluvun
etäisyys. Se kasvaa luvun suuruuden mukana, joten suhteellinen tarkkuus
on vakio, noin $2{,}2 \cdot 10^{-16}$ doublella ja
$1{,}2 \cdot 10^{-7}$ floatilla.

```{.python tiedosto="esimerkit/02-toleranssi.py" osa="ulp"}
```

## Toleranssin valinta

$n$ termin pistetulon pyöristysvirheelle on yläraja
$n\,\varepsilon \sum_i |x_i h_i|$, missä $\varepsilon$ on konetarkkuus.
Raja on pessimistinen: virheet ovat satunnaisia ja kumoavat toisiaan,
joten tyypillinen virhe on lähempänä $\sqrt{n}\,\varepsilon$ kertaa
summan suuruusluokka.

```{.python tiedosto="esimerkit/02-toleranssi.py" osa="raja"}
```

```{.tuloste tiedosto="esimerkit/02-toleranssi.odotettu"}
```

Tulosteen kaksi viimeistä riviä näyttävät yleisen virheen: pelkkä
suhteellinen toleranssi `rtol` hylkää nollan lähellä olevat arvot, koska
$10^{-17}$ on suhteellisesti äärettömän kaukana nollasta. Signaaleissa
nollan ylityksiä on jatkuvasti. Siksi tutoriaalin vertailut normittavat
virheen **signaalin tasoon**: suurin ero jaetaan viitesignaalin
suurimmalla itseisarvolla. Sama periaate on `numpy.isclose`-funktion
`atol`-parametrissa.

Toleranssit valitaan rakenteen mukaan:

| Toteutus | Toleranssi | Perustelu |
|-------------------------|------------|----------------------------------------|
| FIR, FFT, polyfaasi | $10^{-12}$ | virhe ei kasva ajan myötä |
| IIR (toisen asteen lohkot) | $10^{-10}$ | takaisinkytkentä kerryttää virhettä navan lähellä |
| adaptiivinen suodin | $10^{-9}$ | painot riippuvat kaikista aiemmista virheistä |
| kiinteä pilkku | 0 | kokonaisluvut: malli ja toteutus täsmäävät bitilleen |
| sama koodi lohkoittain ja kerralla | 0 | sama laskujärjestys |

Liian tiukka toleranssi tekee testistä hauraan: se epäonnistuu
kääntäjän päivityksen jälkeen, vaikka mikään ei ole rikki. Liian väljä
toleranssi päästää läpi oikeita virheitä, kuten väärän kertoimen,
jonka vaikutus on $10^{-3}$. Hyvä toleranssi on muutama kertaluokka
odotetun pyöristysvirheen yläpuolella ja monta kertaluokkaa
tyypillisten ohjelmointivirheiden alapuolella.

## Käytännössä

- **Kirjoita vaatimus tietorakenteeksi**, joka tarkistaa itsensä, ja
  käytä samaa oliota suunnittelussa ja testeissä.
- **Palauta rikotut vaatimukset listana.** Testin viesti kertoo silloin
  suoraan, mikä vaatimus ja kuinka paljon jäi vajaaksi.
- **Vertaa liukulukutoteutuksia toleranssilla**, joka on normitettu
  signaalin tasoon. Älä vertaa bitilleen, ellei laskujärjestys ole sama.
- **Valitse toleranssi rakenteen mukaan**: FIR tiukemmin kuin IIR,
  adaptiivinen väljemmin kuin kumpikaan.
- **Älä tulosta testattavaan tulosteeseen viimeisiä numeroita**, jotka
  riippuvat prosessorista. Tulosta tieto toleranssin alittumisesta.

## Itsearviointi

- Osaat muuntaa aaltoilu- ja vaimennusvaatimuksen lineaarisiksi
  poikkeamiksi $\delta_p$ ja $\delta_s$.
- Osaat kirjoittaa vaatimuksen tietorakenteeksi ja tarkistaa suotimen
  sitä vastaan tiheällä taajuushilalla.
- Osaat selittää, miksi kaksi oikeaa toteutusta antavat eri tuloksen
  viimeisissä biteissä.
- Osaat valita toleranssin FIR-, IIR- ja kiinteän pilkun toteutukselle
  ja perustella valinnan.
