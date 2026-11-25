# Historian tutkiminen ja korjaaminen

Hyvin kirjoitettu historia on dokumentaatiota, jota luetaan, kun pitää
tietää, miksi koodi on sellainen kuin on, ja milloin jokin hajosi. Git
myös antaa anteeksi: lähes mitään commitoitua ei menetetä, jos tietää,
mistä etsiä.

## Kuka muutti ja miksi: blame

`git blame` näyttää jokaisen rivin viimeisimmän muutoksen commitin,
tekijän ja päivän:

```{.bash tiedosto="esimerkit/08-blame.sh" osa="blame"}
```

Blamen tarkoitus ei ole syyllisen etsintä vaan *syyn* etsintä. Commitin
tunnisteella päästään viestiin, joka kertoo, miksi rivi muuttui:

```{.bash tiedosto="esimerkit/08-blame.sh" osa="miksi"}
```

```{.tuloste tiedosto="esimerkit/08-blame.odotettu"}
```

`git log -L 10,20:tiedosto` näyttää rivialueen koko historian, ja
`git log -L :funktio:tiedosto` yhden funktion historian. Siirretyt ja
kopioidut rivit löytyvät valitsimilla `blame -M -C`.

## Missä virhe syntyi: bisect

Kun virhe tiedetään puuttuvan vanhasta versiosta ja löytyvän uudesta,
`git bisect` etsii virheen tuoneen commitin puolittamalla. N commitin
välillä tarvitaan noin log₂ N testiä, eli tuhannenkin commitin välistä
virhe löytyy kymmenellä testillä. Testi voi olla komento, jonka
paluuarvo kertoo tuloksen: 0 on hyvä, 1–127 huono ja 125 ohita (esim.
versio ei käänny):

```{.bash tiedosto="esimerkit/08-bisect.sh" osa="testi"}
```

```{.bash tiedosto="esimerkit/08-bisect.sh" osa="bisect"}
```

```{.tuloste tiedosto="esimerkit/08-bisect.odotettu"}
```

Yhdeksän commitin välistä virhe löytyi kolmella testiajolla (`good`- ja
`bad`-rivit lähtöpisteiden jälkeen). Bisect toimii
parhaiten, kun jokainen commit kääntyy ja testit menevät läpi (luku
*Muutokset ja commitit*). Käsin tehtävässä bisectissä komennot `git
bisect good` ja `git bisect bad` kertovat kunkin version tuloksen.

## Kadonneen palauttaminen: reflog

*Reflog* on paikallinen päiväkirja jokaisesta `HEAD`in ja haarojen
siirrosta. Kun commit "katoaa" (`reset --hard`, poistettu haara,
epäonnistunut rebase), se on yhä oliona olemassa, ja reflog kertoo sen
tunnisteen:

```{.bash tiedosto="esimerkit/08-reflog.sh" osa="vahinko"}
```

```{.bash tiedosto="esimerkit/08-reflog.sh" osa="reflog"}
```

```{.tuloste tiedosto="esimerkit/08-reflog.odotettu"}
```

Reflogin merkinnät vanhenevat. Merkintä, jonka commit on yhä
saavutettavissa haaran kärjestä, säilyy oletuksena 90 päivää
(`gc.reflogExpire`). Merkintä, jonka commit ei enää ole saavutettavissa,
säilyy 30 päivää (`gc.reflogExpireUnreachable`). Tämän luvun tapaukset,
kuten `reset --hard` ja epäonnistunut rebase, kuuluvat jälkimmäisiin,
joten pelastusaikaa on noin kuukausi. Sen jälkeen `git gc` voi siivota
oliot. Reflog on paikallinen: se ei
siirry kloonissa eikä pushissa. Valmistelemattomia muutoksia se ei pelasta,
koska ne eivät ole koskaan olleet olioita.

## Peruminen: revert, reset ja cherry-pick

Virheellisen muutoksen voi poistaa kahdella tavalla, ja valinta riippuu
siitä, onko historia jaettu:

| Komento | Mitä tekee | Milloin |
|---------|------------|---------|
| `git revert C` | Uusi commit, joka kumoaa C:n muutokset | Jaettu historia |
| `git reset --soft C` | Haara C:hen, muutokset valmisteltuina | Oma historia |
| `git reset --mixed C` | Haara C:hen, muutokset työhakemistossa | Oma historia |
| `git reset --hard C` | Haara C:hen, muutokset hylätään | Oma historia, varoen |

`revert` ei muuta olemassa olevaa historiaa, joten se on turvallinen
jaetussa haarassa:

```{.bash tiedosto="esimerkit/08-peruminen.sh" osa="revert"}
```

`reset` siirtää haaraa taaksepäin. Sen kolme tilaa eroavat siinä, mitä
valmistelualueelle ja työhakemistolle tehdään:

```{.bash tiedosto="esimerkit/08-peruminen.sh" osa="reset"}
```

`git cherry-pick` kopioi yksittäisen commitin muutokset toiseen haaraan.
Tyypillinen käyttö on korjauksen vienti julkaisuhaaraan: korjaus tehdään
päähaaraan ja poimitaan sieltä. `-x` lisää viestiin alkuperäisen commitin
tunnisteen, jotta yhteys säilyy:

```{.bash tiedosto="esimerkit/08-peruminen.sh" osa="cherry-pick"}
```

```{.tuloste tiedosto="esimerkit/08-peruminen.odotettu"}
```

Yhdistämiscommitin peruminen vaatii valitsimen `-m 1` (minkä vanhemman
suhteen perutaan). Peruttua yhdistämistä ei voi yhdistää uudelleen
sellaisenaan, koska Git pitää haaran commitit jo yhdistettyinä. Ensin
perutaan peruminen.

## Käytännössä

- **Jaettu historia: revert. Oma historia: reset tai rebase.** Sama
  kultainen sääntö kuin rebasessa.
- **Ennen riskialtista operaatiota varmuusviite.** `git branch varmuus`
  maksaa yhden tiedoston ja säästää reflogin selaamisen.
- **Automatisoi bisect.** Testi, joka toistaa vian, kannattaa kirjoittaa
  joka tapauksessa. Sama testi kelpaa `git bisect run`ille ja jää
  regressiotestiksi.
- **`.git-blame-ignore-revs`** listaa muotoilucommitit, jotka blamen
  pitää ohittaa (`blame.ignoreRevsFile`). Palvelut tukevat samaa
  tiedostoa.

## Itsearviointi

- Osaat selvittää, kuka muutti rivin ja miksi (`blame`, `log -L`,
  commit-viesti).
- Osaat etsiä virheen tuoneen commitin komennolla `git bisect run` ja
  kirjoittaa sille testin.
- Osaat palauttaa reflogin avulla commitin, joka katosi `reset --hard`in
  tai haaran poiston jälkeen.
- Osaat valita revertin ja resetin kolmen tilan välillä ja viedä
  korjauksen toiseen haaraan cherry-pickillä.
