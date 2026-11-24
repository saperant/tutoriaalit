# Debuggaus gdb:llä

Kun testi kaatuu, ensimmäinen kysymys on *missä*. Sanitoija vastaa
siihen muistivirheiden osalta, mutta tavallinen kaatuminen, väärä arvo
tai jumiutuminen vaatii debuggerin. gdb:tä käytetään tavallisesti
vuorovaikutteisesti. Tässä luvussa sitä käytetään *eräajona*: komennot
annetaan komentorivillä, gdb ajaa ne ja lopettaa. Sama tapa toimii
CI:ssä, jossa kaatuneen testin kutsupino halutaan lokiin, ja
komentosarjoissa, jotka toistavat saman tutkimuksen joka kerta.
C-kielen tutoriaalin luku *Työkalut ja testaus* esitteli gdb:n
peruskomennot.

## Eräajo

Ohjelma käännetään debug-tiedolla (`-g`) ja ilman optimointia
(`-O0`), jotta jokainen muuttuja ja rivi on debuggerin nähtävissä.
Eräajon perusmuoto on:

```{.bash tiedosto="esimerkit/12-gdb/aja.sh" osa="gdb"}
```

`-batch` ajaa komennot ja lopettaa, ja ohjelma tapetaan, jos se on
vielä käynnissä. `-nx` jättää käyttäjän asetustiedoston `~/.gdbinit`
lukematta, jotta tulos ei riipu koneesta. Ubuntun gdb hakee
oletuksena puuttuvat debug-symbolit verkosta (*debuginfod*), mikä
hidastaa ja tuottaa kysymyksiä. Eräajossa se kytketään pois.
Jokainen `-ex` on yksi komento samassa järjestyksessä kuin ne
kirjoitettaisiin kehotteeseen.

## Kaatumiskohta

Ohjelma kysyy asetuksen arvoa, ja hakufunktio palauttaa `NULL`, kun
asetusta ei löydy:

```{.c tiedosto="esimerkit/12-gdb/kaatuu.c"}
```

Ilman debuggeria näkyy vain paluuarvo 139, eli 128 + 11, signaali
`SIGSEGV`. gdb ajaa ohjelman (`run`), pysähtyy signaaliin ja näyttää
kutsupinon (`bt`). Sen jälkeen se tulostaa muuttujan ja kutsuu jopa
ohjelman omaa funktiota (`print hae(nimi)`):

```{.bash tiedosto="esimerkit/12-gdb/aja.sh" osa="kaatuminen"}
```

Kaatumiskohta on rivi 23, funktio `arvo`, ja kutsuja on `main` rivillä
29. Hakufunktio palauttaa tyhjän osoittimen, kun sille annetaan nimi
`syvyys`. Korjaus on joko tarkistaa `NULL` kutsujassa tai muuttaa
rajapintaa niin, että puuttuva asetus on erikseen käsiteltävä tilanne
(esimerkiksi paluuarvo virhekoodina ja arvo osoittimen kautta).

## Vahtipisteet

Hankalimmat virheet ovat sellaisia, joissa arvo on väärä, mutta sen
muuttanut koodi on jossain muualla. *Vahtipiste* (*watchpoint*)
pysäyttää ohjelman, kun lausekkeen arvo muuttuu, ja näyttää vanhan ja
uuden arvon sekä kohdan, jossa muutos tapahtui:

```{.c tiedosto="esimerkit/12-gdb/vahti.c"}
```

Laskurin pitäisi olla 3, mutta ohjelma tulostaa 55. Vahtipiste
asetetaan, kun muuttuja on olemassa ja alustettu: ensin keskeytyskohta
riville 20, sitten `watch t.laskuri` ja `continue`:

```{.bash tiedosto="esimerkit/12-gdb/aja.sh" osa="vahtipiste"}
```

```{.tuloste tiedosto="esimerkit/12-gdb.odotettu"}
```

Laskuri muuttui funktiossa `nimea`, joka ei käsittele laskuria
lainkaan. Muuttuja `i` on 8, ja nimi-taulukossa on 8 merkkiä: silmukka
kirjoitti taulukon ohi, ja yhdeksäs merkki `7` (ASCII 55) osui
rakenteessa seuraavana olevan laskurin alimpaan tavuun. Tämä on sama
virhe kuin luvun 9 ylivuoto, mutta pinossa olevan rakenteen sisällä,
jossa ASan ei sitä huomaa: kirjoitus pysyy rakenteen rajojen sisällä.

