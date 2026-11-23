# Lomakkeet

Lomake on sivun tärkein vuorovaikutuksen väline: tilaukset,
ilmoittautumiset, haku ja kirjautuminen. Natiivit lomake-elementit
tuovat mukanaan näppäimistökäytön, sopivan mobiilinäppäimistön,
automaattisen täytön, syötteen tarkistuksen ja ruudunlukijatuen.
Mikään näistä ei synny itsestään `<div>`-elementistä.

## Kentät ja nimiöt

Uutiskirjeen tilauslomake:

```{.html tiedosto="esimerkit/04-tilaus.html" osa="lomake"}
```

```{.tuloste tiedosto="esimerkit/04-tilaus.odotettu"}
```

- **Jokaisella kentällä on `<label>`.** Nimiö kytketään kenttään
  `for`–`id`-parilla tai kääreenä (`<label><input> Teksti</label>`).
  Nimiö antaa kentälle nimen saavutettavuuspuussa, ja nimiön
  napsauttaminen kohdistaa kentän, mikä suurentaa valintaruudun
  osuma-aluetta.
- **Kentän tyyppi** (`email`, `tel`, `number`, `date`, `search`,
  `url`) valitsee mobiililaitteen näppäimistön ja tarkistuksen.
  Numeroilta näyttävä tieto, jolla ei lasketa (postinumero,
  korttinumero), on `type="text"` ja `inputmode="numeric"`, koska
  `number` hukkaa alkunollat ja lisää nuolipainikkeet.
- **`autocomplete`** kertoo selaimelle, mitä tietoa kenttä kysyy
  (`name`, `email`, `postal-code`, `current-password`). Automaattinen
  täyttö nopeuttaa täyttämistä ja on WCAG 2.2:n vaatimus käyttäjän
  omille tiedoille.
- **`<fieldset>` ja `<legend>`** ryhmittävät toisiinsa liittyvät
  kentät, erityisesti valintanapit. Ruudunlukija lukee ryhmän nimen
  ("Kuinka usein?") ennen vaihtoehtoa.
- **Ohjeteksti** liitetään kenttään `aria-describedby`-attribuutilla,
  jolloin ruudunlukija lukee sen kentän nimen jälkeen.
- **`<button type="submit">`**: painikkeen tyyppi kirjoitetaan aina.
  Lomakkeen sisällä tyypitön painike lähettää lomakkeen, mikä yllättää.

Paikkamerkkiteksti (`placeholder`) ei korvaa nimiötä. Se katoaa, kun
kenttään kirjoitetaan, sen kontrasti on heikko, ja moni ruudunlukija
jättää sen lukematta.

```{.html tiedosto="esimerkit/04-label.ei-kaanny.html" osa="haku"}
```

```text
13:12  error  <input> element does not have a <label>
              input-missing-label
```

```{.tuloste tiedosto="esimerkit/04-label.odotettu"}
```

Jos nimiötä ei haluta näkyviin, kuten hakukentässä, jonka viereinen
painike kertoo tarkoituksen, nimiö piilotetaan visuaalisesti luvun 5
tekniikalla eikä poisteta.

## Selaimen tarkistus

Selain tarkistaa kentät ennen lähetystä attribuuttien perusteella.
Esimerkin skripti tulostaa selaimen tarkistustuloksen kentittäin:

```{.html tiedosto="esimerkit/04-validointi.html" osa="kentat"}
```

```{.html tiedosto="esimerkit/04-validointi.html" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-validointi.odotettu"}
```

| Attribuutti | Ehto | Tilalippu |
|-------------|------|-----------|
| `required` | kenttä ei saa olla tyhjä | `valueMissing` |
| `type="email"`, `url` | muoto | `typeMismatch` |
| `pattern` | säännöllinen lauseke koko arvolle | `patternMismatch` |
| `min`, `max` | lukuarvon rajat | `rangeUnderflow`, `rangeOverflow` |
| `minlength`, `maxlength` | pituus | `tooShort`, `tooLong` |

