# Syöte, tiedostot ja tekstinkäsittely {.runko-tyypit}

Skriptin data kulkee virtoina: vakiosyöte, vakiotuloste, virhetuloste ja
tiedostot. Tämä luku käy läpi rivien lukemisen, uudelleenohjaukset,
tiedostojen generoinnin ja turvallisen kirjoittamisen sekä työnjaon
Bashin ja `awk`:n välillä.

## Rivien lukeminen

Rivi luetaan idiomilla `while IFS= read -r rivi`. Kumpikin osa on
tarpeen:

- `IFS=` estää `read`-komentoa poistamasta rivin alun ja lopun
  välilyöntejä.
- `-r` estää kenoviivojen tulkinnan; ilman sitä `C:\temp` muuttuisi
  muotoon `C:temp`.

Jos tiedoston viimeiseltä riviltä puuttuu rivinvaihto, `read` lukee sen
mutta palauttaa epätoden, ja silmukka päättyy ennen viimeistä riviä.
Idiomi `while IFS= read -r rivi || [[ -n $rivi ]]` käsittelee myös sen
(esimerkki luvussa 8).

Kun `IFS` asetetaan erottimeksi, `read` jakaa rivin kenttiin. Viimeinen
muuttuja saa rivin loppuosan. Esimerkki lukee tilausrivit CSV-muodossa,
validoi ne ja laskee summat asiakkaittain sentteinä:

```{.bash tiedosto="esimerkit/06-csv.sh" osa="lukeminen"}
```

```{.bash tiedosto="esimerkit/06-csv.sh" osa="tulostus"}
```

Syötteellä

```{.tuloste tiedosto="esimerkit/06-csv.syote"}
```

tuloste on

```{.tuloste tiedosto="esimerkit/06-csv.odotettu"}
```

ja virhetulosteeseen kirjoitetaan `rivi 4 hylätty: T-1004`.

Huomioita:

- Hinta muunnetaan senteiksi poistamalla piste: `12.50` → `1250`.
  Etuliite `10#` estää tulkitsemasta arvoa `0.99` → `099` oktaaliluvuksi.
- Hylätty rivi raportoidaan **virhetulosteeseen**, jotta vakiotuloste
  pysyy puhtaana dataa jatkokäsittelevälle ohjelmalle.
- Tämä jäsennin ei tue lainausmerkeissä olevia pilkkuja (`"Oy, Ab"`).
  Oikean CSV:n jäsentämiseen käytetään Pythonin `csv`-moduulia tai
  työkalua kuten `mlr` (Miller). Tämä on tyypillinen raja, jossa Bash
  loppuu.

## Uudelleenohjaukset

| Merkintä | Merkitys |
|----------|----------|
| `> t`, `>> t` | vakiotuloste tiedostoon, korvaten tai lisäten |
| `2> t` | virhetuloste tiedostoon |
| `> t 2>&1` | molemmat samaan tiedostoon (järjestys ratkaisee) |
| `&> t` | sama lyhyemmin (Bash) |
| `>&2` | vakiotuloste virhetulosteeseen: virheilmoitukset |
| `< t` | vakiosyöte tiedostosta |
| `<<< "$x"` | here-merkkijono: muuttuja vakiosyötteeksi |
| `< <(komento)` | prosessikorvaus: komennon tuloste tiedostona |
| `exec 3> t` | avaa tiedostokuvaajan 3 koko skriptin ajaksi |
| `exec {fd}> t` | avaa vapaan kuvaajan ja tallentaa numeron (4.1) |

Uudelleenohjaukset käsitellään vasemmalta oikealle. `komento > t 2>&1`
ohjaa ensin tulosteen tiedostoon ja sitten virhetulosteen samaan paikkaan.
Järjestys `2>&1 > t` ohjaisi virhetulosteen sinne, missä vakiotuloste
*oli*, eli päätteeseen.

## Tiedostojen generointi

Here-dokumentti `<<MERKKI` syöttää monirivisen tekstin komennolle. Kun
merkki on lainaamaton, tekstissä tehdään laajennukset; lainattuna
(`<<'MERKKI'`) teksti säilyy sellaisenaan. Lainattu muoto on oikea, kun
generoitavassa tiedostossa itsessään on `$`-merkkejä, kuten
skripteissä.

```{.bash tiedosto="esimerkit/06-heredoc.sh" osa="laajentuva"}
```

```{.bash tiedosto="esimerkit/06-heredoc.sh" osa="kirjaimellinen"}
```

Here-merkkijono `<<<` on yksirivinen vastine:

```{.bash tiedosto="esimerkit/06-heredoc.sh" osa="merkkijono"}
```

