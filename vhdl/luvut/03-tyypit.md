# Tyypit ja vahva tyypitys

VHDL on vahvasti tyypitetty kieli. Jokaisella arvolla on tyyppi,
eikä tyypistä toiseen muunneta koskaan huomaamatta: bittivektoria ei
voi laskea yhteen kokonaisluvun kanssa, eikä 8-bittistä arvoa voi
sijoittaa 9-bittiseen signaaliin. Tämä tuntuu aluksi kankealta, mutta
se siirtää suuren joukon virheitä simuloinnista ja laboratoriosta
käännösvaiheeseen. Verilogissa samat virheet ovat hiljaisia
katkaisuja ja laajennuksia.

## Skalaarityypit

| Tyyppi | Arvot | Käyttö |
|--------|-------|--------|
| `boolean` | `false`, `true` | ehdot, liput mallin sisällä |
| `integer` | vähintään 32-bittinen (VHDL-2019: 64) | laskurit, indeksit, generic-parametrit |
| `natural`, `positive` | `integer`in alityypit: vähintään 0 ja vähintään 1 | koot ja laskurit |
| luettelotyyppi | omat nimet, esim. `(LEPO, DATA)` | tilakoneet, operaatiokoodit |
| `real` | liukuluku | vain simulointi ja vakioiden laskenta |
| `time` | fysikaalinen tyyppi: `fs`, `ns`, `us` ... | viiveet testipenkeissä |
| `character`, `string` | merkki, merkkijono | tulosteet ja tiedostot |

Kokonaisluvulle annetaan yleensä arvoalue: `signal laskuri : natural
range 0 to 999`. Synteesi päättelee alueesta bittimäärän (tässä 10),
ja simulaattori tarkistaa, ettei arvo karkaa alueelta. Ylivuoto ei
siis kierrä hiljaa ympäri kuten vektorissa, vaan pysäyttää simuloinnin.
Jos kiertämistä halutaan, se kirjoitetaan näkyviin tai käytetään
`unsigned`-tyyppiä.

## std_logic ja std_ulogic

Paketin `std_logic_1164` tyyppi `std_ulogic` kuvaa yhtä johdinta
yhdeksällä arvolla:

| Arvo | Merkitys | Arvo | Merkitys |
|------|----------|------|----------|
| `'U'` | alustamaton | `'Z'` | korkeaimpedanssinen (kolmitila) |
| `'X'` | tuntematon, ristiriita | `'W'` | heikko tuntematon |
| `'0'` | vahva nolla | `'L'` | heikko nolla (alasvetovastus) |
| `'1'` | vahva ykkönen | `'H'` | heikko ykkönen (ylösvetovastus) |
| `'-'` | yhdentekevä (synteesille) | | |

Synteesi tuottaa vain nollia ja ykkösiä. Muut arvot ovat simuloinnin
apuvälineitä: `'U'` paljastaa alustamattoman rekisterin ja `'X'`
ristiriidan tai tuntemattomasta lasketun tuloksen.

`std_logic` on `std_ulogic`in *ratkaistu* alityyppi. Ratkaistulla
signaalilla saa olla useita ajureita, ja *ratkaisufunktio* laskee
niiden yhteisarvon. Seuraava testipenkki ajaa samaa johtoa kahdella
sijoituksella ja tulostaa tuloksen kaikille arvopareille:

```{.vhdl tiedosto="esimerkit/03-ratkaisu.vhd" osa="ajurit"}
```

```{.tuloste tiedosto="esimerkit/03-ratkaisu.odotettu"}
```

Taulukosta näkyy kolme sääntöä. `'Z'` väistyy kaiken tieltä, eli
irti oleva ajuri ei vaikuta tulokseen. Vahva arvo voittaa heikon:
ylösvetovastus `'H'` ja ajuri `'0'` antavat `'0'`. Kaksi erisuuntaista
vahvaa ajuria antaa `'X'`:n, joka piirissä olisi oikosulku.

Ratkaisu on tarpeen kolmitilaväylille, mutta piirin sisällä useampi
ajuri on aina virhe. Seuraavassa esimerkissä varaustilaa ohjaa
vahingossa kaksi lausetta:

```{.vhdl tiedosto="esimerkit/03-ajurit.kaatuu.vhd" osa="ajurit"}
```

Malli kääntyy, ja simulointi kaatuu vasta testipenkin tarkistukseen:

```{.tuloste tiedosto="esimerkit/03-ajurit.virhe"}
```

Jos signaali olisi `std_ulogic`, elaborointi pysähtyisi heti
virheeseen `too many drivers for signal "varattu"`. Siksi osa
suunnittelijoista ja tyylioppaista käyttää sisäisille signaaleille
tyyppiä `std_ulogic` ja `std_ulogic_vector`. VHDL-2008:ssa
`std_logic_vector` on `std_ulogic_vector`in alityyppi, joten
tyypit sopivat yhteen ilman muunnoksia. Kumpi tahansa valinta on
hyvä, kunhan se on johdonmukainen; tämä tutoriaali käyttää yleisempää
`std_logic`ia.

## Vektorit, viipaleet ja koosteet

`std_logic_vector(7 downto 0)` on kahdeksan bitin taulukko, jonka
vasen bitti on 7. Järjestyksellä `downto` eniten merkitsevä bitti on
vasemmalla, kuten luvuissa kirjoitetaan; `to` on tavallisempi
muistitaulukoille. Tärkeimmät operaatiot:

| Merkintä | Merkitys |
|----------|----------|
| `v(7 downto 4)` | viipale (slice) |
| `a & b` | liitos (concatenation) |
| `(others => '0')` | kooste: kaikki bitit nollaksi leveydestä riippumatta |
| `(7 => '1', others => '0')` | nimetty kooste |
| `x"F6"`, `b"1111_0110"`, `o"366"` | bittijonovakiot |
| `12x"800"`, `8d"246"`, `8sx"F"` | VHDL-2008: leveys, desimaali, etumerkin laajennus |
| `v'length`, `v'range`, `v'high` | attribuutit: pituus, indeksialue, suurin indeksi |

Attribuutit tekevät koodista leveydestä riippumatonta: `for i in
v'range loop` ja `(others => '0')` toimivat, vaikka vektorin leveys
muuttuu.

## numeric_std: signed ja unsigned

`std_logic_vector` on pelkkä joukko bittejä ilman lukuarvoa.
Aritmetiikkaa varten paketti `ieee.numeric_std` määrittelee kaksi
samanlaista vektorityyppiä: `unsigned` (etumerkitön) ja `signed`
(kahden komplementti). Niille on määritelty `+`, `-`, `*`, vertailut,
siirrot ja `resize`, myös yhdessä `integer`in kanssa.

Vanhoissa malleissa näkyy Synopsysin paketteja `std_logic_arith`,
`std_logic_unsigned` ja `std_logic_signed`. Ne eivät ole IEEE:n
standardeja, ja `std_logic_unsigned` tulkitsee *kaikki* vektorit
etumerkittömiksi koko tiedostossa. Uudessa koodissa käytetään vain
`numeric_std`:tä. VHDL-2008:n `numeric_std_unsigned` on standardi
mutta kantaa saman ongelman: lukija ei näe tyypistä, onko vektori
luku.

Tyyppien välillä liikutaan kahdella tavalla. Samankaltaiset
taulukkotyypit, kuten `std_logic_vector`, `unsigned` ja `signed`,
muunnetaan *tyyppimuunnoksella* (`unsigned(v)`), joka ei muuta bittejä.
Kokonaisluvun ja vektorin välillä tarvitaan *muunnosfunktio*, joka
tietää leveyden ja etumerkin:

| Mistä → mihin | Lauseke |
|---------------|---------|
| `std_logic_vector` → `unsigned` / `signed` | `unsigned(v)`, `signed(v)` |
| `unsigned` / `signed` → `std_logic_vector` | `std_logic_vector(u)` |
| `unsigned` / `signed` → `integer` | `to_integer(u)` |
| `integer` → `unsigned` | `to_unsigned(i, leveys)` |
| `integer` → `signed` | `to_signed(i, leveys)` |
| `std_logic_vector` → `integer` | `to_integer(unsigned(v))` tai `to_integer(signed(v))` |
| leveyden muutos | `resize(u, leveys)`; `signed` laajenee etumerkillä |

