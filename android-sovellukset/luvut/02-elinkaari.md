# Sovelluksen rakenne ja elinkaari

Työpöytäohjelma päättää itse, milloin se käynnistyy ja loppuu.
Android-sovellus ei päätä: järjestelmä luo, pysäyttää ja tuhoaa sen
komponentteja käyttäjän toimien ja muistitilanteen mukaan. Hyvä
Android-koodi on kirjoitettu niin, että se kestää tämän.

## Manifesti

Manifesti kertoo järjestelmälle sovelluksen komponentit ja tarvitut
oikeudet:

```{.xml tiedosto="esimerkit/app/src/main/AndroidManifest.xml" osa="manifest"}
```

- **`android:name=".OstoksetSovellus"`** valitsee oman
  `Application`-luokan, joka luodaan ennen mitään muuta ja elää koko
  prosessin ajan.
- **`exported="true"`** ja `MAIN`/`LAUNCHER`-suodatin tekevät
  Activitystä käynnistimessä näkyvän aloituspisteen. Muut Activityt
  ovat oletuksena `exported="false"`: muut sovellukset eivät voi
  käynnistää niitä, mikä on oikea oletus tietoturvan kannalta.
- **`uses-permission`** luettelee oikeudet. `INTERNET` myönnetään
  asennuksessa automaattisesti; *vaaralliset* oikeudet (sijainti,
  kamera, ilmoitukset) pitää lisäksi pyytää ajon aikana.
- **Resurssiviittaukset** (`@string/...`, `@drawable/...`) osoittavat
  `res/`-hakemistoon.

## Resurssit

Tekstit, kuvat ja mitat pidetään erillään koodista hakemistossa
`res/`. Sovelluksen merkkijonot ovat tiedostossa
`res/values/strings.xml`:

```{.xml tiedosto="esimerkit/app/src/main/res/values/strings.xml" osa="resurssit"}
```

Käännöstyökalu tuottaa jokaiselle resurssille tunnisteen, esimerkiksi
`R.string.ei_yhteytta`, joten kirjoitusvirhe nimessä on käännösvirhe.
Erillisyydellä on kaksi hyötyä:

- **Kelpuuttimet** (*qualifiers*). Hakemisto `values-en/` sisältää
  englanninkieliset tekstit, `values-night/` tumman teeman arvot ja
  `values-sw600dp/` tablettien mitat. Järjestelmä valitsee sopivan
  version laitteen asetusten mukaan, ja konfiguraatiomuutos (alla)
  lataa resurssit uudelleen.
- **Monikot.** `plurals` valitsee muodon luvun ja kielen sääntöjen
  mukaan. Suomessa ja englannissa muotoja on kaksi (`one`, `other`),
  mutta esimerkiksi venäjässä ja arabiassa useampia, joten
  `if (n == 1)` koodissa ei riitä käännettävään sovellukseen.

Composessa resurssi luetaan funktioilla `stringResource` ja
`pluralStringResource`; luku 5 käyttää niitä viestien sanamuotoon.

## Application ja Activity

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/OstoksetSovellus.kt" osa="sovellus"}
```

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/MainActivity.kt" osa="aktiviteetti"}
```

Sovelluksessa on yksi Activity. `setContent` liittää siihen
Compose-käyttöliittymän, ja ruutujen välillä siirrytään navigoinnilla
(luku 6). `enableEdgeToEdge` piirtää sisällön tilapalkin ja
navigointipalkin alle; Material-komponentit (`Scaffold`) lisäävät
tarvittavat reunukset.

`Application` on oikea paikka sovelluksenlaajuisille olioille, mutta
`onCreate` kannattaa pitää kevyenä: se hidastaa jokaista
käynnistystä, myös silloin, kun järjestelmä käynnistää sovelluksen
vain taustatyötä varten.

## Elinkaari

Activityn elinkaari kulkee tilojen läpi, ja jokaisesta siirtymästä
tulee takaisinkutsu:

```{.dot otsikko="Activityn elinkaari: tilat ja siirtymien takaisinkutsut"}
digraph {
  rankdir=LR; nodesep=0.5; ranksep=0.35;
  ei [label="ei\nolemassa", style="rounded,dashed"];
  ei -> CREATED [label="onCreate"];
  CREATED -> STARTED [label="onStart"];
  STARTED -> RESUMED [label="onResume"];
  edge [color="#B4532A", fontcolor="#B4532A"];
  RESUMED -> STARTED [label="onPause"];
  STARTED -> CREATED [label="onStop"];
  CREATED -> ei [label="onDestroy"];
}
```

- **STARTED**: näkyvissä, mutta ei välttämättä etualalla (esim.
  dialogi päällä tai jaettu näyttö).
