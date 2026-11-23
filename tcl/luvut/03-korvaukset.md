# Komennot, korvaukset ja arvot {.runko-tyypit}

Tcl:n koko syntaksi on kahdentoista säännön mittainen. Ne on kuvattu
käsikirjasivulla `Tcl(n)`, jota kutsutaan *Dodekalogiksi*. Säännöt on
helppo oppia, mutta niiden seuraukset yllättävät. Tämä luku käy ne
läpi ja näyttää, miten arvoja lasketaan, muotoillaan ja luetaan.

## Säännöt tiivistettynä

1. **Skripti** koostuu komennoista, jotka erotetaan rivinvaihdolla tai
   puolipisteellä.
2. **Komento** on sanoja, jotka erotetaan välilyönneillä. Ensimmäinen
   sana on komennon nimi, loput argumentteja. Komento itse päättää,
   miten argumentit tulkitaan.
3. **Lainausmerkit** `"…"` tekevät yhden sanan, jonka sisällä korvaukset
   tehdään.
4. **Aaltosulkeet** `{…}` tekevät yhden sanan ilman mitään korvauksia.
   Sisäkkäiset aaltosulkeet lasketaan pareittain.
5. **Argumenttien levitys** `{*}` sanan alussa jakaa listan alkiot
   erillisiksi sanoiksi.
6. **Komentokorvaus** `[…]` korvataan komennon tuloksella.
7. **Muuttujakorvaus** `$nimi`, `${nimi}` tai `$taulukko(avain)`
   korvataan muuttujan arvolla.
8. **Kenoviivakorvaus** `\n`, `\t`, `\$`, `\[` ja rivin lopun `\`
   (jatkorivi).
9. **Kommentti** alkaa `#`-merkillä vain komennon alussa.
10. **Korvaukset tehdään kerran** vasemmalta oikealle, eikä tulosta
    jäsennetä uudelleen sanoiksi. Korvauksen tulos on yksi sana.

Tiivistelmässä on kymmenen kohtaa, koska alkuperäisen säännöt
arvioinnista, sanoista ja korvausten järjestyksestä on yhdistetty.
Olennaista on kohta 10: kun
`$tiedosto` sisältää välilyönnin, se on silti yksi argumentti. Tcl:ssä
ei ole Bashin sananjakamisongelmaa.

```{.tcl tiedosto="esimerkit/03-korvaukset.tcl" osa="korvaukset"}
```

```{.tcl tiedosto="esimerkit/03-korvaukset.tcl" osa="ryhmittely"}
```

Aaltosulkeet eivät ole "merkkijono", vaan lainaus: ne estävät
korvaukset *nyt*, jotta komento voi tehdä ne *myöhemmin*. Siksi `if`,
`while`, `proc` ja `expr` saavat koodinsa aaltosulkeissa. Ne
korvaavat muuttujat itse, kun koodi suoritetaan.

## Listat ovat lainattuja merkkijonoja

Lista on merkkijono, jonka alkiot on lainattu niin, että se jäsentyy
takaisin samoiksi alkioiksi. `list` lisää lainauksen automaattisesti.
Merkkijonojen liimaaminen ei lisää, joten erikoismerkit rikkovat
rakenteen:

```{.tcl tiedosto="esimerkit/03-korvaukset.tcl" osa="lista"}
```

```{.tuloste tiedosto="esimerkit/03-korvaukset.odotettu"}
```

Tuloste näyttää lainauksen: `{data[3] valid}` on yksi alkio. Sääntö:
komennot, takaisinkutsut ja listat rakennetaan aina `list`-komennolla.

## Luvut ja `expr`

Tcl:ssä ei ole operaattoreita lausekkeiden ulkopuolella. Laskenta
tehdään komennolla `expr`, joka ymmärtää C:n kaltaiset lausekkeet ja
matemaattiset funktiot. Kokonaisluvut ovat rajattomia, liukuluvut
kaksoistarkkuuksisia. Tyyppi määräytyy arvosta: `7 / 2` on
kokonaislukujako.

```{.tcl tiedosto="esimerkit/03-lausekkeet.tcl" osa="luvut"}
```

Vertailuoperaattori `==` vertaa lukuina aina, kun molemmat puolet
näyttävät luvuilta. Merkkijonoille on omat operaattorit:

