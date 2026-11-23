# Bash kokeneelle {.runko-kokeneelle}

Tämä luku on lukijalle, joka osaa jo jonkin yleiskäyttöisen kielen ja
kirjoittaa Bashia satunnaisesti. Luku kokoaa Bashin ajattelutavan,
vastaavuudet tuttuihin kieliin, hinnat ja tärkeimmät sudenkuopat.

## Ajattelutapa

- **Kaikki on merkkijonoja ja komentoja.** Rivi `x=5` tallentaa
  merkkijonon. Lauseke `$x` ei ole arvon haku vaan *laajennus*: Bash
  korvaa sen tekstillä ja jäsentää tuloksen uudelleen sanoiksi ja
  tiedostonimikuvioiksi, ellei laajennusta lainata. Tämä yksi sääntö
  selittää suurimman osan Bash-virheistä (luku 3).
- **Totuusarvo on paluuarvo.** `if` ei arvioi lauseketta vaan ajaa
  komennon ja tarkistaa sen paluuarvon: 0 on tosi, muu epätosi. `[[ ]]`
  ja `(( ))` ovat komentoja, jotka palauttavat 0 tai 1.
- **Funktio on pieni ohjelma.** Funktio ottaa argumentit kuten komento
  (`$1`, `$2`, `"$@"`), palauttaa paluuarvon (0–255) ja tuottaa tuloksensa
  tulosteena. Tuloste kaapataan komentokorvauksella `$(…)`.
- **Prosessit ovat rakennusosia.** Putki, komentokorvaus ja `&`
  käynnistävät uusia prosesseja. Muuttujat eivät siirry prosessista
  toiseen takaisin päin, mikä yllättää (alla).
- **Virhe ei pysäytä oletuksena.** Epäonnistunut komento palauttaa
  nollasta poikkeavan arvon, ja skripti jatkaa seuraavaan riviin.
  `set -euo pipefail` muuttaa tämän, mutta ei kaikkialla (luku 7).

## Vastaavuudet muihin kieliin

| Asia | Python | Bash |
|------|--------|------|
| Merkkijono | `s = "a b"` | `s='a b'`, käyttö aina `"$s"` |
| Lista | `l = ["a", "b c"]` | `l=(a "b c")`, käyttö `"${l[@]}"` (luku 5) |
| Sanakirja | `d = {"k": 1}` | `declare -A d=([k]=1)` (luku 5) |
| Funktion tulos | `return arvo` | `echo arvo` ja kaappaus `x=$(f)` (luku 4) |
| Onnistuminen | poikkeus tai `None` | paluuarvo `return 1` |
| Poikkeus | `raise`, `try` | `set -e`, `if ! komento`, `trap … ERR` (luku 7) |
| `finally`, `with` | `try … finally` | `trap siivoa EXIT` (luku 7) |
| Modulit | `import` | `source tiedosto.sh` (luku 8) |
| Argumentit | `argparse` | `getopts` tai `while`/`case` (luku 8) |
| Säikeet | `threading`, `asyncio` | taustaprosessit `&` ja `wait` (luku 9) |
| Merkkijonon käsittely | `s.split()`, `re` | parametrilaajennukset, `[[ =~ ]]` (luku 3) |
| Testit | `pytest` | bats (luku 11) |

## Hinnat

Bashissa kallista on prosessin käynnistäminen. Sisäänrakennetut komennot
(`echo`, `printf`, `read`, `[[ ]]`, `(( ))`, parametrilaajennukset) ovat
halpoja. Ulkoinen ohjelma (`sed`, `grep`, `date`, `basename`) ja
komentokorvaus `$(…)` maksavat `fork`- ja usein myös `exec`-kutsun, eli
tyypillisesti 0,5–2 millisekuntia. Yksittäin tämä on merkityksetöntä,
mutta silmukassa se ratkaisee:

- **Ulkoinen komento rivi riviltä.** Silmukka, joka kutsuu `sed`:iä
  jokaiselle 100 000 rivistä, kestää minuutteja. Sama työ yhdellä
  `awk`- tai `sed`-ajolla koko tiedostolle kestää alle sekunnin
  (luku 6).
