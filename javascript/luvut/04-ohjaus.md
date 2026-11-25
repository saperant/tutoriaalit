# Ohjausrakenteet ja funktiot {.runko-ohjaus}

Ohjausrakenteet ovat JavaScriptissa tuttuja C-sukuisista kielistä, ja
niistä käydään läpi vain erot. Luvun paino on funktioissa: ne ovat
arvoja, ne muistavat ympäristönsä (sulkeuma), ja niiden `this`
määräytyy kutsuhetkellä. Näihin kolmeen asiaan perustuvat lähes
kaikki myöhempien lukujen mallit.

## Ohjausrakenteet

`if`, `while`, `do`–`while` ja C-tyylinen `for` toimivat kuten C:ssä
ja Javassa. Ehdossa kelpaa mikä tahansa arvo: epätosia ovat `false`,
`0`, `-0`, `0n`, `""`, `null`, `undefined` ja `NaN`, kaikki muu on
totta (myös `[]` ja `{}`).

Kokoelmien läpikäyntiin on kaksi silmukkaa, joita ei pidä sekoittaa:

```{.javascript tiedosto="esimerkit/04-ohjaus.js" osa="silmukat"}
```

`for...of` käy läpi arvot mistä tahansa iteroitavasta (taulukko,
merkkijono, `Map`, `Set`, generaattori). `for...in` käy läpi olion
avaimet merkkijonoina, myös perityt, eikä sovi taulukoille. Olion
kentät käydään läpi `Object.entries`-funktiolla ja purkamisella.

`switch` vertaa `===`-operaattorilla ja valuu seuraavaan haaraan ilman
`break`- tai `return`-lausetta. Muoto `switch (true)` valitsee
ensimmäisen toteutuvan ehdon, mikä on luettava tapa ilmaista
väliluokittelu:

```{.javascript tiedosto="esimerkit/04-ohjaus.js" osa="switch"}
```

Nimetty `break` poistuu sisäkkäisistä silmukoista:

```{.javascript tiedosto="esimerkit/04-ohjaus.js" osa="nimetty"}
```

```{.tuloste tiedosto="esimerkit/04-ohjaus.odotettu"}
```

Usein selkeämpää on kuitenkin siirtää haku omaan funktioonsa ja
palata `return`-lauseella.

## Funktiot

Funktion voi määritellä kolmella tavalla: funktiolauseena
(`function nimi() {}`), joka nostetaan näkyvyysalueensa alkuun,
funktiolausekkeena ja nuolifunktiona (`(x) => x * 2`). Nuolifunktiolla
ei ole omaa `this`-arvoa eikä `arguments`-oliota, eikä sitä voi kutsua
`new`-operaattorilla. Se on oletus takaisinkutsuille ja lyhyille
funktioille.

JavaScriptissa ei ole nimettyjä parametreja eikä ylikuormitusta. Niiden
sijaan käytetään optio-oliota, joka puretaan parametrilistassa
oletusarvoineen:

```{.javascript tiedosto="esimerkit/04-funktiot.js" osa="parametrit"}
```

Optio-olio on itsedokumentoiva (`{ viive: 500 }` kertoo enemmän kuin
`500`), ja uuden option voi lisätä rikkomatta kutsujia. Lopun `= {}`
sallii kutsun kokonaan ilman optioita.

Loppuparametri `...luvut` kerää loput argumentit taulukoksi, ja
levitys `...mittaukset` tekee päinvastoin:

```{.javascript tiedosto="esimerkit/04-funktiot.js" osa="rest"}
```

Funktiot ovat arvoja: niitä välitetään parametreina, palautetaan ja
tallennetaan tietorakenteisiin. Putki koostaa vaiheet yhdeksi
funktioksi:

```{.javascript tiedosto="esimerkit/04-funktiot.js" osa="arvoina"}
```

```{.tuloste tiedosto="esimerkit/04-funktiot.odotettu"}
```

JSDoc-tyyppi `@template T` tekee funktiosta geneerisen: tarkistin
päättelee, että `putki` saa ja palauttaa saman tyypin.

## Sulkeumat

Sulkeuma on funktio, joka muistaa näkyvyysalueen, jossa se luotiin.
Sulkeumalla toteutetaan yksityinen tila ilman luokkaa (*moduulimalli*):

