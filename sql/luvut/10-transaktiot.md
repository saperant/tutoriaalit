# Muutokset ja transaktiot

Tämä luku käsittelee tietojen muuttamisen tuotantokäytössä: lisäyksen,
joka ei kaadu toistoon, muutokset, jotka palauttavat tuloksensa, ja
transaktiot, jotka tekevät monesta muutoksesta yhden kokonaisuuden.
Perussyntaksi (`INSERT`, `UPDATE`, `DELETE`) oletetaan tutuksi.

## UPSERT ja RETURNING

*UPSERT* lisää rivin tai päivittää olemassa olevan, jos yksikäsitteisyys
rikkoutuisi. Varastoon saapuva erä kasvattaa saldoa tai luo uuden
rivin:

```{.sql tiedosto="esimerkit/10-upsert.sql" osa="taulu"}
```

```{.sql tiedosto="esimerkit/10-upsert.sql" osa="upsert"}
```

`excluded` viittaa riviin, jonka lisäys epäonnistui. `RETURNING`
palauttaa muutettujen rivien arvot samalla kertaa, joten sovelluksen ei
tarvitse lukea niitä erikseen. Syntaksi on sama SQLitessä (3.35+) ja
PostgreSQL:ssä.

*Ehdollinen päivitys* tekee tarkistuksen ja muutoksen yhdessä lauseessa:

```{.sql tiedosto="esimerkit/10-upsert.sql" osa="returning"}
```

```{.tuloste tiedosto="esimerkit/10-upsert.odotettu"}
```

Jos saldo ei riitä, lause ei muuta mitään eikä palauta rivejä, ja
sovellus tietää varauksen epäonnistuneen. Tämä on oikein myös
samanaikaisesti: kaksi yhtäaikaista varausta eivät voi molemmat nähdä
riittävää saldoa, toisin kuin erillisillä `SELECT`- ja
`UPDATE`-lauseilla.

## Joukkopäivitys toisesta taulusta

`UPDATE ... FROM` päivittää rivit toisen taulun perusteella, kuten
tuodun hinnaston:

```{.sql tiedosto="esimerkit/10-update-from.sql" osa="update-from"}
```

```{.sql tiedosto="esimerkit/10-update-from.sql" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/10-update-from.odotettu"}
```

Ehto `u.hinta_snt <> tuote.hinta_snt` jättää muuttumattomat rivit
koskematta, jolloin triggerit ja muutoslokit eivät kirjaa turhia
muutoksia. Tuntemattomat tuotteet raportoidaan erikseen sen sijaan, että
ne ohitettaisiin hiljaa.

## Transaktiot

Transaktio on joukko lauseita, jotka joko kaikki onnistuvat tai joista
mikään ei jää voimaan. Ominaisuudet tunnetaan lyhenteellä ACID:
*atomisuus* (kaikki tai ei mitään), *eheys* (rajoitteet pätevät),
*eristys* (samanaikaiset transaktiot eivät näe toistensa keskeneräisiä
muutoksia) ja *pysyvyys* (sitoutettu muutos säilyy kaatumisessa).

Tilaus ja varaston vähennys kuuluvat yhteen:

```{.sql tiedosto="esimerkit/10-transaktio.sql" osa="transaktio"}
```

Tallennuspiste (`SAVEPOINT`) peruu osan transaktiosta:

```{.sql tiedosto="esimerkit/10-transaktio.sql" osa="savepoint"}
```

```{.tuloste tiedosto="esimerkit/10-transaktio.odotettu"}
```

Esimerkin alussa luodaan varastotaulu, jossa jokaisen tuotteen saldo on
10. Ilman `BEGIN`-lausetta jokainen lause on oma transaktionsa
(*autocommit*). Transaktion virheenkäsittely tehdään sovelluksessa:
virheen jälkeen kutsutaan `ROLLBACK` (luku 12).

## Eristystasot

Samanaikaiset transaktiot voivat häiritä toisiaan. Standardi määrittelee
neljä eristystasoa sen mukaan, mitkä poikkeamat ne sallivat:

