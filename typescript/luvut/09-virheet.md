# Virheet ja ulkoisen datan jäsentäminen {.runko-virheet}

TypeScriptin tyypit pätevät vain koodille, jonka kääntäjä on nähnyt.
Verkosta, tiedostosta, käyttäjältä tai tietokannasta tuleva data on
ajossa mitä tahansa. Tämä luku käsittelee kolmea asiaa: poikkeuksia,
virheitä arvoina ja ulkoisen datan muuttamista luotettaviksi tyypeiksi.

## Poikkeukset

Poikkeusten ajonaikainen toiminta (virheluokat, `cause`, `finally`) on
opetettu taidossa *JavaScript*. TypeScript lisää siihen kaksi asiaa:
`catch`-muuttujan tyypin ja sen, ettei heitettävä virhe näy funktion
tyypissä.

```{.typescript tiedosto="esimerkit/09-catch.ts"}
```

```{.tuloste tiedosto="esimerkit/09-catch.odotettu"}
```

- **`catch (e)` on `unknown`** tiukassa tilassa
  (`useUnknownInCatchVariables`), koska JavaScriptissä voi heittää minkä
  tahansa arvon. Kavenna `instanceof`illa ennen käyttöä.
- **Oma virheluokka** periytetään `Error`ista. `override readonly name`
  näkyy pinojäljessä ja lokeissa.
- **Ketjutus** `{ cause: e }` säilyttää alkuperäisen virheen, kun
  matalan tason virhe käännetään sovelluksen käsitteiksi.
- **Poikkeuksia ei tyypitetä.** Funktion allekirjoitus ei kerro, mitä se
  voi heittää (vrt. Javan `throws`). Odotettavissa olevat virheet
  kannattaa siksi palauttaa arvoina.

## Virheet arvoina

Kun epäonnistuminen kuuluu normaaliin toimintaan, kuten loppuunmyyty
tuote tai virheellinen syöte, virhe palautetaan unionina. Kutsujan on
käsiteltävä se, ja virhetyyppi on osa allekirjoitusta:

```{.typescript tiedosto="esimerkit/09-tulos.ts"}
```

```{.tuloste tiedosto="esimerkit/09-tulos.odotettu"}
```

Virhetyyppi on itsekin eroteltu unioni, joten kutsuja voi käsitellä
lajit erikseen kattavasti. Nyrkkisääntö: *odotettu* virhe arvona,
*ohjelmointivirhe* tai poikkeuksellinen tilanne (levy täynnä, rikki
mennyt invariantti) poikkeuksena.

Poikkeuksen hinta on JavaScriptissä kohtuullinen, mutta se ei näy
tyypeissä, ja `await`-ketjussa unohtunut käsittely kaatuu kaukana
syystä. `Tulos`-tyyppi tekee virhepolun näkyväksi.

## as-pakotus ei tarkista

`as` on yleisin syy siihen, että TypeScript-ohjelma kaatuu tyyppivirheeseen
ajossa. Virhe ilmenee vasta, kun puuttuvaa kenttää käytetään, usein
kaukana kohdasta, jossa data luettiin:

```{.typescript tiedosto="esimerkit/09-pakotus.kaatuu.ts"}
```

```
TypeError: Cannot read properties of undefined (reading 'kunta')
```

## Parse, don't validate

Turvallinen malli on *jäsentää* ulkoinen data rajapinnan reunalla:
funktio ottaa vastaan `unknown`-arvon ja palauttaa joko tyypitetyn
arvon tai virheet. Validointi (palauttaa `true` tai `false`) hukkaa
tiedon, jonka tarkistus tuotti; jäsennys säilyttää sen tyypissä. Reunan
jälkeen koodi luottaa tyyppeihin eikä tarkista samoja asioita
uudelleen.

```{.dot otsikko="Ulkoinen data kulkee jäsentimen läpi. Vain jäsennetty arvo pääsee ytimeen; virheet palautetaan lähettäjälle."}
digraph {
  rankdir=LR; node [shape=box];
  ulko [label="verkko, tiedosto,\nlomake", shape=plaintext];
  jasennin [label="jäsennin\n(skeema)"];
  ydin [label="sovelluksen ydin\ntyyppi Tilaus"];
  virhe [label="virheet polkuineen", shape=plaintext];
  ulko -> jasennin [label="unknown"];
  jasennin -> ydin [label="ok: arvo"];
  jasennin -> virhe [label="ei ok: virheet"];
}
```

