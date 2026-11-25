# Johdanto {.runko-johdanto}

Selainsovelluksia tehdään sovelluskehyksillä, ja kehyksiä on paljon:
React, Vue, Angular ja Svelte ovat yleisimmät, ja joka vuosi ilmestyy
uusia. Tämä tutoriaali ei opeta yhtäkään niistä perusteellisesti. Se
opettaa lukemaan niitä kaikkia: mitä ongelmaa kehys ratkaisee, mitkä
harvat perusratkaisut kehysten takana ovat ja miksi kehykset näyttävät
erilaisilta, vaikka ne tekevät saman työn.

Menetelmä on vertailu. Sama pieni sovellus on rakennettu viidesti:
ilman kehystä, Reactilla, Vuella, Angularilla ja Sveltellä. Kaikki
viisi toteutusta läpäisevät **saman testisarjan**, joten erot ovat
rakenteessa eivätkä käyttäytymisessä. Kun toteutukset luetaan rinnakkain,
kehyksen oma sanasto asettuu yhteisten käsitteiden päälle.

Esitietona on taito *Web-sovellukset*: DOM, tila, komponentit, lomakkeet,
efektit ja testaus on käyty siellä läpi Reactilla, eikä niitä toisteta.
TypeScript ja HTML oletetaan samoin.

## Kirjasto vai kehys

**Kirjastoa** sovellus kutsuu silloin kun haluaa. **Kehys** kutsuu
sovellusta: se omistaa ohjelman rungon ja päättää, milloin sovelluksen
koodi ajetaan. Rajaa ei kannata vetää tiukasti. React kutsuu itseään
kirjastoksi, koska se hoitaa vain näkymän ja jättää reitityksen ja
datan haun muille. Angular on kehys sanan täydessä merkityksessä:
reititin, lomakkeet, HTTP-asiakas, testaus ja komentorivityökalu
tulevat samasta paikasta. Vue ja Svelte ovat näiden välissä.

Tässä tutoriaalissa *kehys* tarkoittaa kaikkia neljää, koska
ydinongelma on niille yhteinen: komponentti kutsutaan kehyksen ehdoilla
ja kehys pitää näkymän ajan tasalla.

## Lyhyt historia

Kehysten erot ymmärtää helpoimmin siitä, mihin kukin aikanaan vastasi.

| Vuosi | Tulokas | Mitä se toi |
|-------|---------|-------------|
| 2006 | jQuery | yhtenäinen ja mukava rajapinta DOM:n muokkaamiseen |
| 2010 | AngularJS, Backbone | sovelluksen rakenne: malli, näkymä ja mallipohjat |
| 2013 | React | näkymä tilan funktiona, komponentit, virtuaalinen DOM |
| 2014 | Vue | reaktiivinen tila ja mallipohjat keveämmin |
| 2016 | Angular (2) | uudelleenkirjoitus: TypeScript, komponentit, käännetyt mallipohjat |
| 2016 | Svelte | kehys kääntäjänä: työ tehdään ennen selainta |
| 2019 | Reactin hookit | tila ja efektit funktioihin luokkien sijaan |
| 2020 | Vue 3 | Composition API ja Proxy-pohjainen reaktiivisuus |
| 2023 | Angularin signaalit | hienojakoinen reaktiivisuus muutostentunnistuksen tilalle |
| 2024 | Svelte 5 | riimut: reaktiivisuus näkyväksi osaksi kieltä |

Taulukosta näkyy kaksi asiaa. Ensinnäkin jQuery ei kadonnut siksi,
että se olisi ollut huono, vaan siksi, että ongelma vaihtui: DOM:n
muokkaaminen ei ollut enää vaikeaa, mutta sen pitäminen sovelluksen
tilan tasalla oli (luku 2). Toiseksi kehykset lähestyvät toisiaan.
Kaikki neljä rakentuvat nykyään komponenteista, ja kolme niistä on
siirtynyt signaaleihin tai niiden kaltaiseen reaktiivisuuteen.

## Mikä pysyy ja mikä muuttuu

Kehysten rajapinnat vanhenevat nopeasti. Tämän tutoriaalin esimerkit on
kirjoitettu loppuvuoden 2026 versioilla, ja muutaman vuoden päästä osa
niiden syntaksista on vanhentunut. Siksi teksti erottaa kaksi tasoa:

- **Pysyvät periaatteet.** Näkymä on tilan funktio. Tieto kulkee
  alaspäin ja tapahtumat ylöspäin. Johdettua tietoa ei tallenneta.
  Kehyksen on jotenkin saatava tietää, mikä muuttui, ja tapoja on
  kourallinen (luku 3). Näistä on puhuttu samoin sanoin yli kymmenen
  vuotta.
