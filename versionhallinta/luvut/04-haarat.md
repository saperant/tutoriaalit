# Haarat ja yhdistäminen

Haara on erillinen kehityslinja: kokeilu, ominaisuus tai korjaus, joka
etenee muista riippumatta ja yhdistetään takaisin, kun se on valmis.
Koska haara on pelkkä siirtyvä viite (luku *Gitin tietomalli*), haaran
luominen ja vaihtaminen ovat halpoja.

## Haaran luominen ja vaihtaminen

`git switch -c nimi` luo haaran nykyisestä commitista ja siirtyy siihen.
(Vanhempi `git checkout -b` tekee saman, mutta `checkout` tekee myös
paljon muuta, joten uudemmat `switch` ja `restore` ovat selkeämpiä.)
Uudet commitit siirtävät vain nykyistä haaraa:

```{.bash tiedosto="esimerkit/04-haarat.sh" osa="haara"}
```

Kun `main` ei ole liikkunut haaran luomisen jälkeen, yhdistäminen on
*pikakelaus* (fast-forward): `main` vain siirretään osoittamaan samaan
committiin kuin `sanat`. Uutta committia ei synny. `--ff-only` kieltäytyy,
jos pikakelaus ei ole mahdollinen, joten se ei koskaan luo yllättävää
yhdistämiscommittia:

```{.bash tiedosto="esimerkit/04-haarat.sh" osa="pikakelaus"}
```

```{.tuloste tiedosto="esimerkit/04-haarat.odotettu"}
```

```{.dot tiedosto="kaaviot/04-pikakelaus.dot" otsikko="Pikakelaus: uutta committia ei synny, vaan viite main siirtyy samaan committiin kuin sanat"}
```

`git branch -d` poistaa vain yhdistetyn haaran. `-D` poistaa
yhdistämättömänkin, jolloin sen commitit jäävät vain reflogiin.

## Kolmen osapuolen yhdistäminen

Kun molemmat haarat ovat edenneet, pikakelaus ei onnistu. Git etsii
haarojen *yhteisen kannan* (merge base), eli uusimman commitin, josta
molemmat polveutuvat:

```{.bash tiedosto="esimerkit/04-yhdistaminen.sh" osa="erkaantuminen"}
```

Yhdistäminen on *kolmen osapuolen* vertailu: kanta, oma haara ja toinen
haara. Jokaisen kohdan osalta:

| Kanta → oma | Kanta → toinen | Tulos |
|-------------|----------------|-------|
| ei muutosta | ei muutosta | kanta |
| muuttui | ei muutosta | oma |
| ei muutosta | muuttui | toinen |
| muuttui | muuttui samaksi | sama |
| muuttui | muuttui eri tavoin | konflikti |

Kanta tekee yhdistämisestä luotettavaa. Pelkkiä kahta versiota
vertaamalla ei voisi tietää, lisäsikö toinen haara rivin vai poistiko
toinen sen. Tulos tallennetaan *yhdistämiscommitiksi*, jolla on kaksi
vanhempaa:

```{.bash tiedosto="esimerkit/04-yhdistaminen.sh" osa="yhdistaminen"}
```

```{.tuloste tiedosto="esimerkit/04-yhdistaminen.odotettu"}
```

Molemmat muutokset ovat tuloksessa, vaikka ne olivat samassa
tiedostossa, koska ne koskivat eri kohtia. `--graph` piirtää historian
haarautumisen. Yhdistämiscommitin ensimmäinen vanhempi on haara, johon
yhdistettiin (`HEAD^1`), ja toinen on yhdistetty haara (`HEAD^2`).

```{.dot tiedosto="kaaviot/04-yhdistaminen.dot" otsikko="Kolmen osapuolen yhdistäminen: haarat ovat erkaantuneet yhteisestä kannasta, ja yhdistämiscommitilla on kaksi vanhempaa"}
```

## Haarojen vertailu: revisiovälit

Ennen yhdistämistä halutaan usein tietää, mitä haarassa on. Revisioväli
`A..B` tarkoittaa committeja, jotka ovat saavutettavissa B:stä mutta
eivät A:sta. Kolmen pisteen väli `A...B` tarkoittaa committeja, jotka
ovat vain jommassakummassa. Esimerkissä haarassa `sanat` on kaksi omaa
committia ja `main` on edennyt yhdellä:

```{.bash tiedosto="esimerkit/04-valit.sh" osa="valit"}
```

```{.tuloste tiedosto="esimerkit/04-valit.odotettu"}
```

Komennossa `git diff` pisteet tarkoittavat eri asiaa kuin lokissa:
`git diff main...sanat` näyttää haaran muutokset yhteisestä kannasta
lähtien, eli saman, minkä pull request näyttää. `git diff main sanat`
(tai `main..sanat`) vertaa haarojen kärkiä, jolloin mukana ovat
käänteisinä myös `main`in omat muutokset.

## Yhdistää vai ei yhdistämiscommittia

Pikakelaus jättää historian suoraksi, mutta haaran olemassaolo katoaa.
`git merge --no-ff` luo yhdistämiscommitin aina, jolloin näkyy, mitkä
commitit kuuluivat samaan kokonaisuuteen. Kolmas vaihtoehto on
`git merge --squash`, joka tekee haaran kaikista muutoksista yhden
tavallisen commitin. Historia pysyy siistinä, mutta haaran yksittäiset
commitit katoavat. Pull request -palvelujen "Squash and merge" toimii
näin.

Valinta on tiimin sopimus, ei oikein tai väärin. Tärkeintä on, että
päähaaran historia on luettavaa: `git log --first-parent main` näyttää
päähaaran omat askeleet ilman haarojen sisäisiä committeja (luku
*Työnkulut ja repositorion rakenne*).

## Käytännössä

- **Lyhytikäiset haarat.** Mitä kauemmin haara elää, sitä enemmän
  päähaara ehtii muuttua ja sitä vaikeampi yhdistäminen on. Päivät ovat
  hyvä mitta, viikot huono.
- **Päivitä haara päähaaran muutoksilla usein**, joko yhdistämällä
  `main` haaraan tai rebasella (seuraavat luvut). Pienet ristiriidat on
  helppo ratkaista heti.
- **Kuvaavat haaranimet.** `korjaus/kirjautuminen-aikakatkaisu` tai
  `ominaisuus/haku-suodattimet` kertoo enemmän kuin `testi2`. Kauttaviiva
  ryhmittelee haarat työkaluissa.
- **Kiireellinen korjaus kesken työn.** Keskeneräisen työn voi viedä
  talteen (`git stash`, luku *Muutokset ja commitit*) tai avata toisen
  haaran omaan hakemistoonsa (`git worktree`, luku *Työnkulut ja
  repositorion rakenne*).
- **`git branch --merged main`** listaa haarat, jotka voi poistaa, ja
  `--no-merged` haarat, joissa on vielä yhdistämätöntä työtä.

## Itsearviointi

- Osaat luoda haaran, siirtyä haarojen välillä ja poistaa yhdistetyn
  haaran.
- Osaat selittää pikakelauksen ja yhdistämiscommitin eron ja sen, miksi
  `--ff-only` on turvallinen oletus.
- Osaat selittää kolmen osapuolen yhdistämisen ja yhteisen kannan
  merkityksen.
- Osaat näyttää revisiovälillä, mitkä commitit ja muutokset haarassa
  on päähaaraan verrattuna (`main..haara`, `git diff main...haara`).
- Osaat valita perustellusti yhdistämisen, `--no-ff`:n ja `--squash`in
  välillä.
