# Doxygen ja muiden kielten työkalut

Jokaisella kielellä on oma työkalunsa, joka tuottaa viitteen
lähdekoodin kommenteista. Periaate on sama kuin Pythonissa: kuvaus
kirjoitetaan määrittelyn viereen, ja työkalu varoittaa, kun se puuttuu
tai on ristiriidassa koodin kanssa. Tämä luku käy periaatteen läpi
C-kielellä ja Doxygenilla.

## Otsake on rajapinta

C-kirjaston julkinen rajapinta on sen otsaketiedosto, joten kuvaukset
kirjoitetaan sinne. Toteutustiedostoon kuuluvat vain toteutusta
selittävät kommentit. Doxygen lukee kommentit, jotka alkavat merkeillä
`/**`, ja tulkitsee niiden `@`-alkuiset komennot:

```{.c tiedosto="esimerkit/c/puskuri.h" osa="lisaa"}
```

Komento `@brief` on yhden virkkeen tiivistelmä, joka näkyy
luetteloissa. `@param` kuvaa parametrin, ja suunta `[in]`, `[out]`
tai `[in,out]` kertoo C:ssä olennaisen asian, jota tyyppi ei kerro:
lukeeko funktio osoittimen takaa, kirjoittaako se sinne vai molempia.
`@return` kuvaa paluuarvon; kun arvoja on muutama erillinen,
`@retval` kuvaa kunkin.

Rakenteen kentät kuvataan samalla rivillä merkinnällä `/**<`:

```{.c tiedosto="esimerkit/c/puskuri.h" osa="rakenne"}
```

Kuvaus kertoo myös sen, mitä kääntäjä ei valvo: kenttiin ei saa
koskea suoraan, vaikka ne ovat näkyvissä. Komento `@ref` on
ristiviittaus, ja pelkkä funktion nimi sulkuineen (`puskuri_lisaa()`)
linkittyy automaattisesti.

Liittyvät funktiot kootaan ryhmäksi komennolla `@defgroup`, jolloin
viitteessä on moduulin sivu, jolla on johdanto ja käyttöesimerkki.
Tiedostoluettelo ei kerro lukijalle, mistä aloittaa; ryhmän sivu
kertoo.

## Asetukset ja varoitukset

Doxygenin asetustiedosto on pitkä, mutta olennaisia rivejä on vähän.
Tarkistusten kannalta tärkeimmät:

```{.ini tiedosto="esimerkit/c/Doxyfile" osa="varoitukset"}
```

Oletuksena Doxygen ei välitä dokumentoimattomista nimistä, ja asetus
`EXTRACT_ALL` jopa piilottaa varoitukset ottamalla kaiken mukaan.
Tiukoilla asetuksilla puuttuva tai väärä kuvaus pysäyttää rakennuksen.
Seuraavassa otsakkeessa parametri on nimetty uudelleen, toinen lisätty
ja yksi funktio jäänyt kokonaan kuvaamatta:

```{.c tiedosto="esimerkit/c/puutteellinen.h"}
```

```{.tuloste tiedosto="esimerkit/c/puutteellinen.odotettu"}
```

Vika on sama kuin edellisen luvun Python-esimerkissä, ja niin on
korjauskin: työkalu vertaa kuvauksen parametreja allekirjoitukseen.

Esimerkkien Makefile rakentaa viitteen, vertaa dokumentoitujen
kohteiden luetteloa tallennettuun ja varmistaa, että puutteellinen
otsake jää kiinni:

```{.makefile tiedosto="esimerkit/Makefile" osa="doxygen"}
```

Kohdeluettelo luetaan Doxygenin XML-tulosteesta, joka on tarkoitettu
juuri muiden työkalujen luettavaksi:

```{.tuloste tiedosto="esimerkit/c/kohteet.odotettu"}
```

## Koodi kommentissa

Otsakkeen ryhmäkuvauksessa on käyttöesimerkki lohkossa `@code`.
Toisin kuin Pythonin doctest, Doxygen ei käännä eikä aja sitä, joten
esimerkki voi vanhentua. Tavallinen ratkaisu on pitää esimerkki
oikeana lähdetiedostona, joka käännetään testeissä, ja liittää se
kuvaukseen komennolla `@include` tai `@snippet`. Periaate on sama
kuin tämän tutoriaalisarjan koodilohkoissa (luku 4): näytetty koodi
tulee tiedostosta, joka testataan.

## Muiden kielten työkalut

| Kieli | Työkalu | Kommentin muoto | Esimerkit ajetaan |
|------------|-----------------|--------------------------|------------------|
| C, C++ | Doxygen | `/** ... */`, `@param` | ei (`@snippet` tiedostosta) |
| Python | Sphinx `autodoc` | docstring | kyllä (doctest) |
| Java | Javadoc | `/** ... */`, `@param` | ei (`@snippet` tiedostosta) |
| Kotlin | Dokka | KDoc `/** ... */`, `@param` | ei (`@sample` tiedostosta) |
| Rust | rustdoc | `///`, Markdown | kyllä (`cargo test`) |
| Go | go doc | kommentti määrittelyn yllä | kyllä (`Example`-funktiot) |
| TypeScript | TypeDoc | TSDoc `/** ... */` | ei |
| C# | DocFX | XML-kommentit `///` | ei |

Rust ja Go ovat tässä pisimmällä: molemmissa dokumentaation
esimerkit ovat testejä, jotka kielen oma testityökalu ajaa. Rustin
`cargo test` kääntää ja ajaa jokaisen kommentin koodilohkon, ja Go:n
`Example`-funktion tuloste verrataan sen kommenttiin. Muissa kielissä
sama saavutetaan liittämällä esimerkit testatuista tiedostoista.

Go:n käytäntö on myös hyvä muistutus siitä, ettei merkintäkieltä
välttämättä tarvita: kommentti on tavallista tekstiä, joka alkaa
kuvattavan nimellä, ja työkalu näyttää sen sellaisenaan.

## Käytännössä

- **Dokumentoi otsake, älä toteutusta.** Kutsuja lukee otsakkeen;
  kahteen paikkaan kirjoitettu kuvaus eriytyy.
- **Suunta ja omistajuus näkyviin.** C:ssä kuvauksen tärkein tieto on
  se, kuka varaa, kuka vapauttaa ja saako osoitin olla `NULL`.
- **Varoitukset virheiksi ja `EXTRACT_ALL` pois.** Muuten viite
  näyttää valmiilta, vaikka puolet kuvauksista puuttuu.
- **Ryhmittele moduuleiksi.** Lukija etsii toimintoa, ei tiedostoa.
- **Esimerkit tiedostoista.** Kommenttiin kirjoitettu koodi ei käänny
  missään.
- **Älä kuvaa itsestäänselvää.** `@param p Puskuri` ei kerro mitään.
  Jos parametrista ei ole muuta sanottavaa kuin sen nimi, kerro
  esiehto: ”alustettu funktiolla `puskuri_alusta()`”.

## Itsearviointi

- Osaat kirjoittaa C-funktiolle Doxygen-kuvauksen, jossa on
  tiivistelmä, parametrien suunnat ja paluuarvot.
- Osaat asettaa Doxygenin niin, että puuttuva tai ristiriitainen
  kuvaus pysäyttää rakennuksen.
- Osaat nimetä oman kielesi dokumentaatiotyökalun ja kertoa, ajaako
  se esimerkit.
- Osaat selittää, miten kommentin koodiesimerkki pidetään toimivana
  kielessä, jossa työkalu ei aja sitä.
