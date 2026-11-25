# Arkkitehtuuri: tila, ViewModel ja repository

Androidin suositeltu arkkitehtuuri jakaa sovelluksen kerroksiin, joista
jokainen tietää vain alemmasta:

```{.dot otsikko="Kerrokset: tapahtumat ja kutsut kulkevat alas, tila ja data ylös"}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.45;
  ui [label="käyttöliittymä (composablet)\npiirtää tilan, välittää tapahtumat"];
  vm [label="ViewModel\nruudun tila ja logiikka"];
  repo [label="repository\nainoa tie dataan"];
  ui -> vm [label=" tapahtumat"];
  vm -> ui [label=" tila (StateFlow)", color="#5B8A72", fontcolor="#5B8A72"];
  vm -> repo [label=" kutsut"];
  repo -> vm [label=" data (Flow)", color="#5B8A72", fontcolor="#5B8A72"];
  node [shape=cylinder];
  kanta [label="tietokanta"]; verkko [label="verkko"]; asetukset [label="asetukset"];
  repo -> kanta; repo -> verkko; repo -> asetukset;
}
```

Kerrosten ansiosta jokainen osa voidaan testata erikseen ja
tietolähteen voi vaihtaa koskematta käyttöliittymään. Luku etenee
ylhäältä alas: ruudun tila, ViewModel, ruudun sivuvaikutukset,
repository ja lopuksi se, miten oliot kootaan ja testataan.

## UI-tila yhtenä arvona

Ruudun koko tila kuvataan yhdellä muuttumattomalla arvolla:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaViewModel.kt" osa="tila"}
```

Viesti on suljettu tyyppi eikä merkkijono: ViewModel kertoo, mitä
tapahtui, ja käyttöliittymä valitsee sanamuodon resursseista (luku 2),
jolloin kieli vaihtuu ja monikkomuodot toimivat:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaRuutu.kt" osa="teksti"}
```

Yksi arvo takaa, ettei käyttöliittymä näe ristiriitaisia välitiloja
(esim. lista päivittyi mutta latausilmaisin ei vielä). Johdetut arvot
(`voiLisata`, `ostamatta`) lasketaan tilasta eikä tallenneta erikseen,
joten ne eivät voi joutua ristiriitaan.

## ViewModel

ViewModel säilyy konfiguraatiomuutoksen yli ja tarjoaa
`viewModelScope`n, joka peruuntuu, kun ViewModel lopullisesti
tuhotaan. Se ei viittaa Activityyn, Contextiin eikä composableihin,
joten se on tavallista Kotlinia ja testattavissa JVM:llä.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaViewModel.kt" osa="viewmodel"}
```

- **Tila on `StateFlow`**, jolla on aina arvo. Repositoryn Flow ja
  ruudun oma tila yhdistetään `combine`lla.
- **`stateIn(WhileSubscribed(5_000))`** kerää lähdettä vain, kun
  käyttöliittymä tilaa. Viiden sekunnin viive pitää keruun käynnissä
  konfiguraatiomuutoksen yli, mutta lopettaa sen, kun sovellus on
  taustalla. Tämä säästää akkua ja tietokantakyselyjä.
- **Tapahtumat ovat funktioita** (`lisaa`, `merkitse`). Käyttöliittymä
  ei muokkaa tilaa suoraan.
- **Pitkä työ `viewModelScope`ssa.** Jos käyttäjä poistuu ruudulta
  kesken, työ peruuntuu automaattisesti.

Ruutu kerää tilan elinkaaren mukaan:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaRuutu.kt" osa="tilallinen"}
```

`collectAsStateWithLifecycle` lopettaa keruun, kun ruutu ei ole
näkyvissä (alle `STARTED`). Pelkkä `collectAsState` keräisi
taustallakin. Tilallinen ruutu on ohut: se vain kytkee ViewModelin
tilattomaan sisältöön.

## Sivuvaikutukset

Ruudussa tehdään myös asioita, jotka eivät ole piirtämistä: näytetään
ilmoitus, käynnistetään animaatio, rekisteröidään kuuntelija.
Composable-funktion runko voi suorittua milloin tahansa (luku 3),
joten toiminnot, jotka muuttavat jotain funktion ulkopuolella, tehdään
**efekteissä**. Efekti on sidottu koostumukseen: se alkaa, kun
composable tulee näkyviin, ja peruuntuu, kun se poistuu.

