# Reititys ja selaimen tallennus

Monisivuisessa sovelluksessa jokainen näkymä on oma osoitteensa, ja
selain hoitaa historian, kirjanmerkit ja Takaisin-painikkeen. SPA:n on
toteutettava sama itse, tai käyttäjä menettää ne. Osoite on sovelluksen
tilaa: se, mitä käyttäjä voi jakaa, tallentaa ja palata katsomaan,
kuuluu URL:iin.

## History API

Selaimen History API muuttaa osoitetta lataamatta sivua:
`history.pushState` lisää historiaan uuden kohdan, `replaceState`
korvaa nykyisen, ja Takaisin- ja Eteenpäin-painikkeet laukaisevat
`popstate`-tapahtuman. Reititin on näiden päälle rakennettu tilaus:

```{.typescript tiedosto="esimerkit/src/08-reititys/reititin.tsx" osa="sijainti"}
```

Sijainti luetaan `useSyncExternalStore`-hookilla kuten luvussa 6, koska
URL on Reactin ulkopuolista tilaa. `pushState` ei laukaise tapahtumaa,
joten `siirry` lähettää oman.

## Linkit

Linkki on edelleen `<a href>`, ei klikattava `div` tai painike. Silloin
osoite näkyy tilarivillä, linkin voi avata uuteen välilehteen ja
kopioida, ja ruudunlukija esittää sen linkkinä. Reititin vain sieppaa
tavallisen klikkauksen:

```{.typescript tiedosto="esimerkit/src/08-reititys/reititin.tsx" osa="linkki"}
```

```{.dot otsikko="Reitityksen kierros. Linkki ja selaimen Takaisin-painike päätyvät samaan paikkaan: osoite muuttuu, ja näkymä valitaan osoitteesta."}
digraph {
  rankdir=LR; ranksep=0.3; nodesep=0.25;
  l [label="<Linkki>", shape=ellipse];
  b [label="Takaisin,\nEteenpäin", shape=ellipse];
  h [label="History API:\npushState,\npopstate"];
  s [label="useSijainti:\npathname", style="filled,bold",
     fillcolor="#E6EDF7"];
  n [label="sovita:\nreitti → näkymä"];
  f [label="Sivu:\notsikko, fokus"];
  l -> h; b -> h; h -> s -> n -> f;
}
```

Reitit sovitetaan malleihin. Parametrit puretaan URL-koodauksesta,
koska tunnisteessa voi olla mitä tahansa merkkejä:

```{.typescript tiedosto="esimerkit/src/08-reititys/reititin.tsx" osa="sovita"}
```

## URL tilana

Haku- ja suodatintila kuuluu hakuparametreihin. Silloin sivun päivitys
ei hävitä hakua, ja linkin voi lähettää kollegalle. Jokainen näppäily
korvaa historian kohdan, jotta Takaisin-painike ei käy läpi jokaista
kirjainta:

```{.typescript tiedosto="esimerkit/src/08-reititys/reititin.tsx" osa="hakuparametri"}
```

```{.typescript tiedosto="esimerkit/src/08-reititys/reititin.test.tsx" osa="testi"}
```

## Sivu ja fokus

Kun monisivuinen sovellus lataa uuden sivun, ruudunlukija ilmoittaa
sivun nimen ja aloittaa sen alusta. SPA:ssa mitään tällaista ei
tapahdu: fokus jää painikkeeseen, jota ei enää ole, ja näkövammainen
käyttäjä ei tiedä, että näkymä vaihtui. Jokaisen reitin näkymä asettaa
siksi dokumentin nimen ja siirtää fokuksen pääotsikkoon:

```{.typescript tiedosto="esimerkit/src/sovellus/Sivu.tsx" osa="sivu"}
```

`tabIndex={-1}` tekee otsikosta ohjelmallisesti fokusoitavan, mutta ei
lisää sitä sarkainjärjestykseen. Päästä päähän -testi tarkistaa
fokuksen ja nimen (luku 9).