Esimerkissä on pieni jäsenninkirjasto. Jäsentimet yhdistellään
skeemaksi, ja sovelluksen tyyppi *johdetaan skeemasta*, joten tyyppi ja
tarkistus eivät voi erota toisistaan:

```{.typescript tiedosto="esimerkit/09-jasennys/jasennin.ts"}
```

```{.typescript tiedosto="esimerkit/09-jasennys/malli.ts"}
```

```{.typescript tiedosto="esimerkit/09-jasennys/main.ts"}
```

```{.tuloste tiedosto="esimerkit/09-jasennys.odotettu"}
```

Huomioita:

- **`olio`** käyttää kuvattua tyyppiä: jokaiselle `T`:n kentälle annetaan
  jäsennin, ja tulos on `Jasennin<T>`. `T` päätellään kenttien
  jäsentimistä, joten tyyppiä ei kirjoiteta käsin.
- **`Tyyppi<typeof tilaus>`** purkaa skeemasta sovelluksen tyypin
  `Tilaus` ehdollisella tyypillä ja `infer`illä.
- **Virheet kerätään polkuineen** (`rivit[0].maara`), jotta käyttäjä saa
  kaikki virheet kerralla.
- **`as` esiintyy kirjastossa muutaman kerran** (esim. `x as number`
  ja `tulos as T`). Ne ovat perusteltuja, koska tarkistus on tehty juuri
  ennen.
  Pakotukset kuuluvat pieniin, testattuihin apufunktioihin, ei
  sovelluskoodiin.

Tuotannossa käytetään valmista kirjastoa, kuten Zod, Valibot tai ArkType.
Ne toimivat samalla periaatteella: skeema on ajonaikainen arvo, josta
tyyppi johdetaan (`z.infer<typeof skeema>`).

## Brändätyt tyypit

Jäsennyksen tulos kannattaa merkitä tyyppiin. *Brändätty tyyppi* on
perustyyppi, johon on liitetty pelkästään käännösaikainen merkintä.
Tavallinen merkkijono ei kelpaa paikkaan, joka vaatii tarkistetun
sähköpostiosoitteen:

```{.typescript tiedosto="esimerkit/09-brandi.ei-kaanny.ts"}
```

```
09-brandi.ei-kaanny.ts(14,20): error TS2345: Argument of type 'string'
  is not assignable to parameter of type 'Sahkoposti'.
```

```{.tuloste tiedosto="esimerkit/09-brandi.odotettu"}
```

Brändi ei maksa ajossa mitään: `Sahkoposti` on ajossa tavallinen
merkkijono. Sama malli sopii tunnisteille (`AsiakasId` ei sekoitu
`TilausId`hen), yksiköille (`Sentit`, `Millisekunnit`) ja
puhdistetulle syötteelle (`TurvallinenHtml`).

## Käytännössä

- **Jäsennä reunalla, kerran.** HTTP-pyynnön runko, ympäristömuuttujat,
  tiedostot ja tietokannan rivit jäsennetään `unknown`ista tyypitetyiksi
  heti vastaanotettaessa.
- **Tyyppi skeemasta.** Kun tarkistus ja tyyppi kirjoitetaan erikseen,
  ne erkanevat. Johda tyyppi skeemasta tai käytä kirjastoa, joka tekee
  sen.
- **`as` vain tarkistuksen jälkeen ja apufunktiossa.** Sovelluskoodin
  `as` on lähes aina piilotettu tyyppivirhe. Etsi ne katselmoinnissa.
- **Odotettu virhe arvona, poikkeus ohjelmointivirheelle.**
  `Tulos`-unioni tekee virheen käsittelystä pakollista ja näkyvää.
- **`unknown` catch-lohkoon ja kavennus.** Älä oleta, että heitetty
  arvo on `Error`.
- **Brändi invariantille.** Kun arvon kelpoisuus on tarkistettu, merkitse
  se tyyppiin, jotta tarkistusta ei tarvitse toistaa.

## Itsearviointi

- Osaat käsitellä `unknown`-tyyppisen `catch`-muuttujan, kirjoittaa oman
  virheluokan ja ketjuttaa virheet `cause`-kentällä.
- Osaat suunnitella `Tulos`-tyypin ja valita virheen arvona ja
  poikkeuksen välillä.
- Osaat jäsentää ulkoisen datan `unknown`ista tyypitetyksi niin, että
  tyyppi johdetaan skeemasta.
- Osaat käyttää brändättyjä tyyppejä estämään samanmuotoisten arvojen
  sekoittumisen.
