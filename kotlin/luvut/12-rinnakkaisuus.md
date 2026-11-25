# Rinnakkaisuus ja korutiinit {.runko-rinnakkaisuus}

Kotlin/JVM käyttää JVM:n säikeitä, muistimallia ja
`java.util.concurrent`-kirjastoa sellaisenaan; niiden perusteet ovat
taidossa *Java* ja käsitteet taidossa *Rinnakkaisohjelmointi*. Kotlin
lisää kaksi asiaa: tiiviimmät apufunktiot säikeille ja lukoille sekä
korutiinit, joilla asynkroninen koodi kirjoitetaan peräkkäisenä.

## Säikeet ja lukot

Javan säikeet, suorittajat ja lukot ovat käytössä sellaisinaan.
Kotlinin vakiokirjasto lisää niihin apufunktiot, jotka hoitavat
käynnistyksen, lukon vapautuksen ja sulkemisen:

```{.kotlin tiedosto="esimerkit/12-saikeet.kt"}
```

```{.tuloste tiedosto="esimerkit/12-saikeet.odotettu"}
```

- JDK 21:n virtuaalisäikeet toimivat Kotlinista sellaisenaan.
  `ExecutorService` on `AutoCloseable`, joten `use` odottaa tehtävät
  ja sulkee suorittajan.
- `ReentrantLock.withLock { }` ja `synchronized(lukko) { }` ovat
  `inline`-funktioita: lukko vapautetaan `finally`-lohkossa, eikä
  lambdasta synny oliota.
- `thread { }` luo ja käynnistää säikeen. Säikeen kirjoitukset
  taulukkoon näkyvät pääsäikeelle `join`-kutsun jälkeen
  (*happens-before*).
- Kotlinissa ei ole `volatile`- tai `synchronized`-avainsanoja; ne ovat
  annotaatioita `@Volatile` ja `@Synchronized`.

## Mitä suspend tarkoittaa

`suspend`-funktio voi keskeytyä odottamaan varaamatta säiettä.
Kääntäjä muuntaa funktion tilakoneeksi: jokainen keskeytyskohta on tila,
paikalliset muuttujat tallennetaan olioon, ja funktio saa
lisäparametrina *jatkon* (`Continuation`), jota kutsutaan, kun tulos on
valmis. Tämä on *continuation-passing style* (CPS). Vakiokirjasto
sisältää vain nämä perusrakenteet; ajastus, säikeet ja peruutus ovat
kirjastossa `kotlinx.coroutines`.

```{.dot otsikko="`suspend`-funktio tilakoneena, kun funktiossa on kaksi keskeytyskohtaa. Keskeytyksessä funktio palaa kutsujalleen ja säie vapautuu; jatko-olio muistaa tilan ja paikalliset muuttujat. `resume` kutsuu funktiota uudelleen, ja suoritus jatkuu tallennetusta tilasta."}
digraph {
  rankdir=TB; nodesep=0.5; ranksep=0.45;
  node [fontsize=9, height=0.4, width=2.6];
  alku [label="kutsu", shape=plain, style="", width=0];
  t0 [label="tila 0: koodi ennen 1. keskeytyskohtaa"];
  t1 [label="tila 1: koodi keskeytyskohtien välissä"];
  t2 [label="tila 2: koodi 2. keskeytyskohdan jälkeen"];
  loppu [label="tulos kutsujan jatkolle", shape=plain, style="", width=0];
  alku -> t0;
  t0 -> t1 [label="  keskeytys: säie vapautuu; myöhemmin resume"];
  t1 -> t2 [label="  keskeytys: säie vapautuu; myöhemmin resume"];
  t2 -> loppu;
}
```

Vakiokirjaston `sequence { }` on korutiini: `yield` keskeyttää
rakentajan, ja suoritus jatkuu, kun kuluttaja pyytää seuraavaa alkiota.

```{.kotlin tiedosto="esimerkit/12-sekvenssi.kt"}
```

```{.tuloste tiedosto="esimerkit/12-sekvenssi.odotettu"}
```

Seuraava pieni suorittaja näyttää mekanismin: `suspendCoroutine` antaa
jatkon suorittajalle, joka laittaa sen jonoon ja ajaa sen myöhemmin.
Kaksi tehtävää vuorottelevat yhdessä säikeessä.

```{.kotlin tiedosto="esimerkit/12-suorittaja.kt"}
```

```{.tuloste tiedosto="esimerkit/12-suorittaja.odotettu"}
```

## Rakenteinen rinnakkaisuus: kotlinx.coroutines

Tuotantokoodissa käytetään kirjastoa `kotlinx.coroutines`. Sen
keskeinen periaate on *rakenteinen rinnakkaisuus* (*structured
concurrency*): jokainen korutiini käynnistetään jossakin
näkyvyysalueessa (`CoroutineScope`), ja