![Reitti `/tilat/kivi` heti siirtymän jälkeen: fokus on
pääotsikossa (kehys), ja dokumentin nimi on "Kivi –
Tilavaraus".](kuvat/08-tila.png){width=45%}

## Saavutettavuus sovelluksessa

Taito *HTML ja CSS* käsittelee staattisen sivun saavutettavuuden.
Sovellus lisää siihen muuttuvan sisällön, ja sen ongelmat ovat
omanlaisiaan. Reitin vaihtuminen on niistä ensimmäinen; tässä ovat
kootusti muut, joita edelliset luvut ovat sivunneet:

- **Dynaaminen sisältö** ilmoitetaan elävillä alueilla.
  `aria-live="polite"` lukee muutoksen, kun ruudunlukija vapautuu
  (osumien määrä luvussa 4), `role="alert"` heti (virheet luvuissa 5
  ja 7). Alueen on oltava DOM:ssa ennen kuin sen sisältö muuttuu.
- **Fokuksen hallinta.** Kun elementti, jossa fokus oli, poistuu
  (poistettu rivi, suljettu dialogi), fokus siirretään järkevään
  paikkaan. Modaali dialogi käyttää `<dialog>`-elementtiä ja
  `showModal`-metodia, jotka hoitavat fokuksen ja Escape-näppäimen.
- **Lataus- ja odotustilat** kerrotaan tekstinä (`role="status"`), ei
  pelkällä pyörivällä kuvakkeella.
- **Omat komponentit** (valikko, välilehdet, yhdistelmäruutu) noudattavat
  ARIA Authoring Practices -mallien näppäimistökäyttöä, tai käytetään
  valmista saavutettavaa kirjastoa (React Aria, Radix).

## Valmis sovellus

Sovellus kokoaa luvut yhteen: reititin valitsee näkymän, näkymät
hakevat datan `useHaku`-hookilla, ja lataus, virhe ja valmis data
esitetään yhdellä tavalla. Näkymän ympärillä on luvun 7 virheraja:

```{.typescript tiedosto="esimerkit/src/sovellus/Sovellus.tsx" osa="sovellus"}
```

```{.typescript tiedosto="esimerkit/src/sovellus/Sovellus.tsx" osa="sivut"}
```

`TilaSivu` saa propsiksi `key={tila.id}`. Kun tila vaihtuu, React luo
uuden komponentin, ja lomakkeen tila nollautuu ilman efektiä.
API-asiakas tulee propsina, joten testit ja sovellus käyttävät samaa
koodia eri asiakkailla (riippuvuuksien injektointi):

```{.typescript tiedosto="esimerkit/src/sovellus/main.tsx" osa="main"}
```

Ulkoasu on yhdessä tyylitiedostossa (`src/sovellus/tyyli.css`), joka
on tehty taidon *HTML ja CSS* keinoin: mukautetut ominaisuudet,
luontainen korttiruudukko ja näkyvä fokus. Se linkitetään
`index.html`-tiedostosta eikä kirjoiteta `style`-attribuutteihin,
jolloin luvun 10 tiukka sisällön suojauskäytäntö sallii sen.

Palvelimen on palautettava `index.html` kaikkiin sovelluksen
osoitteisiin (`/tilat/kivi`), koska käyttäjä voi avata minkä tahansa
niistä suoraan. Vite tekee tämän kehityksessä ja esikatselussa;
tuotannon palvelimelle se asetetaan erikseen (*SPA fallback*).

## Selaimen tallennus

| Tallennus | Elinikä | Koko | Rajapinta | Käyttö |
|-----------|---------|------|-----------|--------|
| URL | jaettava | ~2 000 merkkiä käytännössä | `URL`, History | haku, suodattimet, valittu kohde |
| `sessionStorage` | välilehti | ~5 Mt | synkroninen | keskeneräinen lomake |
| `localStorage` | pysyvä | ~5 Mt | synkroninen | asetukset, teema |
| IndexedDB | pysyvä | satoja Mt | asynkroninen | offline-data, välimuisti |
| eväste | palvelimen asettama | 4 kt | lähetetään pyynnöissä | istunto (`HttpOnly`) |

`localStorage` on synkroninen ja estää pääsäikeen, joten sinne ei
tallenneta suurta dataa. IndexedDB:n rajapinta on hankala; käytännössä
käytetään ohutta kääreitä (esim. `idb`). Mikään selaimen tallennus ei
ole salainen: kaikki on luettavissa samalta alkuperältä ajetulla
skriptillä (luku 10).

Sovelluksen omat tiedostot (HTML, JavaScript, CSS) voi tallentaa
selaimeen **Service Workerilla**: se on taustalla ajettava skripti,
joka sieppaa sivun verkkopyynnöt ja voi vastata niihin välimuistista
(Cache API). Näin sovellus käynnistyy ilman verkkoa, ja siitä voi
tehdä asennettavan (PWA). Hinta on välimuistin hallinta: väärin
tehtynä käyttäjät jäävät vanhaan versioon. Siksi Service Worker
otetaan käyttöön vasta, kun yhteydetön käyttö on todellinen vaatimus,
ja silloin työkalulla (Workbox, `vite-plugin-pwa`) eikä käsin.

## Käytännössä

- **Jaettava tila URL:iin.** Jos käyttäjä haluaa jakaa näkymän tai
  palata siihen, sen tila kuuluu polkuun tai hakuparametreihin.
- **Linkit ovat linkkejä.** Siirtymä `<a href>`-elementillä,
  toiminto `<button>`-elementillä. Ohjelmallinen siirtymä (`siirry`)
  toiminnon jälkeen, kuten varauksen tallennuksen jälkeen.
- **Fokus ja otsikko joka reitillä.** Ilman niitä SPA on
  ruudunlukijalle rikki.
- **Saavutettavuus on osa jokaista muutosta,** ei erillinen vaihe:
  roolihaut testeissä, fokus reiteissä ja elävät alueet muutoksille.
- **Reitityskirjasto tuotannossa.** React Router ja TanStack Router
  hoitavat sisäkkäiset reitit, datan haun reitin yhteydessä,
  vierityksen palautuksen ja tyypitetyt parametrit.
- **Tallennettu data on epäluotettavaa ja versioitua.** Jäsennä lukiessa
  ja lisää avaimeen versio (`asetukset:v2`), kun muoto muuttuu.

## Itsearviointi

- Osaat selittää, miten SPA-reititys käyttää History API:a, ja
  toteuttaa linkin, joka kunnioittaa selaimen omaa käytöstä.
- Osaat pitää haun ja suodattimet URL:ssa niin, että historia ei täyty.
- Osaat hoitaa fokuksen ja dokumentin nimen reitin vaihtuessa sekä
  ilmoittaa muuttuvan sisällön ja odotustilat ruudunlukijalle.
- Osaat valita oikean tallennuspaikan URL:n, `sessionStorage`n,
  `localStorage`n ja IndexedDB:n väliltä.
