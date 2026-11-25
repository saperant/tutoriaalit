# Navigointi

Yhden Activityn sovelluksessa ruudut ovat composable-funktioita, ja
**Navigation Compose** hallitsee niiden välisiä siirtymiä: takaisin-
pinon (*back stack*), argumentit, järjestelmän takaisin-eleen ja
ViewModelien elinajan.

## Reitit tyyppeinä

Reitti on sarjallistettava Kotlin-tyyppi. Argumentit ovat tyypin
ominaisuuksia, joten kääntäjä tarkistaa ne:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/navigointi/Navigaatio.kt" osa="reitit"}
```

Ennen tyypitettyjä reittejä reitit olivat merkkijonoja
(`"tuote/{id}"`), ja argumentit luettiin käsin. Kirjoitusvirhe reitissä
tai väärä argumenttityyppi paljastui vasta ajossa. Tyypitetyt reitit
vaativat kotlinx.serialization-liitännäisen (luku 1).

## NavHost

Navigointi on pino: `navigate` lisää ruudun päällimmäiseksi, ja
takaisin-ele poistaa sen.

![Rivin napautus avaa tuoteruudun listan päälle; Takaisin palaa
listaan.](kuvat/navigointi.png){width=62%}

```{.dot otsikko="Takaisin-pino esimerkin siirtymissä"}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=1.3;
  node [shape=record];
  a [label="{ListaReitti}"];
  b [label="{ListaReitti|TuoteReitti(1, maito)}"];
  a -> b [label="navigate(TuoteReitti(...))"];
  b -> a [label="popBackStack()", color="#B4532A", fontcolor="#B4532A"];
}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/navigointi/Navigaatio.kt" osa="navhost"}
```

- **`NavHost`** liittää reitit ruutuihin. Aloitusreitti on pinon pohja.
- **`navigate(TuoteReitti(...))`** lisää ruudun pinoon;
  `popBackStack()` ja järjestelmän takaisin-ele poistavat sen.
- **`toRoute<TuoteReitti>()`** lukee argumentit merkinnästä. Sama
  toimii ViewModelissa: `savedStateHandle.toRoute<TuoteReitti>()`.
- **ViewModel kuuluu pinon merkinnälle.** `viewModel { ... }` luo
  ViewModelin, joka elää niin kauan kuin reitti on pinossa, ja
  tuhoutuu, kun reitti poistetaan. Kahdella ruudulla on eri
  ViewModelit, vaikka niiden tyyppi olisi sama.
- **Navigointi tapahtumana.** Ruutu ei tunne `NavController`ia; se saa
  takaisinkutsun (`onAvaa`), ja navigointikerros päättää, minne
  siirrytään. Ruudun voi siten testata ja käyttää ilman navigointia.

Argumentteihin kannattaa laittaa vain tunnisteita, ei kokonaisia
olioita: argumentit tallentuvat Bundleen prosessin kuoleman varalta,
ja kohderuutu hakee ajantasaisen datan repositorysta. Esimerkin nimi
kulkee mukana vain, jotta otsikko näkyy heti.

## Navigoinnin testaus

`TestNavHostController` on oikea navigointiohjain, jonka pinoa testi
voi tarkastella:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/navigointi/NavigaatioTest.kt" osa="testi"}
```

Testi käyttää samaa väärennettyä repositorya kuin ViewModel-testi ja
tarkistaa sekä siirtymän että välitetyt argumentit.

## Syvät linkit ja suuret näytöt

- **Syvä linkki** (`deepLinks = listOf(navDeepLink<TuoteReitti>(...))`)
  avaa ruudun suoraan URL:sta, esimerkiksi ilmoituksesta tai
  verkkosivulta. Manifestiin lisätään vastaava `intent-filter`, ja
  *App Links* -varmennus todistaa, että sovellus omistaa verkkotunnuksen.
- **Suuret näytöt ja taitettavat.** Tabletilla lista ja tuote voivat
  näkyä rinnakkain. `WindowSizeClass` kertoo ikkunan kokoluokan, ja
  Material 3:n adaptiiviset komponentit (`ListDetailPaneScaffold`,
  `NavigationSuiteScaffold`) vaihtavat asettelua automaattisesti.
  Ikkunan koko voi muuttua ajon aikana (jaettu näyttö), joten asettelu
  valitaan koon eikä laitetyypin perusteella.

## Käytännössä

- **Tyypitetyt reitit.** Kääntäjä tarkistaa argumentit, ja reitin
  muutos näkyy kaikissa käyttökohdissa.
- **Ruudut eivät tunne navigointia.** Takaisinkutsut ruudulle,
  `navigate`-kutsut navigointikerrokseen. Sama ruutu voi olla eri
  navigointirakenteissa (puhelin, tabletti).
- **Tunnisteet argumentteina.** Iso olio argumenttina kasvattaa
  Bundlea (raja on noin 1 Mt koko sovellukselle) ja vanhenee.
- **Ennustettava takaisin-ele.** Älä kaappaa takaisin-elettä ilman
  syytä; jos ruudulla on tallentamattomia muutoksia, käytä
  `BackHandler`ia ja kysy käyttäjältä.
- **Hinnat:** jokainen pinossa oleva merkintä pitää tilansa ja
  ViewModelinsa muistissa. Syvä pino samaa ruutua (lista → tuote →
  tuote → ...) kannattaa estää `launchSingleTop`- ja
  `popUpTo`-valinnoilla.

## Itsearviointi

- Osaat määritellä tyypitetyt reitit ja lukea argumentit
  `toRoute`-funktiolla.
- Osaat rakentaa `NavHost`in, jossa ruudut saavat navigoinnin
  takaisinkutsuina.
- Osaat selittää, miten ViewModelin elinaika sidotaan takaisin-pinon
  merkintään.
- Osaat testata navigoinnin `TestNavHostController`illa.
