# Johdanto {.runko-johdanto}

Tietokonearkkitehtuuri on oppi siitä, miten suoritin ja muisti on
järjestetty, jotta ohjelmat kulkisivat nopeasti, oikein ja kohtuullisella
energialla. Se on ohjelmiston ja laitteiston välinen kerros: ylhäältä
katsottuna sopimus, jonka kääntäjä ja käyttöjärjestelmä näkevät
(käskykanta, rekisterit, poikkeukset, muistimalli), ja alhaalta katsottuna
rakenne, jolla sopimus täytetään (liukuhihna, ennustimet, välimuistit,
osoitteenmuunnos, koherenssi).

Ero näiden kahden välillä on koko alan ydin. Käskykanta lupaa, että
käskyt suoritetaan yksi kerrallaan järjestyksessä ja että jokainen lataus
näkee viimeisimmän talletuksen. Todellinen suoritin noutaa neljä käskyä
jaksossa, arvaa haarojen suunnan, suorittaa käskyjä väärässä
järjestyksessä, pitää dataa kolmessa välimuistitasossa ja jakaa muistin
kymmenien ytimien kesken. Lupaus pitää silti, koska laitteisto peittää
temppunsa. Arkkitehtuurin ymmärtäminen tarkoittaa, että tietää, mitkä
temput on tehty ja milloin ne epäonnistuvat: silloin ohjelma hidastuu,
vaikka sen koodi ei muuttunut.

## Mitä tässä opitaan

Tutoriaali etenee käskykannasta kohti moniytimisiä järjestelmiä:

| Luku | Aihe | Simulaattorin osa |
|------|------|-------------------|
| 2 | Käskykanta, RISC-V:n käskymuodot | kokoaja ja purkaja |
| 3 | Datapolku ja ohjausyksikkö | ohjaussignaalit, monijaksoinen CPI |
| 4 | Liukuhihna, riippuvuudet, eteenpäinkytkentä | ajoitusmalli |
| 5 | Haarautumisen ennustus | ennustimet |
| 6 | Välimuistin rakenne | välimuistimalli, 3C |
| 7 | Kirjoituspolitiikat ja muistihierarkia | AMAT, silmukkajärjestys |
| 8 | Virtuaalimuisti ja MMU | Sv32-sivutaulu, TLB |
| 9 | Poikkeukset, keskeytykset ja I/O | mtvec, mcause, UART |
| 10 | Moniytimet ja koherenssi | MESI |
| 11 | Superskalaarisuus ja epäjärjestys | ILP-rajatutkimus |
| 12 | RISC, CISC ja mikro-operaatiot | µop-purku |

Jokaisessa luvussa väite mitataan. Kun teksti sanoo, että
eteenpäinkytkentä puolittaa CPI:n tai että sarakkeittain luettu matriisi
tuhoaa välimuistin, sama asia näkyy esimerkin tulosteessa luvuilla, jotka
syntyvät oikeista käskyjäljistä.

## Työkalu: oma simulaattori

Tutoriaalin esimerkit rakentuvat pienen C++-simulaattorin ympärille.
Sen osat ovat hakemistossa `esimerkit/yhteinen/`:

- `rv32i.hpp`: RV32I-osajoukon käskyjen koodaus ja purku sekä
  kaksivaiheinen kokoaja (assembler) nimiöineen ja tavallisimpine
  pseudokäskyineen.
- `kone.hpp`: käskytason simulaattori (ISS, *instruction set simulator*).
  Se suorittaa ohjelman käsky kerrallaan ja tuottaa jokaisesta
  käskystä *tapahtuman*: mitä rekistereitä luettiin, mihin osoitteeseen
  viitattiin ja minne hypättiin.
- `liukuhihna.hpp`: viisivaiheisen liukuhihnan ajoitusmalli ja
  haarautumisen ennustimet.
- `valimuisti.hpp`: parametrisoitava välimuistimalli.
- `ohjelmat.hpp`: testiohjelmat assemblynä.

Malli on *jälkiohjattu* (trace-driven): ensin ISS ajaa ohjelman ja
tuottaa oikean käskyjonon, sitten ajoitus- ja välimuistimallit käyvät
jonon läpi ja laskevat, mitä tietyllä laitteistolla olisi tapahtunut.
Sama jälki voidaan syöttää kymmenelle eri kokoonpanolle, jolloin vertailu
on reilu: vain laitteisto muuttuu, ei ohjelma. Tutkimuskäytössä samaa
jakoa käyttävät esimerkiksi gem5:n nopeat mallit ja välimuistisimulaattori
Dinero. Jälkiohjauksen rajoitus on, että väärän polun käskyt eivät näy
jäljessä: malli tietää, että ennuste meni pieleen, mutta ei simuloi
väärältä polulta noudettuja käskyjä.

