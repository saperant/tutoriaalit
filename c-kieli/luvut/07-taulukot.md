# Taulukot ja merkkijonot {.runko-kokoelmat}

Taulukko on C:n ainoa sisäänrakennettu kokoelma, ja merkkijonokin on
vain merkkitaulukko, jonka loppu on merkitty. Kumpikaan ei tunne omaa
pituuttaan, kun se välitetään funktiolle. Tässä luvussa käydään läpi,
miten taulukoita ja merkkijonoja käsitellään niin, että pituus kulkee
mukana ja rajat pysyvät ehjinä.

## Taulukot

Taulukko on kiinteän kokoinen jono samantyyppisiä alkioita, jotka ovat
muistissa peräkkäin. Koko on osa taulukon tyyppiä. Taulukon voi
alustaa aaltosulkein; puuttuvat alkiot saavat arvon nolla. C99:n
nimetyillä alustimilla voi alustaa yksittäisiä alkioita:

```{.c tiedosto="esimerkit/07-taulukot.c" osa="alustus"}
```

Taulukon pituuden voi laskea `sizeof`-operaattorilla. Laskutoimitus
kirjoitetaan usein makroksi:

```{.c tiedosto="esimerkit/07-taulukot.c" osa="pituus"}
```

Indeksejä ei tarkisteta. Lukeminen tai kirjoittaminen taulukon rajojen
ulkopuolelle on määrittelemätöntä käyttäytymistä: ohjelma voi kaatua,
toimia väärin tai näyttää toimivan oikein. Tällaiset *puskurin
ylivuodot* ovat historiallisesti yleisin C-ohjelmien tietoturva-aukkojen
lähde. AddressSanitizer havaitsee ne testauksessa.

### Taulukot funktion parametreina

Taulukkoa ei voi välittää funktiolle arvona. Parametri `double t[]`
tarkoittaa samaa kuin `double *t`: funktio saa osoittimen ensimmäiseen
alkioon eikä tiedä taulukon kokoa. Koko on siksi välitettävä erillisenä
parametrina, ja `PITUUS`-makro ei toimi funktion sisällä.

```{.c tiedosto="esimerkit/07-taulukot.c" osa="parametri"}
```

Kaksiulotteinen taulukko on taulukko taulukoita. Kun sitä käsittelevä
funktio ottaa mitat parametreina, ne voi käyttää parametrin tyypissä
(*variably modified type*). Näin indeksointi `m[i][j]` toimii minkä
tahansa kokoiselle matriisille:

```{.c tiedosto="esimerkit/07-taulukot.c" osa="matriisi"}
```

```{.c tiedosto="esimerkit/07-taulukot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-taulukot.odotettu"}
```

C99 salli myös *muuttuvanpituiset taulukot* (VLA), joiden koko
määräytyy ajoaikana, esimerkiksi `int t[n]`. Ne varataan pinosta, eikä
liian suuren taulukon varaamista voi havaita, joten niitä kannattaa
välttää. Dynaaminen muistinvaraus käsitellään seuraavassa luvussa.

## Merkkijonot

C:ssä ei ole merkkijonotyyppiä. Merkkijono on `char`-taulukko, jonka
lopussa on *päättävä nollamerkki* `'\0'`. Kaikki merkkijonofunktiot
etsivät merkkijonon lopun nollamerkin avulla, joten sen puuttuminen
johtaa lukemiseen taulukon ohi.

```{.c tiedosto="esimerkit/07-merkkijonot.c" osa="perusteet"}
```

`strlen` laskee merkit ilman nollamerkkiä, kun taas `sizeof` antaa
taulukon koon nollamerkki mukaan lukien. Huomaa, että `strlen` laskee
*tavuja*: UTF-8-koodatussa tekstissä ä-kirjain vie kaksi tavua.

Merkkijonoliteraali, kuten `"vakio"`, sijaitsee muistissa, jota ei saa
muuttaa. Osoitin literaaliin kannattaa siksi esitellä tyypillä
`const char *`. Sen sijaan `char t[] = "..."` luo muutettavan taulukon,
johon literaali kopioidaan.