```{.javascript tiedosto="esimerkit/04-sulkeumat.js" osa="laskuri"}
```

Muuttujaan `kaytetty` pääsee käsiksi vain palautetun olion metodeilla.
Sama malli on tehdasfunktion pohja (luku 9).

Sulkeuma kaappaa muuttujan, ei sen arvoa. Vanhan `var`-silmukan
funktiot jakavat yhden muuttujan, kun taas `let` luo jokaiselle
kierrokselle omansa:

```{.javascript tiedosto="esimerkit/04-sulkeumat.js" osa="silmukka"}
```

Memoisaatio on sulkeuman tyyppikäyttö: funktio muistaa aiemmat
tuloksensa piilotetussa `Map`-rakenteessa.

```{.javascript tiedosto="esimerkit/04-sulkeumat.js" osa="memo"}
```

```{.tuloste tiedosto="esimerkit/04-sulkeumat.odotettu"}
```

## this

Metodissa `this` viittaa olioon, jonka kautta metodia kutsuttiin.
Esimerkit käyttävät luokkia, jotka luku 7 käy läpi; tässä riittää
tietää, että `new Luokka()` luo olion ja että luokan sisällä
määritellyt funktiot ovat sen metodeja. `this` määräytyy kutsutavan
mukaan:

| Kutsu | `this` |
|-------|--------|
| `olio.metodi()` | `olio` |
| `metodi()` (irrotettu) | `undefined` (tiukka tila) |
| `metodi.call(x)`, `metodi.apply(x)` | `x` |
| `metodi.bind(x)` | uusi funktio, jossa `this` on aina `x` |
| `new Luokka()` | uusi olio |
| nuolifunktio | ympäröivän näkyvyysalueen `this` |

```{.javascript tiedosto="esimerkit/04-this.js" osa="saannot"}
```

Luokan kenttään tallennettu nuolifunktio sitoo `this`-arvon olioon,
joten sen voi välittää takaisinkutsuna. Hinta on, että jokaisella
oliolla on oma funktionsa eikä metodi ole prototyypissä. Metodin sisällä
nuolifunktio perii metodin `this`-arvon:

```{.javascript tiedosto="esimerkit/04-this.js" osa="takaisinkutsu"}
```

```{.tuloste tiedosto="esimerkit/04-this.odotettu"}
```

`return this` mahdollistaa metodien ketjutuksen (*fluent interface*).

## Käytännössä

- **Optio-olio yli kahdelle parametrille.** Oletusarvot purkamisessa ja
  `= {}` lopussa. Totuusarvoparametri on lähes aina optio
  (`tallenna(tiedot, { korvaa: true })`, ei `tallenna(tiedot, true)`).
- **Nuolifunktiot takaisinkutsuihin, metodisyntaksi metodeihin.**
  Silloin `this` toimii odotetusti molemmissa.
- **Puhtaat funktiot ja muuttumaton data.** Funktio, joka ei muuta
  parametrejaan eikä ulkoista tilaa, on helppo testata, memoisoida ja
  koostaa.
- **Varhainen paluu** pitää onnistuneen polun vasemmassa reunassa.
- **Älä käytä `arguments`-oliota, `eval`-funktiota tai `with`-lausetta.**
  Loppuparametri korvaa ensimmäisen, ja kaksi muuta estävät optimoinnit
  ja ovat tietoturvariski.
- **Hinta.** Funktiokutsu ja sulkeuman luonti ovat halpoja, ja V8
  laajentaa pienet funktiot inline-koodiksi. Sulkeuma pitää kuitenkin
  kaapatut muuttujat elossa: suuren datan kaappaava, pitkäikäinen
  takaisinkutsu (ajastin, tapahtumankuuntelija) on yleinen muistivuoto.

## Itsearviointi

- Osaat valita `for...of`- ja `for...in`-silmukan välillä ja käydä
  olion kentät läpi `Object.entries`-funktiolla.
- Osaat kirjoittaa funktion, joka ottaa optio-olion oletusarvoineen,
  ja käyttää loppuparametria ja levitystä.
- Osaat toteuttaa yksityisen tilan sulkeumalla ja selittää, miksi
  `var`-silmukan sulkeumat näkevät saman arvon.
- Osaat kertoa, mikä `this` on kussakin kutsutavassa, ja korjata
  irrotetun metodin.
