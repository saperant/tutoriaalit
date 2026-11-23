# Työkalut ja testaus {.runko-tyokalut}

C:n työkalut paikkaavat sitä, mitä kieli ei tarkista. Tässä luvussa
käydään läpi C-kehittäjän perustyökalut: varoitukset, debuggeri,
sanitoijat, staattinen analyysi, profilointi ja yksikkötestaus.
Käännösjärjestelmiä ja jatkuvaa integraatiota käsitellään laajemmin
taidossa *Käännösjärjestelmät, testaus ja CI*.

## Käännös ja varoitukset

Käännöksen vaiheet ja perusvalitsimet esiteltiin johdannossa. Projekteissa
käytetään tavallisesti kahta käännöstyyppiä:

| Käännös | Valitsimet | Käyttö |
|---------|------------|--------|
| Kehitys | `-std=c23 -Wall -Wextra -Wpedantic -g -O0 -fsanitize=address,undefined` | debuggaus ja testit |
| Julkaisu | `-std=c23 -Wall -Wextra -O2 -DNDEBUG` | tuotanto |

`-Wall` ei nimestään huolimatta kytke kaikkia varoituksia. Hyödyllisiä
lisiä ovat `-Wconversion` (hiljaiset kavennukset), `-Wshadow`
(peittävät nimet), `-Wformat=2` (muotoilumerkkijonot) ja `-Wvla`
(muuttuvanpituiset taulukot). CI:ssä varoitukset muutetaan virheiksi
valitsimella `-Werror`, jotta niitä ei pääse kertymään.

Tämän tutoriaalin esimerkeillä on oma Makefile, joka kääntää ne kehitys-
valitsimilla: `make` kääntää kaikki, `make aja-10-rivit` ajaa yhden ja
`make virhe-03-etumerkki` näyttää tarkoituksella virheellisen esimerkin
käännösvirheen.

## Debuggaus: gdb

Debuggeria varten ohjelma käännetään valitsimilla `-g -O0`. Optimoinnit
siirtävät ja poistavat muuttujia, jolloin debuggeri ei aina pysty
näyttämään niitä. Tavallisimmat komennot:

```text
gdb ./ohjelma           käynnistä debuggeri
(gdb) break jasenna     pysähdy funktion alussa
(gdb) break tiedosto.c:42
(gdb) run argumentit    aja ohjelma
(gdb) bt                kutsupino (backtrace)
(gdb) frame 2           siirry kutsupinon kehykseen
(gdb) print *p          tulosta lauseke
(gdb) next / step       seuraava rivi / astu funktioon
(gdb) watch laskuri     pysähdy, kun muuttuja muuttuu
(gdb) continue          jatka
```

Kaatuneen ohjelman tilan voi tutkia jälkikäteen ytimen vedoksesta
(*core dump*): `ulimit -c unlimited` sallii vedokset, ja `gdb ohjelma core`
avaa ne. Komento `bt` näyttää heti, missä ohjelma kaatui.

## Sanitoijat

Sanitoijat lisäävät ohjelmaan ajonaikaisia tarkistuksia:

| Sanitoija | Valitsin | Havaitsee |
|-----------|----------|-----------|
| AddressSanitizer | `-fsanitize=address` | rajojen ylitykset, vapautetun muistin käytön, vuodot |
| UndefinedBehaviorSanitizer | `-fsanitize=undefined` | ylivuodot, virheelliset siirrot, tyhjät osoittimet |
| ThreadSanitizer | `-fsanitize=thread` | kilpatilanteet |
| MemorySanitizer (Clang) | `-fsanitize=memory` | alustamattoman muistin lukemisen |

AddressSanitizer ja ThreadSanitizer eivät toimi samassa käännöksessä,
joten testit ajetaan tarvittaessa useampaan kertaan eri sanitoijilla.
Luvuissa 7 ja 11 nähtiin, miltä sanitoijien raportit näyttävät.

## Staattinen analyysi

Staattinen analyysi etsii virheitä ajamatta ohjelmaa. Se löytää
virhepolkuja, joita testit eivät käy läpi:

- `gcc -fanalyzer` seuraa suorituspolkuja ja löytää esimerkiksi
  vapauttamatta jääneet varaukset ja tyhjän osoittimen dereferoinnit.
- `clang-tidy` tarkistaa sekä virheitä että tyylisääntöjä, ja monet sen
  löydöksistä se osaa korjata automaattisesti.
- `cppcheck` on kevyt, erillinen analysaattori, jota käytetään usein
  sulautetuissa projekteissa.

Analysaattorit tuottavat myös vääriä hälytyksiä. Ne kannattaa ottaa
käyttöön projektin alussa, jolloin löydökset pysyvät vähäisinä.

## Profilointi

Ennen optimointia mitataan, mihin aika kuluu. Linuxissa `perf` näyttää
funktiot, joissa ohjelma viettää eniten aikaa:

```text
gcc-14 -std=c23 -O2 -g ohjelma.c -o ohjelma
perf record -g ./ohjelma
perf report
```

Profilointi tehdään optimoidulla käännöksellä, koska optimoimaton koodi
käyttäytyy eri tavalla. Valitsin `-g` säilyttää funktioiden nimet ja
rivitiedot raportissa. Muita työkaluja ovat Valgrindin `callgrind` ja
`cachegrind`, jotka simuloivat ohjelman suorituksen hitaasti mutta
tarkasti. Optimoinnin yleiset menetelmät kuuluvat taitoon *Suorituskyvyn
analyysi ja optimointi*.

## Yksikkötestaus

Yksikkötesti ajaa yhden funktion tunnetuilla syötteillä ja tarkistaa
tuloksen. C:n standardikirjastossa ei ole testikehystä, mutta pienen
kehyksen voi kirjoittaa itse muutamalla makrolla:

```{.c tiedosto="esimerkit/13-testit.c" osa="kehys"}
```

Makrot käyttävät esikääntäjän piirteitä, joita funktio ei voisi
toteuttaa: `#ehto` muuttaa tarkistettavan lausekkeen tekstiksi ja
`__LINE__` kertoo rivin. Testattava funktio siistii merkkijonon:

```{.c tiedosto="esimerkit/13-testit.c" osa="testattava"}
```

Testit kattavat tavallisen tapauksen ja reunatapaukset: tyhjän
merkkijonon, pelkät välilyönnit ja välilyönnit sanojen välissä.

```{.c tiedosto="esimerkit/13-testit.c" osa="testit"}
```

```{.tuloste tiedosto="esimerkit/13-testit.odotettu"}
```

Testiohjelma palauttaa nollasta poikkeavan arvon, jos jokin tarkistus
epäonnistuu. Käännösjärjestelmä ja CI tunnistavat epäonnistumisen
paluuarvosta.

Laajemmissa projekteissa käytetään valmiita kehyksiä:
[Unity](https://www.throwtheswitch.org/unity) on suosittu sulautetuissa
järjestelmissä, [CMocka](https://cmocka.org) tukee korvikkeita
(*mock*) ja [Check](https://libcheck.github.io/check/) ajaa jokaisen
testin omassa prosessissaan, jolloin kaatuva testi ei kaada muita.

### Sumutestaus

*Sumutestaus* (*fuzzing*) syöttää ohjelmalle automaattisesti
generoituja, vähitellen muunneltuja syötteitä ja etsii kaatumisia.
Clangin libFuzzerille kirjoitetaan funktio
`int LLVMFuzzerTestOneInput(const uint8_t *data, size_t n)`, joka antaa
syötteen testattavalle jäsentimelle. Kun ohjelma käännetään valitsimella
`-fsanitize=fuzzer,address`, sumutin ja AddressSanitizer löytävät
yhdessä rajojen ylitykset, jotka käsin kirjoitetuilta testeiltä jäävät
huomaamatta. Jokainen ulkoista syötettä jäsentävä C-funktio kannattaa
sumuttaa.

## Käytännössä

- **Varoitukset virheiksi CI:ssä**, mutta ei välttämättä kehittäjän
  koneella, jossa uusi kääntäjäversio voi tuoda uusia varoituksia.
- **Testit sanitoijien kanssa.** Testisarja ajetaan ainakin
  AddressSanitizerin ja UndefinedBehaviorSanitizerin kanssa ja
  rinnakkaisuutta sisältävä koodi ThreadSanitizerin kanssa.
- **Testattavuus suunnitellaan.** Puhtaat funktiot (syöte sisään, tulos
  ulos) ovat helpoimpia testata. Ulkoiset riippuvuudet, kuten tiedostot
  ja laitteet, kätketään rajapinnan taakse (luku 8), jolloin testi voi
  korvata ne.
- **Reunatapaukset ensin:** tyhjä syöte, yksi alkio, suurin koko,
  virheellinen syöte. Suurin osa C-ohjelmien virheistä on reunoilla.
- **Mittaa ennen optimointia.** Profiloija osoittaa kuuman kohdan;
  arvaus osuu harvoin.
- **Ytimen vedos ja `bt`** ovat nopein tapa selvittää kaatuminen
  tuotannossa.

## Itsearviointi

- Osaat valita käännösvalitsimet kehitys- ja julkaisuversiolle ja
  selittää niiden erot.
- Osaat etsiä kaatumisen syyn gdb:llä: asettaa pysähdyskohdan, tutkia
  kutsupinon ja tulostaa muuttujia.
- Osaat valita oikean sanitoijan ja staattisen analyysin työkalun
  virhetyypin mukaan.
- Osaat kirjoittaa yksikkötestit funktiolle ja sen reunatapauksille.
