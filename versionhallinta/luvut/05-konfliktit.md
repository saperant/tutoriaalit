# Konfliktit

Konflikti syntyy, kun molemmat haarat muuttavat samaa kohtaa eri
tavoin. Git ei arvaa, kumpi on oikein, vaan pysähtyy ja jättää päätöksen
ihmiselle. Konflikti ei ole virhe eikä Gitin vika. Se on tilanne, jossa
kaksi ihmistä teki ristiriitaisen päätöksen, ja ratkaisu vaatii
ymmärrystä molemmista muutoksista.

## Konfliktin anatomia

Kehityshaarassa portti muutettiin arvoon 8000 ja tuotantohaarassa
arvoon 80. Yhdistäminen pysähtyy:

```{.bash tiedosto="esimerkit/05-konflikti.sh" osa="konflikti"}
```

Tiedostoon tulee *konfliktimerkinnät*: `<<<<<<<` ja `=======` välissä on
oma versio (`HEAD`), ja `=======` ja `>>>>>>>` välissä yhdistettävän
haaran versio. Muut kohdat Git yhdisti itse. `git status` näyttää
ratkaisemattomat tiedostot tilalla `UU`. Yhdistäminen on kesken: seuraava
commit on yhdistämiscommit, ja sen tilaa voi tarkistaa komennolla
`git status`.

## Ratkaiseminen

Ratkaisu on muokata tiedosto halutuksi, poistaa merkinnät ja merkitä
tiedosto ratkaistuksi komennolla `git add`. Ratkaisu voi olla toinen
puoli, molemmat tai jotain kolmatta, kuten tässä:

```{.bash tiedosto="esimerkit/05-konflikti.sh" osa="ratkaisu"}
```

```{.tuloste tiedosto="esimerkit/05-konflikti.odotettu"}
```

`git commit --no-edit` käyttää Gitin valmiiksi kirjoittamaa
yhdistämisviestiä. Jos ratkaisu vaati harkintaa, viestiin kannattaa
kirjoittaa, mitä päätettiin ja miksi.

## Kanta näkyviin: zdiff3

Oletusmerkinnöistä puuttuu tärkein tieto: millainen kohta oli ennen
kumpaakaan muutosta. Asetus `merge.conflictStyle zdiff3` lisää kannan
`|||||||`-merkinnän alle. Silloin näkee, mitä kumpikin haara *muutti*,
eikä vain lopputuloksia:

```{.bash tiedosto="esimerkit/05-diff3.sh" osa="zdiff3"}
```

Kannasta näkyy, että kehityshaara lyhensi aikakatkaisua ja
tuotantohaara pidensi sitä. Kyse on siis aidosta erimielisyydestä, ei
kahdesta toisistaan riippumattomasta korjauksesta. Asetus kannattaa
ottaa käyttöön globaalisti.

Koko tiedoston voi valita toiselta puolelta komennolla
`git restore --ours` tai `--theirs`. Se sopii esimerkiksi
lukitustiedostoille, jotka generoidaan uudelleen. Jos yhdistämisestä
halutaan luopua, `git merge --abort` palauttaa tilan ennalleen:

```{.bash tiedosto="esimerkit/05-diff3.sh" osa="valinta"}
```

```{.tuloste tiedosto="esimerkit/05-diff3.odotettu"}
```

Rebasen ja cherry-pickin aikana *ours* ja *theirs* ovat käänteisiä:
rebase toistaa omat commitit toisen haaran päälle, joten "ours" on
kohdehaara ja "theirs" oma commit. Siksi merkinnät kannattaa lukea
sisällöstä eikä nimistä.

## Työkalut

- `git mergetool` avaa konfliktit graafisessa kolmen ruudun työkalussa
  (esim. `meld`, VS Coden oma). Editorit tunnistavat merkinnät itsekin.
- `git log --merge -p` näyttää konfliktin aiheuttaneet commitit
  molemmista haaroista.
- `git rerere` (*reuse recorded resolution*) muistaa ratkaisun ja käyttää
  sitä uudelleen, kun sama konflikti tulee vastaan esimerkiksi toistuvissa
  rebaseissa. Otetaan käyttöön asetuksella `rerere.enabled true`.

## Käytännössä

- **Konfliktin ratkaisu on koodimuutos.** Aja testit ennen yhdistämis-
  commitin tallentamista. Kaksi oikein toimivaa muutosta voi yhdessä
  olla väärin, vaikka tekstikonfliktia ei syntyisi lainkaan (semanttinen
  konflikti). Siksi päähaaran testit ajetaan CI:ssä yhdistämisen jälkeen.
- **Kysy muutoksen tekijältä.** Jos et ymmärrä toisen puolen muutosta,
  `git log --merge` kertoo kuka sen teki ja viesti toivottavasti miksi.
- **Ehkäise rakenteella.** Pienet ja lyhytikäiset haarat, toistuvat
  päivitykset päähaarasta ja pienet tiedostot vähentävät konflikteja.
  Generoituja tiedostoja ei yhdistetä vaan generoidaan uudelleen.
- **Muotoilu sovitaan työkaluilla.** Automaattinen muotoilija (esim.
  `ruff format`, `prettier`, `clang-format`) estää konfliktit, jotka
  syntyisivät pelkistä välilyöntieroista.

## Itsearviointi

- Osaat lukea konfliktimerkinnät ja selittää, mistä kukin osa tulee.
- Osaat ratkaista konfliktin, merkitä sen ratkaistuksi ja viimeistellä
  yhdistämisen tai perua sen komennolla `git merge --abort`.
- Osaat ottaa käyttöön `zdiff3`-tyylin ja kertoa, miksi kanta auttaa
  ratkaisemaan konfliktin.
- Osaat kertoa, miksi ilman tekstikonfliktia yhdistettykin koodi pitää
  testata.