```{.tuloste tiedosto="esimerkit/06-heredoc.odotettu"}
```

Muoto `<<-MERKKI` poistaa rivien alusta sarkaimet, ei välilyöntejä.
Koska sisennys sarkaimilla on hauras, tämä tutoriaali kirjoittaa
here-dokumentit sisentämättä.

## Atominen kirjoitus

Kun palvelu lukee asetustiedostoa, se ei saa koskaan nähdä puoliksi
kirjoitettua tiedostoa. `komento > asetukset.ini` katkaisee tiedoston
heti ja kirjoittaa sen uudelleen vähitellen; jos komento epäonnistuu
kesken, tiedosto jää vajaaksi.

Ratkaisu on **kirjoita–nimeä uudelleen** -malli: kirjoitetaan
väliaikaistiedostoon *samassa hakemistossa* ja nimetään se kohteen päälle.
Uudelleennimeäminen saman tiedostojärjestelmän sisällä on atominen, joten
lukija näkee joko vanhan tai uuden version.

```{.bash tiedosto="esimerkit/06-atominen.sh" osa="funktio"}
```

```{.bash tiedosto="esimerkit/06-atominen.sh" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-atominen.odotettu"}
```

`mktemp` luo tiedoston, jonka nimi on arvaamaton ja jonka oikeudet ovat
0600. Arvattava nimi kuten `/tmp/skripti.$$` on tietoturva-aukko: toinen
käyttäjä voi luoda samannimisen symbolisen linkin etukäteen. Koska
`mktemp` antaa tiedostolle oikeudet 0600, funktio asettaa lopulliset
oikeudet ennen nimeämistä.

## Työnjako awkin kanssa

Bash-silmukka on hidas, koska jokainen kierros tulkitaan erikseen ja
ulkoiset komennot käynnistävät prosessin. `awk` käsittelee kaikki rivit
yhdessä prosessissa ja tuntee kentät, assosiatiiviset taulukot ja
liukuluvut. Raja kulkee näin: Bash ohjaa työtä (tiedostot, komennot,
virheet), ja `awk` käsittelee rivit.

Esimerkki laskee vasteaikojen keskiarvon ja virheiden määrän polku
kerrallaan:

```{.bash tiedosto="esimerkit/06-awk.sh" osa="awk"}
```

```{.tuloste tiedosto="esimerkit/06-awk.odotettu"}
```

`awk`-ohjelma on yksinkertaisissa lainausmerkeissä, jotta Bash ei laajenna
sen `$`-viittauksia. Bashin muuttujat välitetään valitsimella `-v`.
Koska `awk`:n `for (avain in taulu)` -järjestys on määrittelemätön,
tuloste lajitellaan.

## Käytännössä

- **`while IFS= read -r`** rivien lukemiseen, ja `|| [[ -n $rivi ]]`,
  jos viimeinen rivinvaihto voi puuttua.
- **Validoi jokainen kenttä** ennen käyttöä ja raportoi hylätyt rivit
  virhetulosteeseen rivinumeron kanssa.
- **Data vakiotulosteeseen, viestit virhetulosteeseen.** Tämä tekee
  skriptistä putkeen sopivan Unix-työkalun.
- **Kirjoita–nimeä uudelleen** aina, kun toinen prosessi voi lukea
  tiedostoa kirjoituksen aikana: asetukset, tilatiedostot, julkaisut.
- **`mktemp`, ei arvattavia nimiä**, ja siivous `trap`-ansalla
  (luku 7).
- **Lainattu here-dokumentti** generoitaessa skriptejä tai tiedostoja,
  joissa on `$`-merkkejä.
- **awk riveille, Bash ohjaukselle.** Kun silmukassa on enemmän kuin
  satoja kierroksia ja jokaisella kutsutaan ulkoista komentoa, työ
  siirretään yhteen `awk`- tai `sed`-ajoon.
- **Tunne jäsentimen rajat.** Lainatut CSV-kentät, JSON ja XML kuuluvat
  työkaluille (`mlr`, `jq`, `xmlstarlet`) tai toiselle kielelle.

## Itsearviointi

- Osaat lukea tiedoston riveittäin niin, että välilyönnit, kenoviivat
  ja puuttuva viimeinen rivinvaihto käsitellään oikein.
- Osaat jakaa rivin kenttiin `IFS`:n ja `read`:n avulla ja validoida
  kentät.
- Osaat selittää, miksi `2>&1`:n paikka uudelleenohjauksissa ratkaisee.
- Osaat päivittää tiedoston atomisesti `mktemp`:n ja `mv`:n avulla.
- Osaat siirtää rivikohtaisen laskennan `awk`:lle ja välittää sille
  Bashin muuttujia.
