# Etärepositoriot ja yhteistyö

Etärepositorio on toinen kopio samasta historiasta, yleensä palvelimella.
Git ei tee kopioiden välillä mitään automaattisesti: `fetch` hakee,
`push` lähettää ja kaikki muu tapahtuu paikallisesti. Tämän luvun
esimerkeissä "palvelin" on paikallinen *paljas* repositorio (bare), jossa
ei ole työhakemistoa. Palvelimen repositorio on täsmälleen tällainen.

## Kloonaus ja push

`git clone` kopioi koko historian ja nimeää lähteen etärepositorioksi
`origin`. Aino tekee ensimmäisen commitin ja lähettää sen:

```{.bash tiedosto="esimerkit/07-eta.sh" osa="palvelin"}
```

`remotes/origin/main` on *etäseurantahaara*: paikallinen viite, joka
kertoo, missä palvelimen `main` oli viimeksi, kun siitä kuultiin. Sitä ei
voi siirtää itse. Se päivittyy vain `fetch`in ja `push`in yhteydessä.

## Fetch ja pull

Olli kloonaa ja pushaa oman muutoksensa. Esimerkeissä toinen henkilö
on funktio, joka asettaa tekijätiedot:

```{.bash tiedosto="esimerkit/07-eta.sh" osa="olli"}
```

```{.bash tiedosto="esimerkit/07-eta.sh" osa="olli-tyo"}
```

Ainon repositorio ei tiedä tästä mitään ennen kuin se hakee muutokset.
`git fetch` päivittää etäseurantahaarat mutta ei koske omiin haaroihin.
Sen jälkeen omaan haaraan voi yhdistää, jolloin `git pull` on
`fetch` + yhdistäminen samalla komennolla:

```{.bash tiedosto="esimerkit/07-eta.sh" osa="fetch"}
```

```{.tuloste tiedosto="esimerkit/07-eta.odotettu"}
```

`git status -sb` näyttää suhteen etähaaraan: `[behind 1]` tarkoittaa,
että palvelimella on yksi commit, jota ei ole paikallisesti, ja
`[ahead 2]`, että paikallisesti on kaksi lähettämätöntä.

## Kun molemmat ovat edenneet

Jos Olli pushaa ensin, Ainon push hylätään. Palvelin hyväksyy vain
pikakelauksen, jottei kenenkään työ katoa. Aino hakee muutokset ja
toistaa omat committinsa niiden päälle (`pull --rebase`, luku *Rebase ja
historian siistiminen*). Sen jälkeen push onnistuu ja historia pysyy
suorana:

```{.bash tiedosto="esimerkit/07-ristiriita.sh" osa="hylatty"}
```

```{.bash tiedosto="esimerkit/07-ristiriita.sh" osa="pull-rebase"}
```

Pelkkä `git pull` ilman asetuksia tekee tilanteessa yhdistämiscommitin
"Merge branch 'main' of …". Sellaiset commitit eivät kerro mitään ja
sotkevat historian, joten `pull.ff only` (pysähtyy ja pyytää
päättämään) tai `pull.rebase true` ovat parempia oletuksia.

## Pakotettu push

Uudelleenkirjoitettu haara (amend, rebase) ei ole pikakelaus vanhasta,
joten se on pushattava väkisin. `git push --force` korvaa palvelimen
haaran ehdoitta ja hävittää kaiken, mitä muut ovat sinne ehtineet
lähettää. `--force-with-lease` korvaa vain, jos palvelimen haara on
yhä siinä, missä se oli viimeksi haettaessa:

```{.bash tiedosto="esimerkit/07-ristiriita.sh" osa="lease"}
```

```{.tuloste tiedosto="esimerkit/07-ristiriita.odotettu"}
```

Komento kieltäytyi, koska Olli oli pushannut haaraan. Ainon on haettava
ja yhdistettävä Ollin työ ennen pakotusta. Jaettua päähaaraa ei pakoteta
koskaan, ja palveluissa se estetään haarasuojauksella (ks. taito
*Tietoturva kehitystyössä*).

## Pull request -työnkulku

Pull request (GitLabissa merge request) ei ole Gitin ominaisuus vaan
palvelun. Se on pyyntö yhdistää haara toiseen, ja se toimii keskustelun
ja katselmoinnin paikkana:

1. Tee haara päähaarasta, tee muutokset ja pushaa haara
   (`git push -u origin haara`; `-u` asettaa seurannan).
2. Avaa pull request. CI ajaa testit, ja katselmoija kommentoi.
3. Korjaa kommenttien mukaan uusilla commiteilla (tai `--fixup`ina) ja
   pushaa samaan haaraan. Pull request päivittyy.
4. Kun katselmointi ja testit ovat kunnossa, haara yhdistetään
   (merge, squash tai rebase, tiimin sopimuksen mukaan) ja poistetaan.

Avoimessa lähdekoodissa ei yleensä ole kirjoitusoikeutta alkuperäiseen
repositorioon. Silloin työ tehdään omaan *forkkiin*, eli palvelimella
tehtyyn kopioon, ja pull request avataan sieltä. Paikallisesti
alkuperäinen lisätään toiseksi etärepositorioksi (`git remote add
upstream …`), josta haetaan päivitykset.

## Käytännössä

- **`fetch` usein, `pull` harkiten.** `git fetch` on aina turvallinen.
  Sen jälkeen `git log main..origin/main` näyttää, mitä on tulossa,
  ennen kuin mitään yhdistetään.
- **Pushaa keskeneräistäkin työtä omaan haaraan.** Palvelin on
  varmuuskopio, ja luonnos-pull requestissa (draft) työtä voi näyttää
  aikaisin.
- **Aina `--force-with-lease`, ei koskaan pelkkä `--force`.** Moni
  asettaa aliaksen `git config --global alias.pushf
  "push --force-with-lease"`.
- **Pidä pull requestit pieninä.** Alle muutaman sadan rivin muutos
  katselmoidaan huolellisesti, ja tuhansien rivien muutos hyväksytään
  usein lukematta.

## Itsearviointi

- Osaat selittää etäseurantahaaran ja oman haaran eron sekä `fetch`in ja
  `pull`in eron.
- Osaat toimia, kun push hylätään, koska etäpää on edennyt.
- Osaat selittää, miksi `--force-with-lease` on turvallisempi kuin
  `--force`.
- Osaat kuvata pull request -työnkulun ja forkin käytön avoimen
  lähdekoodin projektissa.
