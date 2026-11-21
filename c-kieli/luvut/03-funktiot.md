# Ohjausrakenteet ja funktiot

## Ohjausrakenteet

C:n ohjausrakenteet ovat tuttuja monista muista kielistä, sillä ne ovat
periytyneet C:stä C++:aan, Javaan, C#:iin ja JavaScriptiin. Ehtona
kelpaa mikä tahansa skalaariarvo: nolla on epätosi ja kaikki muu tosi.

```{.c tiedosto="esimerkit/03-ohjaus.c" osa="collatz"}
```

`for`-silmukan alustuksessa voi esitellä muuttujan (C99), jolloin se
näkyy vain silmukassa. `continue` siirtyy seuraavaan kierrokseen ja
`break` poistuu silmukasta:

```{.c tiedosto="esimerkit/03-ohjaus.c" osa="for"}
```

`do`–`while`-silmukka tarkistaa ehdon vasta rungon jälkeen, joten runko
suoritetaan vähintään kerran:

```{.c tiedosto="esimerkit/03-ohjaus.c" osa="dowhile"}
```

`switch` valitsee haaran kokonaislukuarvon perusteella. Suoritus
jatkuu haarasta seuraavaan (*fallthrough*), ellei haara pääty
`break`- tai `return`-lauseeseen. Tätä käytetään tarkoituksella, kun
usea arvo johtaa samaan haaraan. Tahallisen läpiputoamisen voi
merkitä C23:n attribuutilla `[[fallthrough]]`, jolloin kääntäjä ei
varoita siitä.

```{.c tiedosto="esimerkit/03-ohjaus.c" osa="switch"}
```

```{.tuloste tiedosto="esimerkit/03-ohjaus.odotettu"}
```

## Funktiot

Funktio on *esiteltävä* ennen kuin sitä kutsutaan. Esittely eli
*prototyyppi* kertoo funktion nimen, paluutyypin ja parametrien tyypit.
*Määrittely* sisältää lisäksi funktion rungon. Prototyypit kirjoitetaan
yleensä tiedoston alkuun tai otsikkotiedostoon, jolloin funktiot voi
määritellä missä järjestyksessä tahansa.

```{.c tiedosto="esimerkit/03-funktiot.c" osa="prototyypit"}
```

Ennen C99:ää esittelemättömän funktion kutsu oli sallittu, ja kääntäjä
oletti paluutyypiksi `int`. Tämä aiheutti vaikeasti löydettäviä virheitä,
ja nykyään GCC 14 ja Clang hylkäävät tällaisen koodin:

```{.c tiedosto="esimerkit/03-esittely.ei-kaanny.c"}
```

### Arvovälitys

C välittää kaikki argumentit *arvoina*: funktio saa kopiot, eikä
parametrien muuttaminen vaikuta kutsujan muuttujiin. Jotta funktio voi
muuttaa kutsujan muuttujaa, sille on annettava muuttujan osoite. Tähän
palataan seuraavassa luvussa.

```{.c tiedosto="esimerkit/03-funktiot.c" osa="maaritelmat"}
```

```{.c tiedosto="esimerkit/03-funktiot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/03-funktiot.odotettu"}
```

### `static`

Avainsanalla `static` on C:ssä kaksi eri merkitystä:

- **Funktion ulkopuolella** `static` rajaa funktion tai muuttujan
  näkyvyyden nykyiseen tiedostoon (*sisäinen linkitys*). Apufunktiot,
  joita ei ole tarkoitettu muiden tiedostojen käyttöön, kannattaa
  merkitä `static`.
- **Funktion sisällä** `static` tekee paikallisesta muuttujasta
  pysyvän: se alustetaan kerran ohjelman alussa ja säilyttää arvonsa
  kutsujen välillä, kuten `seuraava_tunnus`-funktion laskuri.

### Laskentajärjestys

Funktion argumenttien laskentajärjestystä ei ole määrätty. Siksi
esimerkissä kutsut `seuraava_tunnus()` on kirjoitettu omille
riveilleen: jos ne olisivat saman `printf`-kutsun argumentteina,
tunnukset voisivat tulostua missä järjestyksessä tahansa. Sama koskee
useimpia operaattoreita. Poikkeuksia ovat `&&`, `||`, pilkkuoperaattori
ja ehto-operaattori `?:`, jotka laskevat vasemman operandinsa ensin.
