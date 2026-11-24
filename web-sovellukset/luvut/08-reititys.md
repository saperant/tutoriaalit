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

## Valmis sovellus

Sovellus kokoaa luvut yhteen: reititin valitsee näkymän, näkymät
hakevat datan `useHaku`-hookilla, ja lataus, virhe ja valmis data
esitetään yhdellä tavalla:

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

## Käytännössä

- **Jaettava tila URL:iin.** Jos käyttäjä haluaa jakaa näkymän tai
  palata siihen, sen tila kuuluu polkuun tai hakuparametreihin.
- **Linkit ovat linkkejä.** Siirtymä `<a href>`-elementillä,
  toiminto `<button>`-elementillä. Ohjelmallinen siirtymä (`siirry`)
  toiminnon jälkeen, kuten varauksen tallennuksen jälkeen.
- **Fokus ja otsikko joka reitillä.** Ilman niitä SPA on
  ruudunlukijalle rikki.
- **Reitityskirjasto tuotannossa.** React Router ja TanStack Router
  hoitavat sisäkkäiset reitit, datan haun reitin yhteydessä,
  vierityksen palautuksen ja tyypitetyt parametrit.
- **Tallennettu data on epäluotettavaa ja versioitua.** Jäsennä lukiessa
  ja lisää avaimeen versio (`asetukset:v2`), kun muoto muuttuu.

## Itsearviointi

- Osaat selittää, miten SPA-reititys käyttää History API:a, ja
  toteuttaa linkin, joka kunnioittaa selaimen omaa käytöstä.
- Osaat pitää haun ja suodattimet URL:ssa niin, että historia ei täyty.
- Osaat hoitaa fokuksen ja dokumentin nimen reitin vaihtuessa.
- Osaat valita oikean tallennuspaikan URL:n, `sessionStorage`n,
  `localStorage`n ja IndexedDB:n väliltä.
