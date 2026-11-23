# Tcl kokeneelle {.runko-kokeneelle}

Tämä luku on lukijalle, joka osaa jonkin muun kielen ja joutuu
kirjoittamaan Tcl:ää työkalun takia. Se kokoaa kielen ajattelutavan,
vastaavuudet, hinnat ja sudenkuopat.

## Ajattelutapa

- **Kaikki on komento.** Rivi on komento ja sen argumentit, eroteltuna
  välilyönneillä. `if`, `while`, `proc` ja `set` ovat tavallisia
  komentoja, eivät avainsanoja. Siksi omia ohjausrakenteita voi
  kirjoittaa itse (luku 4).
- **Kaikki on merkkijono.** Jokaisella arvolla on merkkijonoesitys.
  Lista, sanakirja ja luku ovat merkkijonoja, jotka tulkki pitää
  sisäisesti tehokkaassa muodossa (luku 5).
- **Jäsennys tapahtuu kerran.** Tulkki jakaa komennon sanoiksi, tekee
  korvaukset (`$muuttuja`, `[komento]`, `\`) ja kutsuu komentoa.
  Korvauksen tulosta ei jäsennetä uudelleen. Aaltosulkeet estävät
  korvaukset, ja komento itse päättää, tulkitaanko argumentti koodiksi
  (luku 3).
- **Koodi on dataa.** Proseduurin runko, `if`-komennon haarat ja
  takaisinkutsut ovat merkkijonoja, jotka välitetään komennoille.
  Komennot rakennetaan listoina (`list`), ei merkkijonoja liimaamalla.

## Vastaavuudet muihin kieliin

| Asia | Python | Tcl |
|------|--------|-----|
| Sijoitus | `x = 5` | `set x 5` |
| Lauseke | `a + b * 2` | `expr {$a + $b * 2}` |
| Funktiokutsu | `f(a, b)` | `f $a $b`, tulos `[f $a $b]` |
| Lista | `["a", "b c"]` | `list a "b c"` |
| Sanakirja | `{"k": 1}` | `dict create k 1` |
| Merkkijonovertailu | `a == b` | `$a eq $b` |
| Viittausparametri | (ei ole) | `upvar 1 $nimi x` |
| Lambda | `lambda x: x * 2` | `apply {{x} {expr {$x * 2}}} 3` |
| Poikkeus | `raise`, `try` | `throw`, `try`/`trap` (luku 8) |
| Luokka | `class` | `oo::class create` (luku 7) |
| Moduli | `import` | `package require`, `namespace` (luku 9) |
| asyncio | `await` | tapahtumasilmukka, korutiinit (luku 10) |
| pytest | `assert` | `tcltest` (luku 12) |

## Hinnat

Tcl kääntää proseduurien rungot tavukoodiksi ensimmäisellä kutsulla.
Hinnat syntyvät siitä, mitä kääntäjä ei voi tehdä etukäteen:

- **Aaltosulkeeton `expr`** jäsennetään ja käännetään joka kerta
  uudelleen ja on noin 20 kertaa hitaampi. Lisäksi se on
  tietoturva-aukko (luku 3).
- **Esitysten edestakainen muunnos** (*shimmering*): lista, jota
  käsitellään merkkijonona, menettää listaesityksensä ja jäsennetään
  uudelleen seuraavalla listaoperaatiolla. Silmukassa tämä tekee
  lineaarisesta työstä neliöllistä (luku 5).
- **Jaetun arvon muokkaus** kopioi arvon. `lappend` ja `lset`
  muokkaavat muuttujaa paikallaan; `set l [lreplace $l …]` kopioi koko
  listan, jos arvoon on toinenkin viittaus (luku 5).
- **Päätason koodi** on hitaampaa kuin proseduurin koodi, koska
  muuttujat haetaan nimellä. Kuuma silmukka kuuluu proseduuriin.
- **`exec` ja `open |…`** käynnistävät prosessin, mikä maksaa
  millisekunteja. EDA-työkalun komennot (raportit, haut) ovat usein
  vielä kalliimpia: tulos kannattaa hakea kerran ja käsitellä Tcl:ssä.
- **`uplevel`, `eval` ja `subst`** jäsentävät koodin ajonaikana.
  Ne ovat oikea työkalu ohjausrakenteisiin, mutta eivät kuumaan
  silmukkaan.

## Sudenkuopat

1. **Aaltosulkeeton `expr`, `if` tai `while`.** `expr $a + 1` korvaa
   muuttujat kahdesti. Kirjoita aina `expr {$a + 1}` ja `if {…}`.
2. **Kommentti on komento.** `#` aloittaa kommentin vain komennon
   paikalla. Rivin lopussa tarvitaan `;#`. Pariton aaltosulje
   kommentissa rikkoo rungon (luku 4).
3. **Hakasulkeet nimissä.** `data[3]` lainausmerkeissä ajaa komennon
   `3`. Väylä- ja pinninimet kirjoitetaan aaltosulkeisiin:
   `{u_alu/data[3]}`. Tämä on EDA-skriptien yleisin virhe.
4. **Etunolla on oktaaliluku** Tcl 8.6:ssa: `expr {08 + 1}` kaatuu.
   Jäsennä luvut komennolla `scan $x %d` (luku 3).
5. **`==` vertaa lukuina:** `"1.0" == "1"` on tosi. Merkkijonoille
   käytetään `eq` ja `ne`.
6. **Komento merkkijonona.** `eval "komento $arg"` rikkoutuu, kun
   argumentissa on välilyönti tai erikoismerkki. Rakenna komento
   listana: `{*}[list komento $arg]`.
7. **`catch` nielaisee virheet.** Pelkkä `catch {…}` piilottaa virheen
   ja sen syyn. Käsittele vain odotetut virheet `try`/`trap`-rakenteella
   (luku 8).
8. **Globaalit muuttujat proseduurissa** eivät näy ilman `global`- tai
   `variable`-komentoa tai täyttä nimeä `::nimi`.

## Mitä Tcl:ssä ei ole

Rungon kaikki osat soveltuvat Tcl:ään, mutta osa toisin kuin
käännetyissä kielissä. Muistia ei hallita käsin: arvoilla on
viitelaskenta, ja luku 5 käsittelee muistimallia arvojen esitysten ja
kopioinnin kannalta. Rinnakkaisuus on Tcl:ssä tapahtumasilmukka,
korutiinit ja prosessit (luku 10). Säikeet ovat erillisessä
`Thread`-paketissa, jota EDA-työkaluissa harvoin on, joten sitä ei
käsitellä.

## Lukuohje

Lue luvut 3 (korvaussäännöt) ja 5 (esitykset ja hinnat) huolella:
niissä on se, mikä Tcl:ssä on aidosti erilaista. Luvut 4 ja 8 näyttävät
omien ohjausrakenteiden ja virhekoodien mallit. Luku 11 kokoaa
EDA-skriptauksen mallit. Lue jokaisen luvun itsearviointi ensin, ja
ohita luku, jos hallitset sen väitteet. Pikaopas kokoaa syntaksin
muutamalle sivulle.