```{.dot otsikko="Taulukko `tervehdys` sisältää merkit itse, nollamerkki mukaan lukien: `sizeof` on 4 ja `strlen` 3. Osoitin `literaali` sisältää vain literaalin osoitteen."}
digraph {
  rankdir=LR; nodesep=0.35; ranksep=0.7;
  node [shape=plain, style=""];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="4"><i>char tervehdys[]</i> <font point-size="8">(pinossa, muutettava)</font></td></tr>
    <tr><td bgcolor="#EEF1F6" width="30">'H'</td><td bgcolor="#EEF1F6" width="30">'e'</td><td bgcolor="#EEF1F6" width="30">'i'</td><td bgcolor="#EEF1F6" width="30">'\\0'</td></tr></table>>];
  p [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left"><i>const char *literaali</i></td></tr>
    <tr><td port="v" bgcolor="#EEF1F6" width="120">osoite</td></tr></table>>];
  lit [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="6"><font point-size="8">staattinen muisti, vain luku</font></td></tr>
    <tr><td port="a" width="26">'v'</td><td width="26">'a'</td><td width="26">'k'</td><td width="26">'i'</td><td width="26">'o'</td><td width="26">'\\0'</td></tr></table>>];
  p:v:e -> lit:a:w;
  t -> p [style=invis];
  {rank=same; t; p}
}
```

### Vertailu ja haku

Operaattori `==` vertaa merkkijonojen osoitteita eikä sisältöä. Sisältö
vertaillaan funktiolla `strcmp`, joka palauttaa nollan, kun merkkijonot
ovat samat, ja muuten negatiivisen tai positiivisen luvun
aakkosjärjestyksen (tarkemmin: merkkikoodien) mukaan.

```{.c tiedosto="esimerkit/07-merkkijonot.c" osa="vertailu"}
```

Otsikon `<string.h>` hakufunktiot palauttavat osoittimen löydettyyn
kohtaan tai tyhjän osoittimen. `strchr` etsii merkin ensimmäisen ja
`strrchr` viimeisen esiintymän, `strstr` alimerkkijonon:

```{.c tiedosto="esimerkit/07-merkkijonot.c" osa="haku"}
```

### Merkkijonojen muodostaminen

Merkkijonojen kopioiminen ja yhdistäminen on C:n tyypillisimpiä
virhelähteitä. Funktiot `strcpy` ja `strcat` eivät tiedä kohdepuskurin
kokoa, ja `strncpy` jättää pahimmillaan nollamerkin pois. Turvallisin
yleistyökalu on `snprintf`: se ei koskaan kirjoita puskurin ohi, päättää
merkkijonon aina nollamerkkiin ja palauttaa merkkien määrän, joka olisi
tarvittu. Paluuarvosta näkee siis, katkesiko tulos.

```{.c tiedosto="esimerkit/07-merkkijonot.c" osa="tunnus"}
```

```{.c tiedosto="esimerkit/07-merkkijonot.c" osa="snprintf"}
```

```{.tuloste tiedosto="esimerkit/07-merkkijonot.odotettu"}
```

### Merkkijonosta luvuksi

Funktio `atoi` muuntaa merkkijonon luvuksi, mutta se ei kerro
virheistä: `atoi("12abc")` palauttaa 12 ja `atoi("abc")` nollan. Funktio
`strtol` kertoo, mihin kohtaan jäsentäminen päättyi, ja asettaa
muuttujan `errno` arvoon `ERANGE`, jos luku ei mahdu tyyppiin:

```{.c tiedosto="esimerkit/07-luvuiksi.c" osa="jasenna"}
```

```{.c tiedosto="esimerkit/07-luvuiksi.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-luvuiksi.odotettu"}
```

Vastaavat funktiot ovat `strtoul`, `strtoll` ja liukuluvuille `strtod`.

## Merkkijonot ilman kopiointia: viipale

