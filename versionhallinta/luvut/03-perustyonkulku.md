# Muutokset ja commitit

Arkityön sykli on: muokkaa, tarkista, valmistele, tallenna. Tässä
luvussa käydään läpi valmistelualueen käyttö, muutosten tarkastelu ja
hyvä commit.

## Valmistelualue

Valmistelualue erottaa sen, mitä on muutettu, siitä, mitä seuraavaan
committiin tulee. Sen avulla yhdestä työsessiosta voi tehdä useita
loogisia committeja. Seuraavassa `laskuri.py` lisätään valmisteluun ja
sitä muokataan sen jälkeen vielä:

```{.bash tiedosto="esimerkit/03-tila.sh" osa="muutokset"}
```

`MM` kertoo, että tiedostossa on sekä valmisteltu että valmistelematon
muutos. Kaksi diffiä erottaa ne: `git diff` vertaa työhakemistoa
valmistelualueeseen ja `git diff --staged` valmistelualuetta viimeiseen
committiin.

```{.bash tiedosto="esimerkit/03-tila.sh" osa="diffit"}
```

Valmistelua ja työhakemiston muutoksia perutaan komennolla `git restore`.
Ilman valitsinta se palauttaa työhakemiston tiedoston valmistelualueen
tilaan ja hylkää muutoksen pysyvästi. `--staged` poistaa tiedoston
valmistelusta, mutta muutos jää työhakemistoon:

```{.bash tiedosto="esimerkit/03-tila.sh" osa="palautus"}
```

```{.tuloste tiedosto="esimerkit/03-tila.odotettu"}
```

Osan tiedostosta voi valmistella komennolla `git add -p`, joka kysyy
jokaisesta muutoslohkosta erikseen. Se on paras työkalu siihen, että
kaksi asiaa samassa tiedostossa päätyy kahteen eri committiin.
(Interaktiivista komentoa ei voi ajaa esimerkkien testeissä.)

## Historian tarkastelu

`git log` näyttää historian uusimmasta alkaen. Sen muotoilu ja suodatus
kannattaa opetella, koska historiaa luetaan paljon useammin kuin sitä
kirjoitetaan:

```{.bash tiedosto="esimerkit/03-historia.sh" osa="loki"}
```

`-- polku` rajaa historian tiedostoon tai hakemistoon. `-S teksti`
(*pickaxe*) etsii commitit, joissa tekstin esiintymien määrä muuttui,
eli joissa se lisättiin tai poistettiin. `-G regex` etsii muutoksia,
joissa rivi täsmää lausekkeeseen. `git show` näyttää yhden commitin
viesteineen ja muutoksineen:

```{.bash tiedosto="esimerkit/03-historia.sh" osa="show"}
```

```{.tuloste tiedosto="esimerkit/03-historia.odotettu"}
```

Muita hyödyllisiä valitsimia ovat `--stat` (muuttuneet tiedostot),
`--author`, `--since="2 weeks ago"`, `--grep` (viestin haku) ja
`--graph` (haarautuminen, luku *Haarat ja yhdistäminen*).

## Hyvä commit

Hyvä commit on *yksi looginen muutos*: se kääntyy ja läpäisee testit,
ja sen voi perua tai poimia toiseen haaraan yksinään. Kun refaktorointi
ja uusi ominaisuus ovat eri commiteissa, katselmointi on helpompaa, ja
`git bisect` (luku *Historian tutkiminen ja korjaaminen*) osoittaa
tarkemmin.

Commit-viestin vakiintunut muoto:

```text
Korjaa sanojen erotin                         <- otsikko, alle 50 merkkiä

Pelkkä split() jakoi myös rivinvaihdoista,     <- tyhjä rivi, sitten
jolloin sanamäärä oli väärä rivien lopussa.      leipäteksti 72 merkin
Erotin näkyviin, jotta käytös on selvä.          riveinä: miksi, ei mitä
```

- Otsikko on käskymuodossa ("Korjaa", "Lisää"), iso alkukirjain, ei
  pistettä. Se täydentää lauseen "Kun tämä commit otetaan käyttöön,
  se …".
- Leipäteksti kertoo *miksi*: mikä ongelma, mitä vaihtoehtoja hylättiin,
  mitä seurauksia on. *Mitä* näkyy diffistä.
- Viittaukset tehtäviin ja vikailmoituksiin (`Korjaa #123`) loppuun.
  Monet tiimit käyttävät rakenteista muotoa, kuten Conventional Commits
  (`fix: …`, `feat: …`), josta muutosloki voidaan generoida.

## Käytännössä

- **Katso ennen kuin tallennat.** `git diff --staged` ennen jokaista
  committia paljastaa vahingossa mukaan tulleet tiedostot, debug-tulosteet
  ja salaisuudet. `git commit -a` (kaikki seuratut muutokset) on kätevä,
  mutta ohittaa tämän tarkistuksen.
- **Pieniä committeja usein.** Paikallinen commit on halpa ja helppo
  muokata ennen jakamista (luku *Rebase ja historian siistiminen*).
  Pieni commit on helppo katselmoida ja perua.
- **Ei muotoilua ja logiikkaa samaan committiin.** Koko tiedoston
  uudelleenmuotoilu peittää todellisen muutoksen diffissä ja rikkoo
  `git blame`n. Muotoilu omaan committiinsa, ja sen tunniste voidaan
  lisätä tiedostoon `.git-blame-ignore-revs`.
- **`git restore` on peruuttamaton** valmistelemattomille muutoksille:
  ne eivät ole koskaan olleet Gitin olioina. Epävarmassa tilanteessa
  `git stash` tallentaa keskeneräiset muutokset talteen ja `git stash
  pop` palauttaa ne.

## Itsearviointi

- Osaat selittää `git status --short`in kaksi saraketta ja tilan `MM`.
- Osaat näyttää valmistellut ja valmistelemattomat muutokset erikseen ja
  perua kumman tahansa.
- Osaat etsiä historiasta commitin tiedoston, tekijän, ajan tai muuttuneen
  tekstin perusteella (`-- polku`, `--author`, `--since`, `-S`).
- Osaat kirjoittaa commit-viestin, jonka otsikko kertoo mitä ja
  leipäteksti miksi.
