# NP-täydellisyys ja reduktiot

Tähän asti jokaiselle tehtävälle on löytynyt polynomiaikainen
algoritmi. Moni tärkeä tehtävä näyttää kuitenkin vastustavan kaikkia
yrityksiä. Tällaisia ovat aikataulutus rajoitteilla, kauppamatkustajan
lyhin kierros, verkon väritys ja loogisen kaavan toteutuvuus. Paras
tunnettu algoritmi on eksponentiaalinen, eikä kukaan ole osoittanut,
ettei parempaa ole. Vaativuusteoria ei ratkaise kysymystä, mutta se
osoittaa, että nämä tehtävät ovat yhtä vaikeita: jos yksi ratkeaa
polynomiajassa, kaikki ratkeavat. Tehtävän tunnistaminen tällaiseksi
säästää ajan, joka kuluisi tehokkaan tarkan algoritmin etsimiseen.
Sen sijaan voidaan valita approksimaatio, heuristiikka tai
eksponentiaalinen haku pienille syötteille (luku 14).

## P ja NP

Teoria käsittelee *päätösongelmia*, joiden vastaus on kyllä tai ei.
Optimointitehtävä muuttuu päätösongelmaksi kysymällä, onko ratkaisua,
joka on vähintään (tai enintään) annetun arvon $K$ kokoinen. Jos
päätösongelma ratkeaa, optimin löytää binäärihaulla $K$:n yli.

- **P** on niiden päätösongelmien luokka, jotka ratkeavat
  polynomiajassa.
- **NP** on niiden päätösongelmien luokka, joiden kyllä-vastaukselle
  on *todistus* (engl. *certificate*), jonka voi tarkistaa
  polynomiajassa. Toteutuvan kaavan todistus on toteuttava sijoitus,
  ja kierroksen todistus on itse kierros.

Jokainen P:n ongelma on NP:ssä, koska tarkistaja voi ratkaista
ongelman itse. Kysymys $P = NP$ on tietojenkäsittelyn tunnetuin avoin
ongelma. Useimmat tutkijat uskovat, että $P \ne NP$, eli että
ratkaisun löytäminen on joskus olennaisesti vaikeampaa kuin sen
tarkistaminen.

Esimerkin tarkistaja on 3-SAT-kaavan sijoituksen tarkistus. Kaava on
lausekkeiden konjunktio, ja jokainen lauseke on kolmen literaalin
disjunktio, esimerkiksi $(x_1 \lor \lnot x_2 \lor x_3) \land
(\lnot x_1 \lor x_2 \lor x_4)$:

```{.cpp tiedosto="esimerkit/13-reduktio.cpp" osa="kaava"}
```

Tarkistus on lineaarinen, mutta raaka haku käy läpi $2^n$ sijoitusta.
SAT-ratkaisijat (DPLL ja CDCL, taito *Diskreetti matematiikka*)
ratkaisevat käytännössä valtavia teollisia kaavoja, mutta pahimman
tapauksen eksponentiaalisuudesta ne eivät pääse.

## Polynomiset reduktiot

Ongelma $A$ *palautuu* ongelmaan $B$ ($A \le_p B$), jos on
polynomiaikainen muunnos $f$, joka vie $A$:n tapaukset $B$:n
tapauksiksi niin, että vastaus säilyy: $x$ on $A$:n kyllä-tapaus
täsmälleen silloin, kun $f(x)$ on $B$:n kyllä-tapaus. Reduktio
tarkoittaa, että $B$ on vähintään yhtä vaikea kuin $A$. Nopea
algoritmi $B$:lle antaisi nopean algoritmin $A$:lle.

Ongelma on **NP-vaikea**, jos jokainen NP:n ongelma palautuu siihen,
ja **NP-täydellinen**, jos se on lisäksi itse NP:ssä. *Cookin–Levinin
lause* (1971) osoitti, että SAT on NP-täydellinen. Sen jälkeen
NP-täydellisyyden todistamiseen riittää reduktio jostakin jo
tunnetusta NP-täydellisestä ongelmasta. Karp (1972) osoitti näin 21
klassisen ongelman täydellisyyden. Reduktion suunta on tärkeä: tunnettu
vaikea ongelma palautetaan *uuteen* ongelmaan, ei toisin päin.

## Esimerkki: 3-SAT riippumattomaksi joukoksi

