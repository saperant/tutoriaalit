# Komentorivi ja Linux

Tiivis suomenkielinen opas Linuxin käyttöön komentoriviltä:
tiedostot ja oikeudet, putket, tekstinkäsittely, prosessit, ympäristö,
paketit ja palvelut sekä etäkäyttö. Esimerkit ajetaan GNU-työkaluilla
Ubuntu 24.04:ssä. Valmiit dokumentit: [komentorivi.pdf](https://saperant.github.io/tutoriaalit/materiaalit/komentorivi.pdf)
ja pikaopas [komentorivi-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/komentorivi-pikaopas.pdf).

Skriptien kirjoittaminen opetetaan erillisessä
[Bash-skriptauksen tutoriaalissa](../bash/).

## Sisältö

1. Johdanto – pääte, kuori ja komennot, ensimmäinen istunto, ohjeet,
   GNU, BSD ja POSIX
2. Tiedostojärjestelmä – hierarkia, polut, glob, katselu ja editorit
   (`less`, nano, vi), lainausmerkit, inodet ja linkit, atominen
   korvaus, hankalat nimet
3. Käyttäjät ja oikeudet – `chmod`, umask, oikeuksien korjaus,
   setgid ja sticky, `sudo tee`
4. Putket ja uudelleenohjaukset – virrat, `2>&1`:n järjestys, `tee`,
   paluuarvot ja ketjutus, prosessikorvaus, `comm` ja `diff`
5. Tekstin etsiminen – grep, säännölliset lausekkeet, poiminta,
   konteksti, hakemistopuut
6. Tekstinkäsittelyn työkalut – `sort`, `uniq`, `cut`, `sed`,
   `join`, CRLF, putken rakentaminen
7. Raportit awkilla – ryhmittely, koosteet, CSV-raportti, tila rivien
   välillä
8. Etsintä, massatoiminnot ja arkistot – `find`, siivous, `xargs -0`,
   `tar`, tarkistussummat
9. Prosessit ja signaalit – `ps`, `/proc`, signaalit, työt,
   `timeout`, `nice`, `ulimit`
10. Ympäristö ja kuoren asetukset – ympäristömuuttujat, `PATH`,
    lokaali, `.profile` ja `.bashrc`
11. Paketit, palvelut ja lokit – `apt`, `dpkg`, systemd-yksiköt,
    ajastetut tehtävät, `journalctl`, kirjautumislokin analyysi
12. Verkko ja etäkäyttö: ssh – verkon perustyökalut ja `curl`,
    avaimet, `~/.ssh/config`, `rsync`, tunnelit, tmux, kovennus
13. Lopuksi – nyrkkisäännöt, turvallisuus, lähteet

## Rakentaminen

```text
make testaa   # ajaa esimerkit ShellCheckillä ja Bashilla ja vertaa
              # tulosteita odotettuihin
make pdf      # rakentaa komentorivi.pdf:n ja komentorivi-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/komentorivi`.
Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
