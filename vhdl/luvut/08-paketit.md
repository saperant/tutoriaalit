# Paketit, funktiot ja proseduurit

Paketti kokoaa yhteiset tyypit, vakiot ja aliohjelmat yhteen
paikkaan, josta suunnitteluyksiköt ottavat ne käyttöön `use`-lauseella.
Hyvin suunnitellut paketit ovat projektin sanasto: väylien tietueet,
rekisterikartan osoitteet, protokollan vakiot ja apufunktiot
määritellään kerran.

## Paketti ja paketin runko

Paketti jakautuu kahteen suunnitteluyksikköön. *Paketin esittely*
on rajapinta: tyypit, vakiot ja aliohjelmien esittelyt. *Paketin
runko* sisältää aliohjelmien toteutukset ja yksityiset apumäärittelyt.
Kun vain runko muuttuu, sitä käyttäviä yksiköitä ei tarvitse
analysoida uudelleen, kuten C:ssä otsikkotiedoston ja
toteutustiedoston ero.

Esimerkkinä on CRC-8-tarkistussumman paketti. Esittely:

```{.vhdl tiedosto="esimerkit/08-crc/crc.vhd" osa="esittely"}
```

Runko:

```{.vhdl tiedosto="esimerkit/08-crc/crc.vhd" osa="runko"}
```

Paketissa on kolme erilaista funktiota. Ensimmäinen `crc8` laskee
yhden tavun askeleen. Sen silmukalla on vakiorajat, joten synteesi
avaa sen kahdeksaksi XOR-portti- ja siirtovaiheeksi: funktio on
pelkkää kombinaatiologiikkaa. Kaksi muuta `crc8`-funktiota
*ylikuormittavat* nimen eri parametrityypeille ja laskevat kokonaisen
viestin CRC:n. Ne ovat testipenkkien malleja, eivät laitteistoa.
Funktio `bitit` laskee tarvittavan bittimäärän. Sen `while`-silmukka
ei ole synteesikelpoista logiikkaa, mutta funktio on sallittu
vakioiden ja leveyksien laskentaan, koska se evaluoidaan elaboroinnissa.

Laskin käyttää pakettia sekä logiikkaan että porttinsa leveyteen:

```{.vhdl tiedosto="esimerkit/08-crc/crc_laskin.vhd" osa="laskin"}
```

Testipenkki vertaa laitteiston tulosta saman paketin malliin ja
lisäksi standardin tarkistusarvoon. Merkkijono `"123456789"` on CRC-
algoritmien vakiintunut testisyöte, ja CRC-8/SMBUS antaa sille arvon
`F4`:

```{.vhdl tiedosto="esimerkit/08-crc/testipenkki.vhd" osa="testi"}
```

```{.tuloste tiedosto="esimerkit/08-crc.odotettu"}
```

Malli ja laitteisto käyttävät tässä samaa askelfunktiota, joten malli
ei löydä virhettä itse askeleesta. Siksi testissä on myös
riippumaton tarkistusarvo. Yleisemmin malli kirjoitetaan eri tavalla
kuin toteutus: eri algoritmilla, eri kielellä tai taulukosta
(*Laitteiston verifiointi*).

## Funktiot

Funktio palauttaa yhden arvon, ei voi odottaa (`wait`) eikä sijoittaa
signaaleihin. Funktio on oletuksena *puhdas* (`pure`): sen tulos riippuu
vain parametreista. Puhdas funktio ei siksi saa lukea signaalia tai
muuttujaa, joka on esitelty sen ulkopuolella:

```{.vhdl tiedosto="esimerkit/08-puhdas.ei-kaanny.vhd" osa="funktio"}
```

GHDL ilmoittaa `reference to port "siirto" violate pure rule for
function "celsius"`. Korjattu malli välittää kalibroinnin funktion
ulkopuolella:

```{.tuloste tiedosto="esimerkit/08-puhdas.odotettu"}
```

Sääntö ei ole pelkkä muodollisuus: funktio, joka lukee piilotetusti
ulkoista tilaa, on vaikea testata ja vaikea ymmärtää, koska sama kutsu
antaa eri tuloksen eri hetkinä. Jos ulkoista tilaa todella tarvitaan,
funktio esitellään `impure`-funktiona, kuten luvun 9 jonon `ota`, joka
muuttaa jonon tilaa.

## Proseduurit

