# Abstraktit tietotyypit ja rajapinnat

Abstrakti tietotyyppi määritellään sen operaatioiden kautta: mitä
niille annetaan, mitä ne palauttavat ja mitä niistä seuraa. Toteutus –
taulukko, lista tai puu – on yksityiskohta, jonka käyttäjän ei tarvitse
tietää. C:ssä ei ole luokkia, mutta saman erottelun saa aikaan
otsaketiedostolla ja *läpinäkymättömällä osoittimella*. Epätäydelliset
tyypit esiteltiin C-kielen esikääntäjäluvussa; tässä luvussa niistä tehdään
tietorakenteen rajapinta.

## Rajapinta otsaketiedostona

Esimerkkinä on kokonaislukujen joukko. Otsaketiedosto kertoo kaiken,
mitä käyttäjä saa tietää:

```{.c tiedosto="esimerkit/02-joukko/joukko.h" osa="rajapinta"}
```

Rajapinnassa on kolme suunnittelupäätöstä, jotka toistuvat jokaisessa
tämän tutoriaalin rakenteessa:

1. **Läpinäkymätön tyyppi.** `typedef struct joukko Joukko;` esittelee
   tyypin kertomatta sen kenttiä. Käyttäjä voi pitää osoitinta
   `Joukko *` ja välittää sitä funktioille, mutta ei voi lukea kenttiä
   eikä varata joukkoa pinosta, koska kääntäjä ei tiedä sen kokoa.
2. **Virhekoodit.** Operaatiot, jotka voivat epäonnistua tai joiden
   tulos on kiinnostava, palauttavat luettelotyypin arvon. Tieto siitä,
   oliko alkio jo joukossa, on usein hyödyllinen eikä maksa mitään,
   koska toteutus saa sen joka tapauksessa selville.
3. **Omistajuus.** Kommentti kertoo, kuka vapauttaa mitä. Joukko
   kopioi alkiot itseensä, joten kutsujan ei tarvitse pitää alkuperäisiä
   arvoja elossa. Jos alkiot olisivat osoittimia, rajapinnan pitäisi
   kertoa, omistaako joukko osoitetun datan vai ei.

Muistin loppuminen on ainoa virhe, jota käyttäjä ei voi estää omalla
toiminnallaan, ja hyvä rajapinta lupaa, että se jättää rakenteen
ennalleen. Silloin kutsuja voi jatkaa vanhalla datalla tai vapauttaa
sen hallitusti.

## Toteutus piilossa

Tämä toteutus säilyttää alkiot lajiteltuna taulukkona:

```{.c tiedosto="esimerkit/02-joukko/joukko.c" osa="rakenne"}
```

Haku tehdään puolitushaulla, joka palauttaa ensimmäisen paikan, jonka
alkio on vähintään haettava. Sama apufunktio palvelee hakua, lisäystä
ja poistoa. Lisäys siirtää loppuosaa yhdellä `memmove`-kutsulla:

```{.c tiedosto="esimerkit/02-joukko/joukko.c" osa="lisaa"}
```

Huomaa järjestys: tila kasvatetaan *ennen* kuin taulukkoa muutetaan,
ja `realloc`-kutsun tulos tallennetaan apumuuttujaan. Jos muisti
loppuu, `j->alkiot` osoittaa yhä vanhaan, ehjään taulukkoon, ja
funktio palauttaa `JOUKKO_MUISTI` rakenteen muuttumatta.

Käyttäjä näkee vain rajapinnan. Ohjelma pitää kirjaa sallituista
porteista:

```{.c tiedosto="esimerkit/02-joukko/main.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-joukko.odotettu"}
```

Läpikäynti tehdään takaisinkutsulla, jolle annetaan kontekstiosoitin
`void *tieto`. Vaihtoehto olisi iteraattori, eli pieni rakenne, joka
muistaa paikan ja jota siirretään funktiolla eteenpäin. Takaisinkutsu
on yksinkertaisempi toteuttaa, iteraattori joustavampi käyttää
(läpikäynnin voi keskeyttää ja jatkaa).

Joukko-operaatioiden hinnat tällä toteutuksella:

| Operaatio | Hinta | Miksi |
|-----------|-------|-------|
| `joukko_sisaltaa` | $O(\log n)$ | puolitushaku |
| `joukko_lisaa` | $O(n)$ | loppuosan siirto |
| `joukko_poista` | $O(n)$ | loppuosan siirto |
| `joukko_kay_lapi` | $O(n)$ | valmiiksi järjestyksessä |

Sama rajapinta voitaisiin toteuttaa hajautustaululla (luku 6), jolloin
lisäys ja poisto olisivat odotusarvoisesti $O(1)$ mutta järjestetty
läpikäynti vaatisi lajittelun. Tai tasapainotetulla puulla, jolloin
kaikki olisivat $O(\log n)$. Koska käyttäjän koodi ei riipu
toteutuksesta, valinnan voi tehdä myöhemmin mittausten perusteella.

## Kääntäjä vartioi rajaa

Läpinäkymättömyys ei ole pelkkä sopimus. Jos käyttäjä yrittää lukea
kenttää, käännös katkeaa:

```{.c tiedosto="esimerkit/02-lapinakymaton.ei-kaanny.c"}
```

GCC ilmoittaa `invalid use of incomplete typedef 'Laskuri'`. Korjattu
versio (`-DKORJATTU`) käyttää lukufunktiota ja tulostaa:

```{.tuloste tiedosto="esimerkit/02-lapinakymaton.odotettu"}
```

