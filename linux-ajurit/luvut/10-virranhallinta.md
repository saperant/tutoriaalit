# Virranhallinta

Edellisen luvun ajuri kytki anturin päälle sidonnassa ja sammutti sen
irrotuksessa. Akkukäyttöisessä laitteessa se ei riitä: anturi, jota
luetaan kerran minuutissa, kuluttaisi virtaa koko ajan. Linuxin
virranhallinnassa on ajurin kannalta kaksi erillistä tilannetta:

- **Ajonaikainen virranhallinta** (*runtime PM*) sammuttaa yksittäisen
  laitteen, kun kukaan ei käytä sitä, vaikka muu järjestelmä on
  käynnissä.
- **Järjestelmän lepotila** (*system sleep*) pysäyttää koko järjestelmän:
  prosessit jäädytetään, laitteet sammutetaan ja suoritin pysähtyy,
  kunnes jokin herätyslähde käynnistää sen.

Kummassakin ajurin tehtävä on sama: saattaa laite tilaan, jossa siltä
voi katkaista virran, ja palauttaa se toimintaan. Ydin päättää, milloin.
Tässä luvussa edellisen luvun paineanturin ajuriin lisätään molemmat.
Resurssien haku ja kytkentäjärjestys pysyvät ennallaan (`paine.h`), ja
uusi ajuri `paine_pm` sisältää vain sen, mikä virranhallinnasta seuraa.

## Käyttölaskuri ja tilat

Ajonaikainen virranhallinta perustuu jokaisen laitteen
*käyttölaskuriin*. Ajuri kasvattaa laskuria, kun se tarvitsee laitetta,
ja vähentää sitä, kun tarve loppuu. Ydin kutsuu ajurin takaisinkutsuja
laskurin perusteella:

```{.dot otsikko="Ajonaikaisen virranhallinnan tilat. Sulkeissa on tiedoston `power/runtime_status` arvo."}
digraph {
  rankdir=LR; node [shape=box, style=rounded];
  a [label="päällä\n(active)"];
  s [label="sammumassa\n(suspending)"];
  n [label="sammutettu\n(suspended)"];
  r [label="heräämässä\n(resuming)"];
  a -> s [label="laskuri 0 ja\nlepoviive kulunut"];
  s -> n [label="runtime_suspend\npalautti 0"];
  s -> a [label="virhe tai\nuusi käyttäjä"];
  n -> r [label="laskuri 0 → 1"];
  r -> a [label="runtime_resume\npalautti 0"];
}
```

Takaisinkutsut käyttävät edellisen luvun funktioita sellaisinaan:

```{.c tiedosto="esimerkit/07-resurssit/paine_pm.c" osa="runtime"}
```

Ydin takaa, että takaisinkutsuja ei ajeta päällekkäin ja että
`runtime_suspend`-kutsua seuraa aina `runtime_resume` ennen seuraavaa
sammutusta. Ajurin ei siis tarvitse muistaa, onko laite päällä.

Jos laite sammuisi heti laskurin pudottua nollaan, kaksi peräkkäistä
mittausta kytkisi virran kahdesti, ja kytkentä maksaa aikaa ja energiaa.
*Lepoviive* (*autosuspend*) lykkää sammutusta: laite sammuu vasta, kun
se on ollut käyttämättä viiveen verran.

## Laitteen käyttö

Jokainen kohta, jossa ajuri koskee laitteeseen, on käyttölaskurin
kasvatuksen ja vähennyksen välissä:

```{.c tiedosto="esimerkit/07-resurssit/paine_pm.c" osa="mittaus"}
```

`pm_runtime_resume_and_get` palaa vasta, kun laite on päällä, joten se
voi nukkua eikä sitä saa kutsua keskeytyksen yläpuoliskosta.
`pm_runtime_mark_last_busy` kirjaa käyttöhetken, josta lepoviive
lasketaan, ja `pm_runtime_put_autosuspend` vähentää laskuria ja
ajastaa sammutuksen.