- vanhempi ei valmistu ennen lapsiaan, joten korutiini ei voi jäädä
  taustalle vuotamaan
- lapsen virhe peruu sisarukset ja välittyy vanhemmalle
- vanhemman peruutus peruu kaikki lapset.

```{.kotlin tiedosto="esimerkit/12-korutiinit/src/Rakenteinen.kt"}
```

```{.tuloste tiedosto="esimerkit/12-korutiinit/rakenteinen.odotettu"}
```

```{.dot otsikko="Esimerkin funktio `epaonnistuva` korutiinipuuna. Toisen lapsen virhe (1) nousee vanhemmalle, joka peruu ensimmäisen lapsen (2) ja heittää virheen kutsujalleen (3) vasta, kun molemmat lapset ovat päättyneet."}
digraph {
  rankdir=TB; nodesep=0.9; ranksep=0.6;
  node [fontsize=9, height=0.45];
  kutsuja [label="runBlocking\n(main)"];
  scope [label="coroutineScope\n(epaonnistuva)"];
  hidas [label="launch\ndelay(10 000)"];
  virhe [label="launch\nerror(…)"];
  kutsuja -> scope [dir=back, label=" 3. virhe", color="#B04848", fontcolor="#B04848"];
  scope -> hidas [label=" 2. peruutus", style=dashed];
  scope -> virhe [dir=back, label=" 1. virhe", color="#B04848", fontcolor="#B04848"];
}
```

| Rakenne | Tehtävä |
|---------|---------|
| `runBlocking { }` | silta tavallisesta koodista; vain `main` ja testit |
| `coroutineScope { }` | näkyvyysalue funktion sisällä; odottaa lapset |
| `launch { }` | käynnistä, ei tulosta (`Job`) |
| `async { }` ja `await()` | käynnistä, tulos myöhemmin (`Deferred<T>`) |
| `withContext(Dispatchers.IO) { }` | vaihda säieallasta (estävä I/O) |
| `withTimeout`, `withTimeoutOrNull` | aikaraja peruutuksena |
| `delay`, `yield`, `ensureActive()` | keskeytys- ja peruutuskohdat |
| `supervisorScope { }` | lapsen virhe ei peru sisaruksia |

Peruutus on yhteistoiminnallista: se tapahtuu keskeytyskohdassa
`CancellationException`-poikkeuksena. Laskentasilmukka, jossa ei ole
keskeytyskohtia, tarkistaa tilan itse (`ensureActive()`). Ajat voi
antaa myös tyypitettyinä kestoina (`kotlin.time.Duration`):
`delay(400.milliseconds)` ja `withTimeout(2.seconds) { … }`.
Esimerkin `measureTime` palauttaa saman tyypin.

## Jaettu tila ja kanavat

Korutiinit eivät poista kilpailutilanteita. `Dispatchers.Default` ajaa
korutiineja usean säikeen altaassa, joten kaksi korutiinia voi muuttaa
samaa muuttujaa yhtä aikaa, ja päivityksiä katoaa kuten säikeillä.
Javan `synchronized` ja `ReentrantLock` eivät kuitenkaan sovi
suojaukseksi, jos lukon sisällä on keskeytyskohta: lukko kuuluu
säikeelle, ja keskeytynyt korutiini voi jatkua toisessa säikeessä.
Kääntäjä estää tämän:

```{.kotlin tiedosto="esimerkit/12-kriittinen.ei-kaanny.kt"}
```

```
error: the 'tallenna' suspension point is inside a critical section.
```

Korutiineille on kolme tapaa hallita jaettua tilaa:

- **Atominen arvo** (`AtomicInteger`, `AtomicReference`) yhdelle
  muuttujalle, kuten säikeillä.
- **`Mutex`** on korutiinien lukko. `withLock` keskeyttää odottavan
  korutiinin eikä varaa säiettä, ja lukon sisällä saa olla
  keskeytyskohtia. `Mutex` ei ole uudelleen sisään mentävä (*reentrant*):
  korutiini, joka yrittää ottaa omistamansa lukon uudelleen, jää
  odottamaan ikuisesti.
- **Rajaus yhteen omistajaan.** Tilaa käsittelee vain yksi korutiini,
  ja muut lähettävät sille viestejä *kanavan* (`Channel`) kautta.
  Sama saavutetaan ajamalla tilaa koskeva koodi yhden säikeen
  levyisessä näkymässä (`Dispatchers.Default.limitedParallelism(1)`).

`Channel` on korutiinien `BlockingQueue`: `send` ja `receive` ovat
keskeyttäviä, rajattu puskuri antaa vastapainetta ja `close` päättää
vastaanottajien silmukat. Seuraavassa esimerkissä laskuria suojataan
kahdella tavalla, ja kanava jakaa työt kahdelle kuluttajalle:

```{.kotlin tiedosto="esimerkit/12-korutiinit/src/Jaettu.kt"}
```

```{.tuloste tiedosto="esimerkit/12-korutiinit/jaettu.odotettu"}
```

Kanava siirtää arvot korutiinilta toiselle, ja jokainen arvo menee
täsmälleen yhdelle vastaanottajalle. Kun samat arvot halutaan usealle
lukijalle tai kun tuottaja saa käynnistyä vasta tarvittaessa,
käytetään virtaa.

## Flow

`Flow<T>` on asynkroninen arvovirta: `suspend`-maailman `Sequence`.
Virta on kylmä, eli tuottaja käynnistyy jokaiselle keräilijälle
(`collect`) erikseen, ja operaattorit (`map`, `filter`, `take`) ovat
laiskoja. `take` peruu tuottajan, kun arvoja on tarpeeksi.

```{.kotlin tiedosto="esimerkit/12-korutiinit/src/Virta.kt"}
```

```{.tuloste tiedosto="esimerkit/12-korutiinit/virta.odotettu"}
```

Kuumat virrat `StateFlow` (nykyinen tila, esim. käyttöliittymän malli)
ja `SharedFlow` (tapahtumat usealle kuuntelijalle) jakavat yhden
tuottajan monelle kerääjälle.

Esimerkkihakemiston `Makefile` kääntää korutiiniesimerkit
`kotlinc`-kääntäjän mukana tulevaa `kotlinx-coroutines-core`-kirjastoa
vasten ja vertaa tulosteet. Gradle-projektissa kirjasto on tavallinen
riippuvuus (luku 11).

## Käytännössä

- **Rakenteinen rinnakkaisuus aina.** Käynnistä korutiinit
  `coroutineScope`- tai kehyksen antamassa näkyvyysalueessa
  (Androidin `viewModelScope`, Ktorin pyyntö). `GlobalScope` ja
  irralliset `CoroutineScope()`-oliot vuotavat töitä, joita kukaan ei
  odota eikä peru.
- **`suspend`-funktio ei estä.** Estävä kutsu (JDBC, tiedosto, vanha
  HTTP-asiakas) kääritään `withContext(Dispatchers.IO)`-lohkoon, jotta se
  ei pysäytä korutiinien säiepoolia.
- **Peruutusta ei niellä.** `catch (e: Exception)` sieppaa myös
  `CancellationException`-poikkeuksen. Sieppaa tarkat tyypit tai heitä
  peruutus uudelleen, ja vältä `runCatching`-funktiota `suspend`-koodissa.
- **Jaettu tila mahdollisimman pieneksi.** Palauta tulokset
  `async`-lohkoista ja yhdistä ne lopuksi; silloin lukkoa ei tarvita.
  Kun tila on jaettava, käytä atomista arvoa tai `Mutex`ia, älä
  `synchronized`-lohkoa keskeytyskohdan ympärillä.
- **Rinnakkaisuus näkyy koodissa.** Peräkkäiset `await`-kutsut ovat
  rinnakkaisia vain, jos `async`-lohkot käynnistettiin ensin.
  `val a = async {}.await()` on peräkkäinen.
- **Virtuaalisäikeet vai korutiinit?** JDK 21:n virtuaalisäikeet
  tekevät estävästä koodista halpaa ilman kielen muutoksia. Korutiinit
  tuovat lisäksi rakenteisen peruutuksen, `Flow`-virrat ja toimivat
  Androidissa sekä Kotlin Multiplatformissa.
- **Hinta:** korutiini on muutaman sadan tavun olio; satoja tuhansia
  mahtuu muistiin. Jokainen keskeytys tallentaa tilan kekoon, joten
  tiukka laskentasilmukka ei hyödy `suspend`-merkinnästä.
- **Sudenkuoppa:** `runBlocking` korutiinin sisällä estää säikeen ja voi
  johtaa lukkiutumiseen. Se kuuluu vain `main`-funktioon ja testeihin.

## Itsearviointi

- Osaat käyttää JVM:n säikeitä, virtuaalisäikeitä ja lukkoja Kotlinin
  apufunktioilla (`thread`, `withLock`, `use`).
- Osaat selittää, miten kääntäjä toteuttaa `suspend`-funktion jatkoilla
  ja tilakoneella.
- Osaat kirjoittaa rinnakkaisia hakuja `coroutineScope`-, `async`- ja
  `launch`-rakenteilla ja kertoa, miten virhe ja peruutus etenevät.
- Osaat suojata korutiinien jaetun tilan atomisella arvolla tai
  `Mutex`illa ja kertoa, miksi `synchronized` ei sovi keskeytyskohdan
  ympärille.
- Osaat toteuttaa tuottaja–kuluttaja-mallin kanavalla.
- Osaat käyttää `Flow`-virtaa ja selittää kylmän ja kuuman virran eron.
