# Tcl

Tiivis suomenkielinen opas Tcl 8.6:een EDA-työkalujen komentokielenä:
korvaussäännöt, kokoelmat, virheenkäsittely, tapahtumasilmukka ja
EDA-skriptauksen mallit. Valmis dokumentti: [tcl.pdf](tcl.pdf),
pikaopas [tcl-pikaopas.pdf](tcl-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttö EDA-työkaluissa, toteutukset
2. Tcl kokeneelle – ajattelutapa, vastaavuudet, hinnat, sudenkuopat
3. Komennot, korvaukset ja arvot – Dodekalogi, listat, `expr`,
   muotoilu, injektio ja oktaaliluvut
4. Proseduurit ja ohjausrakenteet – valitsimet, `upvar`, omat
   ohjausrakenteet `uplevel`-komennolla
5. Arvot, esitykset ja muisti – viitelaskenta, shimmering,
   copy-on-write, mitatut hinnat
6. Listat, sanakirjat ja merkkijonot – netlistan ja raporttien käsittely
7. Oliot: TclOO – luokat, periytyminen, mixinit
8. Virheenkäsittely – `throw`, `try`/`trap`, virhekoodit, pino
9. Nimiavaruudet, paketit ja tiedostot – `namespace ensemble`,
   `package`, atominen kirjoitus, `exec`
10. Tapahtumasilmukka ja korutiinit – rinnakkaiset ajot,
    generaattorit
11. EDA-skriptauksen mallit – raportin jäsennin, parametrisoitu kulku,
    argumentit
12. Työkalut ja testaus – tcltest, `trace`, `time`, tarkistimet
13. Lopuksi – mallit, nyrkkisäännöt, Tcl 9.0, lähteet

EDA-työkalujen komennot on esimerkeissä simuloitu tavallisilla
proseduureilla, joten kaikki koodi ajetaan ja testataan pelkällä
`tclsh`:lla.

## Rakentaminen

```text
make testaa   # esimerkkien ajo tclsh8.6:lla ja tulosteiden vertailu
make pdf      # rakentaa tcl.pdf:n ja tcl-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