Pitkäkestoinen käyttö pitää viittausta niin kauan kuin tarve jatkuu.
Esimerkissä sitä edustaa attribuutti `jatkuva`: arvo 1 ottaa viittauksen
samalla `pm_runtime_resume_and_get`-kutsulla ja arvo 0 vapauttaa sen.
Merkkilaitteessa vastaava pari on tavallisesti `open` ja `release`, ja
verkkoajurissa liitännän avaus ja sulkeminen.

## Käyttöönotto probessa

Ydin ei tiedä, onko laite päällä, kun `probe` alkaa. Ajuri kertoo sen
ja ottaa virranhallinnan käyttöön:

```{.c tiedosto="esimerkit/07-resurssit/paine_pm.c" osa="probe"}
```

Järjestys on olennainen. `pm_runtime_set_active` kertoo todellisen tilan
ennen kuin `pm_runtime_enable` sallii ytimen toimia sen perusteella, ja
`pm_runtime_get_noresume` pitää laitteen päällä `probe`-funktion
loppuun. Viimeinen `put` vapauttaa viittauksen, jolloin lepoviive alkaa.

Irrotus tekee saman toisin päin:

```{.c tiedosto="esimerkit/07-resurssit/paine_pm.c" osa="remove"}
```

## Tilat näkyvissä

Testin apuohjelma `tila` lukee viisi tiedostoa ja tulostaa ne yhdelle
riville. Polut ovat ne, joista tilaa katsottaisiin käsinkin:

```{.c tiedosto="esimerkit/07-resurssit/tila.c" osa="polut"}
```

Latauksen jälkeen anturi on päällä, ja kahden sekunnin kuluttua se on
sammunut itsestään:

```{.tuloste tiedosto="esimerkit/testit/07-ajonaikainen.odotettu" osa="alku"}
```

Mittaus herättää anturin. Toinen mittaus heti perään ei kytke virtaa
uudelleen, koska lepoviive ei ole ehtinyt kulua:

```{.tuloste tiedosto="esimerkit/testit/07-ajonaikainen.odotettu" osa="mittaus"}
```

Jatkuva tila pitää käyttölaskurin ykkösessä, eikä anturi sammu, vaikka
aikaa kuluu. Kun tila kytketään pois, laskuri putoaa nollaan heti mutta
virta katkeaa vasta lepoviiveen jälkeen:

```{.tuloste tiedosto="esimerkit/testit/07-ajonaikainen.odotettu" osa="jatkuva"}
```

Sama aikajanana. Kaavio on tuotettu yllä olevista tulosteista, ja testi
tarkistaa, että se vastaa niitä:

```{.ajoituskaavio tiedosto="esimerkit/kaaviot/virta.json" otsikko="Anturin virtatila testin vaiheiden jälkeen. Jokainen sarake on yksi `tila`-ohjelman tuloste; ylin rivi kertoo, mitä sitä ennen tehtiin."}
```

Käyttäjä voi ohittaa ajurin päätökset. Laitteen `power`-hakemiston
tiedosto `control` pakottaa laitteen päälle arvolla `on` ja palauttaa
automatiikan arvolla `auto`, ja `autosuspend_delay_ms` muuttaa
lepoviivettä:

```{.tuloste tiedosto="esimerkit/testit/07-ajonaikainen.odotettu" osa="ohjaus"}
```

Moduulin poisto näyttää vielä yhden yksityiskohdan: ydin herättää
laitteen ennen irrotusta, jotta `remove` näkee sen tunnetussa tilassa.

```{.tuloste tiedosto="esimerkit/testit/07-ajonaikainen.odotettu" osa="irrotus"}
```

Tila `unsupported` tarkoittaa, että laitteella ei ole ajuria, joka olisi
ottanut ajonaikaisen virranhallinnan käyttöön.

## Järjestelmän lepotila

