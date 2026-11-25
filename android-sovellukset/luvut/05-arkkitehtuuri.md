# Arkkitehtuuri: tila, ViewModel ja repository

Androidin suositeltu arkkitehtuuri jakaa sovelluksen kerroksiin, joista
jokainen tietää vain alemmasta:

```text
  Käyttöliittymä (composablet)     piirtää tilan, välittää tapahtumat
        │ tapahtumat ▲ tila
  ViewModel                        ruudun tila ja logiikka
        │ kutsut     ▲ Flow
  Repository                       ainoa tie dataan
        │
  Tietokanta, verkko, asetukset    tietolähteet
```

Kerrosten ansiosta jokainen osa voidaan testata erikseen ja
tietolähteen voi vaihtaa koskematta käyttöliittymään.

## UI-tila yhtenä arvona

Ruudun koko tila kuvataan yhdellä muuttumattomalla arvolla:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/lista/ListaViewModel.kt" osa="tila"}
```

Viesti on suljettu tyyppi eikä merkkijono: ViewModel kertoo, mitä
tapahtui, ja käyttöliittymä valitsee sanamuodon resursseista, jolloin
kieli vaihtuu ja monikkomuodot toimivat:

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
tilattomaan sisältöön, jota luku 4 testasi.

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
- Osaat koota riippuvuudet käsin säiliössä ja selittää, mitä Hilt
  automatisoi.
- Osaat testata ViewModelin väärennöksellä, testidispatcherilla ja
  Turbinella.
