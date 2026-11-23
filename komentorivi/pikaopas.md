---
title: Komentorivi ja Linux
subtitle: Pikaopas · GNU-työkalut · Ubuntu 24.04 · Bash 5.2
---

# Ohjeet ja komennot

| Tarkoitus | Komento |
|-----------|---------|
| Ohjesivu, haku | `man grep`, `/sana`, `n`; `man -k avainsana` |
| Kuoren sisäinen | `help cd`, `type -a nimi` |
| Valitsimet tiiviisti | `komento --help` |
| Paluuarvo | `echo $?`; 0 = ok, 1 = ei osumia (`grep`), 2 = virhe |
| Ketjutus | `a && b` jos onnistui, `a; b` aina, `a &` taustalle |
| Valitsimet loppuvat | `rm -- -tiedosto` |

# Tiedostot

| Tehtävä | Komento |
|---------|---------|
| Listaus | `ls -lah`, `ls -lt` (uusin ensin), `stat -c '%a %n' t` |
| Kopio, siirto | `cp -a l k`, `mv v u`, `mkdir -p a/b` |
| Linkit | `ln -s kohde nimi`, `ln -sfn uusi nimi`, `readlink -f` |
| Tila | `df -h`, `du -xh --max-depth=1 /var` |
| Polut | `basename p .c`, `dirname p`, `realpath p` |
| Glob | `*`, `?`, `[a-j]`, `{c,h}` (ennen globia), piilot. eivät osu |
| Atominen korvaus | kirjoita `t.tmp` samaan hakemistoon, `mv t.tmp t` |

- Suurimmat hakemistot: `du -sh * | sort -h`.

# Oikeudet

| r=4 w=2 x=1 | Tiedosto | Hakemisto |
|-------------|----------|-----------|
| `r` | luku | nimien listaus |
| `w` | muutos | nimien lisäys ja poisto |
| `x` | suoritus | läpikulku |

- `chmod 640 t`, `chmod u+x,go-w t`, `chown -R k:r d`.
- Korjaus: `find d -type d -exec chmod 755 {} +` ja `-type f … 644`.
- umask `022` → 644/755, `027` → 640/750, `077` → 600/700.
- `2775` setgid: ryhmä periytyy; `1777` sticky: `/tmp`.
- `echo x | sudo tee -a /etc/t`, ei `sudo echo x > /etc/t`.

# Uudelleenohjaukset

| Merkintä | Merkitys |
|----------|----------|
| `> t`, `>> t` | tuloste tiedostoon, loppuun |
| `2> t`, `> t 2>&1`, `&> t` | virheet; molemmat (järjestys!) |
| `2>&1 > t` | virheet putkeen, tuloste tiedostoon |
| `< t`, `<<< "$x"` | syöte tiedostosta, merkkijonosta |
| `tee t`, `tee -a t` | haara tiedostoon ja eteenpäin |
| `<(k)` | tuloste tiedostonimenä: `diff <(a) <(b)` |

# grep

| Valitsin | Merkitys |
|----------|----------|
| `-i -v -c -n -w -x` | koko, käänteinen, määrä, rivinro, sana, rivi |
| `-o`, `-q`, `-m N` | vain osuma, hiljaa, N osumaa |
| `-A N -B N -C N` | kontekstirivit |
| `-E`, `-F`, `-P` | laajennettu, kiinteä, Perl |
| `-rn --include='*.c' --exclude-dir=.git` | puusta |
| `-l`, `-L`, `-Z` | tiedostot, joissa on, ei ole; nollaerotin |

ERE: `. [abc] [^a] [[:digit:]] ^ $ \b * + ? {n,m} ( )` ja
pystyviiva vaihtoehdoille.

# Tekstityökalut

| Tehtävä | Komento |
|---------|---------|
| Otsikko pois | `tail -n +2` |
| Kentät | `cut -d, -f2,3`, `--output-delimiter=' '` |
| Lajittelu | `sort -t, -k3,3nr -k1`, `-h`, `-V`, `-u` |
| Merkit | `tr -d '\r'`, `tr a-z A-Z`, `tr -s ' '` |
| Rivit yhteen | `paste -sd,` |
| Liitos | `join -t, -1 1 -2 2 -o 1.2,2.3` (lajitellut) |
| Joukot | `comm -13 a b` (vain b:ssä; lajitellut) |
| Näkymättömät | `cat -A`, `od -c` |

- Laskenta: `sort | uniq -c | sort -k1,1nr -k2`.

