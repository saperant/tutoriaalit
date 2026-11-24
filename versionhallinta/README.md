# Versionhallinta (Git)

Tiivis suomenkielinen opas Gitiin: tietomalli, muutokset ja commitit,
haarat, konfliktit, rebase, yhteistyö etärepositorioiden kautta,
historian tutkiminen ja korjaaminen, julkaisut, koukut ja työnkulut.
Valmiit dokumentit:
[versionhallinta.pdf](https://saperant.github.io/tutoriaalit/materiaalit/versionhallinta.pdf)
ja pikaopas
[versionhallinta-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/versionhallinta-pikaopas.pdf).

## Sisältö

1. Johdanto – hajautettu versionhallinta, asetukset, ensimmäinen
   repositorio
2. Gitin tietomalli – blobit, puut, commitit, viitteet ja `HEAD`
3. Muutokset ja commitit – valmistelualue, diffit, historia, hyvä commit
4. Haarat ja yhdistäminen – pikakelaus, kolmen osapuolen yhdistäminen
5. Konfliktit – merkinnät, ratkaisu, `zdiff3`, `--ours`/`--theirs`
6. Rebase ja historian siistiminen – `fixup`, `--autosquash`,
   kultainen sääntö
7. Etärepositoriot ja yhteistyö – fetch, pull, hylätty push,
   `--force-with-lease`, pull requestit
8. Historian tutkiminen ja korjaaminen – blame, bisect, reflog, revert,
   reset, cherry-pick
9. Tagit, julkaisut ja alimodulit
10. Koukut, `.gitignore` ja `.gitattributes`
11. Työnkulut ja repositorion rakenne – runkopohjainen kehitys,
    monorepo, sparse-checkout, worktree
12. Lopuksi – nyrkkisäännöt ja lähteet

## Esimerkit

Esimerkit (`esimerkit/*.sh`) luovat tilapäiseen hakemistoon repositorion
ja tulostavat tuloksen. Tekijä ja kello ovat kiinteitä, joten
commit-tunnisteet ovat joka ajolla samat. Aja esimerkit tyhjässä
hakemistossa:

```text
cd "$(mktemp -d)" && bash /polku/esimerkit/04-yhdistaminen.sh
```

## Rakentaminen

```text
make testaa   # rakenteen tarkistus, ShellCheck ja esimerkkien ajo
make pdf      # versionhallinta.pdf ja versionhallinta-pikaopas.pdf
```

Kehityskontti: `.devcontainer/versionhallinta` (Git ja ShellCheck).

Lisenssi: CC BY-SA 4.0.
