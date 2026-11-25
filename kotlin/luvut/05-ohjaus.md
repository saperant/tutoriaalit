# Ohjausrakenteet ja funktiot {.runko-ohjaus}

Tyypit ja null-turvallisuus on nyt käsitelty, joten seuraavaksi
kootaan lausekkeista ohjelmia. Silmukat ja ehdot poikkeavat Javasta
vähän, funktiot paljon: oletusargumentit, laajennusfunktiot ja
lambdan kirjoittaminen sulkujen jälkeen ovat piirteitä, joiden varaan
vakiokirjasto ja seuraavien lukujen esimerkit rakentuvat.

## Silmukat, välit ja when

Kotlinissa ei ole Javan kolmiosaista `for`-silmukkaa. `for` käy läpi
minkä tahansa iteroitavan: kokoelman, välin tai merkkijonon. Välit
kirjoitetaan `a..b` (suljettu), `a..<b` (puoliavoin), `b downTo a` ja
`step n`. `in` tarkistaa kuulumisen väliin tai kokoelmaan. Luvussa 3
`when` oli lauseke, joka valitsi arvon; seuraava lekseri käyttää sen
kaikkia haaramuotoja ja näyttää silmukat oikeassa tehtävässä,
merkkijonon pilkkomisessa sanasiksi:

```{.kotlin tiedosto="esimerkit/05-lekseri.kt"}
```

```{.tuloste tiedosto="esimerkit/05-lekseri.odotettu"}
```

- `when` ilman argumenttia on `if-else`-ketju, argumentin kanssa
  `switch`, joka hyväksyy vakiot, välit (`in`), tyyppitarkistukset
  (`is`) ja useita arvoja pilkulla erotettuna.
- `throw` on lauseke, jonka tyyppi on `Nothing`, joten se kelpaa
  `when`-haaraksi missä tahansa.
- Nimetty silmukka (`ulompi@`) ja `break@ulompi` poistuvat sisäkkäisistä
  silmukoista ilman lippumuuttujaa.
- Tilakone, joka on kirjoitettu `while`-silmukkana ja `when`-lausekkeena,
  on edelleen selkein tapa jäsentää merkkivirtaa käsin.

## Funktiot

Funktion parametreilla voi olla oletusarvot, ja argumentit voi antaa
nimellä. Tämä korvaa Javan ylikuormitusketjut ja useimmat
rakentajaoliot. Yksilausekkeinen funktio kirjoitetaan `=`-merkillä ja
sen paluutyyppi päätellään.

```{.kotlin tiedosto="esimerkit/05-funktiot.kt"}
```

```{.tuloste tiedosto="esimerkit/05-funktiot.odotettu"}
```

- Funktiotyyppi `(Ilmoitus) -> Boolean` on rajapinta, jota lambda,
  funktioviite (`::onKiireellinen`) tai olio toteuttaa.
- Jos viimeinen parametri on funktio, lambda kirjoitetaan sulkujen
  jälkeen (*trailing lambda*). Tämä tekee kokoelmafunktioista ja
  DSL:istä (luku 10) luettavia.
- Yksiparametrisen lambdan parametri on `it`. Kun lambda on pitkä tai
  sisäkkäinen, nimeä parametri.
- `tailrec` muuttaa häntärekursion silmukaksi. Kääntäjä varoittaa, jos
  kutsu ei ole häntäasemassa.
- Paikallinen funktio (`laheta`) näkee ympäröivän funktion muuttujat
  ja voi muuttaa niitä. Se on sulkeuma.

## Laajennusfunktiot

Laajennusfunktio lisää tyyppiin uuden operaation muuttamatta tyyppiä.
Kutsupaikassa se näyttää metodilta, mutta tavukoodissa se on staattinen
metodi, jonka ensimmäinen parametri on vastaanottaja.

```{.kotlin tiedosto="esimerkit/05-laajennus.kt"}
```

```{.tuloste tiedosto="esimerkit/05-laajennus.odotettu"}
```

- Laajennus näkee vain vastaanottajan julkiset jäsenet. Se ei riko
  kapselointia.
