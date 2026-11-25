# Lopuksi: käytännöt ja lähteet {.runko-kaytannot .runko-lahteet}

## Idiomit ja mallit

| Malli | Tcl:ssä | Luku |
|-------|---------|------|
| Komento listana | `set k [list komento $a $b]`, ajo `{*}$k` | 3 |
| Nimetyt valitsimet | oletukset `dict merge` -komennolla, tuntemattomat hylätään | 4 |
| Viittausparametri | `upvar 1 $nimi muuttuja` | 4 |
| Oma ohjausrakenne | `uplevel 1 $runko` ja paluukoodien välitys | 4 |
| K-yhdistelmä | `[lreplace $l[set l {}] …]` muokkaa paikallaan | 5 |
| Koristele, lajittele, riisu | `lmap` avaimeksi, `lsort -index 0` | 6, 11 |
| Taulukko nimellä | `upvar 1 $nimi t`, muunnos `array get` | 6 |
| Johdettu tieto | summat lasketaan tarvittaessa, ei tallenneta | 6 |
| Resurssin vapautus | `try {…} finally {close $f}` | 8 |
| Virheluokka | `throw {LUOKKA ALALUOKKA tieto} viesti`, `trap` | 8 |
| Komentokokoelma | `namespace ensemble create` | 9 |
| Atominen kirjoitus | väliaikaistiedosto ja `file rename -force` | 9 |
| Rinnakkaiset ajot | putki `open`-komennolla, `fileevent`, `vwait` | 10 |
| Generaattori | `coroutine`, `yield` | 10 |
| Tilakonejäsennin | `switch -regexp -matchvar`, yhteenvedon tarkistus | 11 |
| Turvallinen lapsitulkki | `interp create -safe`, `interp alias` | 11 |
| Ohut työkalukerros | logiikka testattavina proseduureina | 11, 12 |

## Nyrkkisäännöt

1. **Aaltosulkeet lausekkeisiin ja runkoihin.** `expr {…}`, `if {…}`.
2. **Listat ja komennot `list`-komennolla,** ei merkkijonoja liimaamalla.
3. **Pinninimet aaltosulkeisiin tai muuttujiin,** ei lainausmerkkeihin.
4. **`eq` merkkijonoille, `==` luvuille.**
5. **`scan $x %d`** ulkoiselle luvulle, jossa voi olla etunolla.
6. **Logiikka proseduureihin ja nimiavaruuksiin,** ei päätasolle.
7. **Virhekoodi jokaiseen virheeseen,** käsittely `trap`-haaroilla.
8. **Ei tyhjää `catch`-komentoa.** Tuntematon virhe eteenpäin.
9. **Merkistö ja polut eksplisiittisesti:** `fconfigure -encoding
   utf-8`, polut `info script`-komennon suhteen.
10. **Paluuarvo kertoo tuloksen** CI:lle ja Makelle.
11. **Testaa logiikka tclsh:lla,** tarkista koodi staattisesti.
12. **Siirrä työ Pythoniin,** kun skripti ei enää ohjaa työkalua vaan
    käsittelee dataa: tilastot, tietokannat, verkkopalvelut ja laajat
    tietorakenteet.

## Tcl 9.0

Tcl 9.0 julkaistiin syyskuussa 2024. EDA-työkalut siirtyvät siihen
hitaasti, mutta uusi koodi kannattaa kirjoittaa toimimaan molemmissa.
Merkittävimmät muutokset:

- Nollalla alkava luku ei ole enää oktaaliluku; oktaalit kirjoitetaan
  `0o17`.
- Tiedostojen merkistövirheet ovat oletuksena virheitä (`-profile
  strict`), ei hiljaa korvattuja merkkejä.
- Tilde `~` ei laajene kotihakemistoksi tiedostokomennoissa; käytä
  `file home` tai `file tildeexpand`.
- Uusia komentoja: `dict getdef`, `lseq`, `lpop`, `ledit`, `string
  insert`.
- Merkkijonojen ja listojen enimmäiskoko kasvoi 64-bittiseksi.

## Jatkotaidot

- *EDA-työkaluketjujen automatisointi*: Tcl-skriptit osana kulkua,
  jota ohjataan Pythonilla, Makella ja CI:llä.
- *RTL-suunnittelu SystemVerilogilla*, *FPGA-toteutus* ja
  *ASIC-toteutus*: työkalut, joita Tcl:llä ohjataan, ja rajoitteet,
  joita sillä kirjoitetaan.
- *Python työkaluohjelmointiin*: raporttien ja tulosten käsittely
  työkalun ulkopuolella.
- *Tekninen dokumentaatio*: skriptikirjaston ja kulun dokumentointi.

## Lähteet ja jatkolukeminen

- **Tcl:n dokumentaatio** (<https://www.tcl-lang.org/man/tcl8.6/>):
  käsikirjasivut, mukaan lukien `Tcl(n)` (Dodekalogi). Sama
  dokumentaatio on komennolla `man n komento`.
- **Tcl Developer Xchange** (<https://www.tcl-lang.org/>): julkaisut,
  TIP-ehdotukset ja muutoslistat, mm. Tcl 9.0:n muutokset.
- **Tcler's Wiki** (<https://wiki.tcl-lang.org/>): yhteisön laaja
  tietopankki. Sivut *Tcl performance*, *Shimmering*, *K* ja
  *Brace your expr-essions* täydentävät lukua 5.
- **Tcllib** (<https://core.tcl-lang.org/tcllib/>): vakiokirjaston
  täydennys.
- **Kirjat:** John Ousterhoutin ja Ken Jonesin *Tcl and the Tk Toolkit*
  (2. painos, 2009) on kielen tekijän kirjoittama perusteos. Brent
  Welchin, Ken Jonesin ja Jeffrey Hobbsin *Practical Programming in
  Tcl and Tk* (4. painos) kattaa kielen laajasti.
- **EDA-työkalujen Tcl-oppaat:** valmistajien omat käyttöoppaat
  (esim. AMD:n *Vivado Design Suite Tcl Command Reference* ja
  *Using Tcl Scripting* -opas, Alteran *Quartus Prime Scripting*) ja
  avoimen OpenROAD-projektin dokumentaatio
  (<https://openroad.readthedocs.io/>).

### Työkalut

- **Nagelfar** (<https://nagelfar.sourceforge.net/>): staattinen
  tarkistin.
- **tclint** (<https://github.com/nmoroze/tclint>): tarkistin ja
  muotoilija.
- **tkcon** (<https://tkcon.sourceforge.net/>): interaktiivinen konsoli.
