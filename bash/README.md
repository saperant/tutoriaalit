# Bash-skriptaus

Tiivis suomenkielinen opas luotettavien Bash-skriptien kirjoittamiseen
Bash 5.2:lla. Valmis dokumentti: [bash.pdf](bash.pdf), pikaopas
[bash-pikaopas.pdf](bash-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttökohteet ja rajat, kuoret ja standardit,
   työkalut
2. Bash kokeneelle – ajattelutapa, vastaavuudet, hinnat, sudenkuopat
3. Muuttujat, lainaus ja laajennukset – laajennusten järjestys,
   parametrilaajennukset, aritmetiikka, `printf`
4. Ehdot, silmukat ja funktiot – `[[ ]]`, `case`, glob ja `find -print0`,
   funktion tulos, nimiviittaukset
5. Taulukot ja assosiatiiviset taulukot – `mapfile`, komento taulukkona,
   laskenta avaimittain
6. Syöte, tiedostot ja tekstinkäsittely – `read`, uudelleenohjaukset,
   here-dokumentit, atominen kirjoitus, `awk`
7. Virheiden käsittely – `set -euo pipefail` ja sen aukot, `trap`
   EXIT ja ERR, `PIPESTATUS`
8. Argumentit, kirjastot ja skriptin rakenne – `getopts`, pitkät
   valitsimet, `source`, asetustiedostot
9. Putket, prosessit ja rinnakkaiset työt – `wait -n`, `xargs -P`,
   `flock`, signaalit, `timeout`
10. Automaatioskriptien mallit – idempotenssi, kuivaharjoitus, atominen
    julkaisu, uudelleenyritys
11. Työkalut – ShellCheck, shfmt, jäljitys, profilointi, bats
12. Lopuksi – mallit, nyrkkisäännöt, turvallisuus, milloin vaihtaa
    kieltä, lähteet

## Rakentaminen

```text
make testaa   # ShellCheck ja esimerkkien ajo (Bash 5.2, bats)
make pdf      # rakentaa bash.pdf:n ja bash-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
