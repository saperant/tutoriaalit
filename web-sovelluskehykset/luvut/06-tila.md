# Tila ja lomakkeet

Komponentin sisällä on kolmenlaista tietoa: **tila**, joka muuttuu
käyttäjän toimista, **johdettu tieto**, joka lasketaan tilasta, ja
viittaukset DOM-elementteihin niitä harvoja tilanteita varten, joissa
elementtiä on käskettävä suoraan. Kaikissa neljässä kehyksessä nämä
kolme ovat olemassa. Ero on siinä, miten ne kirjoitetaan, ja yhdessä
perustavassa asiassa: ajetaanko komponentin koodi kerran vai joka
päivityksellä.

## Sama sanasto neljästi

| Käsite | React | Vue | Angular | Svelte |
|-------|-------|-------|-------|-------|
| tila | `useState` | `ref` | `signal` | `$state` |
| lukeminen | `x` | `x.value` | `x()` | `x` |
| kirjoitus | `setX(uusi)` | `x.value = uusi` | `x.set(uusi)` | `x = uusi` |
| johdettu tieto | lauseke, `useMemo` | `computed` | `computed` | `$derived` |
| efekti | `useEffect` | `watchEffect` | `effect` | `$effect` |
| viittaus elementtiin | `useRef` | `useTemplateRef` | `viewChild` | `bind:this` |

Nimet ovat tämän hetken yksityiskohtia, rivit pysyviä käsitteitä.
Kolme oikeanpuoleista saraketta ovat luvun 3 signaaleja eri
kirjoitusasuissa: Vue näyttää kääreen (`.value`), Angular tekee
lukemisesta funktiokutsun, ja Svelten kääntäjä piilottaa kääreen
kokonaan. Vuen mallipohjassa `.value` jätetään pois, koska kääntäjä
lisää sen.

Päänäkymän tila on jo nähty Reactilla, Vuella ja Angularilla luvussa
4. Tässä sama Sveltellä:

```{.html tiedosto="esimerkit/svelte/src/Sovellus.svelte" osa="skripti"}
```

Suodatin on **paikallista tilaa**: se kuuluu vain tälle näkymälle, eikä
sitä tallenneta. Näkyvien tehtävien lista on **johdettua tietoa**: se
lasketaan tehtävistä ja suodattimesta jaetun moduulin `suodata`-
funktiolla.

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.ts" osa="johdetut"}
```

Sääntö, joka pätee kaikissa kehyksissä: **johdettua tietoa ei
tallenneta tilaan**. Jos näkyvät tehtävät olisivat oma tilansa, ne
pitäisi muistaa päivittää aina, kun tehtävät tai suodatin muuttuvat,
ja se on luvun 2 unohtuneen päivityksen virhe uudessa paikassa.

## Kerran vai joka kerta

Suurin käsitteellinen ero Reactin ja kolmen muun välillä ei näy
taulukosta.

**Reactissa komponenttifunktio ajetaan uudelleen jokaisella
päivityksellä.** `Sovellus`-funktion jokainen rivi suoritetaan aina,
kun sen tila muuttuu. Siksi johdettu tieto on tavallinen lauseke:
`const nakyvat = suodata(…)` lasketaan joka kerralla uudelleen, ja se
on aina ajan tasalla. Tila säilyy ajojen välillä vain, koska
`useState` hakee sen Reactin muistista. Tästä seuraavat hookien
säännöt (aina samassa järjestyksessä, ei ehtolauseiden sisällä) ja
se, että käsittelijä näkee sen ajokerran arvot, jolla se luotiin.

**Vuessa, Angularissa ja Sveltessä komponentin koodi ajetaan kerran.**
`<script setup>`, luokan muodostin ja Svelten `<script>` suoritetaan,
kun komponentti luodaan. Sen jälkeen päivittyvät vain reaktiiviset
arvot ja niitä lukevat sidokset. Siksi johdettu tieto on merkittävä
erikseen: tavallinen `const nakyvat = suodata(…)` laskettaisiin yhden
kerran eikä päivittyisi koskaan. `computed` ja `$derived` kertovat
kehykselle, että lauseke on laskettava uudelleen, kun sen lukemat
arvot muuttuvat.

| Asia | Koodi ajetaan joka kerta (React) | Koodi ajetaan kerran (muut) |
|-------|---------------|---------------|
| johdettu tieto | tavallinen lauseke | merkittävä: `computed`, `$derived` |
| tyypillinen virhe | vanhentunut arvo sulkeumassa, puuttuva riippuvuus | reaktiivisuus katoaa, kun arvo kopioidaan tavalliseen muuttujaan |
| raskas laskenta | ajetaan turhaan, ellei muistiin panna | ajetaan vain riippuvuuden muuttuessa |
| ajattelutapa | "mitä näytetään tällä tilalla" | "mikä riippuu mistä" |

Kumpikaan ei ole parempi. Reactin malli on yksinkertaisempi selittää ja
vaikeampi tehdä tehokkaaksi. Signaalien malli on tehokas oletuksena,
mutta siinä on pidettävä mielessä, mikä arvo on reaktiivinen ja mikä
tavallinen kopio.

## Lomake

Lisäyslomakkeessa on kolme paikallista tilaa (nimi, kiireellisyys ja
tieto siitä, onko lähetystä yritetty), yksi johdettu arvo (virheteksti)
ja viittaus kenttään kohdistuksen palauttamista varten. Validointisääntö
on jaetussa moduulissa:

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.ts" osa="validointi"}
```

