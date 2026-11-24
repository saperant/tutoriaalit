# Tiedostot ja I/O

Unixin tunnetuin periaate on, että "kaikki on tiedosto": tavalliset
tiedostot, hakemistot, laitteet, putket ja soketit käsitellään samoilla
kutsuilla `open`, `read`, `write` ja `close`. Tämä luku käy läpi
tiedostorajapinnan kolme kerrosta: kuvaajat ja avoimet tiedostot,
nimet ja inodet sekä puskurointi ja pysyvyys. Seuraava luku toteuttaa
tiedostojärjestelmän itse.

## Kuvaajat ja avoimet tiedostot

Tiedostokuvaaja (engl. file descriptor) on pieni kokonaisluku, indeksi
prosessin *kuvaajataulukkoon*. Taulukon alkio osoittaa ytimen *avoimen
tiedoston* olioon (`struct file`), jossa on tiedostosijainti, avaustila
ja liput kuten `O_APPEND`. Avoin tiedosto taas osoittaa inodeen, joka
on itse tiedosto. Kerroksia on siis kolme:

| Kerros | Kenen | Sisältö |
|----------------|------------------------|--------------------------------|
| kuvaajataulukko | prosessin (säikeet jakavat) | numero → avoin tiedosto, `FD_CLOEXEC` |
| avoin tiedosto | jaettu `dup`- ja `fork`-kutsuissa | sijainti, tila, liput |
| inode | yksi tiedostoa kohti | koko, oikeudet, datalohkot |

`open` antaa aina pienimmän vapaan numeron. Kuvaajat 0, 1 ja 2 ovat
vakiosyöte, -tuloste ja -virhe, joten ensimmäinen avattu tiedosto saa
numeron 3:

```{.c tiedosto="esimerkit/08-kuvaajat.c" osa="pienin"}
```

`dup2(vanha, uusi)` kopioi kuvaajan haluttuun numeroon. Näin
komentotulkki toteuttaa uudelleenohjauksen `komento > loki.txt`:
lapsi avaa tiedoston, kopioi sen kuvaajaksi 1 ja suorittaa ohjelman,
joka kirjoittaa vakiotulosteeseen tietämättä sen olevan tiedosto:

```{.c tiedosto="esimerkit/08-kuvaajat.c" osa="dup2"}
```

Koska `dup` ja `fork` kopioivat vain kuvaajan, molemmat kuvaajat
osoittavat samaan avoimeen tiedostoon, ja niillä on *yhteinen
sijainti*. Kaksi erillistä `open`-kutsua taas luo kaksi avointa
tiedostoa, joilla on omat sijaintinsa:

```{.c tiedosto="esimerkit/08-kuvaajat.c" osa="jaettu"}
```

```{.tuloste tiedosto="esimerkit/08-kuvaajat.odotettu"}
```

Lapsen ja vanhemman rivit ovat peräkkäin, koska sijainti on yhteinen.
Erillisillä avauksilla toinen kirjoitus alkoi kohdasta 0 ja kirjoitti
ensimmäisen päälle. `O_APPEND` siirtää sijainnin tiedoston loppuun
atomisesti jokaisessa kirjoituksessa, minkä vuoksi lokitiedostot
avataan sillä: usean prosessin rivit eivät kirjoitu toistensa päälle.

Lippu `O_CLOEXEC` (tai `FD_CLOEXEC`) sulkee kuvaajan automaattisesti
`exec`-kutsussa. Ilman sitä kaikki kuvaajat periytyvät käynnistetylle
ohjelmalle, mikä on tavallinen tietovuodon ja jumiutuneiden putkien
syy. Monisäikeisessä ohjelmassa lippu on annettava jo `open`-kutsussa,
koska toinen säie voi forkata välissä.

## Nimet ja inodet

Inode on tiedoston ytimen kuvaus: tyyppi, oikeudet, omistaja, koko,
aikaleimat, linkkien määrä ja datalohkojen sijainnit. Inodessa ei ole
nimeä. Nimi on *hakemistotietue*, joka liittää nimen inoden numeroon,
ja hakemisto on tiedosto, joka sisältää tällaisia tietueita.

- **Kova linkki** (`link`, `ln`) on uusi hakemistotietue samaan
  inodeen. Kaikki nimet ovat tasavertaisia; mikään ei ole
  "alkuperäinen".
- **Symbolinen linkki** (`symlink`, `ln -s`) on oma pieni tiedostonsa,
  jonka sisältö on polku. Ydin seuraa sitä polkua selvittäessään.
- **Poisto** (`unlink`) poistaa nimen ja vähentää linkkilaskuria. Data
  vapautetaan vasta, kun laskuri on nolla *eikä* yksikään prosessi
  pidä tiedostoa auki.

```{.c tiedosto="esimerkit/08-inodet.c" osa="linkit"}
```

`stat` seuraa symbolista linkkiä ja kertoo kohteesta; `lstat` kertoo
linkistä itsestään. Linkin koko on sen sisältämän polun pituus. Kun
kohde poistetaan, kova linkki pitää datan elossa, mutta symbolinen
linkki jää roikkumaan.

Hakemiston sisällön lukee `opendir`- ja `readdir`-funktioilla.
Järjestys on tiedostojärjestelmän sisäinen (esimerkiksi ext4:n
hajautusjärjestys), joten ohjelman on lajiteltava nimet itse, jos
järjestyksellä on väliä. Hakemistossa ovat aina myös `.` ja `..`.