| Efekti | Käyttö |
|--------|--------|
| `LaunchedEffect(avain)` | korutiini, joka käynnistyy uudelleen avaimen muuttuessa: ilmoitus, animaatio, kertaluonteinen haku |
| `DisposableEffect(avain)` | rekisteröinti ja purku (`onDispose`): kuuntelija, sensori, elinkaaritarkkailija |
| `SideEffect` | suoritetaan jokaisen onnistuneen koostamisen jälkeen; tilan välitys koodille, jota Compose ei hallitse |
| `rememberCoroutineScope()` | korutiini tapahtumankäsittelijästä, esim. vieritys napin painalluksesta |
| `rememberUpdatedState(arvo)` | pitkäkestoinen efekti näkee uusimman arvon ilman uudelleenkäynnistystä |
| `derivedStateOf` | tila, joka lasketaan toisesta tilasta ja muuttuu harvemmin (esim. "vieritetty alas") |

Ostoslistan tilaton sisältö saa koko tilan parametrina. Kun tilassa
on viesti, se näytetään ilmoituksena (*snackbar*) ja kuitataan:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaRuutu.kt" osa="tilaton"}
```

`LaunchedEffect(viesti)` käynnistyy aina, kun viesti vaihtuu, ja
`showSnackbar` odottaa, kunnes ilmoitus suljetaan. Jos ruutu poistuu
kesken, korutiini peruuntuu, eikä viestiä kuitata. Viestin teksti
haetaan resursseista koostamisen aikana, koska efektin korutiini ei
ole composable-funktio.

![Synkronoinnin jälkeen: viesti näkyy ilmoituksena ruudun
alareunassa.](kuvat/viesti.png){width=32%}

Samassa funktiossa on sovelluksen ainoa lomake. Tekstikenttä on tilaton
kuten muutkin komponentit: `value` tulee tilasta ja `onValueChange`
vie jokaisen muutoksen ViewModeliin, joten kentän sisältö säilyy
konfiguraatiomuutoksessa. `KeyboardOptions` valitsee näppäimistön
toimintonäppäimen, ja painike on käytössä vain, kun tilasta johdettu
`voiLisata` on tosi. Virheellinen syöte näytetään samalla tavalla
tilasta: `isError` ja `supportingText` kentässä.

Testi kelaa Composen kelloa, jotta ilmoituksen aikakatkaisu kuluu
heti:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/lista/ListaSisaltoTest.kt" osa="testi"}
```

Ensimmäinen testi näyttää tilan nostamisen arvon: tilaton ruutu
testataan antamalla sille tila, ilman ViewModelia, tietokantaa tai
verkkoa.

## Korutiinien näkyvyysalueet

Jokainen korutiini käynnistetään näkyvyysalueessa, joka päättää, milloin
se peruuntuu. Käyttöliittymäkerroksessa alueita on kolme:

- **`viewModelScope`**: ruudun logiikka. Peruuntuu, kun ViewModel
  tuhotaan eli ruutu poistetaan pinosta (luku 6).
- **Efektit** (`LaunchedEffect`, `rememberCoroutineScope`): työ, joka
  kuuluu koostumukseen ja peruuntuu, kun composable poistuu.
- **`collectAsStateWithLifecycle`** ja **`repeatOnLifecycle`**:
  keräävät Flow'ta vain, kun käyttöliittymä on näkyvissä. Taustalla
  kerätty Flow pitää tietokantakyselyt ja sensorit käynnissä turhaan.

**`GlobalScope`** ei kuulu sovelluskoodiin: sen korutiineja ei voi
peruuttaa, eikä niiden virheitä käsitellä. Työ, jonka pitää valmistua
ruudusta riippumatta, annetaan WorkManagerille (luku 9).

## Repository

Repository on rajapinta, jonka takana tietolähteet ovat:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/data/OstosRepository.kt" osa="rajapinta"}
```

ViewModel ei tiedä, tuleeko lista tietokannasta, verkosta vai
muistista. Toteutus esitellään luvussa 8; tässä riittää, että
repository tarjoaa tuotteet Flow'na ja muutokset suspend-funktioina.

## Riippuvuuksien injektointi käsin

Olioiden ei pidä luoda omia riippuvuuksiaan, vaan ne annetaan
muodostimen parametreina. Pienessä sovelluksessa riittää yksi
**säiliö**, joka kokoaa oliot:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/Sailio.kt" osa="sailio"}
```

`Application` omistaa säiliön (luku 2), ja navigointi luo
ViewModelin säiliön tehtaalla (luku 6). Testit eivät käytä säiliötä
lainkaan, vaan antavat ViewModelille väärennöksen.