*Riippumaton joukko* on solmujoukko, jonka solmujen välillä ei ole
kaaria. Päätösongelma kysyy, onko verkossa $K$:n kokoinen riippumaton
joukko. Ongelma on NP:ssä, koska joukon voi tarkistaa ajassa
$O(K^2)$. Vaikeus osoitetaan reduktiolla 3-SAT:sta.

Jokaisesta lausekkeesta tehdään kolmio, jossa on yksi solmu kutakin
literaalia kohden. Lisäksi jokainen literaali $x$ yhdistetään
jokaiseen literaaliin $\lnot x$. Kysytään, onko verkossa $m$:n
kokoinen riippumaton joukko, missä $m$ on lausekkeiden määrä:

```{.cpp tiedosto="esimerkit/13-reduktio.cpp" osa="reduktio"}
```

Esimerkkiohjelma tekee reduktion ensin pienelle kaavalle
$(x_1 \lor x_2 \lor \lnot x_3) \land (\lnot x_1 \lor x_2 \lor x_3)
\land (\lnot x_2 \lor \lnot x_3 \lor x_1)$. Literaalit on tulosteessa
merkitty etumerkillä ja solmut numeroitu lausekkeittain:

```{.tuloste tiedosto="esimerkit/13-reduktio.odotettu" rivit="1-4"}
```

```{.dot tiedosto="kaaviot/reduktio-verkko.dot" otsikko="Kaavasta rakennettu verkko: lausekkeiden kolmiot, ristiriitakaaret katkoviivalla ja kolmen solmun riippumaton joukko korostettuna (esimerkin tulosteesta)" leveys="55%"}
```

Korostetut solmut $x_1$, $x_2$ ja $\lnot x_3$ ovat eri kolmioista,
eikä niiden välillä ole kaaria. Niistä luetaan sijoitus $x_1 = 1$,
$x_2 = 1$, $x_3 = 0$, joka toteuttaa kaavan.

Oikeellisuus todistetaan kumpaankin suuntaan:

- **Kaava toteutuu $\Rightarrow$ joukko on olemassa.** Toteuttava
  sijoitus tekee jokaisesta lausekkeesta ainakin yhden literaalin
  todeksi. Valitaan kustakin kolmiosta yksi tosi literaali. Saman
  kolmion solmuja valitaan vain yksi, eikä $x$:ää ja $\lnot x$:ää voi
  valita yhtä aikaa, koska ne eivät ole molemmat tosia.
- **Joukko on olemassa $\Rightarrow$ kaava toteutuu.** $m$:n kokoinen
  riippumaton joukko ottaa jokaisesta kolmiosta täsmälleen yhden
  solmun. Ristiriitaiset literaalit eivät ole joukossa yhtä aikaa,
  joten valituista literaaleista saadaan sijoitus, joka tekee jokaisen
  lausekkeen todeksi.

Toinen suunta on lisäksi *rakentava*: riippumattomasta joukosta saa
toteuttavan sijoituksen. Reduktio kuljettaa siis myös ratkaisut.

## Reduktion testaus

Reduktio on ohjelma, ja siinä voi olla virhe. Esimerkiksi kaari voi
puuttua tai literaalien vertailu voi olla väärin. Vertailutesti ratkaisee
satunnaiset pienet kaavat raa'asti molemmilla puolilla ja tarkistaa,
että vastaukset täsmäävät. Riippumaton joukko etsitään peruuttavalla
haulla (taito *Algoritmit*), jota nopeutetaan karsinnalla: haara
hylätään, jos edes yläraja sille, mitä haarasta voi vielä saada, ei
ylitä parasta löydettyä ratkaisua. Luku 14 käsittelee tämän
*haarautumisen ja karsinnan* yleisesti. Solmujoukot ovat 64-bittisiä
maskeja, ja yläraja saadaan jakamalla ehdokkaat ahneesti klikkeihin,
koska kustakin klikistä voi ottaa vain yhden solmun:

```{.cpp tiedosto="esimerkit/13-reduktio.cpp" osa="haku"}
```

Testi arpoo 300 kaavaa, joissa on 3–5 muuttujaa, rakentaa niistä
verkot ja vertaa raa'an SAT-haun ja riippumattoman joukon haun
vastauksia. Toteutuvissa kaavoissa löydetty joukko muunnetaan
sijoitukseksi, ja varmentaja tarkistaa sen:

```{.tuloste tiedosto="esimerkit/13-reduktio.odotettu" alkaen="300 kaavaa"}
```