- **RESUMED**: etualalla ja vastaanottaa syötettä.
- **CREATED**: ei näkyvissä. Animaatiot, sijaintipäivitykset ja
  kameran esikatselu pysäytetään viimeistään tässä.

Siirtymiä ei kannata kirjoittaa Activityyn vaan erilliseen
tarkkailijaan, jonka voi liittää mihin tahansa elinkaaren omistajaan:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/elinkaari/Elinkaari.kt" osa="tarkkailija"}
```

Testi käynnistää Activityn Robolectricilla ja luo sen uudelleen,
kuten järjestelmä tekee esimerkiksi näyttöä käännettäessä:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/ElinkaariTest.kt" osa="elinkaari"}
```

**Konfiguraatiomuutos** (kierto, kieli, tumma tila, ikkunan koko)
tuhoaa Activityn ja luo uuden, jotta resurssit ladataan uusilla
arvoilla. Tarkkailija oli liitetty vanhaan Activityyn, joten se näkee
vain tämän tuhoutumisen. Kaikki Activityn kentissä ollut tila katoaa.

## Tila, joka säilyy

Tilaa uhkaa kaksi eri tapahtumaa:

1. **Konfiguraatiomuutos**: Activity luodaan uudelleen, prosessi jatkaa.
   ViewModel säilyy (luku 5).
2. **Prosessin kuolema**: käyttäjä siirtyy toiseen sovellukseen, ja
   järjestelmä lopettaa prosessin muistin tarpeen vuoksi. Kun käyttäjä
   palaa, järjestelmä luo prosessin ja Activityn uudelleen ja antaa
   sille tallennetun tilan (`Bundle`). ViewModel ei säily.

| Missä tila on | Uudelleenkoostaminen | Konfiguraatiomuutos | Prosessin kuolema |
|------------------------------|----------------------|---------------------|-------------------|
| paikallinen muuttuja | katoaa | katoaa | katoaa |
| `remember` | säilyy | katoaa | katoaa |
| ViewModel | säilyy | säilyy | katoaa |
| `rememberSaveable` | säilyy | säilyy | säilyy |
| tietokanta, DataStore | säilyy | säilyy | säilyy |

Composen omat muistit ovat `remember` ja `rememberSaveable`:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/elinkaari/Elinkaari.kt" osa="laskurit"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/ElinkaariTest.kt" osa="tallennus"}
```

`StateRestorationTester` jäljittelee tallennusta ja palautusta.
`remember` säilyy vain niin kauan kuin composable on koostumuksessa;
`rememberSaveable` tallentaa arvon Bundleen, joten se kestää sekä
konfiguraatiomuutoksen että prosessin kuoleman. Bundleen mahtuu vain
pieni, sarjallistettava tila: valinta, syötekentän teksti, vierityksen
sijainti. Varsinainen data on tietokannassa (luku 7).

Prosessin kuoleman voi kokeilla laitteella: sovellus viedään
taustalle ja prosessi lopetetaan komennolla `adb shell am kill` ja
sovelluksen tunnisteella (`fi.esimerkki.ostokset`). Moni sovellus,
joka toimii kiertäessä, menettää tässä tilansa.

## Intentit ja toiset sovellukset

Komponentit eivät kutsu toisiaan suoraan, vaan lähettävät
järjestelmälle **intentin**: viestin, joka kuvaa, mitä halutaan tehdä.
Manifestin `MAIN`/`LAUNCHER`-suodatin on tästä jo esimerkki:
käynnistin lähettää intentin, ja suodatin kertoo, että `MainActivity`
ottaa sen vastaan. Intenttejä on kahta lajia:

- **Eksplisiittinen** nimeää kohdeluokan. Sitä käytetään sovelluksen
  sisällä, esimerkiksi kun ilmoituksen napautus avaa sovelluksen.
- **Implisiittinen** kertoo vain toiminnon (`ACTION_SEND`,
  `ACTION_VIEW`) ja datan tyypin. Järjestelmä etsii sovellukset,
  joiden manifestin suodatin sopii, ja käyttäjä valitsee niistä.

Ostoslistan jakaminen on implisiittinen intent. Sovelluksen ei
tarvitse tietää, onko vastaanottaja viestisovellus, sähköposti vai
muistio:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/elinkaari/Intentit.kt" osa="jako"}
```

Testissä Robolectric tallentaa käynnistetyn intentin, joten sen
sisällön voi tarkistaa avaamatta toista sovellusta. Kolmas testi
näyttää eksplisiittisen intentin:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/IntentitTest.kt" osa="jako"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/IntentitTest.kt" osa="eksplisiittinen"}
```

Sovellus voi olla myös vastaanottaja. Silloin Activity ilmoittaa
manifestissa suodattimen ja on `exported="true"`:

```text
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