Kun järjestelmä siirtyy lepotilaan, ydin käy kaikki laitteet läpi
laitepuun mukaisessa järjestyksessä: lapset ennen vanhempia ja
kuluttajat ennen tarjoajia. Herätessä järjestys on käänteinen. Ajurin
kannalta vaiheita on neljä:

| Vaihe | Takaisinkutsu | Tilanne |
|-------|---------------|---------|
| valmistelu | `prepare` | uusia lapsilaitteita ei saa enää syntyä |
| sammutus | `suspend` | keskeytykset toimivat, saa nukkua |
| myöhäinen sammutus | `suspend_late`, `suspend_noirq` | ensin ajonaikainen virranhallinta, sitten laitekeskeytykset pois |
| herätys | `resume_noirq`, `resume_early`, `resume`, `complete` | samat käänteisessä järjestyksessä |

Useimmille ajureille riittää `suspend` ja `resume`. Anturin ajurissa
niitäkään ei tarvitse kirjoittaa, koska lepotila vaatii siltä saman kuin
ajonaikainen sammutus. Makro `DEFINE_RUNTIME_DEV_PM_OPS` asettaa
lepotilan takaisinkutsuiksi ytimen funktiot `pm_runtime_force_suspend`
ja `pm_runtime_force_resume`: ensimmäinen ajaa ajurin
`runtime_suspend`-funktion, jos laite on päällä, ja jälkimmäinen
palauttaa laitteen siihen tilaan, jossa se oli. Rakenne annetaan
ajurille kentässä `.driver.pm`.

Lepotilaa on vaikea testata: järjestelmä pysähtyy, ja sen herättämiseen
tarvitaan herätyslähde. Ytimessä on tätä varten testitila, joka ajaa
lepotilan valittuun vaiheeseen asti, odottaa hetken ja palaa:

```{.tuloste tiedosto="esimerkit/testit/07-lepotila.odotettu" osa="testitila"}
```

Tiedosto `/sys/power/state` luettelee tuetut lepotilat. `freeze` on
ohjelmallinen lepotila (*suspend-to-idle*), jossa suorittimet jäävät
tyhjäkäyntiin, ja `mem` katkaisee virran kaikesta paitsi muistista.
Testitason `devices` kohdalla ydin jäädyttää prosessit, ajaa laitteiden
sammutuksen, odottaa asetetun sekunnin ja ajaa herätyksen.

Jos anturi on jo sammutettu ajonaikaisesti, lepotilassa ei tapahdu sille
mitään:

```{.tuloste tiedosto="esimerkit/testit/07-lepotila.odotettu" osa="nukkuva"}
```

Jos se on käytössä, se sammutetaan lepotilan ajaksi ja käynnistetään
uudelleen, ja käyttölaskuri säilyy:

```{.tuloste tiedosto="esimerkit/testit/07-lepotila.odotettu" osa="kaytossa"}
```

Myös kellon tarjoajan rivit näkyvät: kello sammui, koska sen ainoa
käyttäjä sammutti sen, eikä tarjoajassa ole lepotilakoodia lainkaan.

## Mitä herätessä on palautettava

Kun laitteelta katkaistaan jännite, sen rekisterit nollautuvat. Ajurin
`runtime_resume` ja `resume` eivät siis saa olettaa, että laite on
samassa tilassa kuin ennen:

- **Asetukset kirjoitetaan uudelleen.** Mittausalue, suodattimet ja
  keskeytysmaskit on palautettava. Jos ajuri käyttää regmapia ja sen
  välimuistia (luku 7), `regcache_mark_dirty` sammutuksessa ja
  `regcache_sync` herätyksessä tekevät sen yhdellä kutsulla.
- **Kehysten tila säilyy.** Kellon taajuus, säätimen jännite ja
  GPIO-linjojen suunnat ovat ytimen muistissa, ja tarjoajat palauttavat
  ne itse.