| Taso | Estää |
|------|-------|
| *read uncommitted* | ei mitään (PostgreSQL toimii kuten seuraava) |
| *read committed* | sitomattomien muutosten lukemisen |
| *repeatable read* | lisäksi saman rivin eri arvot saman transaktion aikana |
| *serializable* | kaikki: tulos on kuin transaktiot olisi ajettu peräkkäin |

**PostgreSQL**:n oletus on *read committed*: jokainen lause näkee
lauseen alussa sitoutetun tilan. Sovelluksen tekemä
*luku–muokkaus–kirjoitus* (`SELECT saldo`, lasku sovelluksessa,
`UPDATE saldo = ?`) kadottaa toisen transaktion samanaikaisen
muutoksen (*lost update*). Korjauksia ovat atominen päivitys
(`SET saldo = saldo - 5`), rivilukko `SELECT ... FOR UPDATE` tai taso
*serializable*, jolloin tietokanta keskeyttää ristiriitaisen
transaktion ja sovellus yrittää uudelleen.

**SQLite** on aina *serializable*, koska kirjoittajia on kerrallaan yksi.
WAL-tilassa lukijat näkevät tilannekuvan eivätkä estä kirjoittajaa:

```{.python tiedosto="esimerkit/10-lukitus.py" osa="wal"}
```

```{.python tiedosto="esimerkit/10-lukitus.py" osa="lukko"}
```

```{.tuloste tiedosto="esimerkit/10-lukitus.odotettu"}
```

`BEGIN IMMEDIATE` varaa kirjoitusoikeuden heti. Oletus `BEGIN`
(*deferred*) varaa sen vasta ensimmäisessä kirjoituksessa, ja jos
toinen yhteys ehti väliin, transaktio kaatuu virheeseen `database is
locked`, vaikka odotusaika olisi asetettu. Kirjoittavat transaktiot
aloitetaan siksi `BEGIN IMMEDIATE` -lauseella.

## Käytännössä

- **Lyhyet transaktiot.** Transaktion aikana ei odoteta käyttäjää,
  verkkokutsuja eikä tiedostoja. Pitkä transaktio pitää lukkoja ja
  SQLitessä estää kaikki muut kirjoittajat.
- **Atominen päivitys luku–muokkaus–kirjoitus-kierroksen sijaan.**
  `SET saldo = saldo - ?` ja ehto `WHERE saldo >= ?` ovat oikein
  kaikilla eristystasoilla.
- **Idempotentit operaatiot.** UPSERT ja luonnollisen avaimen
  `UNIQUE`-rajoite tekevät toistetusta pyynnöstä vaarattoman, mikä on
  välttämätöntä, kun verkkopyyntöjä yritetään uudelleen.
- **Uudelleenyritys.** *Serializable*-tasolla ja SQLiten lukituksissa
  sovellus varautuu yrittämään transaktion uudelleen. SQLitessä asetetaan
  odotusaika (`PRAGMA busy_timeout = 5000` tai Pythonin `timeout`),
  ja WAL-tila otetaan käyttöön, kun lukijoita on monta.
- **Hinnat**: jokainen sitoutus kirjoittaa levylle ja odottaa sen
  valmistumista (*fsync*), mikä kestää millisekunteja. Tuhat lisäystä
  tuhannessa transaktiossa on siksi kertaluokkia hitaampaa kuin sama
  yhdessä transaktiossa. Joukkolisäykset tehdään aina yhdessä
  transaktiossa.

## Itsearviointi

- Osaat kirjoittaa UPSERT-lauseen ja palauttaa muutetut rivit
  `RETURNING`-osalla.
- Osaat tehdä tarkistuksen ja muutoksen samassa lauseessa niin, että
  se on oikein samanaikaisesti.
- Osaat selittää eristystasot, *lost update* -ongelman ja sen
  korjaukset PostgreSQL:ssä.
- Osaat kertoa, miten SQLiten lukitus ja WAL-tila toimivat ja miksi
  kirjoittava transaktio aloitetaan `BEGIN IMMEDIATE` -lauseella.
