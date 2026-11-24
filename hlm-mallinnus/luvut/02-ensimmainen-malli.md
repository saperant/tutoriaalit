# Ensimmäinen malli

SystemC-malli koostuu *moduuleista*, jotka vastaavat laitteiston lohkoja.
Moduulilla on *portit*, joiden kautta se näkee ympäristönsä, ja
*prosesseja*, jotka toimivat rinnakkain. Moduulit kytketään toisiinsa
*kanavilla*, joista yksinkertaisin on signaali. Tämä luku rakentaa
nelibittisen laskurin ja sille testipenkin; sama rakenne toistuu
jokaisessa mallissa.

## Moduuli, portit ja prosessi

Laskuri laskee kellon nousevalla reunalla, kun sen tulo `laske` on 1, ja
nollautuu synkronisesti. Ylivuodosta kertoo oma lähtö:

```{.cpp tiedosto="esimerkit/01-laskuri/laskuri.hpp" osa="moduuli"}
```

`SC_MODULE(Laskuri)` on makro, joka tarkoittaa samaa kuin
`struct Laskuri : sc_core::sc_module`. Moduuli on siis tavallinen
C++-luokka, ja sillä voi olla jäseniä, metodeja ja kantaluokkia kuten
muillakin. `SC_CTOR(Laskuri)` määrittelee rakentimen, joka ottaa
moduulin nimen. Makrot eivät ole pakollisia: luvun 8 TLM-mallit
periytyvät suoraan `sc_module`-luokasta ja määrittelevät rakentimen itse,
mikä on tavallista, kun rakentimella on muitakin parametreja.

Portit ovat jäsenmuuttujia. `sc_in<T>` lukee ja `sc_out<T>` kirjoittaa
arvon tyyppiä `T`; `sc_inout<T>` tekee molempia. Portin tyyppi on
signaalin tyyppi, tässä `bool` ja nelibittinen etumerkitön
`sc_uint<4>` (luku 6). Portit nimetään merkkijonolla: ilman nimeä
SystemC antaa nimen `port_0`, ja virheilmoitus kertoo silloin vain, että
`laskuri.port_0` jäi kytkemättä.

Rakentimessa rekisteröidään prosessit. `SC_METHOD(paivita)` kertoo
simulaattorille, että jäsenfunktio `paivita` on prosessi, joka ajetaan
alusta loppuun aina, kun jokin sen *herkkyyslistan* tapahtumista
tapahtuu. `sensitive << clk.pos()` lisää listaan kellon nousevan
reunan. `dont_initialize()` estää ajon simuloinnin alussa: muuten
jokainen prosessi ajetaan kerran alustusvaiheessa, mikä on
kombinaatiologiikalle oikein mutta rekisterille väärin.

Prosessi lukee porttia funktiolla `read()` ja kirjoittaa funktiolla
`write()`. Rekisterin tila on tavallinen jäsenmuuttuja `tila`: koska
prosessi ajetaan vain kellon reunalla, muuttuja käyttäytyy kuin
kiikku. Portti `arvo` on rekisterin lähtö, ja kirjoitettu arvo näkyy
muille vasta, kun simulaattori päivittää signaalin (luku 4).

## Testipenkki

Testipenkki on kaksi moduulia: herätteet syöttävä säie ja tulosteita
seuraava tarkkailija.

```{.cpp tiedosto="esimerkit/01-laskuri/main.cpp" osa="testipenkki"}
```

`Heratteet` käyttää prosessityyppiä `SC_THREAD`. Säie ajetaan kerran,
mutta se voi pysähtyä kesken funktiolla `wait()` ja jatkaa myöhemmin
samasta kohdasta; jokaisella säikeellä on oma pinonsa. Ilman argumenttia
`wait()` odottaa staattisen herkkyyden tapahtumaa, tässä kellon laskevaa
reunaa, ja `wait(8)` kahdeksaa sellaista. Tulot vaihdetaan laskevalla
reunalla, jotta ne ovat vakaat nousevalla reunalla: sama periaate kuin
RTL-testipenkissä. Lopuksi `sc_stop()` pysäyttää simuloinnin.

`Tarkkailija` on `SC_METHOD`, joka on herkkä signaalien arvoille:
`sensitive << arvo` tarkoittaa porttiin kytketyn signaalin
muutostapahtumaa (*value changed event*). Se tulostaa arvon aina, kun
laskuri muuttuu.

## Elaborointi ja simulointi

Ohjelman pääfunktio on `sc_main`. SystemC-kirjasto määrittelee `main`-
funktion, joka alustaa simulaattorin ja kutsuu `sc_main`ia:

```{.cpp tiedosto="esimerkit/01-laskuri/main.cpp" osa="main"}
```