- **`$(…)` tuloksen palauttamiseen.** Jokainen funktiokutsu
  komentokorvauksessa käynnistää alikuoren. Kuumissa silmukoissa tulos
  välitetään nimiviittauksella tai globaalilla muuttujalla (luku 4).
- **Bashin oma silmukka** on itsessään hidas: kymmeniä kertoja Pythonia
  hitaampi. Bash ei ole laskentakieli.
- **Taulukot** ovat halpoja pienillä määrillä. Assosiatiivinen taulukko on
  hajautustaulu, mutta tavallinen taulukko on Bash 5.2:ssa linkitetty
  lista, joten hajasaanti suureen taulukkoon ei ole vakioaikaista.

Kalleimpia ovat kuitenkin virheet: lainaamaton muuttuja `rm`-komennossa
tai huomaamatta jäänyt epäonnistuminen. Siksi tämä tutoriaali painottaa
oikeellisuutta ennen nopeutta.

## Tärkeimmät sudenkuopat

1. **Lainaamaton laajennus.** `rm $tiedosto` jakaa nimen välilyönneistä ja
   laajentaa `*`-merkit. Lainaa aina: `rm -- "$tiedosto"` (luku 3).
2. **Putken alikuori.** Putken jokainen osa ajetaan omassa
   alikuoressaan, joten putken sisällä asetetut muuttujat katoavat:

```{.bash tiedosto="esimerkit/02-alikuori.sh"}
```

```{.tuloste tiedosto="esimerkit/02-alikuori.odotettu"}
```

3. **`set -e`:n aukot.** Ehdon sisällä (`if f`, `f && …`, `f || …`)
   kutsuttu funktio ei pysähdy virheeseen, eikä `local x=$(komento)`
   huomaa komennon epäonnistumista (luvut 4 ja 7).
4. **`[` vs. `[[`.** `[` on tavallinen komento, jonka argumentit
   jaetaan sanoiksi; `[[ ]]` on kielen rakenne, joka ei jaa. Bash-
   skripteissä käytetään `[[ ]]`:ta (luku 4).
5. **`echo` mielivaltaiselle datalle.** `echo "$x"` tulkitsee arvon `-n`
   tai `-e` valitsimeksi. Datan tulostus tehdään `printf '%s\n' "$x"`
   (luku 3).
6. **Tiedostonimet ovat mielivaltaisia.** Nimessä voi olla välilyönti,
   rivinvaihto tai alussa viiva. `ls`-komennon tulostetta ei jäsennetä;
   käytetään globia tai `find -print0` (luku 4).

## Mitä Bashista puuttuu

Kielipakettien yhteisestä rungosta puuttuu tästä tutoriaalista kaksi
osaa (`runko_ei_sovellu` paketin metatiedoissa):

- **Muistimalli ja resurssienhallinta.** Bash varaa ja vapauttaa muistin
  itse, eikä ohjelmoija näe osoittimia tai elinaikoja. Skriptin resurssit
  ovat väliaikaisia tiedostoja, lukkoja ja taustaprosesseja, ja niiden
  siivous käsitellään virheenkäsittelyn yhteydessä (`trap … EXIT`,
  luku 7).
- **Omat tyypit.** Bashissa ei ole rakenteita, luokkia eikä rajapintoja.
  Lähimmät korvikkeet ovat assosiatiivinen taulukko, nimeämiskäytäntö
  (`palvelin_nimi`, `palvelin_portti`) ja nimiviittaus (luku 4). Kun
  niitä tarvitaan, skripti on yleensä kasvanut kieltään suuremmaksi.

## Lukuohje

Kokenut lukija lukee ensin lukujen itsearvioinnit. Kannattaa kuitenkin
lukea kokonaan ainakin luvut 3 (lainaus ja laajennukset) ja 7
(virheiden käsittely): ne poikkeavat eniten muista kielistä. Luku 12 kokoaa
nyrkkisäännöt, ja pikaopas on erillinen muistilista.