Tiedoston koko ja sen viemä levytila ovat eri asioita. Jos sijaintia
siirretään tiedoston lopun ohi ja kirjoitetaan, väliin jää *aukko*,
jolle ei varata lohkoja; luku palauttaa aukosta nollia. Tällaisia
*harvoja* tiedostoja käyttävät levykuvat ja tietokannat:

```{.c tiedosto="esimerkit/08-inodet.c" osa="harva"}
```

```{.tuloste tiedosto="esimerkit/08-inodet.odotettu"}
```

## Puskurointi

Ytimessä on kaksi puskuria ohjelman ja levyn välissä, ja käyttäjätilan
kirjastossa usein kolmas:

1. **stdio-puskuri** käyttäjätilassa: `fputc` ja `printf` kirjoittavat
   muistiin, ja `write`-kutsu tehdään vasta puskurin täyttyessä.
2. **Sivuvälimuisti** ytimessä: `write` kopioi datan sivuvälimuistiin
   ja palaa heti. Sivu merkitään likaiseksi.
3. **Laitteen välimuisti:** levyohjain voi pitää dataa omassa
   muistissaan ennen kuin se on pysyvästi tallessa.

stdio-puskurin vaikutuksen näkee ohjaamalla virran omaan
kirjoitusfunktioon (`fopencookie`, GNU-laajennus), joka laskee
kutsut. Funktio `kokeile` avaa tällaisen virran, asettaa
puskurointitilan `setvbuf`-kutsulla ja kirjoittaa 100 riviä, joissa on
100 merkkiä, merkki kerrallaan:

```{.c tiedosto="esimerkit/08-puskurointi.c" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/08-puskurointi.odotettu"}
```

Täysi puskurointi tekee 10 000 merkistä kolme kirjoitusta,
rivipuskurointi yhden riviä kohti, ja puskuroimaton virta yhden
jokaista merkkiä kohti – jokainen niistä olisi järjestelmäkutsu.
Päätteeseen kytketty stdout on rivipuskuroitu, putkeen tai tiedostoon
kytketty täysin puskuroitu ja stderr aina puskuroimaton, jotta
virheilmoitus näkyy, vaikka ohjelma kaatuisi heti sen jälkeen.

## Pysyvyys: fsync ja atominen tallennus

Kun `write` palaa, data on sivuvälimuistissa, ei levyllä. Ydin
kirjoittaa likaiset sivut taustalla (Linuxissa tyypillisesti 5–30
sekunnin kuluessa). Virtakatko ennen sitä hukkaa datan, vaikka ohjelma
luuli tallentaneensa sen. `fsync(fd)` odottaa, kunnes tiedoston data
ja metatiedot ovat laitteella, ja pyytää laitetta tyhjentämään oman
välimuistinsa. `fdatasync` jättää pois metatiedot, joita datan
lukeminen ei tarvitse, kuten muutosajan.

Pelkkä `fsync` ei kuitenkaan riitä tiedoston turvalliseen
korvaamiseen. Jos ohjelma avaa tiedoston `O_TRUNC`-lipulla ja kaatuu
ennen kirjoituksen loppua, vanha sisältö on menetetty eikä uusi ole
valmis. Oikea tapa on kirjoittaa uusi versio väliaikaiseen
tiedostoon ja vaihtaa se paikalleen `rename`-kutsulla, joka on POSIXin
mukaan atominen: nimi osoittaa aina joko vanhaan tai uuteen
tiedostoon. Lopuksi synkronoidaan hakemisto, jotta itse nimenvaihtokin
on levyllä:

```{.c tiedosto="esimerkit/08-tallennus.c" osa="tallenna"}
```

Esimerkki tallentaa kaksi versiota peräkkäin ja lukee tiedoston
kummankin jälkeen:

```{.tuloste tiedosto="esimerkit/08-tallennus.odotettu"}
```

`write` voi kirjoittaa vähemmän kuin pyydettiin (osittainen
kirjoitus), esimerkiksi signaalin keskeyttämänä tai levyn täyttyessä,
joten kirjoitus tehdään silmukassa. `close`-kutsun virhe on myös
tarkistettava: verkkotiedostojärjestelmät voivat ilmoittaa
kirjoitusvirheestä vasta siinä.

## Käytännössä

- **`O_CLOEXEC` jokaiseen avaukseen:** periytyvät kuvaajat ovat
  vaikeasti löydettäviä vikoja.
- **`O_APPEND` lokeihin:** usean kirjoittajan rivit eivät sekoitu
  eivätkä kirjoitu päällekkäin.
- **Korvaa tiedostot atomisesti:** väliaikainen tiedosto samaan
  hakemistoon, `fsync`, `rename`, hakemiston `fsync`.
- **Kirjoita silmukassa ja tarkista `close`:** osittaiset kirjoitukset
  ja myöhään ilmoitetut virheet ovat todellisia.
- **Puskuroi pienet kirjoitukset:** tavu kerrallaan kirjoittaminen
  ilman puskuria on tuhat kertaa hitaampaa.
- **Älä luota `readdir`in järjestykseen:** lajittele itse.

## Itsearviointi

- Osaat selittää kuvaajataulukon, avoimen tiedoston ja inoden suhteen
  ja ennustaa, milloin kaksi kuvaajaa jakavat sijainnin.
- Osaat toteuttaa uudelleenohjauksen `dup2`-kutsulla.
- Osaat erottaa kovan ja symbolisen linkin ja kertoa, milloin
  tiedoston data todella vapautetaan.
- Osaat kuvata puskurointikerrokset stdiosta levyyn ja valita
  puskurointitilan.
- Osaat tallentaa tiedoston niin, että kaatuminen ei jätä
  puolivalmista sisältöä.
