# Virheenkäsittely {.runko-virheet}

JavaScriptin virheenkäsittely perustuu poikkeuksiin: `throw` heittää,
`try`–`catch`–`finally` käsittelee. Heittää voi minkä tahansa arvon,
mutta käytäntö on heittää vain `Error`-olioita, koska niissä on viesti,
pinojälki ja syyketju.

## Omat virheluokat ja syyketju

```{.javascript tiedosto="esimerkit/08-virheet.js" osa="luokat"}
```

`new.target.name` asettaa nimeksi todellisen aliluokan nimen, joten
kantaluokka hoitaa sen kaikille. Hierarkian avulla kutsuja voi
käsitellä virhelajin (`instanceof EiLoydy`) tai kaikki sovelluksen virheet
(`instanceof SovellusVirhe`).

Kun matalan tason virhe käännetään sovelluksen virheeksi, alkuperäinen
säilytetään optiona `cause` (ES2022). Lokiin ja debuggeriin jää koko
ketju, mutta kutsuja näkee oman tasonsa virheen:

```{.javascript tiedosto="esimerkit/08-virheet.js" osa="ketju"}
```

`catch` käsittelee vain virheet, jotka se tuntee, ja heittää muut
eteenpäin. Kaikki nielevä `catch` piilottaa ohjelmointivirheet.

```{.javascript tiedosto="esimerkit/08-virheet.js" osa="kasittely"}
```

```{.tuloste tiedosto="esimerkit/08-virheet.odotettu"}
```

`finally` ajetaan aina, myös kun `try` palaa `return`-lauseella tai
virhe jatkaa eteenpäin.

## Resurssien vapauttaminen

Tiedostokahva, tietokantayhteys, lukko tai ajastin on vapautettava
myös silloin, kun työ päättyy virheeseen. Perinteinen keino on
`try`–`finally`. Uudempi on sopia vapautuksesta olion kanssa: resurssi
toteuttaa metodin `[Symbol.dispose]()`, joka sulkee sen.

```{.javascript tiedosto="esimerkit/08-resurssit/yhteys.js"}
```

```{.javascript tiedosto="esimerkit/08-resurssit/finally.js"}
```

Määrittely `using` (*explicit resource management*) tekee saman
ilman `try`-lohkoa: kun lohko päättyy paluuseen tai virheeseen,
muuttujan `[Symbol.dispose]()` kutsutaan automaattisesti, ja useat
resurssit vapautetaan käänteisessä järjestyksessä. Se vastaa Pythonin
`with`-lausetta ja Javan try-with-resources-lohkoa.

```{.javascript tiedosto="esimerkit/08-resurssit/using.js"}
```

`using` kuuluu standardiin versiosta ES2026 alkaen, ja se toimii Node
24:ssä mutta ei Node 22:ssa. Asynkroniselle sulkemiselle on
vastaavasti `await using` ja `[Symbol.asyncDispose]()`. Esimerkin
pääohjelma lataa `using`-version ja vaihtaa vanhassa Nodessa
`finally`-versioon, joten tuloste on molemmissa sama:

```{.javascript tiedosto="esimerkit/08-resurssit/main.js"}
```

```{.tuloste tiedosto="esimerkit/08-resurssit.odotettu"}
```

Yhteys suljetaan ennen kuin paluuarvo tulostetaan ja myös silloin, kun
kysely heittää virheen.

## catch-muuttujan tyyppi

Koska heitetty arvo voi olla mitä tahansa, tiukka tila antaa
`catch`-muuttujalle tyypin `unknown`. Ennen käyttöä tyyppi on
kavennettava:

```{.javascript tiedosto="esimerkit/08-catch.ei-kaanny.js"}
```

```text
08-catch.ei-kaanny.js(4,15): error TS18046: 'virhe' is of type
'unknown'.
```

## Asynkroniset virheet

`async`-funktion heittämä virhe hylkää sen palauttaman lupauksen.
`await` heittää virheen uudelleen, joten tavallinen `try`–`catch`
toimii. Lupaus, jota kukaan ei odota eikä käsittele, on
*käsittelemätön hylkäys*, ja Node lopettaa silloin prosessin:

