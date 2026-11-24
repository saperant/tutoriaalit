# Rebase ja historian siistiminen

Yhdistäminen säilyttää historian sellaisena kuin se tapahtui. Rebase
kirjoittaa sen uudelleen: se toistaa haaran commitit uuden kannan
päälle. Tuloksena on suora historia, mutta commitit ovat uusia olioita.
Tässä luvussa opetellaan rebase, historian siistiminen ennen jakamista
ja rebasen tärkein sääntö.

## Rebase

Haarassa `sanat` on kaksi committia, ja `main` on edennyt yhdellä:

```{.bash tiedosto="esimerkit/06-rebase.sh" osa="ennen"}
```

`git rebase main` ottaa haaran commitit, joita `main`issa ei ole,
ja toistaa ne yksi kerrallaan `main`in kärjen päälle:

```{.bash tiedosto="esimerkit/06-rebase.sh" osa="rebase"}
```

Commitien sisältö ja viestit ovat samat, mutta tunnisteet muuttuivat.
Vanhempi on eri, joten commit on eri olio (luku *Gitin tietomalli*).
Vanhat commitit ovat yhä olemassa, ja ne löytyvät viitteistä `ORIG_HEAD`
ja reflog. Nyt `main` voidaan pikakelata, ja historia on suora:

```{.bash tiedosto="esimerkit/06-rebase.sh" osa="pikakelaus"}
```

```{.tuloste tiedosto="esimerkit/06-rebase.odotettu"}
```

Jos toistettava commit on ristiriidassa uuden kannan kanssa, rebase
pysähtyy konfliktiin. Ratkaise se kuten luvussa *Konfliktit*, merkitse
`git add`illa ja jatka komennolla `git rebase --continue`. Komento
`--abort` palauttaa haaran ennalleen.

## Historian siistiminen ennen jakamista

Omat paikalliset commitit ovat työpäiväkirja: "WIP", "korjaa
kirjoitusvirhe", "nyt toimii". Ennen jakamista ne kannattaa järjestää
loogisiksi muutoksiksi, jotka on helppo katselmoida. Interaktiivinen
rebase (`git rebase -i`) avaa tehtävälistan, jossa jokaisen commitin
kohtalon voi valita: `pick` (säilytä), `reword` (muuta viesti), `edit`
(pysähdy muokkaamaan), `squash` tai `fixup` (yhdistä edelliseen) ja
`drop` (pudota). Rivien järjestystä vaihtamalla commitit järjestyvät
uudelleen.

Kun virhe huomataan vanhemmassa commitissa, korjaus tehdään omana
committinaan ja merkitään korjaukseksi:

```{.bash tiedosto="esimerkit/06-siistiminen.sh" osa="fixup"}
```

`git rebase -i --autosquash` siirtää `fixup!`-commitit automaattisesti
korjattavan commitin perään ja merkitsee ne yhdistettäviksi. Normaalisti
tehtävälista avautuu editoriin. Skriptissä se muokataan
`GIT_SEQUENCE_EDITOR`-muuttujalla, tässä pudottamaan WIP-commit:

```{.bash tiedosto="esimerkit/06-siistiminen.sh" osa="interaktiivinen"}
```

```{.tuloste tiedosto="esimerkit/06-siistiminen.odotettu"}
```

Neljästä paikallisesta commitista tuli kaksi siistiä, ja sanalaskurin
commitissa on nyt oikea koodi. Viimeisimpään commitiin pääsee
suoremmin: `git commit --amend` korvaa sen uudella. Pitkässä
interaktiivisessa rebasessa kannattaa ensin tehdä varmuusviite
(`git branch varmuus`) tai muistaa reflog.

## Rebasen kultainen sääntö

> Älä kirjoita uudelleen historiaa, jonka joku muu on jo saanut.

Jos muut ovat rakentaneet työnsä haaran vanhojen commitien päälle,
uudelleenkirjoitus pakottaa heidät selvittämään, mitkä commitit ovat
"samoja". Omaa, vielä jakamatonta haaraa saa ja kannattaa siistiä.
Jaettua päähaaraa ei koskaan kirjoiteta uudelleen. Oman ominaisuushaaran
päivittäminen pull requestin aikana on tiimin sopimus. Silloin
pakotetaan aina komennolla `git push --force-with-lease`, joka
kieltäytyy, jos joku muu on ehtinyt pushata välissä (luku
*Etärepositoriot ja yhteistyö*).

## Yhdistää vai rebase

| | Yhdistäminen | Rebase |
|---|--------------|--------|
| Historia | Totuudenmukainen, haarautuva | Suora, luettava |
| Commitit | Ennallaan | Uusia olioita |
| Konfliktit | Kerran, yhdistämiscommitissa | Commit kerrallaan |
| Jaettu haara | Turvallinen | Vain sopimuksesta |

Yleinen yhdistelmä on rebase oman haaran päivittämiseen ja siistimiseen
ja yhdistäminen (tai squash) päähaaraan.

## Käytännössä

- **`git pull --rebase`** toistaa omat commitit etäpään muutosten päälle
  sen sijaan, että tekisi yhdistämiscommitin. Asetus
  `pull.rebase true` tekee siitä oletuksen.
- **`--fixup` ja `--autosquash`** ovat helpoin tapa pitää ominaisuushaara
  siistinä katselmoinnin aikana: korjaukset ovat ensin näkyvissä
  katselmoijalle omina committeinaan ja yhdistetään lopuksi.
  `rebase.autoSquash true` tekee `--autosquash`ista oletuksen.
- **Testaa jokainen commit.** Rebase voi rikkoa välicommitin, vaikka
  lopputulos toimii. `git rebase --exec "make testaa" main` ajaa testit
  jokaisen toistetun commitin jälkeen.
- **`--update-refs`** siirtää rebasen aikana myös haaraan osuvat muut
  haarat, mikä helpottaa pinottuja (toisistaan riippuvia) haaroja.

## Itsearviointi

- Osaat selittää, mitä rebase tekee olioille ja miksi commit-tunnisteet
  muuttuvat.
- Osaat siistiä paikallisen historian interaktiivisella rebasella ja
  `--fixup`/`--autosquash`-parilla.
- Osaat selittää rebasen kultaisen säännön ja milloin pakotettu push on
  hyväksyttävä.
- Osaat valita yhdistämisen ja rebasen välillä tilanteen mukaan.