- **Keskeneräinen työ lopetetaan ennen sammutusta.** `suspend` peruu
  työjonon työt ja ajastimet ja odottaa kesken olevan siirron loppuun,
  ennen kuin kello katkaistaan.

Esimerkin anturilla ei ole rekistereitä, joten palautettavaa ei ole.
Oikeassa ajurissa `paine_virta_paalle`-funktion perään tulisi
asetusten kirjoitus.

## Herätyslähteet

Lepotilasta herättää laite, joka on merkitty *herätyslähteeksi*:
virtapainike, reaaliaikakellon hälytys tai verkkoliitäntä. Ajuri
ilmoittaa kyvystä funktiolla `device_init_wakeup`, tavallisesti silloin,
kun laitteen solmussa on ominaisuus `wakeup-source`, ja
`dev_pm_set_wake_irq` kertoo, mikä keskeytys herättää. Ydin virittää
keskeytyksen herätyskäyttöön lepotilaan mennessä, ja käyttäjä voi sallia
tai kieltää herätyksen laitteen tiedostolla `power/wakeup`.

Herätyslähteen on pysyttävä päällä lepotilan ajan, joten sen `suspend`
ei saa katkaista laitteen virtaa, jos `device_may_wakeup` palauttaa
toden. Paineanturi ei ole herätyslähde: kun siltä katkaistaan jännite,
se ei pysty nostamaan hälytyslinjaansa. Testitila ei myöskään testaa
herätystä, vaan palaa ajastimella.

Oikeassa järjestelmäpiirissä laitteet kuuluvat lisäksi *tehoalueisiin*
(*power domain*): piirin lohkoihin, joilta virta katkaistaan yhdessä.
Alue sammuu, kun sen kaikki laitteet ovat ajonaikaisesti sammutettuja,
joten yksikin ajuri ilman virranhallintaa pitää koko alueen päällä.

## Käytännössä

- **Toteuta ajonaikainen virranhallinta ensin.** Kun `runtime_suspend`
  ja `runtime_resume` toimivat, järjestelmän lepotila on useimmiten
  sama pari makron `DEFINE_RUNTIME_DEV_PM_OPS` kautta.
- **Jokaisella `get`-kutsulla on `put`.** Vuotanut viittaus pitää
  laitteen päällä ikuisesti, eikä siitä tule virheilmoitusta.
  `runtime_usage` ja `runtime_status` paljastavat sen.
- **Käytä lepoviivettä laitteissa, joiden käynnistys on hidasta.**
  Viiveen pituus on kompromissi kytkentöjen määrän ja turhan päälläolon
  välillä.
- **Testaa irrotus ja lepotila sekä päällä että sammutettuna.** Virheet
  ovat lähes aina tilassa, jota ei kokeiltu: laite irrotetaan
  sammutettuna tai järjestelmä nukahtaa kesken siirron.
- **Aja lepotila testitilassa ennen oikeaa laitetta.**
  `/sys/power/pm_test` erottaa ajurin viat alustan ja laiteohjelmiston
  vioista.

## Itsearviointi

- Osaat selittää ajonaikaisen virranhallinnan ja järjestelmän lepotilan
  eron ja sen, kumpaa ydin käyttää missäkin tilanteessa.
- Osaat lisätä ajuriin `runtime_suspend`- ja
  `runtime_resume`-takaisinkutsut ja ottaa virranhallinnan käyttöön
  `probe`-funktiossa oikeassa järjestyksessä.
- Osaat suojata laitteen käytön käyttölaskurilla ja selittää, mitä
  lepoviive muuttaa.
- Osaat lukea laitteen virtatilan sysfsistä ja pakottaa laitteen päälle
  vianetsintää varten.
- Osaat selittää lepotilan vaiheet, ajaa ne testitilassa ja kertoa, mitä
  ajurin on palautettava herätessä.
- Osaat selittää, mikä tekee laitteesta herätyslähteen ja miksi
  herätyslähdettä ei saa sammuttaa lepotilassa.
