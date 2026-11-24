# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Ajattele olioina ja viitteinä.** Commit on tilannekuva, haara on
   siirtyvä nimilappu ja `HEAD` kertoo, missä olet.
2. **Pieni looginen commit, viesti kertoo miksi.**
3. **`git diff --staged` ennen jokaista committia.**
4. **Lyhytikäiset haarat ja usein päivitetty päähaara.** Konfliktit
   pysyvät pieninä.
5. **Siisti oma historia ennen jakamista, älä koskaan jaettua.**
   Jaetun virheen peruu `revert`.
6. **`--force-with-lease`, ei `--force`.** `pull.ff only` tai
   `pull.rebase true` oletukseksi.
7. **Mikään commitoitu ei katoa heti.** Reflog muistaa 90 päivää, ja
   varmuusviite (`git branch varmuus`) maksaa yhden tiedoston.
8. **Julkaisu on annotoitu tagi**, josta CI rakentaa artefaktit.
9. **`.gitignore` ja `.gitattributes` alusta asti.** Käännöstuotteet,
   riippuvuudet ja salaisuudet eivät kuulu historiaan.
10. **Pakolliset tarkistukset CI:ssä, koukut nopeaksi palautteeksi.**

## Mihin tästä eteenpäin

- *Käännösjärjestelmät, testaus ja CI* rakentaa tämän päälle: CI-putki
  ajaa testit jokaiselle pushille ja pull requestille.
- *Tietoturva kehitystyössä* käsittelee salaisuusvuodot ja niiden
  siivouksen historiasta, commitien ja julkaisujen allekirjoitukset sekä
  haarasuojaukset.
- *Kontit ja pilvi* esittelee GitOpsin, jossa versionhallinta on myös
  infrastruktuurin totuuden lähde.

## Lähteet ja lisämateriaali

- Scott Chacon ja Ben Straub: *Pro Git*, 2. painos. Apress. Vapaasti
  luettavissa: <https://git-scm.com/book>. Lisenssi CC BY-NC-SA 3.0, joten
  siitä ei ole lainattu tekstiä tähän tutoriaaliin. Luvut *Git Internals*
  ja *Git Branching* syventävät tämän tutoriaalin lukuja 2 ja 4.
- Gitin oma dokumentaatio: <https://git-scm.com/docs> ja komennot
  `git help <komento>`, `git help revisions`, `git help gitglossary`,
  `git help githooks`, `git help gitattributes`, `git help gitignore`.
- *Git User Manual* ja *Git Tutorial*: <https://git-scm.com/docs/user-manual>.
- Paul Hammant ym.: *Trunk Based Development*,
  <https://trunkbaseddevelopment.com>.
- Chris Beams: *How to Write a Git Commit Message*,
  <https://cbea.ms/git-commit/>.
- *Conventional Commits*, <https://www.conventionalcommits.org>.
- Semanttinen versiointi: <https://semver.org/lang/fi/>.
- GitHubin `gitignore`-mallipohjat: <https://github.com/github/gitignore>.

## Lisenssi

Tämä tutoriaali ja sen esimerkit on lisensoitu Creative Commons
Nimeä–JaaSamoin 4.0 Kansainvälinen -lisenssillä (CC BY-SA 4.0).