Reactissa kenttä on **ohjattu**: sen arvo tulee tilasta, ja jokainen
näppäily vie uuden arvon tilaan.

```{.typescript tiedosto="esimerkit/react/src/Lisayslomake.tsx" osa="lomake"}
```

Vuessa `v-model` sitoo kentän ja tilan kumpaankin suuntaan, ja
`@submit.prevent` estää oletuslähetyksen:

```{.html tiedosto="esimerkit/vue/src/Lisayslomake.vue" osa="skripti"}
```

```{.html tiedosto="esimerkit/vue/src/Lisayslomake.vue" osa="pohja"}
```

Angularissa sidos on `[(ngModel)]`, ja se tulee kehyksen omasta
lomakemoduulista:

```{.typescript tiedosto="esimerkit/angular/src/app/lisayslomake.ts" osa="luokka"}
```

```{.html tiedosto="esimerkit/angular/src/app/lisayslomake.html"}
```

Sveltessä tila on tavallisen näköisiä muuttujia ja sidos on
`bind:value`:

```{.html tiedosto="esimerkit/svelte/src/Lisayslomake.svelte" osa="skripti"}
```

```{.html tiedosto="esimerkit/svelte/src/Lisayslomake.svelte" osa="pohja"}
```

Neljä toteutusta ovat rivi riviltä samat. Lähetysfunktio validoi,
lisää tai merkitsee yrityksen, ja palauttaa kohdistuksen kenttään.
Erot ovat siinä, mikä jää näkyviin:

- Reactissa jokainen kentän ja tilan välinen liike on kirjoitettu:
  `value={nimi}` ja `onChange`. Muissa sama on yksi sidos.
- Angular lisää lomakkeeseen omaa koneistoaan. `FormsModule` tuo
  mukanaan `ngSubmit`-tapahtuman ja pitää kirjaa kenttien tilasta
  (koskettu, muutettu, kelvollinen). Tässä siitä käytetään vain sidos.
  Suuremmissa lomakkeissa käytetään saman moduulin reaktiivisia
  lomakkeita, joissa kentät ja validointisäännöt kuvataan koodissa.
- Kohdistuksen palautus vaatii joka kehyksessä viittauksen oikeaan
  DOM-elementtiin. Tämä on se kohta, jossa "näkymä on tilan funktio"
  ei riitä: kohdistus on käsky, ei tila.

## Listat ja avaimet

Luvussa 3 nähtiin, mitä avaimen puuttuminen aiheuttaa. Jokaisessa
toteutuksessa listan rivi tunnistetaan tehtävän `id`-kentästä:
`key={t.id}`, `:key="t.id"`, `track t.id` ja `(t.id)`. Angular vaatii
`track`-lausekkeen aina, eikä mallipohja käänny ilman sitä. Muissa
kehyksissä avaimen unohtaminen on varoitus tai hiljainen virhe.

Avaimeksi ei kelpaa taulukon järjestysnumero. Se on sama asia kuin
avaimen puuttuminen: kun ensimmäinen rivi poistetaan, toinen rivi saa
numeron nolla ja perii ensimmäisen rivin elementin. Yhteinen testisarja
merkitsee yhden rivin DOM-solmun, poistaa toisen rivin ja tarkistaa,
että merkki on yhä oikealla rivillä (luku 8).

## Käytännössä

- **Aloita kysymällä, mikä on tilaa.** Tilaa on vain se, mitä ei voi
  laskea muusta. Tässä sovelluksessa tehtävät, suodatin ja lomakkeen
  kentät ovat tilaa. Näkyvät tehtävät, laskurit, virheteksti ja
  painikkeen `disabled` ovat johdettuja.
- **Pidä tila niin lähellä käyttöä kuin voi.** Lomakkeen kentät
  kuuluvat lomakkeelle. Tila nostetaan ylemmäs tai jaetuksi vasta, kun
  toinen komponentti tarvitsee sitä.
- **Signaalikehyksessä älä pura reaktiivista arvoa tavalliseen
  muuttujaan.** `const n = laskuri.value` on luku, ei viittaus, eikä se
  päivity. Sama koskee signaalin arvon lukemista muodostimessa.
- **Reactissa älä pane johdettua tietoa tilaan efektillä.**
  `useEffect`, joka kutsuu `setNakyvat`, on tavallisin tapa rikkoa
  johdetun tiedon sääntö. Lauseke riittää.
- **Näytä virhe vasta, kun siitä on hyötyä.** Kaikki toteutukset
  näyttävät virheen ensimmäisen lähetysyrityksen jälkeen ja päivittävät
  sitä sen jälkeen näppäily kerrallaan. Sääntö on käyttöliittymän, ei
  kehyksen, ja siksi se on helppo toteuttaa samoin kaikissa.
- **Validoi sama asia myös palvelimella.** Selaimen validointi on
  käyttömukavuutta (taito *Web-sovellusten
  tietoturva*).

## Itsearviointi

- Osaat nimetä tilan, johdetun tiedon, efektin ja elementtiviittauksen
  välineet neljässä kehyksessä.
- Osaat selittää, miksi Reactissa johdettu tieto on tavallinen lauseke
  mutta muissa se on merkittävä erikseen.
- Osaat erottaa annetusta näkymästä tilan ja johdetun tiedon.
- Osaat kirjoittaa lomakekentän sidonnan sekä auki kirjoitettuna
  (arvo ja muutostapahtuma) että kaksisuuntaisena sidoksena.
- Osaat perustella, miksi listan avain on tiedon tunniste eikä
  järjestysnumero.
