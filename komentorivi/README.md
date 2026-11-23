# Komentorivi ja Linux

Tiivis suomenkielinen opas Linuxin käyttöön komentoriviltä:
tiedostot ja oikeudet, putket, tekstinkäsittely, prosessit, ympäristö,
paketit ja palvelut sekä etäkäyttö. Esimerkit ajetaan GNU-työkaluilla
Ubuntu 24.04:ssä. Valmiit dokumentit: [komentorivi.pdf](komentorivi.pdf)
ja pikaopas [komentorivi-pikaopas.pdf](komentorivi-pikaopas.pdf).

Skriptien kirjoittaminen opetetaan erillisessä
[Bash-skriptauksen tutoriaalissa](../bash/).

## Sisältö

1. Johdanto – pääte, kuori ja komennot, paluuarvot, ohjeet, GNU,
   BSD ja POSIX
2. Tiedostojärjestelmä – hierarkia, polut, glob, inodet ja linkit,
   atominen korvaus, hankalat nimet
3. Käyttäjät ja oikeudet – `chmod`, umask, oikeuksien korjaus,
   setgid ja sticky, `sudo tee`
4. Putket ja uudelleenohjaukset – virrat, `2>&1`:n järjestys, `tee`,
   prosessikorvaus, `comm` ja `diff`
5. Tekstin etsiminen – grep, säännölliset lausekkeet, poiminta,
   konteksti, hakemistopuut
6. Tekstinkäsittelyn työkalut – `sort`, `uniq`, `cut`, `sed`,
   `join`, CRLF, putken rakentaminen
7. Raportit awkilla – ryhmittely, koosteet, CSV-raportti, tila rivien
   välillä
8. Tiedostojen etsintä ja massatoiminnot – `find`, siivous, `xargs -0`,
   `tar`, tarkistussummat
9. Prosessit ja signaalit – `ps`, `/proc`, signaalit, työt,
   `timeout`, `nice`, `ulimit`
10. Ympäristö ja kuoren asetukset – ympäristömuuttujat, `PATH`,
    lokaali, `.profile` ja `.bashrc`
11. Paketit, palvelut ja lokit – `apt`, `dpkg`, systemd-yksiköt,
    `journalctl`, kirjautumislokin analyysi
12. Etäkäyttö: ssh – avaimet, `~/.ssh/config`, `rsync`, tunnelit,
    tmux, kovennus
13. Lopuksi – nyrkkisäännöt, turvallisuus, lähteet

## Rakentaminen

```text
make testaa   # ajaa esimerkit ShellCheckillä ja Bashilla ja vertaa
              # tulosteita odotettuihin
make pdf      # rakentaa komentorivi.pdf:n ja komentorivi-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/komentorivi`.
