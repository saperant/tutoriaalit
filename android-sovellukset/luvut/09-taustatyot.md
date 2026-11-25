# Taustatyöt

Android rajoittaa taustatyötä akun säästämiseksi tiukemmin version
version jälkeen. Sovellus ei voi pitää omaa säiettään käynnissä
taustalla: järjestelmä lopettaa prosessin, ja *Doze*-tila sekä
sovelluskohtaiset valmiustilan ryhmät (*App Standby Buckets*)
lykkäävät työtä. Oikea väline riippuu siitä, kuinka pitkä työ on ja
pitääkö sen valmistua.

| Työ | Väline |
|-----|--------|
| ruudun elinaikana, peruuntuu poistuttaessa | `viewModelScope`, `LaunchedEffect` (luku 5) |
| sovelluksen elinaikana, ei ruutuun sidottu | sovelluksenlaajuinen `CoroutineScope` |
| pitää valmistua, voi odottaa sopivaa hetkeä | **WorkManager** |
| käyttäjän käynnistämä, näkyvä ja pitkä (navigointi, toisto) | etualan palvelu (*foreground service*) ilmoituksineen |
| tarkka kellonaika (herätys) | `AlarmManager` (vaatii erillisen oikeuden) |

## WorkManager

WorkManager ajaa työn, vaikka sovellus suljettaisiin tai laite
käynnistettäisiin uudelleen. Se tallentaa työn omaan tietokantaansa,
odottaa annettuja ehtoja ja yrittää uudelleen epäonnistumisen jälkeen.

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/tyo/SynkronointiTyo.kt" osa="tyo"}
```

- **`CoroutineWorker`** ajaa `doWork`in korutiinina. Työ peruuntuu, jos
  ehdot lakkaavat täyttymästä (esim. verkko katkeaa), joten pitkä työ
  tarkistaa peruutuksen kuten mikä tahansa korutiini.
- **Paluuarvo** ohjaa jatkoa: `success`, `failure` tai `retry`.
  `retry` ajastaa uuden yrityksen takaisinvetopolitiikan mukaan;
  `runAttemptCount` rajaa yritysten määrän.
- **Kaksi muodostinta.** WorkManager luo työn heijastuksella kahden
  parametrin muodostimella. Testi ja tuotantokoodi, joka käyttää
  `WorkerFactory`a (tai Hiltin `@HiltWorker`ia), antavat repositoryn
  kolmannella parametrilla.

Työ ajastetaan ehtoineen:

```{.kotlin tiedosto="esimerkit/app/src/main/java/fi/esimerkki/ostokset/tyo/SynkronointiTyo.kt" osa="ajastus"}
```

- **Ehdot** (`Constraints`) lykkäävät työtä, kunnes laite on verkossa
  ja akku riittää. Ehtoja voi lisätä: lataus, Wi-Fi
  (`NetworkType.UNMETERED`), laitteen joutilaisuus.
- **Toistuva työ** voi olla vähintään 15 minuutin välein, ja
  järjestelmä päättää tarkan ajankohdan. Kerran ajettava työ tehdään
  `OneTimeWorkRequestBuilder`illa, esimerkiksi heti muutoksen jälkeen
  ehdolla "kun verkko on".
- **Ainutkertainen nimi** (`enqueueUniquePeriodicWork`) estää
  päällekkäiset ajastukset, kun `Application.onCreate` ajastaa saman
  työn jokaisella käynnistyksellä. `KEEP` säilyttää olemassa olevan.

## Taustatyön testaus

`TestListenableWorkerBuilder` luo työn testissä, ja tehdas antaa sille
väärennetyn repositoryn:

```{.kotlin tiedosto="esimerkit/app/src/test/java/fi/esimerkki/ostokset/tyo/SynkronointiTyoTest.kt" osa="testi"}
```

Testi kutsuu `doWork`ia suoraan ja tarkistaa paluuarvon. Ehtojen ja
ajastuksen testaamiseen `work-testing` tarjoaa myös
`WorkManagerTestInitHelper`in, jolla ehdot voi asettaa täyttyneiksi ja
viiveet kulumaan.

## Käytännössä

- **Valitse väline työn luonteen mukaan.** Ruutuun sidottu työ
  korutiinilla, valmistuttava työ WorkManagerilla, käyttäjän näkemä
  pitkä työ etualan palvelulla. Väärä valinta näkyy joko kadonneena
  työnä tai tyhjenevänä akkuna.
- **Taustatyö on idempotentti.** Työ voi suorittua useasti
  (uudelleenyritys, prosessin kuolema kesken työn), joten
  sen on oltava turvallista toistaa.
- **Ainutkertaiset nimet.** Sama työ ajastetaan nimellä, jotta
  päällekkäisiä ajoja ei synny.
- **Ehdot ennen ajoitusta.** Anna järjestelmän valita hetki
  (verkko, lataus) eikä pakota tarkkaa aikaa.
- **Hinnat:** jokainen herätys maksaa akkua; usein toistuva työ näkyy
  käyttäjälle akun kulutuksena ja järjestelmälle huonona sovelluksena,
  jonka työt lykätään yhä pidemmälle. Etualan palvelu vaatii näkyvän
  ilmoituksen ja tyypin (`foregroundServiceType`), ja Google Play
  tarkistaa sen käytön.

## Itsearviointi

- Osaat valita taustatyölle oikean välineen sen keston ja
  valmistumisvaatimuksen mukaan.
- Osaat kirjoittaa `CoroutineWorker`in, joka palauttaa onnistumisen,
  uudelleenyrityksen tai epäonnistumisen.
- Osaat ajastaa työn ehdoin ja ainutkertaisella nimellä.
- Osaat testata taustatyön tehtaalla annetulla väärennöksellä.