- Laajennusominaisuudella ei ole taustakenttää, joten sen arvo
  lasketaan joka käytöllä.
- Nullable-vastaanotin (`String?.`) sallii kutsun myös `null`-arvolle.
  Vakiokirjaston `isNullOrBlank` ja `orEmpty` ovat tällaisia.
- Laajennus valitaan muuttujan **staattisen** tyypin mukaan:
  `m.nimi()` kutsuu `Muoto`-tyypin laajennusta, vaikka olio on
  `Ympyra`. Kun tarvitaan dynaamista sidontaa, tarvitaan jäsenmetodi.
- Jos luokalla on samanniminen jäsenmetodi, jäsen voittaa aina.

## Scope-funktiot

Vakiokirjaston viisi scope-funktiota ajavat lohkon olion yhteydessä.
Ne eroavat siinä, miten olioon viitataan ja mitä funktio palauttaa:

| Funktio | Olio lohkossa | Palauttaa | Tyypillinen käyttö |
|---------|---------------|-----------|--------------------|
| `let` | `it` | lohkon arvon | muunnos, nullable-arvon käsittely |
| `run` | `this` | lohkon arvon | arvon laskeminen olion jäsenistä |
| `with(x)` | `this` | lohkon arvon | useita kutsuja samalle oliolle |
| `apply` | `this` | olion | alustus ja asetukset |
| `also` | `it` | olion | sivuvaikutus ketjussa: loki, tarkistus |

```{.kotlin tiedosto="esimerkit/05-scope.kt"}
```

```{.tuloste tiedosto="esimerkit/05-scope.odotettu"}
```

`takeIf` ja `takeUnless` palauttavat olion tai `null`-arvon ehdon
mukaan, joten ne yhdistyvät elvis-operaattoriin.

## Käytännössä

- **Oletus- ja nimetyt argumentit rakentajan sijaan.** Monen
  valinnaisen parametrin funktio tai `data class` oletusarvoineen
  korvaa rakentajamallin (*builder*). Nimeä argumentit kutsussa, kun
  niitä on useita samaa tyyppiä tai `Boolean`-tyyppisiä.
- **Laajennukset apuluokkien tilalle.** `StringUtils.isBlank(s)` on
  Kotlinissa `s.isBlank()`. Kirjoita laajennus sen tiedoston tai paketin
  yhteyteen, jossa sitä tarvitaan, ja pidä se `private`- tai
  `internal`-näkyvyydellä, ellei se ole yleiskäyttöinen.
- **Scope-funktiot säästeliäästi.** `apply` alustukseen ja `let`
  nullable-arvolle ovat idiomaattisia. Jos lohkoja on sisäkkäin
  useampi kuin yksi, kirjoita tilapäinen muuttuja: luettavuus ratkaisee.
- **Hinta:** lambda tavallisen (ei-inline) funktion parametrina on olio.
  Kaappaamaton lambda on singleton, kaappaava luodaan joka kutsulla.
  `inline` poistaa molemmat (luku 6).
- **Hinta:** oletusargumentit toteutetaan apumetodilla ja bittimaskilla.
  Kustannus on mitätön, mutta Java-kutsuja näkee vain täyden
  parametrilistan ilman `@JvmOverloads`-annotaatiota (luku 11).
- **Sudenkuoppa:** `return` lambdassa palaa ympäröivästä funktiosta vain
  `inline`-funktioissa (kuten `forEach`). Lambdasta itsestään palataan
  nimiöllä: `return@forEach`.

## Itsearviointi

- Osaat käyttää välejä (`..`, `..<`, `downTo`, `step`) ja `when`-
  lauseketta argumentin kanssa ja ilman.
- Osaat kirjoittaa funktion oletus- ja nimetyillä parametreilla sekä
  korkeamman asteen funktion, joka ottaa tai palauttaa funktion.
- Osaat kirjoittaa laajennusfunktion ja selittää, miksi se valitaan
  staattisen tyypin mukaan.
- Osaat valita sopivan scope-funktion ja tunnistat, milloin tilapäinen
  muuttuja on selkeämpi.
