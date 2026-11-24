# Gitin tietomalli

Gitin komentoja on paljon, ja niiden valitsimet ovat epäjohdonmukaisia.
Tietomalli sen sijaan on pieni ja johdonmukainen. Kun se on hallussa,
oudoltakin näyttävä komento selittyy sillä, mitä se tekee olioille ja
viitteille. Tämä luku on tutoriaalin tärkein.

## Neljä oliotyyppiä

Git on pohjimmiltaan *sisällön mukaan osoitettu* oliovarasto
(content-addressable store). Jokainen olio tallennetaan hakemistoon
`.git/objects`, ja sen nimi on sisällön SHA-1-tiiviste:

| Olio | Sisältö |
|------|---------|
| blob | Tiedoston sisältö (ei nimeä, ei oikeuksia) |
| tree | Hakemisto: nimet, tilat ja niiden blobit ja alipuut |
| commit | Juuripuu, vanhemmat, tekijä, aika ja viesti |
| tag | Annotoitu tagi: osoitin olioon, tekijä ja viesti |

Komento `git cat-file -p` näyttää olion sisällön. Commit osoittaa
juuripuuhun ja kertoo tekijän ja ajan (Unix-aikaleimana ja
aikavyöhykkeenä):

```{.bash tiedosto="esimerkit/02-oliot.sh" osa="commit"}
```

Puu listaa hakemiston sisällön: tila (`100644` tavallinen tiedosto,
`100755` suoritettava, `040000` hakemisto, `120000` symbolinen linkki),
tyyppi, tunniste ja nimi. Puun alipuut muodostavat hakemistorakenteen:

```{.bash tiedosto="esimerkit/02-oliot.sh" osa="puu"}
```

Tunniste lasketaan sisällöstä, joten sen voi laskea itse komennolla
`git hash-object`, ja sama sisältö saa aina saman tunnisteen:

```{.bash tiedosto="esimerkit/02-oliot.sh" osa="tunniste"}
```

Tästä seuraa kaksi Gitin tärkeintä ominaisuutta. Ensinnäkin eheys: koska
commit osoittaa puuhun tunnisteella ja puu blobeihin tunnisteilla, commitin
tunniste takaa koko tilannekuvan ja koko historian sisällön. Yhtäkään
tavua ei voi muuttaa muuttamatta tunnistetta. Toiseksi tallennus on
tehokasta: muuttumaton tiedosto ei vie uutta tilaa.

## Commit on tilannekuva, ei muutos

Commit ei tallenna muutosta edelliseen vaan koko projektin tilan.
Muutokset (diffit) lasketaan vertaamalla kahta tilannekuvaa. Muuttumattomat
tiedostot ja hakemistot jaetaan commitien välillä, joten tilannekuvat ovat
halpoja. Nimen muuttaminen ei luo uutta blobia, ja sisällön muuttaminen
luo uuden blobin vain muuttuneelle tiedostolle:

```{.bash tiedosto="esimerkit/02-tilannekuvat.sh" osa="nimeaminen"}
```

```{.tuloste tiedosto="esimerkit/02-tilannekuvat.odotettu"}
```

`LICENSE` on sama blob kaikissa kolmessa commitissa. Git ei tallenna
nimenmuutoksia erikseen. Se *päättelee* ne vertaamalla tilannekuvia:
jos poistettu ja lisätty tiedosto ovat riittävän samankaltaisia,
`git log --follow` ja `git diff -M` näyttävät ne nimenmuutoksena.
(Levyllä Git pakkaa olioita deltoiksi pakkatiedostoihin, mutta se on
tallennuksen optimointi eikä näy mallissa.)

## Viitteet ja HEAD

Tunnisteita on hankala muistaa, joten Gitissä on *viitteitä*: nimiä,
jotka osoittavat committiin. Haara on tiedosto `.git/refs/heads/<nimi>`,
jossa on yhden commitin tunniste. `HEAD` kertoo, mikä haara on
nykyinen:

```{.bash tiedosto="esimerkit/02-oliot.sh" osa="viitteet"}
```

Koko esimerkin tuloste:

```{.tuloste tiedosto="esimerkit/02-oliot.odotettu"}
```

Kun teet commitin, Git luo uuden commit-olion, jonka vanhempi on
nykyinen commit, ja siirtää nykyisen haaran osoittamaan siihen. Haara on
siis pelkkä siirtyvä osoitin. Tästä seuraa, että haaran luominen on
halpaa (yksi tiedosto) ja että commitit eivät "kuulu" haaroille.
Commitit muodostavat suunnatun syklittömän verkon (DAG), jossa jokainen
commit osoittaa vanhempiinsa, ja haarat ovat nimilappuja verkon
solmuissa. Jos `HEAD` osoittaa suoraan committiin eikä haaraan, ollaan
*irrallisessa HEAD-tilassa* (detached HEAD). Silloin tehdyt commitit
eivät ole minkään haaran varassa, mutta ne löytyvät reflogista
(luku *Historian tutkiminen ja korjaaminen*).

Revisiot voi nimetä monella tavalla: `HEAD~2` (kaksi sukupolvea taakse
ensimmäisiä vanhempia pitkin), `HEAD^2` (yhdistämiscommitin toinen
vanhempi), `main@{yesterday}`, `:/viestin teksti` (uusin commit, jonka
viestissä on teksti) ja `HEAD:polku` (tiedosto commitissa). `git help
revisions` luettelee kaikki.

## Kolme aluetta

Työskentelyssä tiedostolla on kolme olinpaikkaa:

| Alue | Mikä se on |
|------|------------|
| Työhakemisto | Tavalliset tiedostot, joita muokkaat |
| Valmistelualue (index) | Seuraavan commitin tilannekuva, tiedostossa `.git/index` |
| Repositorio | Commitit ja muut oliot hakemistossa `.git/objects` |

`git add` kopioi tiedoston työhakemistosta valmistelualueelle (ja tekee
siitä blobin), ja `git commit` tekee valmistelualueesta puun ja commitin.
Valmistelualue on seuraava luku.

## Käytännössä

- **Ajattele olioina ja viitteinä.** Kun komento hämmentää, kysy: mitä
  olioita se luo ja mitä viitteitä se siirtää? Esimerkiksi `git reset`
  siirtää haaraviitettä, `git commit` luo olion ja siirtää viitettä, ja
  `git checkout` tai `git switch` siirtää `HEAD`ia ja päivittää
  työhakemiston.
- **Commit-tunniste on eheyden tae.** Kun kerrot kollegalle commitin
  tunnisteen, tiedätte molemmat tarkalleen saman tilan. Julkaisut ja
  käyttöönotot kannattaa sitoa tunnisteeseen, ei pelkkään haaranimeen,
  joka voi siirtyä.
- **Haarat ovat halpoja.** Haaran luominen ei kopioi tiedostoja, joten
  jokaiselle kokeilulle kannattaa tehdä oma haara.
- **SHA-1 ja SHA-256.** Git käyttää oletuksena SHA-1:tä, johon tunnetaan
  törmäyshyökkäyksiä. Git käyttää törmäyksen tunnistavaa SHA-1-versiota,
  ja SHA-256-repositoriot ovat mahdollisia (`git init
  --object-format=sha256`), mutta palvelut tukevat niitä vielä
  rajallisesti.

## Itsearviointi

- Osaat nimetä Gitin neljä oliotyyppiä ja näyttää niiden sisällön
  komennolla `git cat-file -p`.
- Osaat selittää, miksi commit-tunniste takaa koko historian eheyden ja
  miksi muuttumaton tiedosto ei vie uutta tilaa.
- Osaat kertoa, mitä haara ja `HEAD` ovat levyllä ja mitä tapahtuu, kun
  teet commitin.
- Osaat nimetä revision tavoilla `HEAD~2`, `HEAD^2` ja `HEAD:polku`.