Hinta on se, että jokainen kentän luku on funktiokutsu, eikä kääntäjä
voi upottaa sitä toiseen käännösyksikköön ilman linkitysaikaista
optimointia (`-flto`). Pienissä, kuumissa rakenteissa – esimerkiksi
kahden kentän vektorissa – tämä voi näkyä. Silloin rakenne kannattaa
julkaista otsaketiedostossa ja nimetä kentät niin, että niiden
yksityisyys on selvä (esimerkiksi etuliite `sis_`), tai tarjota
`static inline` -lukufunktiot.

## Yksi rakenne, monta tyyppiä

Luvun joukko tallentaa vain `int`-arvoja, ja samoin tekevät
tutoriaalin muut rakenteet: yksi alkiotyyppi pitää koodin lyhyenä.
Oikeassa ohjelmassa sama vektori tai hajautustaulu tarvitaan monelle
tyypille. C:ssä ei ole malleja eikä geneerisiä tyyppejä, joten valinta
on tehtävä itse kolmesta tavasta:

| Tapa | Tyyppitarkistus | Koodin määrä | Hinta ajon aikana |
|------|-----------------|--------------|-------------------|
| `void *` ja alkion koko | ei ole: kutsuja muuntaa osoittimet | yksi toteutus | `memcpy` ja kutsu funktio-osoittimen kautta |
| makro tuottaa toteutuksen | on | kopio tyyppiä kohti | ei lisähintaa, kääntäjä optimoi tyypin mukaan |
| tunkeileva rakenne (luku 4) | osittain: makro laskee sisältävän tietueen | yksi toteutus | ei varauksia, linkit alkion sisällä |

Ensimmäinen tapa on standardikirjaston `qsort`in ja `bsearch`in tapa.
Rakenne käsittelee alkioita tavuina ja saa alkion koon parametrina;
vertailu tai hajautus annetaan funktio-osoittimena:

```{.c tiedosto="esimerkit/02-geneerinen.c" osa="void"}
```

Toinen tapa kirjoittaa toteutuksen makroksi, jonka parametreina ovat
tyypin nimi ja alkiotyyppi. Jokainen käyttö tuottaa oman tietueen ja
omat funktiot:

```{.c tiedosto="esimerkit/02-geneerinen.c" osa="makro"}
```

Käytössä ero näkyy tyyppitarkistuksessa. `void *` -versio hyväksyy
minkä tahansa osoittimen, ja virhe näkyy vasta ajon aikana vääränä
datana. Makroversiossa kääntäjä hylkää väärän tyypin:

```{.c tiedosto="esimerkit/02-geneerinen.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/02-geneerinen.odotettu"}
```

Makron hinta on luettavuus: virheilmoitukset viittaavat makron
laajennukseen, ja debuggeri näyttää yhden pitkän rivin. Käytännön
kirjastot valitsevat tarpeen mukaan. Kun nopeus ratkaisee ja tyyppejä
on vähän, makro; kun rakenne on suuri ja tyyppejä paljon, `void *`;
kun alkio kuuluu moneen rakenteeseen yhtä aikaa, tunkeileva rakenne.

## Invariantti

Jokaisella rakenteella on *invariantti*: ehto, joka on voimassa aina
julkisen operaation alussa ja lopussa. Lajitellun joukon invariantti on

- `koko <= kapasiteetti`,
- `alkiot` on tyhjä osoitin vain, jos `kapasiteetti` on 0, ja
- `alkiot[i] < alkiot[i + 1]` kaikilla `i < koko - 1`.

Invariantti kannattaa kirjoittaa funktioksi, joka palauttaa
totuusarvon. Testissä sitä kutsutaan jokaisen operaation jälkeen, ja
ensimmäinen rikkoutuminen osoittaa operaation, joka rikkoi rakenteen.
Kehitysversiossa sen voi lisäksi tarkistaa `assert`-makrolla julkisten
funktioiden lopussa. Seuraavissa luvuissa jokaiselle rakenteelle
kirjoitetaan tällainen funktio.

## Käytännössä

- **Yksi otsake, yksi toteutus.** Rajapinta tiedostossa `x.h`,
  toteutus tiedostossa `x.c`; kaikki apufunktiot ovat `static`.
- **Etuliite jokaiseen julkiseen nimeen.** C:ssä ei ole nimiavaruuksia,
  joten `joukko_lisaa` eikä `lisaa`. Sama etuliite tyypeissä ja
  luettelovakioissa (`JOUKKO_OK`).
- **Tuhoamisfunktio hyväksyy tyhjän osoittimen,** kuten `free`.
  Virhepolkujen siivous yksinkertaistuu.
- **Tila ennen muutosta.** Varaa muisti ensin ja muuta rakennetta vasta
  sitten. Näin muistin loppuminen ei jätä rakennetta puolivalmiiksi.
- **Geneerisyys on valinta.** `void *` ja alkion koko, kun yksi
  toteutus riittää kaikille; makro, kun kääntäjän pitää tarkistaa
  tyypit ja optimoida niiden mukaan.
- **Älä paljasta sisäisiä osoittimia.** Funktio, joka palauttaa
  osoittimen rakenteen sisälle, sitoo käyttäjän toteutukseen ja
  tuottaa roikkuvia osoittimia, kun rakenne kasvaa (luku 3).

## Itsearviointi

- Osaat kirjoittaa otsaketiedoston, jossa tietotyyppi on
  läpinäkymätön, ja selittää, mitä käyttäjä sen ansiosta ei voi tehdä.
- Osaat suunnitella virhekoodit niin, että muistin loppuminen jättää
  rakenteen ennalleen.
- Osaat kertoa rajapinnan kommentissa, kuka omistaa minkäkin muistin.
- Osaat muotoilla rakenteen invariantin ja kirjoittaa sille
  tarkistusfunktion.
- Osaat nimetä kolme tapaa tehdä C:n tietorakenteesta
  tyyppiriippumaton ja kertoa kunkin hinnan.
