# Unionit ja tilakoneet {.runko-omat-tyypit}

Eroteltu unioni (*discriminated union*) on TypeScriptin tärkein
suunnittelun väline. Se vastaa Rustin `enum`ia ja Kotlinin
`sealed`-luokkia: arvo on täsmälleen yksi vaihtoehdoista, ja jokaisella
vaihtoehdolla on omat kenttänsä.

## Mahdottomat tilat pois

Tavallinen tapa kuvata tilaus on yksi tyyppi, jossa on kaikki kentät
valinnaisina: `tila`, `maksuviite?`, `seurantakoodi?`, `syy?`. Tällainen
tyyppi sallii mahdottomat yhdistelmät, kuten lähetetyn tilauksen ilman
seurantakoodia tai perutun tilauksen, jolla on maksuviite. Jokainen
käyttökohta joutuu tarkistamaan kentät erikseen.

Eroteltu unioni kuvaa jokaisen tilan omana tyyppinään. Yhteinen
literaalikenttä (`tila`) on *erotin*, jonka tarkistus kaventaa tyypin:

```{.typescript tiedosto="esimerkit/06-tilakone.ts"}
```

```{.tuloste tiedosto="esimerkit/06-tilakone.odotettu"}
```

- `siirry` on tilakoneen siirtymäfunktio: vanha tila ja tapahtuma
  sisään, uusi tila ulos. Kielletty siirtymä on poikkeus, koska se
  tarkoittaa ohjelmointivirhettä tai väärää käyttöä.
- `kuvaa` käsittelee kaikki tilat. Koska `switch` kattaa unionin,
  funktiolla ei ole puuttuvaa paluuarvoa. Uusi tila ilman käsittelyä
  olisi käännösvirhe, koska merkitty paluutyyppi `string` ei salli
  `undefined`ia (vrt. kattavuustarkistus, luku 4).
- Kentät, kuten `maksuviite`, ovat pakollisia siinä tilassa, jossa ne
  ovat merkityksellisiä. Kenttää ei tarvitse tarkistaa käytettäessä.

Malli tunnetaan nimellä *make illegal states unrepresentable*. Sama
rakenne sopii verkkopyynnön tilaan (`lataa`, `valmis`, `virhe`),
käyttöliittymän näkymiin, viesteihin ja jäsennyspuun solmuihin.

## enumin korvaajat

`enum` ei ole poistettavaa syntaksia (luku 2). Sen tilalle on kolme
mallia sen mukaan, mitä tarvitaan:

```{.typescript tiedosto="esimerkit/06-vakiot.ts"}
```

```{.tuloste tiedosto="esimerkit/06-vakiot.odotettu"}
```

| Tarve | Malli |
|-------|-------|
| Joukko nimettyjä vaihtoehtoja | Literaaliunioni (`type Taso`) |
| Nimet ja niihin liittyvät arvot | `as const` -olio ja `(typeof O)[keyof typeof O]` |
| Arvojen läpikäynti ja tarkistus ajossa | `as const` -taulukko ja `(typeof T)[number]` |

`as const` tekee literaalista syvästi `readonly`-tyyppisen ja säilyttää
literaalityypit. `satisfies Taso[]` tarkistaa, että taulukon arvot
kuuluvat unioniin, mutta ei levennä tyyppiä (luku 8). Ajonaikainen
tarkistus `onTaso` tarvitaan, kun arvo tulee ulkoa merkkijonona.

Numeeristen `enum`ien ongelmia, joita korvaajissa ei ole: mikä tahansa
luku kelpaa `enum`-tyyppiseen paikkaan, käänteinen kuvaus tuottaa
yllätyksiä, eikä kahta samanlaista `enum`ia voi sijoittaa toisiinsa
rakenteellisesti.

## Käytännössä

- **Mallinna tilat unioneina, älä lippuina.** Jos tyypissä on
  `onLadattu: boolean` ja `virhe?: string`, ne kuvaavat todennäköisesti
  tilaa, joka kuuluu erotelluksi unioniksi.
- **Erotin on literaali.** Käytä samaa kenttää (`laji`, `tyyppi`,
  `tila`) kaikissa vaihtoehdoissa ja merkkijonoliteraaleja arvoina.
  Merkkijonot näkyvät lokeissa ja JSONissa luettavina.
- **Siirtymät yhteen funktioon.** Tilakoneen säännöt ovat yhdessä
  paikassa, ja kielletyt siirtymät käsitellään keskitetysti. Sama malli
  on Reduxin ja `useReducer`in reduktori.
- **Kattavuus aina.** Jokainen unionin `switch` päättyy
  kattavuustarkistukseen tai palauttaa arvon jokaisesta haarasta.
- **Literaaliunioni ensin, `as const` kun tarvitaan arvoja.** Pelkkä
  unioni on yksinkertaisin ja riittää useimmiten.

## Itsearviointi

- Osaat mallintaa tilakoneen erotelluilla unioneilla niin, että
  mahdottomia tiloja ei voi esittää.
- Osaat kirjoittaa siirtymäfunktion ja käsitellä kaikki tilat
  kattavasti.
- Osaat korvata `enum`in literaaliunionilla, `as const` -oliolla tai
  -taulukolla ja johtaa niistä tyypin.
- Osaat tarkistaa ajossa, kuuluuko merkkijono literaaliunioniin.
