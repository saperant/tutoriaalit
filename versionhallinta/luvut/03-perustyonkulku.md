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

Osan tiedostosta voi valmistella komennolla `git add -p`, joka näyttää
jokaisen muutoslohkon ja kysyy siitä erikseen. Se on paras työkalu
siihen, että kaksi asiaa samassa tiedostossa päätyy kahteen eri
committiin. Interaktiivista komentoa ei voi ajaa esimerkkien testeissä,
joten alla on mallituloste:

```text
@@ -2,3 +2,4 @@ def rivit(teksti):
     return teksti.count("\n")
 def sanat(teksti):
     return len(teksti.split())
+# TODO: merkit
(1/1) Stage this hunk [y,n,q,a,d,e,?]?
```

Vastaus `y` valmistelee lohkon ja `n` ohittaa sen. `s` jakaa lohkon
pienempiin, kun se on mahdollista, `q` lopettaa ja `?` näyttää ohjeen.

Tiedoston poisto ja uudelleennimeäminen ovat nekin muutoksia, jotka
valmistellaan. `git rm tiedosto` poistaa tiedoston sekä työhakemistosta
että valmistelualueelta, ja `git rm --cached tiedosto` vain
valmistelualueelta, jolloin tiedosto jää levylle mutta poistuu
versionhallinnasta. `git mv vanha uusi` nimeää tiedoston uudelleen ja
valmistelee muutoksen.

## Tiedostot, joita ei versioida: .gitignore

Työhakemistoon kertyy tiedostoja, jotka eivät kuulu historiaan:
käännöstuotteita, lokeja, editorin tiedostoja ja salaisuuksia.
`git status` näyttää ne seuraamattomina (`??`), ja `git add .` ottaisi
ne mukaan. Tiedosto `.gitignore` luettelee kuviot, joihin täsmäävät
seuraamattomat tiedostot Git jättää huomiotta:

```{.bash tiedosto="esimerkit/03-ignore.sh" osa="ignore"}
```

```{.tuloste tiedosto="esimerkit/03-ignore.odotettu"}
```

`.gitignore` on itse versioitava tiedosto, joten säännöt koskevat
kaikkia repositorion käyttäjiä. Se kannattaa tehdä ennen ensimmäistä
committia, koska jo versioituun tiedostoon se ei vaikuta. Kuvioiden
tarkka kielioppi, poikkeukset ja vianetsintä käsitellään luvussa
*Koukut, .gitignore ja .gitattributes*.

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

## Keskeneräinen työ talteen: stash

Kesken työn tulee usein tarve vaihtaa haaraa tai hakea muiden muutokset,
mutta keskeneräisestä työstä ei vielä kannata tehdä committia. `git stash`
tallentaa työhakemiston ja valmistelualueen muutokset pinoon ja palauttaa
työhakemiston viimeisen commitin tilaan:

```{.bash tiedosto="esimerkit/03-stash.sh" osa="stash"}
```

`git stash pop` palauttaa päällimmäisen tallennuksen ja poistaa sen
pinosta. `git stash apply` palauttaa poistamatta:

```{.bash tiedosto="esimerkit/03-stash.sh" osa="pop"}
```

Ilman valitsinta `-u` seuraamattomat tiedostot jäävät työhakemistoon.
Jos palautus osuu samoihin riveihin, joita on välillä muutettu, syntyy
konflikti (luku *Konfliktit*), ja tallennus jää pinoon, kunnes se
poistetaan komennolla `git stash drop`. Stash on tarkoitettu minuuttien
tai tuntien säilytykseen. Pidempään säilytettävä työ kuuluu omaan
haaraansa committina.

Seuraamattomat tiedostot poistaa `git clean`. Se on peruuttamaton,
joten ensin katsotaan valitsimella `-n`, mitä poistettaisiin:

```{.bash tiedosto="esimerkit/03-stash.sh" osa="clean"}
```

```{.tuloste tiedosto="esimerkit/03-stash.odotettu"}
```

`git clean -n` olisi poistanut myös muistiinpanon, joten esimerkissä
poistettava tiedosto nimetään. Koko työhakemiston siivoaa `git clean
-fd`, ja `-x` poistaa myös `.gitignore`n ohittamat tiedostot.

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
  `git blame`n. Muotoilu tehdään omaan committiinsa, jonka blame voi
  ohittaa (luku *Historian tutkiminen ja korjaaminen*).
- **`git restore` on peruuttamaton** valmistelemattomille muutoksille:
  ne eivät ole koskaan olleet Gitin olioina. Epävarmassa tilanteessa
  `git stash` vie muutokset talteen hylkäämättä niitä.
- **`.gitignore` ensimmäiseen committiin.** Valmiita pohjia eri
  kielille on osoitteessa <https://github.com/github/gitignore>.

## Itsearviointi

- Osaat selittää `git status --short`in kaksi saraketta ja tilan `MM`.
- Osaat näyttää valmistellut ja valmistelemattomat muutokset erikseen ja
  perua kumman tahansa.
- Osaat jättää käännöstuotteet ja salaisuudet pois versionhallinnasta
  `.gitignore`-tiedostolla.
- Osaat viedä keskeneräisen työn talteen ja palauttaa sen (`git stash`)
  sekä tarkistaa ennen `git clean` -komentoa, mitä se poistaisi.
- Osaat etsiä historiasta commitin tiedoston, tekijän, ajan tai muuttuneen
  tekstin perusteella (`-- polku`, `--author`, `--since`, `-S`).
- Osaat kirjoittaa commit-viestin, jonka otsikko kertoo mitä ja
  leipäteksti miksi.