# sed

- `sed 's/a/b/g'`, `sed -E 's/([0-9]+)-([0-9]+)/\2.\1/'`
- `sed -n '3,5p'`, `sed '/^#/d'`, `sed '2~3d'` (GNU)
- `sed -i.bak 's/^portti = .*/portti = 9090/' t`
- Erotin vapaa: `s|/usr/local|/opt|`

# awk

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="awk"}
```

- `$0 $1 $NF NR NF`; `BEGIN`, `END`; alustamaton muuttuja on 0 tai tyhjä.
- Ubuntun oletus on `mawk`: ei `gensub`, `asort`, `strftime`.

# Reseptit

```{.bash tiedosto="esimerkit/pikaopas.sh" osa="reseptit"}
```

# find ja xargs

| Ehto | Merkitys |
|------|----------|
| `-name '*.log'`, `-path`, `-type f/d/l` | nimi, polku, tyyppi |
| `-mtime +7` (väh. 8 vrk), `-mmin -30`, `-newer t` | ikä |
| `-size +100M`, `-empty`, `-perm -o+w` | koko, tyhjä, oikeudet |
| `-path ./x -prune -o … -print` | ohita hakemisto |
| `-print0`, `-delete`, `-exec k {} +` | toiminnot |

- `find . -name '*.txt' -print0 | xargs -0 -P4 -n1 gzip`
- Ensin pelkkä `find`, sitten `-delete` viimeiseksi.
- `tar -czf a.tgz --sort=name d`, `tar -tzf`, `tar -xzf a.tgz -C k`
- `sha256sum t > SUMS`, `sha256sum -c SUMS`

# Prosessit

| Tehtävä | Komento |
|---------|---------|
| Listaus | `ps aux`, `ps -ef --forest`, `pgrep -a nimi`, `top` |
| Portti | `ss -tlnp`, `lsof -i :8080` |
| Lopetus | `kill PID` (TERM), odota, `kill -9 PID` |
| Paluuarvo | 128 + signaali: 130 INT, 137 KILL, 143 TERM |
| Aikaraja | `timeout 30 k` (124), `timeout -k 5 30 k` |
| Tausta | `k &`, `jobs`, `fg`, Ctrl+Z, `bg`, `nohup`, `tmux` |
| Prioriteetti | `nice -n 10 k`, `renice`, `ionice -c3 k` |
| Kuorma | `uptime`, `free -h`, `nproc`, `df -h` |

# Ympäristö

- `export X=1`; kertaluonteinen `X=1 komento`; tyhjä `env -i k`.
- `PATH="$HOME/.local/bin:$PATH"`; `type -a k`; `hash -r`.
- `LC_ALL=C` skripteihin; `sort -V` versioille; `locale -a`.
- Kirjautuminen: `~/.profile`; pääte: `~/.bashrc`; skripti: ei mitään.
- Ctrl+R historiahaku, `Alt+.` edellinen argumentti, Ctrl+A/E.

# Paketit ja palvelut

| Tehtävä | Komento |
|---------|---------|
| Asennus | `sudo apt update && sudo apt install p` |
| Haku, tiedot | `apt search p`, `apt show p`, `apt-cache policy p` |
| Mistä tiedosto | `dpkg -S /usr/bin/x`, `dpkg -L p` |
| Palvelu | `systemctl status/start/stop/restart/reload s` |
| Käyttöön | `sudo systemctl enable --now s` |
| Muutos | `sudo systemctl edit s`, `daemon-reload` |
| Loki | `journalctl -u s -f`, `-p err`, `-b`, `--since` |
| Epäonnistuneet | `systemctl list-units --failed` |

# ssh

| Tehtävä | Komento |
|---------|---------|
| Avain | `ssh-keygen -t ed25519 -C kuka@kone`, `ssh-copy-id -i k.pub h` |
| Agentti | `ssh-add`, `ssh-add -l` |
| Asetukset | `~/.ssh/config`: `Host`, `HostName`, `User`, `ProxyJump` |
| Tulkinta, vianetsintä | `ssh -G h`, `ssh -v h` |
| Avain muuttui | tarkista sormenjälki, sitten `ssh-keygen -R h` |
| Siirto | `scp t h:/p`, `rsync -av --dry-run --delete l/ h:/p/` |
| Tunneli | `ssh -L 5433:localhost:5432 h`, `ssh -J hyppy h` |
| Istunto | `tmux new -s n`, Ctrl+B d, `tmux attach -t n` |