Vastaanotettu intent on syötettä sovelluksen ulkopuolelta: sen voi
lähettää mikä tahansa laitteen sovellus, ja sisältö voi olla mitä
tahansa. Siksi toiminto ja tyyppi tarkistetaan ja pituudet rajataan
ennen kuin sisältöä käytetään:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/elinkaari/Intentit.kt" osa="vastaanotto"}
```

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/IntentitTest.kt" osa="vastaanotto"}
```

Esimerkkisovelluksen manifestissa tätä suodatinta ei ole, joten
sovellus ei näy jakovalikossa; jäsennysfunktio on mukana testattuna.

Kun toiselta sovellukselta odotetaan *tulosta* (valittu kuva, otettu
valokuva, käyttäjän vastaus lupakysymykseen), käytetään
**aktiviteettitulosta**: `ActivityResultContract` kuvaa pyynnön ja
tuloksen tyypit, ja tulos tulee takaisinkutsuna. Valmiita sopimuksia
ovat esimerkiksi `GetContent`, `TakePicture` ja `RequestPermission`,
jota seuraava osio käyttää.

## Ajonaikaiset oikeudet

Vaarallinen oikeus pyydetään silloin, kun käyttäjä tarvitsee
ominaisuutta, ei käynnistyksessä. Pyyntö on aktiviteettitulos:
järjestelmä näyttää oman dialoginsa, ja vastaus tulee
takaisinkutsuna.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/elinkaari/Lupa.kt" osa="lupa"}
```

Ilmoitusoikeus tuli Android 13:ssa (API 33). Vanhemmissa versioissa
sitä ei pyydetä, ja Lint huomauttaa, jos versiotarkistus puuttuu.
Testi korvaa järjestelmän dialogin rekisterillä, joka vastaa heti:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/elinkaari/ElinkaariTest.kt" osa="lupa"}
```

Jos käyttäjä kieltää oikeuden kahdesti, järjestelmä ei enää näytä
dialogia, ja sovelluksen on ohjattava asetuksiin. Siksi ennen pyyntöä
kerrotaan, miksi oikeutta tarvitaan
(`shouldShowRequestPermissionRationale`), ja ominaisuuden on toimittava
rajoitetusti ilman oikeutta.

## Käytännössä

- **Oleta, että prosessi kuolee.** Kaikki, mitä käyttäjä ei saa
  menettää, tallennetaan heti pysyvästi (tietokanta tai DataStore).
  Bundle on vain käyttöliittymän tilaa varten.
- **Yksi Activity.** Useat Activityt tekevät navigoinnista, tilan
  jakamisesta ja animaatioista vaikeita. Erillinen Activity on
  perusteltu vain, kun järjestelmä sitä vaatii (esim. jakamisen
  kohde).
- **Ei tilaa Activityn kentissä eikä staattisissa muuttujissa.**
  Activityyn viittaava staattinen kenttä vuotaa muistia
  konfiguraatiomuutoksessa, koska vanha Activity ei vapaudu.
- **Kevyt käynnistys.** `Application.onCreate` ja ensimmäinen ruutu
  ratkaisevat käynnistysajan. Raskas alustus siirretään laiskaksi tai
  taustalle.
- **Intentin sisältö on epäluotettavaa syötettä.** Vie (`exported`)
  vain ne komponentit, joiden on tarkoitus näkyä muille, ja tarkista
  kaikki, mitä vastaanotettu intent sisältää.
- **Oikeus käyttötilanteessa ja perusteltuna.** Pyydä vain tarvittava
  (esim. likimääräinen sijainti tarkan sijaan), ja tarjoa toimiva
  vaihtoehto kieltäytyjälle.
- **Hinta:** jokainen konfiguraatiomuutos luo käyttöliittymän
  uudelleen. Activityn voi estää luomasta itseään uudelleen
  (`configChanges`), mutta se on virheiden lähde, koska resurssit eivät
  päivity. Tila kuuluu ViewModeliin ja `rememberSaveable`en.

## Itsearviointi

- Osaat lukea manifestista sovelluksen komponentit, oikeudet ja
  aloituspisteen.
- Osaat selittää elinkaaren tilat ja sen, mitä konfiguraatiomuutos ja
  prosessin kuolema tekevät sovelluksen tilalle.
- Osaat valita `remember`in, `rememberSaveable`n, ViewModelin ja
  pysyvän tallennuksen välillä.
- Osaat lähettää implisiittisen intentin, erottaa sen
  eksplisiittisestä ja käsitellä vastaanotetun intentin sisällön
  epäluotettavana syötteenä.
- Osaat pyytää ajonaikaisen oikeuden versiotarkistuksineen ja testata
  pyynnön ilman järjestelmän dialogia.
