# Muutokset ja transaktiot

Edelliset luvut lukivat dataa ja määrittelivät sille säännöt. Tämä
luku muuttaa sitä: ensin muutoslauseet `INSERT`, `UPDATE` ja `DELETE`,
sitten lisäys, joka ei kaadu toistoon, ja muutokset, jotka palauttavat
tuloksensa, ja lopuksi transaktiot, jotka tekevät monesta muutoksesta
yhden kokonaisuuden myös silloin, kun kirjoittajia on monta.

## INSERT, UPDATE ja DELETE

`INSERT` lisää rivejä joko luetelluista arvoista tai toisen kyselyn
tuloksesta:

```{.sql tiedosto="esimerkit/10-muutokset.sql" osa="insert"}
```

`UPDATE` muuttaa ja `DELETE` poistaa ne rivit, joille `WHERE`-ehto on
tosi. Ehto on sama kuin kyselyissä, joten osuvat rivit voi tarkistaa
ensin `SELECT`-lauseella:

```{.sql tiedosto="esimerkit/10-muutokset.sql" osa="update"}
```

```{.sql tiedosto="esimerkit/10-muutokset.sql" osa="delete"}
```

```{.tuloste tiedosto="esimerkit/10-muutokset.odotettu"}
```

`SET`-lausekkeen oikea puoli näkee rivin vanhat arvot, joten
`hinta_snt = hinta_snt * 90 / 100` laskee uuden hinnan vanhasta.
`changes()` kertoo SQLitessä muuttuneiden rivien määrän; sovelluksessa
sama tieto tulee ajurilta (luku 14).

`UPDATE` ja `DELETE` ilman `WHERE`-ehtoa koskevat *jokaista* riviä,
eikä tietokanta kysy varmistusta. Käsin tehtävät muutokset ajetaan
siksi transaktiossa (alla), jolloin tuloksen voi tarkistaa ennen
sitoutusta ja perua.

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
virheen jälkeen kutsutaan `ROLLBACK` (luku 14).

## Eristystasot

Samanaikaiset transaktiot voivat häiritä toisiaan. Tavallisin
esimerkki on *kadonnut päivitys* (*lost update*): kaksi transaktiota
lukee saman saldon, laskee uuden arvon sovelluksessa ja kirjoittaa sen
takaisin. Jälkimmäinen kirjoitus peittää ensimmäisen:

```{.dot otsikko="Kadonnut päivitys. Aika kulkee ylhäältä alas. Kumpikin transaktio laskee uuden saldon lukemastaan arvosta 10, joten A:n vähennys häviää."}
digraph {
  rankdir=TB; nodesep=0.35; ranksep=0.2; splines=false;
  node [fontsize=9, width=1.9, height=0.34, fixedsize=true];
  ha [label="Transaktio A", shape=plain, style="", fontsize=10, fixedsize=false];
  hb [label="Transaktio B", shape=plain, style="", fontsize=10, fixedsize=false];
  hk [label="saldo kannassa", shape=plain, style="", fontsize=10, fixedsize=false];
  a1 [label="SELECT saldo → 10"];
  b1 [label="SELECT saldo → 10"];
  a2 [label="UPDATE saldo = 7 (10 − 3)"];
  a3 [label="COMMIT"];
  b2 [label="UPDATE saldo = 5 (10 − 5)"];
  b3 [label="COMMIT"];
  node [shape=plain, style="", fixedsize=false];
  k0 [label="10"]; k1 [label="10"]; k2 [label="10"]; k3 [label="7"];
  k4 [label="7"]; k5 [label="5 (pitäisi olla 2)"];
  node [style=invis];
  x1; x2; x3; x4; x5; x6;
  { rank=same; ha; hb; hk; }
  { rank=same; a1; x1; k0; }
  { rank=same; x2; b1; k1; }
  { rank=same; a2; x3; k2; }
  { rank=same; a3; x4; k3; }
  { rank=same; x5; b2; k4; }
  { rank=same; x6; b3; k5; }
  edge [style=invis];
  ha -> a1 -> x2 -> a2 -> a3 -> x5 -> x6;
  hb -> x1 -> b1 -> x3 -> x4 -> b2 -> b3;
  hk -> k0 -> k1 -> k2 -> k3 -> k4 -> k5;
  edge [style=solid, constraint=false];
  a1 -> a2 -> a3;
  b1 -> b2 -> b3;
}
```

Muita poikkeamia ovat

- *likainen luku* (*dirty read*): transaktio näkee toisen sitomattoman
  muutoksen, joka ehkä perutaan,
- *toistumaton luku* (*non-repeatable read*): sama rivi antaa saman
  transaktion aikana kaksi eri arvoa,
- *haamurivi* (*phantom*): sama ehto palauttaa toisella kerralla
  rivejä, joita ensimmäisellä ei ollut,
- *kirjoitusvinouma* (*write skew*): kaksi transaktiota tarkistaa saman
  ehdon ("päivystäjiä on vähintään kaksi") ja muuttaa kumpikin eri
  riviä niin, että ehto rikkoutuu.

Standardi määrittelee neljä eristystasoa sen mukaan, mitkä poikkeamat
ne sallivat:

| Taso | Estää |
|------|-------|
| *read uncommitted* | ei mitään (PostgreSQL toimii kuten seuraava) |
| *read committed* | sitomattomien muutosten lukemisen |
| *repeatable read* | lisäksi saman rivin eri arvot saman transaktion aikana |
| *serializable* | kaikki: tulos on kuin transaktiot olisi ajettu peräkkäin |

**PostgreSQL**:n oletus on *read committed*: jokainen lause näkee
lauseen alussa sitoutetun tilan. Kuvan *luku–muokkaus–kirjoitus*
(`SELECT saldo`, lasku sovelluksessa, `UPDATE saldo = ?`) kadottaa
sillä toisen transaktion samanaikaisen muutoksen. Kirjoitusvinouman
estää vasta *serializable*. Kadonneen päivityksen korjauksia ovat atominen päivitys
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

- Osaat lisätä, muuttaa ja poistaa rivejä ja tarkistaa etukäteen,
  mihin riveihin muutos osuu.
- Osaat kirjoittaa UPSERT-lauseen ja palauttaa muutetut rivit
  `RETURNING`-osalla.
- Osaat tehdä tarkistuksen ja muutoksen samassa lauseessa niin, että
  se on oikein samanaikaisesti.
- Osaat selittää eristystasot, kadonneen päivityksen ja sen
  korjaukset PostgreSQL:ssä sekä nimetä muut samanaikaisuuden
  poikkeamat.
- Osaat kertoa, miten SQLiten lukitus ja WAL-tila toimivat ja miksi
  kirjoittava transaktio aloitetaan `BEGIN IMMEDIATE` -lauseella.
