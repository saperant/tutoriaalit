# Efektit ja omat hookit

Komponentin pitää olla puhdas, mutta sovelluksen on kuitenkin
käynnistettävä ajastimia, tilattava tapahtumia ja haettava dataa.
**Efekti** (`useEffect`) on Reactin paikka sivuvaikutuksille, jotka
*synkronoivat* komponentin ulkoisen järjestelmän kanssa: selaimen
rajapinnan, verkkoyhteyden tai kolmannen osapuolen kirjaston.

## Efektin elinkaari

Efekti ajetaan kiinnityksen jälkeen. Jos se palauttaa funktion, React
kutsuu sitä ennen seuraavaa ajoa ja komponentin poistuessa. Tämä
**siivous** on efektin tärkein osa: jokainen tilaus perutaan, jokainen
ajastin pysäytetään. Riippuvuuslista kertoo, minkä arvojen muuttuessa
efekti ajetaan uudelleen.

```{.typescript tiedosto="esimerkit/src/06-efektit/useViivastetty.ts" osa="viivastetty"}
```

`useViivastetty` on **oma hook**: tavallinen funktio, jonka nimi alkaa
`use` ja joka kutsuu muita hookeja. Se paketoi uudelleenkäytettävän
käyttäytymisen, tässä *debouncen*: hakukenttä voi lähettää pyynnön vasta,
kun käyttäjä on lopettanut kirjoittamisen. Jokainen uusi arvo ajaa
efektin, jonka siivous peruu edellisen ajastimen.

Hookeilla on kaksi sääntöä: niitä kutsutaan vain komponentin tai toisen
hookin ylätasolla, eikä koskaan ehtolauseessa tai silmukassa. React
tunnistaa hookit kutsujärjestyksestä.

Kutsujärjestyksen sääntö ja käsin kirjoitettu riippuvuuslista ovat
Reactin toteutuksen piirteitä: signaaleihin perustuvat kehykset
keräävät riippuvuudet itse, kuten luvun 3 `efekti`. Yleistä on sen
sijaan se, mitä efektillä tehdään. Jokaisessa kehyksessä
sivuvaikutus sidotaan komponentin elinkaareen, ajetaan uudelleen
riippuvuuksien muuttuessa ja siivotaan, kun komponentti poistuu.

## Vanhentunut sulkeuma

Efektin funktio on sulkeuma, joka näkee sen renderöinnin arvot, jossa se
luotiin. Jos efektiä ei ajeta uudelleen arvon muuttuessa, se näkee
vanhan arvon:

```{.typescript tiedosto="esimerkit/src/06-efektit/Laskuri.tsx" osa="sulkeuma"}
```

Testi siirtää näennäiskelloa kolme sekuntia. Vanha versio näyttää yhä
"1 s", koska ajastin laskee joka kerta `0 + 1`. Ratkaisu on
päivitysfunktio `setSekunnit((s) => s + 1)`, joka saa aina tuoreen
arvon. Toinen ratkaisu olisi lisätä `sekunnit` riippuvuuksiin, jolloin
ajastin luotaisiin joka sekunti uudelleen.

```{.typescript tiedosto="esimerkit/src/06-efektit/efektit.test.tsx" osa="testi"}
```

Valeajastimet (`vi.useFakeTimers`) tekevät ajasta testin hallitseman:
kolmen sekunnin testi kestää millisekunteja, ja tulos on toistettava.
`act` kertoo Reactille, että sen sisällä tapahtuvat päivitykset
käsitellään ennen tarkistuksia.

## Ulkoinen tila: useSyncExternalStore

Kun tila on Reactin ulkopuolella, kuten `localStorage`, URL tai
WebSocket-yhteys, sitä ei kopioida efektillä `useState`-muuttujaan.
`useSyncExternalStore` tilaa ulkoisen lähteen ja lukee siitä
tilannekuvan joka renderöinnissä. Näin näkymä ei koskaan näytä
ristiriitaisia arvoja.

```{.typescript tiedosto="esimerkit/src/06-efektit/useTallennettu.ts" osa="tallennettu"}
```

Tilannekuvan pitää olla sama arvo, jos lähde ei ole muuttunut. Siksi
hook palauttaa merkkijonon eikä jäsennettyä oliota, joka olisi joka
kerta uusi. Tallennettu data on epäluotettavaa: sovelluksen vanha
versio on voinut tallentaa toisen muotoisen arvon, tai käyttäjä on
muokannut sitä. Siksi se jäsennetään, ja kelvoton arvo korvataan
oletuksella.

## Et ehkä tarvitse efektiä

Efektejä käytetään usein väärin. Nämä tapaukset eivät tarvitse efektiä:

| Tarve | Väärin | Oikein |
|-------|--------|--------|
| johdettu arvo | efekti asettaa toisen tilan | lasketaan renderöinnissä |
| raskas johdettu arvo | efekti ja tila | `useMemo` |
| käyttäjän toiminnon seuraus | efekti reagoi tilan muutokseen | tapahtumankäsittelijä |
| tilan nollaus propsin vaihtuessa | efekti nollaa tilan | `key`-propsi komponentille |
| datan haku | `useEffect` + `fetch` ilman peruutusta | peruutettava haku (luku 7) tai kirjasto |

Nyrkkisääntö: efekti on oikea työkalu, kun komponentin pitää pysyä
synkronissa jonkin Reactin ulkopuolisen kanssa niin kauan kuin se on
näkyvissä. Kaikki muu on joko renderöintiä tai tapahtumankäsittelyä.

## Käytännössä

- **Jokaisella tilauksella on siivous.** Ajastin, kuuntelija,
  WebSocket, `IntersectionObserver`: efekti palauttaa niiden
  lopetuksen. `StrictMode` ajaa efektin kehitystilassa kahdesti
  (ajo–siivous–ajo), mikä paljastaa puuttuvan siivouksen heti.
- **Riippuvuuslista on rehellinen.** Kaikki efektissä käytetyt
  propsit, tilat ja funktiot kuuluvat listaan; ESLintin sääntö
  `react-hooks/exhaustive-deps` tarkistaa sen. Jos lista on hankala,
  efekti tekee liikaa tai funktio pitää siirtää efektin sisään.
- **Olio riippuvuutena ajaa efektin joka kerta.** `{ a: 1 } !==
  { a: 1 }`. Riippuvuuksiksi primitiiviarvot, tai olio vakautetaan
  `useMemo`-hookilla.
- **Päivitysfunktio sulkeumissa.** Ajastimissa, tilauksissa ja
  peräkkäisissä päivityksissä `setX((x) => …)`.
- **Omat hookit kertovat aikomuksen.** `useViivastetty(haku, 300)` on
  luettavampi kuin efekti ja kaksi tilaa komponentissa. Hookia
  testataan `renderHook`-funktiolla.
- **`useRef` arvoille, jotka eivät vaikuta näkymään,** kuten DOM-
  elementti, edellinen arvo tai ajastimen tunniste. Refin muutos ei
  renderöi.

## Itsearviointi

- Osaat kirjoittaa efektin, jolla on oikea siivous ja riippuvuuslista.
- Osaat tunnistaa vanhentuneen sulkeuman ja korjata sen
  päivitysfunktiolla.
- Osaat kirjoittaa ja testata oman hookin valeajastimilla.
- Osaat käyttää `useSyncExternalStore`-hookia ulkoisen tilan
  lukemiseen ja jäsentää tallennetun datan.
- Osaat tunnistaa tapaukset, joissa efekti on väärä työkalu.