Tapahtuma näyttää tältä:

```{.cpp tiedosto="esimerkit/yhteinen/kone.hpp" osa="tapahtuma"}
```

Testiohjelmat valittiin niin, että jokainen korostaa eri ilmiötä:

| Ohjelma | Mitä se tekee | Mitä se korostaa |
|---------|---------------|------------------|
| `summa` | täyttää ja summaa 200 alkion taulukon | latauksen käyttö heti, silmukka |
| `kupla` | kuplalajittelee 48 näennäissatunnaista lukua | datasta riippuvat haarat |
| `matriisi` | kertoo kaksi 12 × 12 -matriisia | välimuistiristiriidat, kertolaskut |
| `fib` | laskee fib(16) rekursiivisesti | kutsut, paluut, pino |
| `lista` | kulkee sekoitetun linkitetyn listan | osoitinjahti |

Esimerkiksi `summa` on tällainen:

```{.cpp tiedosto="esimerkit/yhteinen/ohjelmat.hpp" osa="summa"}
```

Assemblyn syntaksi ja kutsukäytännöt käydään läpi taidossa *Assembly*;
tässä niitä vain luetaan.

## Ensimmäinen ajo

Ensimmäinen esimerkki kokoaa `summa`-ohjelman, ajaa sen ja laskee,
millaisia käskyjä suoritettiin:

```{.cpp tiedosto="esimerkit/01-ensimmainen.cpp" osa="ajo"}
```

```{.cpp tiedosto="esimerkit/01-ensimmainen.cpp" osa="jakauma"}
```

```{.tuloste tiedosto="esimerkit/01-ensimmainen.odotettu"}
```

Staattisesti ohjelmassa on 24 käskyä, mutta niistä suoritettiin 2 810,
koska silmukat toistuvat. Arkkitehtuurin kannalta ratkaisevaa on
*dynaaminen* käskysekoitus: noin joka seitsemäs käsky on haara, joka
seitsemäs lataus ja joka seitsemäs talletus. Tyypillisissä
kokonaislukuohjelmissa (SPEC CPU) latauksia on 20–30 %, talletuksia
10 % ja haaroja 15–20 %. Näistä luvuista johtuu, miksi välimuistit ja
haarojen ennustus ovat suorittimen tärkeimmät rakenteet.

## Suorituskyvyn rautalaki

Ohjelman suoritusaika jakautuu kolmeen tekijään:

$$
\text{aika} = \text{käskyt} \times \frac{\text{jaksot}}{\text{käsky}}
\times \frac{\text{aika}}{\text{jakso}} = N \cdot \text{CPI} \cdot T.
$$

Käskymäärä $N$ riippuu ohjelmasta, kääntäjästä ja käskykannasta.
CPI (*cycles per instruction*) riippuu mikroarkkitehtuurista: kuinka
usein liukuhihna pysähtyy, kuinka usein välimuisti hutii. Jakson aika
$T = 1/f$ riippuu piiritekniikasta ja siitä, kuinka paljon logiikkaa
yhteen jaksoon mahtuu. Tekijät eivät ole riippumattomia: pidempi
liukuhihna lyhentää jaksoa mutta kasvattaa väärän ennusteen hintaa,
monimutkaisempi käsky vähentää käskyjä mutta voi pidentää jaksoa.
Jokainen tämän tutoriaalin rakenne on keino pienentää yhtä tekijää
kasvattamatta muita liikaa.

CPI:n käänteisluku IPC (*instructions per cycle*) on tavallisempi
nykyaikaisten suorittimien yhteydessä, koska ne suorittavat useamman
käskyn jaksossa: IPC 4 on CPI 0,25.

Toinen perussääntö on **Amdahlin laki**. Jos osuus $p$ suoritusajasta
nopeutuu kertoimella $s$, koko ohjelma nopeutuu

$$
\frac{1}{(1 - p) + p / s}.
$$

Jos välimuistihuteihin kuluu 40 % ajasta ja ne poistetaan kokonaan,
ohjelma nopeutuu enintään $1/0{,}6 \approx 1{,}67$-kertaisesti. Laki
muistuttaa, että optimointi kannattaa kohdistaa siihen, mihin aika
oikeasti kuluu, ja että nopeutuksella on yläraja.

## Teho ja energia