Satunnaiset 3-SAT-kaavat ovat helppoja, kun lausekkeita on vähän
(lähes kaikki toteutuvat) tai paljon (lähes mikään ei toteudu).
Vaikeimmat kaavat ovat lähellä suhdetta $m/n \approx 4{,}26$, jossa
toteutuvuuden todennäköisyys putoaa jyrkästi. Testi arpoo
lausekkeiden määrän väliltä $3n \ldots 5n$, jotta molempia vastauksia
tulee.

Klikkipeiteraja on yleinen, mutta tässä verkossa se on erityisen
tehokas, koska kolmiot ovat klikkejä. Haku käy keskimäärin vain noin
sata solmua. Raja ei tunne kaavaa, mutta reduktion rakenne näkyy
sille.

## NP-täydellisiä ongelmia

| Ongelma | Kysymys | Tyypillinen esiintymä |
|----------------|--------------------|----------------------|
| SAT, 3-SAT | toteutuuko kaava | laitteiston ja ohjelmien verifiointi |
| riippumaton joukko, klikki | onko $K$ solmun joukko | yhteensopivuus, ryhmien etsintä |
| solmupeite | riittääkö $K$ solmua kattamaan kaaret | valvontapisteiden sijoittelu |
| verkon väritys | riittääkö $k$ väriä | rekisterien varaus, aikataulut |
| kauppamatkustaja | onko kierros pituudeltaan $\le K$ | reititys, piirilevyjen poraus |
| osajoukon summa, reppu | saako summan $K$ | budjetointi, lastaus |
| Hamiltonin kierto | käykö kierros jokaisessa solmussa kerran | sekvensointi |
| joukkopeite | riittääkö $K$ joukkoa | palveluiden sijoittelu |

Riippumaton joukko, klikki ja solmupeite ovat saman ongelman kolme
muotoa. $S$ on riippumaton täsmälleen silloin, kun $V \setminus S$ on
solmupeite, ja täsmälleen silloin, kun $S$ on klikki
komplementtiverkossa. Kaksijakoisessa verkossa solmupeite on kuitenkin helppo
(luku 10, Königin lause), ja 2-SAT ratkeaa lineaarisessa ajassa.
Pieni muutos rajoitteissa voi siis siirtää ongelman P:n ja
NP-täydellisen välillä.

*Pseudopolynomiset* ongelmat ovat erityistapaus. Reppuongelma
ratkeaa dynaamisella ohjelmoinnilla ajassa $O(nW)$, joka on
polynomi kapasiteetin $W$ *arvon* suhteen. Syötteen koko on
kuitenkin vain $\log W$ bittiä, joten aika on syötteen koon suhteen
eksponentiaalinen.

## Käytännössä

- Kun et löydä polynomiaikaista algoritmia, etsi tunnettu
  NP-täydellinen ongelma, joka on uuden ongelman erikoistapaus. Jos
  sellainen löytyy, uusi ongelma on vähintään yhtä vaikea.
- Tarkista, onko syötteessä rajoitus, joka tekee ongelmasta helpon.
  Puut, kaksijakoiset verkot, pienet painot, kaksi literaalia
  lausekkeessa ja tasoverkot ovat yleisiä esimerkkejä.
- Muotoile vaikea ongelma SAT-, ILP- tai rajoiteongelmaksi ja anna se
  valmiille ratkaisijalle (MiniSat, CaDiCaL, OR-Tools, HiGHS). Ne
  ratkaisevat käytännön tapauksia, joihin oma raaka haku ei pysty.
- NP-täydellisyys koskee pahinta tapausta. Käytännön syötteet ovat
  usein helppoja, joten mittaa ennen kuin luovutat tarkasta ratkaisusta.
- Testaa reduktiot kuten muutkin algoritmit: pienet satunnaiset
  tapaukset ratkaistaan raa'asti molemmin puolin, ja ratkaisu
  kuljetetaan takaisin ja tarkistetaan.

## Itsearviointi

- Osaat määritellä luokat P ja NP todistuksen ja tarkistajan avulla ja
  kirjoittaa tarkistajan esimerkiksi 3-SAT:lle.
- Osaat selittää, mitä polynominen reduktio on ja miksi sen suunta
  ratkaisee, kumpi ongelma on vaikeampi.
- Osaat rakentaa reduktion 3-SAT:sta riippumattomaan joukkoon ja
  todistaa sen oikeellisuuden molempiin suuntiin.
- Osaat testata reduktion satunnaisilla tapauksilla ja kuljettaa
  ratkaisun takaisin alkuperäiseen ongelmaan.
- Osaat tunnistaa yleisiä NP-täydellisiä ongelmia ja niiden helppoja
  erikoistapauksia.
