# DSL:t, operaattorit ja delegointi

Kotlinin syntaksi on suunniteltu niin, että kirjastot voivat tarjota
rajapintoja, jotka näyttävät kielen omilta rakenteilta. Gradlen
`build.gradle.kts`, Ktorin reititys, Jetpack Compose ja
`kotlinx.html` ovat tällaisia *sisäisiä DSL:iä*. Ne rakentuvat
kolmesta piirteestä: vastaanottajallisesta lambdasta, operaattorien
ylikuormituksesta ja delegoinnista.

## Vastaanottajallinen lambda

Funktiotyyppi `Taulukko.() -> Unit` on lambda, jonka sisällä `this` on
`Taulukko`. Rakentajafunktio luo olion, ajaa lambdan sitä vasten
(`apply`) ja palauttaa tuloksen. Kutsupaikassa lohkot näyttävät
sisäkkäisiltä elementeiltä.

```{.kotlin tiedosto="esimerkit/10-dsl.kt"}
```

```{.tuloste tiedosto="esimerkit/10-dsl.odotettu"}
```

Ilman `@DslMarker`-annotaatiota `taulukko`-lohkon sisällä voisi kutsua
ulomman `Raportti`-olion `kappale`-funktiota, koska molemmat
vastaanottajat ovat näkyvissä. Annotaatio rajaa implisiittiset
vastaanottajat sisimpään, ja virheellinen sisäkkäisyys on
käännösvirhe.

## Operaattorit

Operaattori ylikuormitetaan merkitsemällä nimetty funktio sanalla
`operator`. Joukko on kiinteä, eikä uusia symboleita voi keksiä:

| Lauseke | Funktio |
|---------|---------|
| `a + b`, `a * b`, `-a` | `plus`, `times`, `unaryMinus` |
| `a += b` | `plusAssign` (tai `plus` ja sijoitus) |
| `a[i]`, `a[i] = x` | `get`, `set` |
| `x in a` | `contains` |
| `a(x)` | `invoke` |
| `a < b` | `compareTo` |
| `val (x, y) = a` | `component1`, `component2` |
| `a..b`, `a..<b` | `rangeTo`, `rangeUntil` |

Luvun 6 `Sentit`-arvoluokka käytti `plus`- ja `times`-operaattoreita.
Operaattori kannattaa määritellä vain, kun sen merkitys on lukijalle
ilmeinen: rahasummien yhteenlasku kyllä, tilauksen "kertominen"
asiakkaalla ei.

## Delegointi

`by` ohjaa toteutuksen toiselle oliolle. **Luokan delegointi**
toteuttaa rajapinnan välittämällä kaikki kutsut kentälle; vain
muuttuvat metodit kirjoitetaan. Tämä tekee koristelijamallista
(*decorator*) muutaman rivin mittaisen. **Delegoitu ominaisuus**
siirtää getterin ja setterin logiikan oliolle, jolla on
`getValue`- ja `setValue`-operaattorit.

```{.kotlin tiedosto="esimerkit/10-delegointi.kt"}
```

```{.tuloste tiedosto="esimerkit/10-delegointi.odotettu"}
```

| Delegaatti | Käyttö |
|------------|--------|
| `by lazy { }` | kallis arvo lasketaan ensimmäisellä käytöllä |
| `by Delegates.observable(alku) { }` | kuuntelija jokaiselle muutokselle |
| `by Delegates.vetoable(alku) { }` | muutos hyväksytään tai hylätään |
| `by map` | ominaisuus luetaan mapista nimellä (asetukset, JSON) |
| `by ::toinen` | ominaisuus on toisen alias (vanhan nimen säilytys) |

## Käytännössä

- **DSL rakenteiselle konfiguraatiolle ja puille**: käyttöliittymät,
  raportit, reitit, testiaineisto, käännösskriptit. Lineaariselle
  logiikalle tavallinen funktiokutsu on parempi.
- **`@DslMarker` jokaiseen DSL:ään.** Se estää virheet, joissa
  sisemmässä lohkossa kutsutaan vahingossa ulomman tason funktiota.
- **Luokan delegointi periytymisen sijaan**, kun haluat muuttaa
  yhden tai kaksi metodia valmiista toteutuksesta. Periytyminen
  `HashSet`-luokasta ja `add`-metodin ylikirjoitus rikkoutuu, jos
  `addAll` kutsuu sisäisesti `add`-metodia, kuten *Effective Java*
  kuvaa. Delegoinnissa `addAll` ohjautuu sisäiselle joukolle, joten
  esimerkki ylikirjoittaa sen itse.
- **Hinta:** `lazy` on oletuksena synkronoitu (`SYNCHRONIZED`). Jos
  arvoa käytetään vain yhdestä säikeestä, `lazy(LazyThreadSafetyMode.NONE)`
  poistaa lukituksen.
- **Hinta:** delegoitu ominaisuus luo apuolion jokaista oliota kohden.
  Miljoonien olioiden luokassa se näkyy muistissa.
- **Sudenkuoppa:** `by map` heittää poikkeuksen vasta luettaessa, jos
  avain puuttuu tai tyyppi ei täsmää. Ulkoista dataa varten
  validoiva jäsennys (luku 9) on turvallisempi.

## Itsearviointi

- Osaat kirjoittaa vastaanottajallista lambdaa käyttävän
  rakentajafunktion ja suojata sen `@DslMarker`-annotaatiolla.
- Osaat ylikuormittaa operaattorin ja arvioida, onko sen merkitys
  ilmeinen.
- Osaat toteuttaa rajapinnan luokan delegoinnilla ja selittää, miksi se
  on turvallisempi kuin periytyminen.
- Osaat käyttää delegoituja ominaisuuksia `lazy`, `observable` ja
  `by map` ja tiedät niiden hinnan.
