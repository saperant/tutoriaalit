# Jaettu tila ja sivuvaikutukset

Tehtävien lista on tilaa, jota tarvitsee kolme komponenttia eri puolilla
puuta: lista näyttää sen, lomake lisää siihen ja tarkistaa
kaksoiskappaleet, ja ylätunnisteen yhteenveto laskee siitä. Jos tila
olisi päänäkymässä, se pitäisi kuljettaa ominaisuuksina jokaisen
välissä olevan komponentin läpi, vaikka välikomponentit eivät sitä itse
käytä. Kaikissa kehyksissä on tapa antaa tila suoraan sitä
tarvitseville, ja tavat ovat keskenään erilaisempia kuin mikään muu
tässä tutoriaalissa.

## Neljä tapaa jakaa

**React: reducer ja konteksti.** Tila on yksi muuttumaton arvo, ja
kaikki muutokset ovat nimettyjä toimintoja, jotka puhdas funktio
muuntaa uudeksi tilaksi:

```{.typescript tiedosto="esimerkit/react/src/tila.tsx" osa="reducer"}
```

Konteksti tarjoaa tilan ja lähetysfunktion kaikille puun komponenteille.
Lataus ja tallennus ovat efektejä:

```{.typescript tiedosto="esimerkit/react/src/tila.tsx" osa="konteksti"}
```

**Vue: reaktiiviset viittaukset ja provide/inject.** Tila on funktio,
joka luo viittaukset ja palauttaa ne muutosfunktioineen. Tällaista
funktiota kutsutaan Vuessa *composableksi*.

```{.typescript tiedosto="esimerkit/vue/src/tila.ts" osa="tila"}
```

```{.typescript tiedosto="esimerkit/vue/src/tila.ts" osa="inject"}
```

**Angular: palvelu ja riippuvuuksien injektointi.** Tila on luokka,
jonka kehys luo ja antaa sitä pyytäville:

```{.typescript tiedosto="esimerkit/angular/src/app/tehtavat.palvelu.ts" osa="palvelu"}
```

**Svelte: reaktiivinen olio moduulissa.** Tila on luokka, jonka kentät
ovat riimuja, ja siitä luodaan yksi olio, jonka komponentit tuovat
tavallisella `import`-lauseella:

```{.typescript tiedosto="esimerkit/svelte/src/tila.svelte.ts" osa="tila"}
```

Yhteenvetokomponentti näyttää, miltä tilan käyttäminen näyttää
lukijan päässä. Yksikään versio ei saa mitään vanhemmaltaan:

```{.typescript tiedosto="esimerkit/react/src/Yhteenveto.tsx" osa="yhteenveto"}
```

```{.html tiedosto="esimerkit/vue/src/Yhteenveto.vue"}
```

```{.typescript tiedosto="esimerkit/angular/src/app/yhteenveto.ts" osa="yhteenveto"}
```

```{.html tiedosto="esimerkit/svelte/src/Yhteenveto.svelte"}
```

## Mistä tila tulee

| Kehys | Miten komponentti saa tilan | Kuka luo tilan | Miten sen vaihtaa testissä |
|-------|-----------------------------|----------------|----------------------------|
| React | `useContext` | tarjoajakomponentti puussa | toinen tarjoaja testin puussa |
| Vue | `inject` | `provide` sovelluksessa tai komponentissa | `provide` testissä |
| Angular | `inject(Palvelu)` | injektori, kun palvelua pyydetään | toinen toteutus injektorin asetuksissa |
| Svelte | `import` | moduuli latautuessaan | moduulin korvaaminen tai konteksti |

Kolme ensimmäistä ovat sama ajatus: komponentti **pyytää** tilaa
nimellä eikä tiedä, mistä se tulee. Tämä on riippuvuuksien
injektointia, vaikka vain Angular kutsuu sitä sillä nimellä. Angularissa
se on kehyksen keskeisin rakenne: palvelut, reititin, HTTP-asiakas ja
sivun otsikko (`Title` yllä) saadaan kaikki samalla `inject`-kutsulla.
Perustelu on sama kuin taustajärjestelmissä, joista malli on peräisin:
riippuvuuden voi vaihtaa testissä toiseen, ja kehys hallitsee olioiden
elinkaaren.

Svelten moduulitason olio on yksinkertaisin, ja sen rajoitus on juuri
se, mitä muut välttävät: olio on yksi ja yhteinen kaikille. Selaimessa
se on sitä, mitä halutaan. Palvelimella renderöitäessä (luku 9) sama
moduuli palvelee kaikkia käyttäjiä, jolloin moduulitason tila vuotaisi
käyttäjältä toiselle. Siihen Sveltessäkin on kontekstirajapinta.

Toinen ero on tilan muoto. Reactin reducer pakottaa kaikki muutokset
yhden funktion läpi nimettyinä toimintoina. Muissa kolmessa tila on
olio, jolla on metodit. Lopputulos on sama, yksi paikka, jossa tila
muuttuu, mutta Reactin versio antaa lisäksi muutoksille nimet, jotka
voi kirjata, toistaa ja testata ilman käyttöliittymää.

## Sivuvaikutukset

Tallennus selaimen muistiin ja sivun otsikon päivitys eivät ole
näkymää. Ne ovat **sivuvaikutuksia**: jotain kehyksen ulkopuolista
pidetään tilan tasalla. Kaikissa neljässä tämä kirjoitetaan efektinä,
ja kaikissa efekti ajetaan uudelleen, kun sen lukema tila muuttuu.

```{.typescript tiedosto="esimerkit/yhteinen/logiikka.ts" osa="tallennus"}
```

Efekteissä on kaksi eroa, joista kumpikin on tullut jo vastaan.