Rautalaki kertoo ajan, mutta nykyisen suorittimen suunnittelua rajoittaa
yhtä usein teho. CMOS-piirin tehonkulutus on kahden osan summa:

$$
P \approx \alpha C V^2 f + V I_\text{vuoto}.
$$

Ensimmäinen termi on **dynaaminen teho**: jokainen tilanvaihto lataa
tai purkaa kapasitanssin $C$, $\alpha$ on jaksossa vaihtuvien solmujen
osuus, $V$ käyttöjännite ja $f$ kellotaajuus. Toinen on **vuototeho**,
joka kuluu, vaikka piiri ei tee mitään (taito *Digitaalitekniikka*).
Kolme seurausta ohjaa kaikkea, mitä tässä tutoriaalissa rakennetaan:

- **Jännite ratkaisee.** Dynaaminen teho riippuu jännitteestä
  neliöllisesti ja taajuudesta lineaarisesti. Koska korkeampi taajuus
  vaatii korkeamman jännitteen, teho kasvaa taajuuden mukana lähes
  kuutiollisesti. Tähän pysähtyi kellotaajuuksien kasvu 2000-luvun
  alussa (luku 4), ja tästä seuraa moniytimisyys (luku 10).
- **Teho ja energia ovat eri asioita.** Teho (wattia) määrää
  jäähdytyksen ja virransyötön, energia (joulea) akun keston ja
  sähkölaskun. Tehtävän energia on teho kertaa aika: suoritin, joka
  tekee työn nopeasti ja nukahtaa, voi kuluttaa vähemmän energiaa kuin
  hitaampi ja vähätehoisempi.
- **Suorituskyky wattia kohden on mittari.** Epäjärjestyssuoritus
  (luku 11) nopeuttaa ohjelmaa, mutta sen jonot ja spekulaatio kuluttavat
  energiaa myös työhön, joka hylätään. Siksi samassa piirissä on usein
  suuria ja pieniä ytimiä, ja siksi palvelinsalin ja puhelimen
  suorittimet päätyvät erilaisiin ratkaisuihin samasta käskykannasta.

Simulaattori ei mallinna tehoa, mutta sen laskemat suureet (käskyt,
jaksot, hudit, väylätapahtumat) ovat juuri niitä, joihin energia
kuluu.

## Esitiedot ja rajaus

Tutoriaali olettaa, että lukija tuntee:

- *Digitaalitekniikka*: portit, kiikut, rekisterit, multiplekserit ja
  ajoitus. Datapolku rakennetaan näistä palikoista.
- *Assembly*: rekisterit, lataukset ja talletukset, haarat, kutsut ja
  pino. RISC-V-assemblyä luetaan sujuvasti.

Esimerkit ovat C++23:a. Simulaattorin lukemiseen riittää C-tausta ja
valmius lukea luokkia ja `std::vector`ia; käytetyt piirteet
(`std::print`, `std::format`, `constexpr`, nimetyt alustimet) esitellään
taidossa *Moderni C++*.

Seuraavat aiheet on rajattu pois, koska niille on oma taitonsa:

- *Miten tietokone laskee*: kokonais- ja liukulukujen esitys ja
  aritmetiikka.
- *SoC-integraatio*: väylästandardit (AXI, APB), keskeytysohjaimet ja
  oheislaitteet piirin suunnittelijan näkökulmasta.
- *RTL-suunnittelu SystemVerilogilla*: datapolun toteutus
  synteesikelpoisena laitteistona.
- *GPU-laskenta*: datarinnakkaiset suorittimet.

Tämä tutoriaali katsoo samoja asioita arkkitehdin silmin: mitä rakenne
tekee, miksi se on olemassa ja mitä se maksaa.

## Esimerkkien ajaminen

Esimerkit käännetään GCC 14:llä ja Clang 20:llä C++23-tilassa
varoitukset virheinä sekä AddressSanitizerin ja UBSanin kanssa:

```text
make testaa                    # kaikki esimerkit molemmilla kääntäjillä
g++ -std=c++23 -O2 -I esimerkit esimerkit/05-ennustimet.cpp -o e && ./e
```

Jokaisen esimerkin tuloste on tallennettu `.odotettu`-tiedostoon, ja
testi vertaa ajon tulostetta siihen. Simulaattori on täysin
deterministinen: sama ohjelma tuottaa aina saman jäljen, samat jaksot ja
samat osumasuhteet. Tämä on simulaattorin hyve, jota oikea laitteisto ei
tarjoa, ja syy siihen, että arkkitehtuuritutkimus tehdään
simulaattoreilla.