Ennen ensimmäistä `sc_start`-kutsua ohjelma on *elaborointivaiheessa*:
se luo moduulit ja kanavat ja kytkee portit. Kytkentä `laskuri.clk(clk)`
sitoo portin kanavaan; portti ei omista kanavaa vaan viittaa siihen.
Rakenne on elaboroinnin jälkeen kiinteä: moduuleja ei voi luoda
simuloinnin aikana, ja kytkemätön portti on virhe, joka huomataan heti
simuloinnin alussa. Elaborointi on tavallista C++:aa, joten rakenteen
voi muodostaa silmukoilla ja ehdoilla, esimerkiksi parametrista
riippuvan määrän kanavia.

`sc_clock` on valmis kanava, joka tuottaa kellosignaalin: tässä jakso
10 ns ja ensimmäinen nouseva reuna hetkellä 0. `sc_start()` ilman
argumenttia simuloi, kunnes `sc_stop()` kutsutaan tai tapahtumat
loppuvat; `sc_start(100, SC_NS)` simuloisi 100 ns.

```{.tuloste tiedosto="esimerkit/01-laskuri/odotettu"}
```

Nollaus on voimassa toiseen laskevaan reunaan 15 ns asti, joten laskuri
kasvaa ensimmäisen kerran 20 ns:n nousevalla reunalla. Laskenta pysähtyy 90 ns:n
jälkeen kahden jakson ajaksi, ja 190 ns:n kohdalla arvo kiertää 15:stä
nollaan ja ylivuoto näkyy yhden jakson ajan. Alla oleva kuva näyttää
samat signaalit aaltoina 210 ns:n ajalta. Se on piirretty samojen
moduulien VCD-tiedostosta (ks. seuraava kappale),
ja testi tarkistaa, että kuva vastaa simulaatiota.

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/laskuri.json" otsikko="Laskurin signaalit SystemC:n VCD-tiedostosta"}
```

Viimeinen rivi `Info:` on
simulaattorin oma ilmoitus `sc_stop`-kutsusta. Ilmoitukset kulkevat
raportointijärjestelmän `sc_report_handler` kautta, ja niiden toiminnon
voi vaihtaa (luku 12 vaimentaa tämän).

Signaaleja voi tarkastella myös aaltomuotoina. `sc_create_vcd_trace_file`
avaa VCD-tiedoston, `sc_trace(tiedosto, signaali, "nimi")` lisää siihen
signaalin, ja tiedoston avaa esimerkiksi GTKWave. Transaktiotason
malleissa aaltomuodot ovat harvoin hyödyllisiä; niissä käytetään
lokeja ja tilastoja, kuten tämän tutoriaalin esimerkeissä.

## Käytännössä

- **Rakenne kuin RTL:ssä, toteutus kuin ohjelmassa.** Moduulijako
  kannattaa tehdä samoista lohkoista kuin tulevassa piirissä, koska
  malli toimii myöhemmin RTL:n referenssinä ja osat voi vaihtaa
  toteutukseen yksi kerrallaan (luku 12). Moduulin sisällä käytetään
  tavallista C++:aa: kokoelmia, algoritmeja ja apuluokkia.
- **Nimeä kaikki.** Moduulit, portit ja kanavat saavat nimen
  rakentimessa. Hierarkkinen nimi (`laskuri.arvo`) näkyy
  virheilmoituksissa, lokeissa ja aaltomuodoissa, ja ilman sitä
  ison mallin vian paikallistaminen on arvailua.
- **Otsake moduulia kohden.** Moduuli määritellään otsaketiedostossa ja
  kytketään ylemmällä tasolla, kuten `laskuri.hpp` ja `main.cpp`. Ison
  mallin käännösaikaa lyhentää jakaminen otsakkeeseen ja
  toteutustiedostoon: SystemC:n otsakkeet ovat raskaita.
- **`dont_initialize` rekistereille.** Alustusajo on tarkoitettu
  kombinaatioprosesseille, jotta niiden lähdöt vastaavat tuloja alusta
  asti. Kellotettu prosessi, joka ajetaan alustuksessa, tekee yhden
  ylimääräisen tilasiirtymän ennen ensimmäistä kellonreunaa.
- **`SC_METHOD` ensin.** Metodi on halvempi kuin säie, koska sillä ei
  ole omaa pinoa eikä kontekstinvaihtoa. Säie on oikea valinta, kun
  prosessi on luontevimmin peräkkäinen ohjelma, kuten testipenkki tai
  protokollan tilakone, joka odottaa vuorotellen eri asioita.

## Itsearviointi

- Osaat kirjoittaa moduulin, jolla on nimetyt tulo- ja lähtöportit ja
  kellon nousevalle reunalle herkkä `SC_METHOD`.
- Osaat kytkeä moduulit signaaleilla ja kellolla `sc_main`issa ja
  selittää, mitä elaborointi- ja simulointivaihe tarkoittavat.
- Osaat kertoa, mitä `dont_initialize()` tekee ja milloin sitä tarvitaan.
- Osaat valita `SC_METHOD`- ja `SC_THREAD`-prosessin välillä ja
  perustella valinnan.