Vahtipiste toteutetaan prosessorin debug-rekistereillä (*hardware
watchpoint*), jolloin ohjelma toimii täydellä nopeudella. Rekistereitä
on vähän (x86-64:ssä neljä), joten kerralla voi vahtia vain muutamaa
pientä muuttujaa. Ohjelmistovahtipiste toimii aina, mutta ajaa
ohjelmaa käsky kerrallaan ja on tuhansia kertoja hitaampi. Kun
muuttujan näkyvyysalue päättyy, gdb poistaa vahtipisteen. `rwatch`
pysäyttää lukuun ja `awatch` sekä lukuun että kirjoitukseen.

## Tuloste suodatettuna

Esimerkin suodatin poistaa gdb:n tulosteesta osoitteet ja ilmoitukset,
jotka vaihtelevat ajosta toiseen: osoitinten arvot riippuvat
osoiteavaruuden satunnaistuksesta, ja säiekirjaston ilmoitus riippuu
järjestelmästä. Vahtipisteen sana `Hardware` poistetaan, koska
virtuaalikoneessa gdb voi joutua käyttämään ohjelmistovahtipistettä.
gdb:n lähdekoodirivit sisältävät sarkaimen, joka muutetaan
välilyönneiksi:

```{.bash tiedosto="esimerkit/12-gdb/aja.sh" osa="siisti"}
```

Samoin kannattaa toimia, kun gdb:n tulostetta verrataan odotettuun tai
haetaan lokista. CI:ssä hyödyllisin yksittäinen komento
on täysi kutsupino kaikista säikeistä:

```text
gdb -batch -nx -ex run -ex 'thread apply all bt full' --args ./testit
```

`bt full` tulostaa myös jokaisen kehyksen paikalliset muuttujat. Jos
ohjelma kaatuu vain CI:ssä, ytimen vedos (*core dump*) on parempi:
`ulimit -c unlimited` sallii sen, ja vedoksen voi tallentaa artefaktiksi
ja tutkia omalla koneella komennolla `gdb ./testit core`. Komento
`gdb -p <pid>` liittyy jumiutuneeseen prosessiin, ja `bt` näyttää,
missä se odottaa.

## Optimoitu koodi

Julkaisuversio on optimoitu, ja sen virheet esiintyvät usein vain
optimoituna. Debug-tiedon voi lisätä optimoituun käännökseen (`-O2 -g`,
CMaken `RelWithDebInfo`), mutta debuggeri näyttää silloin muuttujia
merkinnällä `<optimized out>`, rivit hyppivät ja funktioita on
upotettu kutsujiinsa. Valitsin `-Og` optimoi vain sen verran kuin
debuggausta haittaamatta voi. Jakeluissa debug-tieto erotetaan omaan
tiedostoonsa (`objcopy --only-keep-debug`), jolloin binääri pysyy
pienenä, ja debuggeri hakee tiedon erikseen, esimerkiksi juuri
debuginfod-palvelimelta.

## Käytännössä

- **Kutsupino ensin.** `bt` kertoo kaatumiskohdan ja reitin sinne.
  Usein se riittää, eikä vianetsintää tarvitse aloittaa
  tulostuslauseilla.
- **Vahtipiste väärälle arvolle.** Kun arvo muuttuu jossain, missä sen
  ei pitäisi, vahtipiste löytää kohdan suoraan. Se on nopeampi kuin
  keskeytyskohtien asettelu arvaamalla.
- **Eräajo toistettavaan tutkimukseen.** Komennot komentorivillä tai
  tiedostossa (`gdb -batch -x komennot.gdb`) toistavat saman
  tutkimuksen joka kerta ja sopivat CI:hin.
- **Ytimen vedos CI:stä.** Kaatuminen, joka tapahtuu vain CI:ssä,
  tutkitaan vedoksesta, ei arvaamalla. Vedos ja binääri tallennetaan
  artefakteiksi.
- **`-Og` tai `-O0 -g` debuggaukseen.** Täysin optimoidun ohjelman
  debuggaus on mahdollista, mutta muuttujat ja rivit eivät vastaa
  lähdekoodia.

## Itsearviointi

- Osaat ajaa gdb:n eräajona ja tulostaa kaatuneen ohjelman kutsupinon
  ja muuttujat.
- Osaat asettaa vahtipisteen muuttujaan oikealla hetkellä ja tulkita
  sen tulosteen.
- Osaat kertoa laitteisto- ja ohjelmistovahtipisteen eron.
- Osaat tutkia CI:ssä kaatuneen ohjelman ytimen vedoksesta ja
  kertoa, miksi optimoitu koodi on vaikeampi debugata.