- **Tämän hetken yksityiskohdat.** Funktioiden ja direktiivien nimet,
  kuten `useState`, `ref`, `signal` ja `$state`, tiedostojen rakenne ja
  rakennustyökalut. Ne katsotaan kehyksen omasta dokumentaatiosta silloin
  kun niitä tarvitaan.

Kun tekstissä on versiosta riippuva yksityiskohta, se sanotaan. Kehysten
viralliset dokumentaatiot on lueteltu viimeisessä luvussa.

## Esimerkkisovellus

Sovellus on tehtävälista. Se on tarkoituksella pieni, mutta jokainen sen
ominaisuus on valittu paljastamaan jokin kehysten ero.

![Tehtävälista: lomake virheilmoituksineen, suodatin ja lista. Kaikki
viisi toteutusta näyttävät tältä.](kuvat/sovellus.png){width=72%}

| Ominaisuus | Mitä se paljastaa | Luku |
|------------|-------------------|------|
| rivi omana komponenttinaan | komponentin rajapinta: tieto alas, tapahtumat ylös | 5 |
| suodatinvalinta | kaksisuuntainen sidos vanhemman ja lapsen välillä | 5 |
| suodatettu lista ja laskurit | johdettu tila | 6 |
| lista, josta poistetaan rivejä | avaimet ja DOM-solmujen säilyminen | 6 |
| lomake ja validointi | lomakekenttien sidonta | 6 |
| tallennus selaimeen, sivun otsikko | sivuvaikutukset | 6 |
| yhteenveto ylätunnisteessa | jaettu tila ilman propsien kuljettamista | 7 |
| alkutilan lataus palvelimelta | asynkroninen tila: lataus, virhe, valmis | 7 |

Sovelluksen säännöt eli tehtävien lisääminen, suodatus, validointi ja
tallennus ovat yhdessä moduulissa, joka ei tunne yhtäkään kehystä.
Kaikki viisi toteutusta käyttävät sitä. Ratkaisu on sekä käytännöllinen
(vertailussa näkyy vain kehyksen osuus) että itsessään opetus, johon
palataan luvussa 10: mitä vähemmän koodia on sidottu kehykseen, sitä
halvempaa kehyksen vaihtaminen on.

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.ts" osa="tyypit"}
```

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.ts" osa="muutokset"}
```

Muutosfunktiot palauttavat aina uuden taulukon. Syy selviää luvussa 3:
osa kehyksistä huomaa muutoksen vertaamalla viittauksia, osa
seuraamalla sijoituksia, ja uusi taulukko kelpaa molemmille.

## Työkalut ja versiot

| Työkalu | Versio | Tehtävä |
|---------|--------|---------|
| Node.js | 24 LTS (tai 22) | rakennustyökalujen ja testien ajoympäristö |
| TypeScript | 6.0 | tyyppitarkistus; versio on Angularin sallima |
| Vite | 8.3 | Reactin, Vuen ja Svelten käännös |
| React | 19.3 | kirjasto: JSX ja virtuaalinen DOM |
| Vue | 3.5 | mallipohjat, reaktiiviset viittaukset |
| Angular | 22 | kehys omine työkaluineen, signaalit |
| Svelte | 5 | kääntäjä, riimut |
| Playwright | 1.63 | yhteinen testisarja oikeassa selaimessa |

TypeScriptin versio on esimerkki riippuvuuksien ketjusta: Angularin
kääntäjä hyväksyy vain tietyn TypeScript-version, joten koko projekti
käyttää sitä. Muut taidot tässä tutoriaalisarjassa käyttävät uudempaa.

Kaikki toteutukset ovat yhdessä npm-projektissa, jolla on yksi
lukitustiedosto ja yksi `node_modules`:

```text
esimerkit/
  yhteinen/      logiikka.ts, sen testit, tyyli.css ja palvelimen data
  paljas/        toteutus ilman kehystä
  react/ vue/ angular/ svelte/     sama sovellus neljästi
  periaatteet/   renderöintimallit muutamalla kymmenellä rivillä
  e2e/           yksi Playwright-testisarja kaikille toteutuksille
  tyokalut/      mittaukset: koot, rivimäärät ja riippuvuudet
  tulokset/      tekstissä näytetyt mittaustulokset
```

Esimerkit ajetaan komennolla `make` hakemistossa `esimerkit`. Se
asentaa riippuvuudet lukitustiedoston mukaan, tarkistaa tyypit, kääntää
kaikki viisi toteutusta ja ajaa testisarjan jokaista vasten. Yksittäisen
toteutuksen kehityspalvelin käynnistyy komennolla
`npx vite --config vue/vite.config.ts` (Angularilla `npx ng serve`).