Proseduuri ei palauta arvoa, vaan vaikuttaa parametreihinsa
(`out`, `inout`) tai signaaleihin. Proseduuri saa sisältää `wait`-
lauseita, joten se on testipenkkien perustyökalu: luvun 5
Fletcher-testin `syota`, luvun 6 UART-lähettäjän `laheta` ja tämän
luvun `tarkista` ovat proseduureja, jotka kuvaavat yhden tapahtuman
väylällä.

Prosessin sisällä esitelty proseduuri näkee prosessin signaalit ja voi
sijoittaa niihin suoraan. Paketissa esitelty proseduuri saa
signaalit parametreina (`signal clk : in std_logic`), jolloin samaa
proseduuria voidaan käyttää monessa testipenkissä. Tämä on testipenkkien
uudelleenkäytettävien *väylämallien* (bus functional model, BFM) perusta.

Aliohjelman parametreilla voi olla oletusarvoja, ja kutsussa voi
käyttää nimettyä liitosta: `laheta(x"00", lopetus => '0')`.

## Standardipaketit

| Paketti | Sisältö |
|---------|---------|
| `ieee.std_logic_1164` | `std_ulogic`, `std_logic`, vektorit, loogiset operaattorit |
| `ieee.numeric_std` | `signed`, `unsigned`, aritmetiikka, `resize`, `shift_left` |
| `ieee.fixed_pkg` | VHDL-2008: kiinteän pilkun `sfixed`, `ufixed` (taito *Lukujen esitys ja kiinteän pilkun aritmetiikka*) |
| `ieee.float_pkg` | VHDL-2008: parametroitu liukuluku |
| `ieee.math_real` | `real`-funktiot: `sqrt`, `log2`, `ceil`, `uniform` |
| `std.textio` | rivipohjainen tiedostojen ja tulosteen käsittely |
| `std.env` | VHDL-2008: `stop`, `finish`, `resolution_limit` |

`math_real` ei ole synteesikelpoista logiikkaa, mutta sitä käytetään
vakioiden laskentaan, esimerkiksi `integer(ceil(log2(real(N))))`, ja
testipenkkien satunnaislukuihin.

## Geneeriset paketit

VHDL-2008:ssa myös paketilla voi olla generic-parametreja. `fixed_pkg`
on itse tällainen paketti: `fixed_generic_pkg` instansioidaan
pyöristys- ja ylivuotoasetuksilla. Omat geneeriset paketit sopivat
esimerkiksi tyyppiparametroiduille jonoille ja tulostauluille
testipenkeissä. Synteesityökalujen tuki niille on vielä
vaihtelevaa, joten synteesikoodissa niitä käytetään harkiten.

## Käytännössä

- **Paketti on projektin sanasto.** Väylätietueet, vakiot ja
  rekisterikartta ovat paketissa, eivät kopioina entiteeteissä.
  Rekisterikartta kannattaa generoida samasta lähteestä kuin
  ohjelmiston otsikkotiedosto (esim. SystemRDL).
- **Synteesikelpoiset ja testipenkin aliohjelmat erikseen.**
  Synteesikoodin paketissa on vain synteesikelpoisia funktioita tai
  elaborointiaikana laskettavia apufunktioita. Mallit, tulostaulut ja
  väylämallit ovat omassa simulointipaketissaan.
- **Puhtaat funktiot.** Funktio laskee tuloksen parametreistaan.
  `impure` on poikkeus, joka perustellaan.
- **Funktio silmukalle, joka on logiikkaa.** Bittitason algoritmit,
  kuten CRC, pariteetti ja Gray-koodi, kirjoitetaan funktioiksi, jotta
  sama koodi palvelee laitteistoa ja testipenkin mallia.
- **Analyysijärjestys.** Paketti analysoidaan ennen käyttäjiään.
  Kun paketin esittely muuttuu, kaikki käyttäjät on analysoitava
  uudelleen; käännösjärjestelmä hoitaa tämän riippuvuuksien perusteella.

## Itsearviointi

- Osaat kirjoittaa paketin esittelyn ja rungon ja käyttää niitä
  entiteetissä ja testipenkissä.
- Osaat kirjoittaa synteesikelpoisen funktion, jossa on vakiorajainen
  silmukka, ja kertoa, millaista logiikkaa siitä syntyy.
- Osaat kertoa puhtaan ja epäpuhtaan funktion eron ja proseduurin
  käyttötarkoituksen testipenkeissä.
- Osaat valita oikean standardipaketin kiinteän pilkun laskentaan,
  satunnaislukuihin ja tulostukseen.
