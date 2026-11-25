---
title: Versionhallinta (Git)
subtitle: Pikaopas · Git 2.43+
---

# Tietomalli

| Käsite | Mitä se on |
|--------|------------|
| blob, tree, commit, tag | Oliot, nimenä sisällön tiiviste |
| Haara | Siirtyvä viite committiin (`.git/refs/heads/`) |
| `HEAD` | Nykyinen haara tai commit (irrallinen) |
| Valmistelualue | Seuraavan commitin tilannekuva (`.git/index`) |
| `HEAD~2`, `HEAD^2` | 2 sukupolvea taakse; yhdistämisen 2. vanhempi |
| `HEAD:polku`, `:/teksti` | Tiedosto commitissa; uusin commit viestin tekstillä |
| Tutkiminen | `git cat-file -p X`, `git ls-tree X`, `git rev-parse X` |

# Asetukset

| Asetus | Arvo |
|--------|------|
| `user.name`, `user.email` | Tekijätiedot |
| `init.defaultBranch` | `main` |
| `pull.ff` / `pull.rebase` | `only` / `true` |
| `merge.conflictStyle` | `zdiff3` |
| `rerere.enabled`, `rebase.autoSquash` | `true` |
| `core.hooksPath` | `.githooks` (versioidut koukut) |
| Mistä asetus tulee | `git config --list --show-origin` |

# Arkityö

| Tehtävä | Komento |
|---------|---------|
| Tila | `git status -sb` (`??`, `A`, `M`, `MM`, `UU`) |
| Valmistele | `git add tiedosto`, osittain `git add -p` |
| Erot | `git diff` (työ↔valm.), `git diff --staged` (valm.↔HEAD) |
| Peru valmistelu | `git restore --staged t` |
| Hylkää muutos | `git restore t` (peruuttamaton) |
| Talteen | `git stash -u`, `git stash pop`, `git stash list` |
| Älä versioi | `.gitignore`: `build/`, `*.log`, `.env`; `git clean -n` |
| Commit | `git commit -m "Otsikko" -m "Miksi"` |
| Korjaa viimeisin | `git commit --amend` (vain jakamaton) |

# Historia

| Tehtävä | Komento |
|---------|---------|
| Loki | `git log --oneline --graph --all` |
| Muoto | `git log --format='%h %ad %an: %s' --date=short` |
| Rajaus | `-- polku`, `--author=`, `--since=`, `--grep=`, `-S teksti` |
| Päähaaran askeleet | `git log --first-parent main` |
| Commit | `git show --stat X` |
| Rivit | `git blame t`, `git log -L 10,20:t`, `git log -L :f:t` |
| Mitä on tulossa | `git fetch; git log main..origin/main` |
| Haaran omat | `git log main..haara`, `git diff main...haara` |

# Haarat ja yhdistäminen

| Tehtävä | Komento |
|---------|---------|
| Uusi ja siirry | `git switch -c nimi` |
| Siirry | `git switch nimi` |
| Pikakelaus | `git merge --ff-only nimi` |
| Yhdistämiscommit aina | `git merge --no-ff nimi` |
| Yhdeksi commitiksi | `git merge --squash nimi` |
| Kanta | `git merge-base a b` |
| Poista | `git branch -d nimi` (`-D` väkisin) |
| Siivottavat | `git branch --merged main` |

# Konfliktit

| Tehtävä | Komento |
|---------|---------|
| Ratkaistuksi | muokkaa, `git add t`, `git commit` |
| Toinen puoli | `git checkout --ours t` / `--theirs t` |
| Luovu | `git merge --abort`, `git rebase --abort` |
| Aiheuttajat | `git log --merge -p` |

Rebasessa *ours* = kohdehaara, *theirs* = oma commit.

# Rebase

| Tehtävä | Komento |
|---------|---------|
| Uuden kannan päälle | `git rebase main` |
| Siistiminen | `git rebase -i main` (pick, reword, squash, fixup, drop) |
| Korjaus vanhaan | `git commit --fixup=X`, `git rebase -i --autosquash main` |
| Testaa joka commit | `git rebase --exec "make testaa" main` |
| Jatka | `git add t; git rebase --continue` |

Kultainen sääntö: ei jaetun historian uudelleenkirjoitusta.

# Etärepositoriot

| Tehtävä | Komento |
|---------|---------|
| Kloonaa | `git clone url`, `--recurse-submodules` |
| Hae | `git fetch` (aina turvallinen) |
| Hae ja päivitä | `git pull --ff-only` tai `--rebase` |
| Lähetä uusi haara | `git push -u origin haara` |
| Pakota omaan haaraan | `git push --force-with-lease` |
| Toinen etäpää | `git remote add upstream url` |

# Korjaaminen

| Tilanne | Komento |
|---------|---------|
| Jaettu virhe | `git revert X` (yhdistäminen: `-m 1`) |
| Oma historia taakse | `git reset --soft`/`--mixed`/`--hard X` |
| Kadonnut commit | `git reflog`, `git branch pelastus HEAD@{1}` |
| Virheen etsintä | `git bisect start huono hyvä; git bisect run ./testi` |
| Korjaus toiseen haaraan | `git cherry-pick -x X` |

# Julkaisut ja muut

| Tehtävä | Komento |
|---------|---------|
| Tagi | `git tag -a v1.2.0 -m "…"`, `git push --follow-tags` |
| Versio | `git describe --tags --dirty` |
| Järjestys | `git tag -l --sort=v:refname` |
| Alimoduli | `git submodule add url polku`, `update --init --recursive` |
| Ohitus | `git check-ignore -v t`, `git rm --cached t` |
| Attribuutit | `git check-attr -a -- t`, `git ls-files --eol` |
| Osittainen työpuu | `git sparse-checkout set hak1 hak2` |
| Rinnakkainen työpuu | `git worktree add -b haara ../polku main` |