Koska C:n merkkijonot päättyvät nollamerkkiin, alijonon käsittely vaatii
yleensä kopion. Moni C-projekti käyttää siksi *viipaletta*: rakennetta,
jossa on osoitin ja pituus. Viipale viittaa alkuperäiseen dataan, ja sen
pituus on aina tiedossa ilman `strlen`-kutsua.

```{.c tiedosto="esimerkit/07-viipale.c" osa="viipale"}
```

```{.c tiedosto="esimerkit/07-viipale.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/07-viipale.odotettu"}
```

```{.dot otsikko="Viipale `nimi` toisella kierroksella: osoitin ja pituus viittaavat alkuperäisen merkkijonon keskelle, eikä viipaleen lopussa ole nollamerkkiä."}
digraph {
  rankdir=TB; nodesep=0.3; ranksep=0.4;
  node [shape=plain, style=""];
  v [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="2"><i>Viipale nimi</i></td></tr>
    <tr><td port="d" bgcolor="#EEF1F6" width="60">data</td><td bgcolor="#EEF1F6" width="60">pituus = 6</td></tr></table>>];
  m [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="13"><font point-size="8">otsakkeet</font></td></tr>
    <tr><td width="18">…</td><td width="18">f</td><td width="18">i</td><td width="18">;</td><td port="a" bgcolor="#EEF1F6" width="18">A</td><td bgcolor="#EEF1F6" width="18">c</td><td bgcolor="#EEF1F6" width="18">c</td><td bgcolor="#EEF1F6" width="18">e</td><td bgcolor="#EEF1F6" width="18">p</td><td bgcolor="#EEF1F6" width="18">t</td><td width="18">:</td><td width="18">…</td><td width="18">'\\0'</td></tr></table>>];
  v:d:s -> m:a:n;
}
```

Muotoilumääre `%.*s` tulostaa annetun määrän merkkejä, joten viipaleen
voi tulostaa ilman nollamerkkiä. Viipale on lainaus: data ei saa
vapautua tai muuttua, kun viipaletta vielä käytetään.

## Käytännössä

- **Pituus kulkee aina mukana.** Rajapinnat ottavat parin
  `(const T *t, size_t n)` tai viipaleen. Tämä poistaa toistuvat
  `strlen`-kutsut ja mahdollistaa alijonot ilman kopiointia.
- **Puskurin koko `sizeof`illa.** `snprintf(p, sizeof p, ...)` pysyy
  oikeana, vaikka puskurin kokoa muutetaan. Kovakoodattu luku jää
  helposti jälkeen.
- **Kaikki muotoilu `snprintf`illä** ja katkeamisen tarkistus
  paluuarvosta. Merkkijonoja ei kopioida `strcpy`llä eikä yhdistetä
  `strcat`illa.
- **Luvut `strto*`-funktioilla**, aina loppuosoitin ja `errno`
  tarkistaen. `atoi` ei kerro virheistä.
- **Ei `strtok`ia.** Se säilyttää tilaa globaalisti eikä ole
  säieturvallinen. Korvaajia ovat POSIX:n `strtok_r` ja oma jäsennin,
  kuten yllä.
- **Kokoelmat itse tai kirjastosta.** C:n standardikirjastossa ei ole
  dynaamista taulukkoa eikä hajautustaulua. Pienet rakenteet toteutetaan
  itse (luku 8); muuten käytetään laajasti testattua kirjastoa, kuten
  GLibiä tai yksitiedostoisia kirjastoja (stb_ds, klib).
- **UTF-8:** `strlen` laskee tavuja, ei merkkejä. Merkkitason käsittely
  (kirjainkoko, leveys) vaatii kirjaston.

## Itsearviointi

- Osaat selittää taulukon ja osoittimen eron `sizeof`-operaattorin
  kannalta ja välittää taulukon funktiolle pituuksineen.
- Osaat muodostaa merkkijonon `snprintf`illä ja havaita katkeamisen.
- Osaat jäsentää kokonaisluvun `strtol`illa kaikki virhetilanteet
  tarkistaen.
- Osaat käsitellä alijonoja viipaleina kopioimatta niitä.
