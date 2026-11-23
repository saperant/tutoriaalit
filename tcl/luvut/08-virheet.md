# Virheenkäsittely {.runko-virheet}

Tcl:n virhe on paluukoodi 1, jonka mukana kulkee viesti ja
valintasanakirja. Valinnoista tärkeimmät ovat `-errorcode`, koneluettava
virheen luokka, ja `-errorinfo`, pinojälki. Virhe kulkee ylöspäin,
kunnes `catch` tai `try` pysäyttää sen. Muuten tclsh päättyy
paluuarvolla 1, mikä on CI-ajossa oikea toiminta.

## Virheen heittäminen

- `error viesti` heittää virheen ilman koodia (`-errorcode NONE`).
- `throw {LUOKKA ALALUOKKA tieto} viesti` heittää virheen koodin kanssa.
  Koodi on lista yleisimmästä tarkimpaan, samaan tapaan kuin Tcl:n
  omat koodit `POSIX ENOENT …`, `ARITH DIVZERO …` ja `CHILDSTATUS pid
  koodi`.
- `return -code error -errorcode … viesti` heittää virheen kutsujan
  kohdalta (luku 4).

```{.tcl tiedosto="esimerkit/08-virheet.tcl" osa="heitto"}
```

`try … finally` sulkee tiedoston myös virheen sattuessa. Se on Tcl:n
vastine Pythonin `with`-lauseelle ja C++:n RAII:lle.

## Virheen käsittely: `try`

`try` valitsee haaran virhekoodin alun mukaan (`trap`) tai paluukoodin
mukaan (`on error`, `on break` …). Haara saa viestin ja valinnat
muuttujiin. Tuntematon virhe heitetään eteenpäin
`return -options`-komennolla, jolloin alkuperäinen koodi ja pino
säilyvät. Pinoon voi lisätä kontekstia:

```{.tcl tiedosto="esimerkit/08-virheet.tcl" osa="try"}
```

```{.tcl tiedosto="esimerkit/08-virheet.tcl" osa="kaytto"}
```

## `catch` ja paluukoodit

`catch` on vanhempi ja yleiskäyttöisempi: se palauttaa minkä tahansa
paluukoodin, ja valinnat saa kolmanteen muuttujaan. Sitä tarvitaan
omissa ohjausrakenteissa (luku 4) ja vanhoissa tulkeissa, joissa ei ole
`try`-komentoa.

```{.tcl tiedosto="esimerkit/08-virheet.tcl" osa="koodit"}
```

```{.tuloste tiedosto="esimerkit/08-virheet.odotettu"}
```

## Pinojälki

Käsittelemätön virhe tulostaa `errorInfo`-pinon: virheen aiheuttanut
komento ja jokainen kutsutaso riveineen.

```{.tcl tiedosto="esimerkit/08-pino.kaatuu.tcl"}
```

Virhetulosteen olennaiset rivit:

```{.tuloste tiedosto="esimerkit/08-pino.virhe"}
```

Pino luetaan ylhäältä alas: virhe syntyi `dict get` -komennossa
proseduurin `lue_jakso` toisella rivillä, jota kutsuttiin proseduurista
`taajuus_mhz`. Sama tieto on muuttujassa `::errorInfo` ja valinnassa
`-errorinfo`.

## Virheet EDA-työkaluissa

EDA-työkalut käyttävät virheiden lisäksi omia viestijärjestelmiään:
komento voi onnistua Tcl:n mielestä, mutta kirjata varoituksen tai
kriittisen varoituksen lokiin. Siksi skriptin on tarkistettava myös
komennon tulos (tyhjä haku, nolla osumaa) ja lopuksi viestien määrät.
Luku 11 näyttää mallin, jossa tarkistus ja paluuarvo kootaan yhteen.

## Käytännössä

- **Virhekoodi jokaiseen omaan virheeseen.** Käsittely valitsee koodin,
  ei viestin, perusteella. Viesti on ihmiselle ja voi muuttua.
- **Käsittele vain odotetut virheet.** `trap` tietylle koodille; muut
  heitetään eteenpäin `return -options`-komennolla. Pelkkä
  `catch {…}` ilman tarkistusta on virhe, joka piilottaa toisen
  virheen.
- **`try … finally` resursseille:** tiedostot, väliaikaiset
  hakemistot, työkalun avoimet projektit.
- **Lisää kontekstia, älä korvaa virhettä.** Liitä tieto
  `-errorinfo`-pinoon tai viestiin, mutta säilytä alkuperäinen koodi.
- **Päätä skripti nollasta poikkeavalla paluuarvolla** (`exit 1`), kun
  tulos ei kelpaa. CI ja Make luottavat paluuarvoon.

## Itsearviointi

- Osaat heittää virheen virhekoodin kanssa ja käsitellä sen
  `try`/`trap`-rakenteella.
- Osaat välittää tuntemattoman virheen eteenpäin niin, että koodi ja
  pino säilyvät.
- Osaat lukea `errorInfo`-pinon ja paikantaa virheen.
- Osaat varmistaa resurssin vapauttamisen `try … finally`
  -rakenteella.