Isommissa sovelluksissa käytetään **Hiltiä** (Daggerin päälle
rakennettu, Googlen suosittelema) tai **Koinia**. Ne generoivat tai
ratkaisevat saman kokoamisen automaattisesti, tarjoavat
elinkaarisidonnaiset näkyvyysalueet (`@Singleton`, `@ViewModelScoped`)
ja `hiltViewModel()`-funktion. Periaate on sama kuin käsin: riippuvuus
tulee ulkoa.

## ViewModelin testaus

ViewModel testataan JVM:llä ilman Robolectricia. Kaksi apuvälinettä:
sääntö, joka korvaa pääsäikeen dispatcherin, ja väärennetty
repository.

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/testi/Apuvalineet.kt" osa="saannot"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/testi/Apuvalineet.kt" osa="vaarennos"}
```

Testi kerää tilaa **Turbine**-kirjastolla, joka tekee Flow'n arvoista
jonon: `awaitItem` odottaa seuraavaa arvoa, ja testi epäonnistuu, jos
arvoja jää käsittelemättä. StateFlow yhdistää peräkkäiset arvot, joten
välitilojen määrä voi vaihdella koneen nopeuden mukaan. Siksi testit
odottavat ehtoja (`odota`) eivätkä laske tiloja: tiloja laskeva versio
meni läpi kehityskoneella mutta epäonnistui toisinaan CI:ssä.

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/lista/ListaViewModelTest.kt" osa="testi"}
```

Väärennös (*fake*) on toimiva toteutus muistissa. Se on parempi kuin
mokkaus (*mock*) kirjastolla, koska testi tarkistaa lopputuloksen eikä
sitoudu siihen, mitä metodeja missä järjestyksessä kutsuttiin. Sama
väärennös palvelee ViewModel-, navigointi- ja taustatyötestejä.

## Käytännössä

- **Yksisuuntainen datavirta (UDF).** Tila virtaa ViewModelista alas,
  tapahtumat käyttöliittymästä ylös. Kun tila muuttuu vain yhdessä
  paikassa, virheen syy löytyy yhdestä paikasta.
- **Yksi totuuden lähde** (*single source of truth*). Jokaisella
  tiedolla on yksi omistaja: lista tietokannassa, syötekentän teksti
  ViewModelissa, vierityksen sijainti käyttöliittymässä. Kopiot
  vanhenevat.
- **Ei sivuvaikutuksia rungossa.** Lokitus, analytiikka, verkkopyyntö
  tai tilan kirjoittaminen rungossa toistuu jokaisella koostamisella.
  Valitse efekti sen mukaan, milloin työn pitää alkaa ja loppua.
- **Kertaluonteinen tapahtuma on tilaa, joka kuitataan.** Viesti tai
  siirtymä mallinnetaan tilaan (`viesti: Viesti?`), käyttöliittymä
  käsittelee sen efektissä ja kuittaa. Näin tapahtuma ei katoa
  konfiguraatiomuutoksessa eikä toistu.
- **ViewModel ei tunne Androidia.** Ei Contextia, ei resursseja, ei
  composableja. Merkkijonon sijaan ViewModel palauttaa tyypin
  (`Viesti`), ja käyttöliittymä hakee tekstin resursseista.
- **Riippuvuudet muodostimeen.** Luokka, joka luo itse tietokantansa,
  on testattavissa vain oikealla tietokannalla.
- **Hinnat:** `StateFlow` vertaa uutta arvoa vanhaan `equals`illa ja
  jättää samat arvot lähettämättä, joten data-luokka tilana on halpa.
  Iso lista tilassa kopioidaan jokaisessa `copy`ssa viitteenä, ei
  sisältönä.

## Itsearviointi

- Osaat kuvata ruudun tilan yhtenä muuttumattomana data-luokkana ja
  johtaa siitä lasketut arvot.
- Osaat kirjoittaa ViewModelin, joka yhdistää repositoryn Flow'n ja
  oman tilan `StateFlow`ksi oikealla jakamisstrategialla.
- Osaat valita oikean efektin (`LaunchedEffect`, `DisposableEffect`,
  `rememberCoroutineScope`) tilanteen mukaan sekä mallintaa
  kertaluonteisen tapahtuman tilana ja kuitata sen.
- Osaat koota riippuvuudet käsin säiliössä ja selittää, mitä Hilt
  automatisoi.
- Osaat testata ViewModelin väärennöksellä, testidispatcherilla ja
  Turbinella.
