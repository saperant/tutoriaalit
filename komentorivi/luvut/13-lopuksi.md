# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Pienet työkalut, yksi kerrallaan.** Rakenna putki vaiheittain ja
   katso välitulos ennen seuraavaa vaihetta.
2. **Kokeile ennen kuin muutat.** `echo` ennen `rm`-komentoa, `find`
   ilman `-delete`-toimintoa, `sed` ilman valitsinta `-i`, `rsync
   --dry-run`.
3. **Lainaa nimet ja käytä `--`-erotinta.** Välilyönnit ja viivat
   tiedostonimissä ovat normaaleja, eivät poikkeuksia.
4. **Nollatavu erottimeksi**, kun nimiä välitetään putkessa:
   `-print0`, `-z`, `-Z`, `xargs -0`.
5. **Toistettavuus**: `LC_ALL=C`, tasapelisäännöt lajittelussa,
   `tar --sort=name`. Sama komento antaa saman tuloksen kaikilla
   koneilla.
6. **Vähimmät oikeudet**: palvelut omina käyttäjinään, salaisuudet
   `600`, `sudo` yksittäisille komennoille, ei koskaan `777`.
7. **Hallittu lopetus**: `TERM` ennen `KILL`-signaalia ja aikaraja
   kaikkeen, mikä odottaa.
8. **Rakenteinen data jäsentimelle**: JSON `jq`:lle, CSV, jossa on
   lainauksia, ohjelmalle, ja liitokset SQL:lle.
9. **Toistuva komento skriptiksi.** Kun samaa putkea kirjoitetaan
   kolmatta kertaa, se kuuluu tiedostoon versionhallintaan (taito
   *Bash-skriptaus*).

## Turvallisuus

- **`curl … | sh`** ajaa verkosta ladattua koodia sellaisenaan, usein
  pääkäyttäjänä. Lataa skripti ensin tiedostoon, lue se ja aja vasta
  sitten.
- **`rm -rf "$HAKEMISTO/"*`** poistaa nykyisen hakemiston sisällön,
  jos muuttuja on tyhjä. Skripteissä `${HAKEMISTO:?}` keskeyttää
  ajon tyhjällä arvolla.
- **Salaisuudet komentorivillä** näkyvät muille käyttäjille
  (`ps aux`) ja jäävät historiaan. Välitä ne tiedostosta tai
  syötteestä. Välilyönnillä alkava komento ei tallennu historiaan, kun
  asetuksena on `HISTCONTROL=ignorespace`.
- **Kopioitu komento verkkosivulta** voi sisältää näkymättömiä
  merkkejä tai muuta kuin miltä näyttää. Liitä se ensin editoriin.

## Jatkotaidot

- *Bash-skriptaus*: putket ja työkalut kootaan luotettaviksi
  skripteiksi.
- *Versionhallinta (Git)*, *C-kieli*, *Python työkaluohjelmointiin* ja
  *Tietoverkot*: komentorivi on näiden esitieto.
- *Käyttöjärjestelmät*: järjestelmän sisäinen toiminta, eli prosessit,
  muisti, tiedostojärjestelmät ja järjestelmäkutsut.
- *Kontit ja pilvi-infrastruktuuri*: kontit ja palvelinten automaatio.

## Lähteet ja lisämateriaali

### Ensisijainen dokumentaatio

- **Ohjesivut** (`man`, `info`), verkossa **The Linux man-pages
  project** (<https://man7.org/linux/man-pages/>). Komennon
  oma ohjesivu on aina tarkin lähde valitsimille.
- **GNU Coreutils Manual**
  (<https://www.gnu.org/software/coreutils/manual/>) sekä GNU grepin,
  sedin, findutilsin ja gawkin käsikirjat (<https://www.gnu.org/manual/>).
  Gawkin käsikirja *GAWK: Effective AWK Programming* on myös paras
  awk-kielen opas.
- **POSIX Shell and Utilities**
  (<https://pubs.opengroup.org/onlinepubs/9799919799/>), kun skriptin
  on toimittava muuallakin kuin GNU-ympäristössä.
- **systemd-dokumentaatio** (<https://systemd.io> ja ohjesivut
  `systemd.service`, `systemd.exec`, `journalctl`).
- **OpenSSH:n ohjesivut** (<https://www.openssh.com/manual.html>),
  erityisesti `ssh_config` ja `sshd_config`.
- **Filesystem Hierarchy Standard**
  (<https://refspecs.linuxfoundation.org/fhs.shtml>).

### Oppaat

- **The Missing Semester of Your CS Education**, MIT
  (<https://missing.csail.mit.edu>): kuori, datan käsittely,
  etäkäyttö ja työkalut luentoina ja harjoituksina.
- **The Linux Command Line**, William Shotts
  (<https://linuxcommand.org/tlcl.php>), kattava kirja komentorivistä,
  vapaasti luettavissa verkossa.
- **The Debian Administrator's Handbook**
  (<https://debian-handbook.info>): paketinhallinta, palvelut ja
  ylläpito Debian-pohjaisissa jakeluissa.
- **ArchWiki** (<https://wiki.archlinux.org>), jakelusta riippumatta
  yksi parhaista lähteistä systemd:lle, ssh:lle ja järjestelmän
  asetuksille.
- **Greg's Wiki** (<https://mywiki.wooledge.org>): *BashFAQ* ja
  *BashPitfalls* kuoren sudenkuopista, mukaan lukien `ls`-tulosteen
  jäsentämisen ongelmat.

### Työkalut

- **tldr-pages** (<https://tldr.sh>): tiiviit käyttöesimerkit
  yleisimmille komennoille ohjesivujen rinnalle.
- **explainshell** (<https://explainshell.com>) selittää komentorivin
  osa kerrallaan ohjesivujen perusteella.
- **ShellCheck** (<https://www.shellcheck.net>) löytää virheet myös
  yhden rivin komennoista.
- Modernit vaihtoehdot: `ripgrep` (`rg`) grepin, `fd` findin, `jq`
  JSON-datan ja `htop` topin tilalle. Perustyökalut on silti osattava,
  koska ne löytyvät jokaisesta järjestelmästä.