```{.javascript tiedosto="esimerkit/08-hylkays.kaatuu.js"}
```

```text
Error: hintaa ei löydy: kahvi
    at haeHinta (file:///.../08-hylkays.kaatuu.js:7:9)
```

Jokainen lupaus joko odotetaan, palautetaan kutsujalle tai sille
lisätään `.catch`. Tarkoituksellisesti irrallaan ajettava työ
(*fire and forget*) saa oman `.catch`-käsittelijänsä, joka kirjaa
virheen. Moni lupaus yhdistetään luvun 10 funktioilla
(`Promise.all`, `allSettled`, `any`).

## Poikkeus vai paluuarvo

Poikkeus sopii tilanteisiin, joita kutsuja ei voi järkevästi käsitellä
heti: ohjelmointivirheet, rikkinäinen konfiguraatio, kadonnut yhteys.
Odotettu epäonnistuminen, kuten käyttäjän virheellinen syöte, on usein
selkeämpi paluuarvona: luvun 7 *Tulos*-tyyppi `{ ok, arvo }` tai
`{ ok, virhe }` pakottaa tyyppitarkistimen avulla käsittelemään
molemmat tapaukset. Validointikirjastot (esim. Zodin `safeParse`)
noudattavat samaa mallia.

| Tilanne | Keino |
|---------|-------|
| ohjelmointivirhe (bugi) | anna kaatua; `TypeError`, `RangeError`, `assert` |
| ulkoinen vika (verkko, tiedosto) | poikkeus syyketjun kanssa, käsittely ylätasolla |
| odotettu epäonnistuminen (validointi) | *Tulos*-olio tai `null`/`undefined` |
| peruutus | `AbortError` (luku 10), ei kirjata virheenä |

## Käytännössä

- **Heitä vain `Error`-olioita.** `throw "virhe"` ei sisällä pinojälkeä.
- **Omat virheluokat sovelluksen rajoille** ja syyketju `{ cause }`,
  kun virhe käännetään toiselle tasolle.
- **Resurssi vapautetaan samassa funktiossa, joka sen avasi**:
  `using` tai `try`–`finally`. Kirjaston resurssiolio saa metodin
  `[Symbol.dispose]()`, jolloin käyttäjä voi valita kumman tahansa.
- **Käsittele vain tunnetut virheet.** `catch`, joka ei tunnista virhettä,
  heittää sen eteenpäin. Kirjaa virhe kerran, ylimmällä tasolla.
- **Ei irrallisia lupauksia.** ESLint-sääntö `no-floating-promises`
  (typescript-eslint) löytää unohtuneen `await`-sanan.
- **Prosessin tasolla** `process.on("uncaughtException")` ja
  `unhandledRejection` kirjaavat virheen ja lopettavat prosessin
  hallitusti. Prosessin jatkaminen tuntemattomassa tilassa on
  vaarallisempaa kuin uudelleenkäynnistys.
- **Hinta.** `try`-lohko ei maksa mitään, kun virhettä ei heitetä.
  Heittäminen on kallista, koska pinojälki kerätään: tuhansia kertoja
  sekunnissa tapahtuva "normaali" poikkeus näkyy profiilissa. Siksi
  odotetut epäonnistumiset kuuluvat paluuarvoon. Python suosii päinvastaista
  EAFP-tyyliä, koska siellä poikkeus on halvempi suhteessa muuhun koodiin.

## Itsearviointi

- Osaat kirjoittaa virheluokkien hierarkian ja käyttää syyketjua
  `cause`.
- Osaat kaventaa `catch`-muuttujan tyypin ja käsitellä vain tunnetut
  virheet.
- Osaat vapauttaa resurssin `try`–`finally`-lohkolla ja
  `using`-määrittelyllä ja toteuttaa vapautusprotokollan omalle
  luokalle.
- Osaat kertoa, mikä on käsittelemätön hylkäys ja miten se estetään.
- Osaat valita poikkeuksen ja paluuarvon välillä ja perustella valinnan
  hinnalla ja käytettävyydellä.