Kun vektori muunnetaan luvuksi, kirjoittaja päättää, onko se
etumerkillinen. Tämä on vahvan tyypityksen hyöty: sama bittikuvio
`x"F6"` on `unsigned`ina 246 ja `signed`inä −10, ja koodista näkee,
kumpaa tarkoitetaan.

Seuraavassa esimerkissä osoitelaskuri on `unsigned`, mutta väylän
osoite on `std_logic_vector`. Suora sijoitus ei käänny:

```{.vhdl tiedosto="esimerkit/03-osoite.ei-kaanny.vhd" osa="virhe"}
```

GHDL ilmoittaa `can't match "laskuri" with type array type
"STD_ULOGIC_VECTOR"`. Korjattu rivi tekee muunnoksen näkyväksi:

```{.tuloste tiedosto="esimerkit/03-osoite.odotettu"}
```

## Leveydet aritmetiikassa

`numeric_std`:n laskutoimitusten tuloksen leveys on kiinteä:

| Operaatio | Tuloksen leveys |
|-----------|-----------------|
| `a + b`, `a - b` | leveämmän operandin leveys; kanto katoaa |
| `a + 1` (kokonaisluku) | `a`:n leveys |
| `a * b` | leveyksien summa |
| `resize(a, n)` | `n`; `signed` laajennetaan etumerkillä |
| vertailut `<`, `=` | `boolean`; operandit voivat olla eri levyisiä |

Kanto ei siis synny itsestään. Kun summa sijoitetaan bitin
leveämpään signaaliin, leveydet eivät täsmää:

```{.vhdl tiedosto="esimerkit/03-leveys.kaatuu.vhd" osa="summa"}
```

Virhe havaitaan simuloinnissa heti ensimmäisellä sijoituksella:

```{.tuloste tiedosto="esimerkit/03-leveys.virhe"}
```

Korjaus on laajentaa operandi ennen laskua: `resize(a, 9) + b` tai
`('0' & a) + b`. Tällöin kanto on tuloksen ylin bitti. Osa
työkaluista havaitsee leveysvirheen jo elaboroinnissa, GHDL vasta
simuloinnissa. Siksi jokainen lohko simuloidaan ainakin kerran ennen
synteesiä.

Kaksi muuta sudenkuoppaa:

- `resize` kaventaa `signed`-arvon säilyttämällä etumerkkibitin ja
  alimmat bitit. Liian suuri arvo ei siis kyllästy, vaan muuttuu
  toiseksi luvuksi. Kavennus tehdään vasta, kun arvon tiedetään
  mahtuvan, kuten seuraavan esimerkin kyllästyksessä.
- `to_unsigned(300, 8)` katkaisee arvon ja antaa simuloinnissa vain
  varoituksen `vector truncated`. Varoitukset kannattaa lukea.

## Omat tyypit ja tietueet

Luettelotyyppi (`type tila_t is (LEPO, DATA)`), taulukkotyyppi ja
tietue (`record`) ryhmittelevät dataa. Alityyppi (`subtype tavu_t is
std_logic_vector(7 downto 0)`) antaa nimen rajatulle tyypille ilman
uutta tyyppiä, joten se sopii yhteen perustyyppinsä kanssa.

Tietue yhdistää toisiinsa liittyvät signaalit. Porteissa käytettävä
tyyppi esitellään paketissa, jotta sekä entiteetti että sen käyttäjä
näkevät sen:

```{.vhdl tiedosto="esimerkit/03-naytteet.vhd" osa="paketti"}
```

Esimerkin sovitin ottaa 12-bittisen AD-muuntimen näytteen, joka on
offset-binääriä (0x800 on nolla), muuntaa sen kahden komplementiksi,
vahvistaa sitä ja kyllästää tuloksen 16 bittiin:

```{.vhdl tiedosto="esimerkit/03-naytteet.vhd" osa="sovitin"}
```

Esimerkissä näkyvät tyypillinen muunnosketju ja leveyksien hallinta.
Ylimmän bitin kääntäminen muuntaa offset-binäärin kahden
komplementiksi, ja tyyppimuunnos `signed(...)` kertoo, miten bitit
tulkitaan. Tulo on leveyksien summan levyinen, 20 bittiä, joten
kertolasku ei vuoda yli. Vertailu kokonaislukuun tehdään täydellä
leveydellä, ja vasta sen jälkeen `resize` kaventaa arvon, joka tiedetään
mahtuvaksi. Välitulokset ovat prosessin muuttujia, joista lisää
luvussa 5.

```{.vhdl tiedosto="esimerkit/03-naytteet.vhd" osa="testipenkki"}
```

```{.tuloste tiedosto="esimerkit/03-naytteet.odotettu"}
```

Tietueen kenttiä sijoitetaan erikseen (`ulos.arvo <= ...`) tai
kerralla koosteella (`ulos <= (arvo => x, kyllastyi => '0')`).
VHDL-2008 sallii tietueeseen myös rajoittamattomia kenttiä, joiden
leveys kiinnitetään signaalin esittelyssä.

## Tekstimuunnokset

VHDL-2008 lisäsi kaikille perustyypeille funktion `to_string` sekä
vektoreille `to_hstring` (heksadesimaali) ja `to_ostring`. Kokonaisluku
muunnetaan myös attribuutilla `integer'image(i)` ja luettelotyypin arvo
`tila_t'image(t)`. Niitä käytetään testipenkkien tulosteissa ja
`assert`-viesteissä.

## Käytännössä

- **Tyyppi kertoo merkityksen.** Rajapinnoissa `std_logic_vector`
  on bittijoukko, `unsigned` ja `signed` ovat lukuja, ja `natural
  range` on laskuri tai indeksi. Muunnokset tehdään rajapinnan
  reunalla kerran, ei jokaisessa lausekkeessa.
- **Vain `numeric_std`.** Ei `std_logic_arith`-, `std_logic_unsigned`-
  tai `std_logic_signed`-paketteja. Kun niitä löytyy vanhasta
  koodista, ne poistetaan koodin muun muokkauksen yhteydessä.
- **Leveys on suunnittelupäätös.** Summan kanto ja tulon leveys
  lasketaan auki, ja kavennus tehdään vasta, kun arvon tiedetään
  mahtuvan tai kun ylivuoto on käsitelty (kyllästys tai kierto).
- **Rajattu kokonaisluku laskuriksi.** `natural range 0 to N - 1`
  dokumentoi arvoalueen, ja simulaattori valvoo sitä. Vektori sopii
  silloin, kun bittitason käsittelyä tai kiertoa tarvitaan.
- **`std_ulogic` tai `std_logic`, johdonmukaisesti.** Ratkaisematon
  tyyppi löytää moninkertaiset ajurit elaboroinnissa; ratkaistu
  tyyppi on yleisempi ja yhteensopiva IP-lohkojen kanssa. Kolmitila
  (`'Z'`) kuuluu vain piirin nastoihin.
- **`'-'` ei ole vertailun jokerimerkki.** `v = "1--"` vertaa
  kirjaimellisesti merkkiin `'-'`. Yhdentekeviä bittejä verrataan
  VHDL-2008:n operaattorilla `?=` tai `std_match`-funktiolla.

## Itsearviointi

- Osaat valita `std_logic_vector`in, `unsigned`in, `signed`in ja
  rajatun kokonaisluvun välillä ja muuntaa niiden välillä.
- Osaat laskea yhteen- ja kertolaskun tuloksen leveyden ja säilyttää
  kannon.
- Osaat kertoa, mitä ratkaistu tyyppi tarkoittaa ja miksi kaksi ajuria
  näkyy `std_logic`-signaalissa arvona `'X'`.
- Osaat määritellä paketissa tietueen ja käyttää sitä porttina.