Tyylit kytketään pseudoluokkiin `:user-invalid` ja `:user-valid`. Ne
ovat voimassa vasta, kun käyttäjä on muokannut kenttää tai yrittänyt
lähettää lomakkeen. Vanhempi `:invalid` on voimassa heti, joten tyhjä
pakollinen kenttä näkyisi virheellisenä jo ennen kuin käyttäjä on
ehtinyt tehdä mitään:

```{.css tiedosto="esimerkit/04-validointi.html" osa="tyyli"}
```

Selaimen tarkistus on käyttäjää varten. Palvelin tarkistaa syötteen
aina uudelleen, koska pyynnön voi lähettää ohi lomakkeen.

## Virheiden näyttäminen

Kun palvelin hylkää lomakkeen, se palauttaa saman lomakkeen
virheineen. Hyväksi todettu malli (esimerkiksi Ison-Britannian
hallinnon GOV.UK-suunnittelujärjestelmästä):

```{.html tiedosto="esimerkit/04-virheet.html" osa="virheet"}
```

```{.tuloste tiedosto="esimerkit/04-virheet.odotettu"}
```

1. **Otsikko alkaa sanalla "Virhe:"**, jolloin virhe huomataan jo
   välilehden nimestä ja ruudunlukijan lukemasta otsikosta.
2. **Virheyhteenveto** sivun alussa luettelee virheet linkkeinä
   kenttiin. Se saa fokuksen sivun latautuessa (`tabindex="-1"` ja
   `autofocus`), joten ruudunlukija lukee sen ensimmäisenä.
3. **Kentän virheviesti** on kentän vieressä ja liitetty siihen
   `aria-describedby`-attribuutilla, ja kenttä on merkitty
   `aria-invalid="true"`. Saavutettavuuspuussa kenttä näkyy tilassa
   `[invalid]`.
4. **Viesti kertoo, miten virhe korjataan**, ei vain, että jokin on
   väärin. Käyttäjän syöttämä arvo säilytetään kentässä.
5. `novalidate` ohittaa selaimen tarkistuksen, kun palvelin näyttää
   virheet itse, jotta virheet näkyvät yhdellä yhtenäisellä tavalla.

Virheen ilmaiseminen pelkällä värillä (punainen reunus) ei riitä:
värisokea ei erota sitä, eikä ruudunlukija näe sitä lainkaan.

## Käytännössä

- **Kysy vain tarpeellinen.** Jokainen kenttä vähentää lomakkeen
  täyttäneiden osuutta. Valinnaiset kentät merkitään "(valinnainen)";
  pakolliset ovat oletus.
- **Yksi sarake.** Kentät allekkain luetaan ja täytetään nopeammin
  kuin rinnakkain, ja asettelu toimii sellaisenaan puhelimessa.
- **Nimiö kentän yläpuolelle.** Se pysyy näkyvissä kirjoitettaessa ja
  zoomattaessa. Kentän leveys vihjaa odotetun syötteen pituuden.
- **Älä estä liittämistä tai automaattista täyttöä.** Salasanakenttään
  liittäminen ja salasanojen hallintaohjelmat parantavat turvallisuutta.
- **Natiivit kentät ennen omia komponentteja.** Oma pudotusvalikko tai
  päivämäärävalitsin vaatii näppäimistökäytön, ARIA-roolit ja
  testauksen ruudunlukijoilla; natiivi `<select>` ja
  `<input type="date">` toimivat valmiiksi.

## Itsearviointi

- Osaat kytkeä jokaiseen kenttään nimiön ja ohjetekstin ja ryhmitellä
  valintanapit.
- Osaat valita kenttätyypin, `inputmode`- ja `autocomplete`-arvon
  kysytyn tiedon mukaan.
- Osaat käyttää selaimen tarkistusta attribuuteilla ja tyylitellä
  virheet vasta käyttäjän toimien jälkeen.
- Osaat toteuttaa palvelimen palauttamat virheet yhteenvetona ja
  kenttäkohtaisina viesteinä saavutettavasti.