**Riippuvuudet.** Reactin `useEffect` saa riippuvuutensa listana
(`[tila]`), koska komponenttifunktio ajetaan joka kerta eikä React
muuten tietäisi, onko efekti ajettava. Vuen, Angularin ja Svelten
efektit ovat luvun 3 signaaliefektejä: ne kirjaavat lukemansa arvot
itse, eikä listaa ole.

**Ajoitus.** Efekti ei aja heti, kun tila muuttuu. Kehys kerää
muutokset ja ajaa efektit omalla hetkellään: jokin ennen DOM:n
päivitystä, jokin sen jälkeen, kaikki myöhemmin kuin tilan muutos.
Tämä paljastui testistä, joka lisäsi tehtävän ja latasi sivun heti
uudelleen. Yhdessä toteutuksessa sivu ehdittiin ladata ennen kuin
tallennusefekti oli ajettu, ja muutos katosi. Testi korjattiin
odottamaan näkyvää seurausta (luku 8). Käyttäjälle sama ilmiö on
harvinainen, mutta siitä seuraa sääntö: tieto, jonka on pakko
tallentua, tallennetaan tapahtumankäsittelijässä eikä efektissä.

## Lataus on tila

Alkutilan haku palvelimelta on asynkroninen, ja sillä on kolme
vaihetta: ladataan, virhe ja valmis. Jokainen toteutus pitää vaihetta
tilana ja näyttää sen mukaisen näkymän. Virheestä toipuminen on sama
latausfunktio uudelleen kutsuttuna.

Tehtävälistassa tämä on tehty käsin, jotta rakenne näkyy. Oikeissa
sovelluksissa palvelimelta haettu tieto on oma lajinsa: se vanhenee,
sitä haetaan uudelleen, sitä on välimuistissa ja useampi komponentti
pyytää samaa. Siihen on jokaisessa kehyksessä vakiintuneita kirjastoja
ja osin kehyksen omia rakenteita, ja periaatteet on käyty läpi taidossa
*Web-sovellukset*. Kehyksestä riippumatta sääntö on sama: palvelimen
tieto ja käyttöliittymän tila pidetään erillään.

## Tilasäilöt

Kun sovellus kasvaa, jaetulle tilalle halutaan usein yksi sovittu
paikka ja tapa: **säilö** (*store*). Reactin maailmassa tunnetuin on
Redux, Vuessa Pinia, Angularissa NgRx. Niiden ydin on sama ja mahtuu
kolmeenkymmeneen riviin:

```{.typescript tiedosto="esimerkit/periaatteet/sailo.ts" osa="sailo"}
```

```{.typescript tiedosto="esimerkit/periaatteet/sailo.ts" osa="demo"}
```

```{.tuloste tiedosto="esimerkit/periaatteet/sailo.odotettu"}
```

Säilö ei tiedä kehyksestä mitään. Kehyksen osuus on pieni sovitin,
joka tilaa säilön ja kertoo kehykselle muutoksesta. Koska kaikki
muutokset ovat nimettyjä toimintoja, niistä syntyy historia: tilan voi
rakentaa uudelleen toistamalla toiminnot, ja kehitystyökalut näyttävät,
mikä toiminto muutti mitäkin.

Säilökirjaston tarve on vähentynyt. Signaalit ovat itsessään jaettavaa
tilaa: Vuen, Angularin ja Svelten toteutuksissa yllä ei ole kirjastoa,
ja ne tekevät saman kuin säilö. Kirjastoon siirrytään, kun halutaan sen
tuomat sopimukset ja työkalut, ei siksi, että tilaa ei muuten voisi
jakaa.

## Käytännössä

- **Jaa vain se, mikä on jaettua.** Suodatin ja lomakkeen kentät ovat
  paikallista tilaa kaikissa toteutuksissa. Jaetun tilan jokainen
  lukija on riippuvuus, joka vaikeuttaa komponentin siirtämistä ja
  testaamista.
- **Tilan muutokset yhteen paikkaan.** Reducer, composable, palvelu tai
  luokka: muoto vaihtelee, mutta jokaisessa toteutuksessa komponentit
  kutsuvat nimettyä operaatiota (`lisaa`, `vaihda`) eivätkä muokkaa
  listaa itse. Angular-toteutus valvoo tätä tyypeillä: signaalit ovat
  yksityisiä, ja ulos näkyy vain luettava versio.
- **Efekti on synkronointia ulkomaailmaan, ei tapa reagoida
  tapahtumaan.** Jos jotain pitää tehdä, koska käyttäjä painoi
  painiketta, tee se käsittelijässä. Efekti kuuluu asioihin, joiden on
  seurattava tilaa riippumatta siitä, miksi tila muuttui.
- **Älä ota säilökirjastoa varmuuden vuoksi.** Aloita kehyksen omilla
  välineillä. Siirry kirjastoon, kun tilan muutoksia on vaikea jäljittää
  tai tiimi tarvitsee yhteisen tavan.
- **Varo moduulitason tilaa, jos sovellus renderöidään palvelimella.**
  Se on yhteinen kaikille pyynnöille.

## Itsearviointi

- Osaat selittää, mitä ongelmaa jaettu tila ratkaisee ja miksi sitä ei
  kuljeteta ominaisuuksina.
- Osaat kuvata, miten komponentti saa jaetun tilan kussakin neljässä
  kehyksessä, ja sanoa, mitä yhteistä tavoilla on.
- Osaat perustella, miksi Angular rakentuu riippuvuuksien injektoinnin
  varaan.
- Osaat kertoa, miten efektin riippuvuudet määräytyvät Reactissa ja
  signaalikehyksissä, ja miksi efektin ajoitukseen ei saa luottaa.
- Osaat selittää tilasäilön periaatteen ja arvioida, milloin
  säilökirjasto on tarpeen.
