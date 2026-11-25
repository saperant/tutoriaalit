---
title: Hajautetut järjestelmät
subtitle: Pikaopas · vikamallit, kellot, replikointi, konsensus ja simulointitestaus
lang: fi
---

# Vikamallit

| Malli | Mitä voi tapahtua |
|--------------------------|----------------------------|
| kaatuminen ja pysähtyminen | solmu lakkaa toimimasta pysyvästi |
| kaatuminen ja palautuminen | muisti katoaa, levy säilyy |
| puutteellinen toiminta | viestejä jää lähettämättä tai vastaanottamatta |
| bysanttilainen | mitä tahansa, myös valheita |

- **Verkko:** katoaa, viivästyy, monistuu, järjestyy uudelleen, jakautuu.
- **Ajoitus:** synkroninen (yläraja tunnettu), asynkroninen (ei ylärajaa,
  FLP), osittain synkroninen (yläraja lopulta).
- **Turvallisuus** (ei koskaan pahaa) ennen **etenemistä** (lopulta
  hyvää).
- **Vikailmaisin:** lyhyt aikaraja → vääriä epäilyjä, pitkä → hidas
  tunnistus.
- **Kuittaa vasta, kun lupaus on levyllä.**

# Simulaattori

- Solmu on tilakone: `kaynnisty`, `vastaanota(lahettaja, viesti)`,
  `ajastin(tunniste)`; maailma näkyy vain `Yhteys`-rajapinnan kautta
  (`laheta`, `ajasta`, `kello`, `satunnainen`).
- Viive, katoaminen ja monistus arvotaan siemenestä; sama siemen →
  sama suoritus.
- `kaada(i)` tuhoaa olion (haihtuva tila katoaa), `kaynnista(i)` luo
  uuden samalla levyllä; `jaa({...})`, `paranna()`.
- Yksi satunnaisluku lauseessa, `std::map` eikä `unordered_map`.

# Kellot

| Kello | Takuu | Hinta |
|-------|-------|-------|
| fyysinen | lähellä oikeaa aikaa | ei järjestystakuuta |
| Lamport | a → b ⇒ L(a) < L(b) | ei tunnista samanaikaisuutta |
| vektori | a → b ⇔ V(a) < V(b) | yksi alkio solmua kohden |
| hybridi (HLC) | kuten Lamport, l lähellä fyysistä | kaksi kenttää |

- Lamport: tapahtuma `++t`, vastaanotto `t = max(t, m) + 1`.
- Vektori: oma `++v[i]`, vastaanotto alkioittain maksimi.
- LWW fyysisillä leimoilla hukkaa myöhemmän kirjoituksen, kun kellot
  poikkeavat.

# Replikointi

| Tapa | Kuittaus | Riski |
|------|----------|-------|
| asynkroninen | heti | vaihto hukkaa kuitattua |
| puolisynkroninen | yksi seuraaja | uusi johtaja voi olla väärä |
| synkroninen | kaikki seuraajat | yksi kaatunut pysäyttää |
| kvoorumi | W kuittausta, R vastausta | R + W ≤ N → vanhoja lukuja |

- **Kvoorumit leikkaavat**, kun R + W > N; tyypillisesti N = 3, R = W = 2.
- **Lukukorjaus** päivittää jäljessä olevan, **anti-entropia** loput.
- Kvoorumi ei yksin ole linearisoituva: luku tarvitsee
  takaisinkirjoituksen (ABD).
- **Vuokra + aitausmerkki:** vuokralla kasvava numero, resurssi hylkää
  pienemmän; tauon jälkeen heräävä vanha haltija ei pääse kirjoittamaan.

# CRDT

- Yhdistäminen vaihdannainen, liitännäinen ja idempotentti →
  lähentyminen ilman järjestystä tai kertalähetystä.
- **G-laskuri:** oma osuus, maksimi, summa. **PN:** kaksi G-laskuria.
- **OR-joukko:** lisäys saa tunnisteen, poisto poistaa nähdyt;
  lisäys voittaa, hautakivet kasvavat.
- Ei takaa invariantteja (saldo ≥ 0) → koordinointi.

# Konsistenssi

| Malli | Lyhyesti |
|-------|----------|
| linearisoituva | yksi kopio, reaaliaika |
| sarjallistuva | transaktiot jossain järjestyksessä |
| kausaalinen | syy ennen seurausta kaikille |
| istuntotakuut | omat kirjoitukset, ei taaksepäin |
| lopullinen | lähentyy, kun kirjoitukset loppuvat |

```{.cpp tiedosto="esimerkit/yhteinen/historia.hpp" osa="operaatio"}
```

- Tarkistin: valitse operaatio, jonka alkua ennen mikään tekemätön ei
  päättynyt; sovella; palaa umpikujasta; muista (tehdyt, arvo).
- Kesken jäänyt kirjoitus voi tapahtua tai olla tapahtumatta.

# Raft

- **Pysyvä:** termi, ääni, loki. Kirjoita ennen vastausta.
- **Vaali:** aikaraja satunnainen (150–300 ms), termi + 1, ääni itselle,
  enemmistö voittaa. Ääni vain ehdokkaalle, jonka loki on vähintään yhtä
  tuore (viimeinen termi, sitten pituus).
- **Suurempi termi viestissä** → päivitä termi, seuraajaksi.
- **Lisäys:** edeltävä (indeksi, termi) täsmättävä, ristiriita
  katkaistaan, johtaja perääntyy.
- **Sitoutus:** suurin enemmistön indeksi, jonka merkintä on *oman*
  termin; tyhjä merkintä termin alussa.
- **Ominaisuudet:** vaaliturvallisuus, vain lisäys, lokien
  yhtäpitävyys, johtajan täydellisyys, tilakoneen turvallisuus.
- Lisäksi tuotannossa: esiäänestys, tilannevedokset, kokoonpanon
  muutokset, ReadIndex tai vuokra.

# CAP, PACELC ja transaktiot

- **CAP:** jakautuessa joko hylkää (CP) tai vastaa vanhalla (AP).
- **PACELC:** muuten valitse viive (L) tai konsistenssi (C).
- **2PC:** valmistelu (kirjaa, lukitse, kyllä) → koordinaattori kirjaa
  päätöksen → lähettää. Koordinaattorin kaatuminen jättää osallistujat
  lukkoihin; palautuessa lokissa ei päätöstä → peru.
- **Täsmälleen kerran** = vähintään kerran + idempotenssiavain, joka
  tallennetaan samassa transaktiossa kuin muutos.

# Simulointitestaus

- Determinismi, vikojen ruiskutus, oraakkeli.
- Tarkista turvallisuus jokaisessa tilassa, eteneminen lopussa.
- Pienennä delta-debuggauksella: poista osa vioista kerrallaan, pidä
  poisto, jos virhe säilyy; tallenna siemen regressioksi.
- Mittaa kiinnostavat tilat; nolla esiintymää = puuttuva testi.
- Harvinaiset sarjat: parveilu, ohjattu ajoitus, TLA+.

# Tyypilliset virheet

| Oire | Syy |
|------|-----|
| kuitattu katoaa kaatuessa | kuittaus ennen `fsync`iä |
| kaksi johtajaa | ääni ei pysyvä tai ei enemmistöä |
| sitoutettu merkintä katoaa | vaalin lokiehto puuttuu |
| myöhempi kirjoitus häviää | LWW ja ajautuneet kellot |
| uusi arvo, sitten vanha | kvoorumiluku ilman takaisinkirjoitusta |
| tuplaveloitus | uudelleenyritys ilman idempotenssiavainta |
| siemen ei toistu | piilotettu epädeterminismi |