```{.tcl tiedosto="esimerkit/03-lausekkeet.tcl" osa="vertailu"}
```

Totuusarvoja ovat luvut (0 epätosi) sekä sanat `true`, `false`, `yes`,
`no`, `on` ja `off`. `string is boolean` tarkistaa ne.

## Muotoilu ja syöte

`format` toimii kuten C:n `printf` ja `scan` kuten `sscanf`. Jälkimmäinen
palauttaa onnistuneiden muunnosten määrän, joten sillä myös
validoidaan syöte (luku 1).

```{.tcl tiedosto="esimerkit/03-lausekkeet.tcl" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/03-lausekkeet.odotettu"}
```

Tulostus: `puts ?-nonewline? ?kanava? teksti`. Syöte: `gets stdin rivi`
palauttaa rivin pituuden tai `-1` tiedoston lopussa, ja `read stdin`
lukee kaiken. Syötteen tarkistukseen sopii `string is integer -strict`
tai `string is double -strict`. Ilman valitsinta `-strict` tyhjä
merkkijono kelpaa luvuksi.

## Kaksinkertainen korvaus

Jos `expr`-lauseke kirjoitetaan ilman aaltosulkeita, Tcl korvaa
muuttujat ensin itse, ja `expr` jäsentää tuloksen uudelleen. Arvo
tulkitaan siis koodiksi:

```{.tcl tiedosto="esimerkit/03-injektio.kaatuu.tcl"}
```

```{.tuloste tiedosto="esimerkit/03-injektio.virhe"}
```

Hakasulkeissa oleva komento suoritettiin. `error` olisi voinut olla
`file delete` tai `exec`. Sama koskee komentoja `if`, `while` ja
`for`, joiden ehto on lauseke.

## Etunolla ja oktaaliluvut

Tcl 8.6 tulkitsee nollalla alkavan kokonaisluvun oktaaliluvuksi. `07`
toimii, `08` ei. Väyläindeksit, päivämäärät ja kellonajat ovat
tyypillisiä nollalla alkavia lukuja:

```{.tcl tiedosto="esimerkit/03-oktaali.kaatuu.tcl"}
```

```{.tuloste tiedosto="esimerkit/03-oktaali.virhe"}
```

`scan $x %d` tulkitsee luvun aina kymmenjärjestelmässä. Tcl 9.0
poisti oktaalitulkinnan, mutta EDA-työkalujen 8.6-tulkeissa se on
voimassa vielä pitkään.

## Käytännössä

- **Aaltosulkeet kaikkialle, missä komento tulkitsee koodia:**
  `expr {…}`, `if {…} {…}`, `while {…}`, `proc nimi {args} {…}`.
  Tämä on sekä nopein että ainoa turvallinen tapa.
- **Rakenna listat ja komennot `list`-komennolla.** Kun komento
  halutaan suorittaa myöhemmin (takaisinkutsu, `after`, `exec`),
  `list` takaa, että jokainen argumentti pysyy yhtenä sanana.
- **Väylä- ja pinninimet aaltosulkeisiin** `{u0/data[3]}`, ja
  muuttujissa ne ovat turvassa: `$pinni` ei korvaa uudelleen.
- **Käytä merkkijonoille `eq`/`ne`** ja luvuille `==`/`!=`.
- **Jäsennä luvut `scan`-komennolla** ulkoisesta syötteestä, jos niissä
  voi olla etunollia.
- **Ilmoita virheet virhevirtaan** (`puts stderr`) ja tulokset
  tulosteeseen, jotta skriptiä voi ketjuttaa.

## Itsearviointi

- Osaat selittää, mitä `"…"`, `{…}`, `[…]` ja `$` tekevät ja miksi
  korvauksen tulosta ei jaeta sanoiksi.
- Osaat rakentaa komennon tai listan `list`-komennolla ja levittää sen
  `{*}`-merkinnällä.
- Osaat selittää, miksi aaltosulkeeton `expr` on sekä hidas että
  vaarallinen.
- Osaat jäsentää ja validoida numeerisen syötteen `scan`- ja
  `string is` -komennoilla ja tunnet oktaalisudenkuopan.
