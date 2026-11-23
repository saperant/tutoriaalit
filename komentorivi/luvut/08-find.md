# Tiedostojen etsintä ja massatoiminnot

Jokerimerkit riittävät yhteen hakemistoon. Kun tiedostoja etsitään
koko puusta nimen, koon, iän tai oikeuksien perusteella ja niille
tehdään jotain, työkalut ovat `find` ja `xargs`. Tämä luku käy läpi
niiden turvallisen käytön ja tavalliset ylläpitotehtävät: siivouksen,
arkistoinnin ja eheyden tarkistuksen.

## find

`find` käy hakemistopuun läpi ja arvioi jokaiselle tiedostolle
lausekkeen vasemmalta oikealle. Peräkkäiset ehdot yhdistetään
JA-operaatiolla, `-o` on TAI ja `!` negaatio.

| Ehto | Merkitys |
|------|----------|
| `-name '*.log'`, `-iname` | Nimi globilla (lainaa!), kirjainkoosta välittämättä |
| `-path 'x/*/y'` | Koko polku globilla |
| `-type f`, `-type d`, `-type l` | Tiedosto, hakemisto, symbolinen linkki |
| `-size +100k`, `-size -1M` | Koko yli tai alle |
| `-mtime +7`, `-mtime -1` | Muokattu yli 7 vrk tai alle 1 vrk sitten |
| `-mmin -30`, `-newer viite` | Minuutteina, uudempi kuin viitetiedosto |
| `-perm -o+w`, `-user`, `-group` | Oikeudet, omistaja |
| `-empty` | Tyhjä tiedosto tai hakemisto |
| `-maxdepth 1` | Rajaa syvyyden (kirjoitetaan ensimmäiseksi) |
| `-prune` | Älä mene hakemistoon |

```{.bash tiedosto="esimerkit/08-find.sh" osa="nimi"}
```

```{.bash tiedosto="esimerkit/08-find.sh" osa="ominaisuudet"}
```

```{.tuloste tiedosto="esimerkit/08-find.odotettu"}
```

Karsintalauseke `-path X -prune -o EHDOT -print` luetaan: "jos polku on
X, älä laskeudu siihen; muuten, jos ehdot täyttyvät, tulosta". Lopun
`-print` on pakollinen, muuten myös karsittu hakemisto tulostuu.

`-mtime` laskee kokonaisina vuorokausina, ja pyöristys yllättää:
`-mtime +7` tarkoittaa *vähintään kahdeksan* vuorokautta vanhaa.
Tarkkaan rajaan tarvitaan `-mmin` tai `-newer`.

`find`-komennon tulosteen järjestys on hakemiston sisäinen järjestys,
ei aakkosjärjestys. Esimerkit lajittelevat sen, jotta tulos on
toistettava.

## Toiminnot

`find` voi tehdä jotain löytämilleen tiedostoille:

- `-delete` poistaa (ja vaatii syvyys ensin -järjestyksen, jonka se
  asettaa itse).
- `-exec komento {} +` ajaa komennon niin, että `{}` korvataan
  mahdollisimman monella tiedostonimellä kerralla.
- `-exec komento {} \;` ajaa komennon kerran jokaiselle tiedostolle.
  Se on hidas suurella määrällä tiedostoja.
- `-printf '%s %p\n'` tulostaa valitut tiedot (GNU).

Lokien siivous on tavallinen ylläpitotehtävä. Yli viikon vanhat
lokit pakataan ja yli 30 päivän ikäiset poistetaan. `-print` ennen
`-delete`-toimintoa kirjaa poistetut:

```{.bash tiedosto="esimerkit/08-siivous.sh" osa="siivous"}
```

```{.tuloste tiedosto="esimerkit/08-siivous.odotettu"}
```

Poistavan komennon kehitys tehdään vaiheittain: ensin pelkkä `find`
ehtoineen ja tuloksen tarkistus, sitten `-delete` loppuun. `-delete`
lausekkeen alussa poistaisi kaiken, koska se on aina tosi ja arvioidaan
ennen ehtoja. Lokien kiertoon on myös valmis työkalu `logrotate`, joka
hoitaa pakkaamisen, poistot ja palvelun ilmoittamisen.

## xargs

`xargs` lukee syötteestä argumentteja ja ajaa komennon niillä. Se on
`-exec`-toiminnon yleistys: syöte voi tulla mistä tahansa, ja komento
voidaan ajaa rinnakkain.

Oletuksena `xargs` jakaa syötteen välilyönneistä ja rivinvaihdoista,
joten välilyönti tiedostonimessä rikkoo sen. ShellCheck varoittaa tästä
muodosta (SC2038):

```{.bash tiedosto="esimerkit/08-xargs.sh" osa="naiivi"}
```

Turvallinen muoto erottaa nimet nollatavulla, jota tiedostonimessä ei
voi olla: `find -print0`, `sort -z`, `grep -Z` ja `xargs -0`.

```{.bash tiedosto="esimerkit/08-xargs.sh" osa="turvallinen"}
```

`-P N` ajaa enintään N komentoa rinnakkain ja `-I{}` sijoittaa nimen
haluttuun kohtaan. Kun komento on monimutkaisempi, se ajetaan
`sh -c`-muodossa, jolloin nimi välitetään argumenttina `$1`. Nimeä ei
koskaan upoteta komentotekstiin:

```{.bash tiedosto="esimerkit/08-xargs.sh" osa="rinnakkain"}
```

```{.tuloste tiedosto="esimerkit/08-xargs.odotettu"}
```

Rinnakkaisten töiden tulosteet tulevat valmistumisjärjestyksessä,
joten ne lajitellaan. Suurempiin rinnakkaisiin eräajoihin on työkalu
GNU `parallel`.

## Arkistot ja tarkistussummat

`tar` kokoaa hakemistopuun yhdeksi tiedostoksi ja säilyttää oikeudet,
ajat ja linkit. Pakkaus valitaan valitsimella: `-z` gzip, `-J` xz,
`--zstd` zstd. `-c` luo, `-t` listaa ja `-x` purkaa. `-C hakemisto`
vaihtaa hakemiston ennen toimintoa:

```{.bash tiedosto="esimerkit/08-arkisto.sh" osa="tar"}
```

`--sort=name` tekee arkiston järjestyksestä toistettavan. Ilman sitä
tiedostot ovat hakemiston sisäisessä järjestyksessä.

Tarkistussummalla todetaan, että tiedosto on muuttumaton: ladattu
asennuspaketti vastaa julkaistua tai varmuuskopio on ehjä.
`sha256sum -c` tarkistaa listan:

```{.bash tiedosto="esimerkit/08-arkisto.sh" osa="summat"}
```

```{.tuloste tiedosto="esimerkit/08-arkisto.odotettu"}
```

Hakemistojen synkronointiin ja etäkopiointiin on `rsync` (luku
*Etäkäyttö: ssh*). Se siirtää vain muuttuneet osat ja osaa poistaa
kohteesta tiedostot, jotka on poistettu lähteestä (`--delete`).

## Käytännössä

- **Kokeile ennen kuin muutat.** Aja `find` ensin ilman toimintoa tai
  `-print`-toiminnolla. Lisää `-delete` tai `-exec` vasta, kun lista on
  oikea.
- **`-print0 | xargs -0`** aina, kun nimiä välitetään putkessa. Muu
  muoto toimii, kunnes ensimmäinen välilyönti tulee vastaan.
- **`-exec … {} +` ennen `\;`-muotoa.** Ero voi olla satakertainen,
  kun tiedostoja on paljon.
- **Lainaa globit `find`-ehdoissa** (`-name '*.log'`). Lainaamaton
  `*.log` laajenee kuoressa nykyisen hakemiston nimiksi ennen kuin
  `find` näkee sen.
- **Varmuuskopio ei ole valmis ennen palautuskoetta.** Pura arkisto
  toiseen hakemistoon ja vertaa (`diff -r`) tai tarkista summat.
- **Ajastetut siivoukset** kuuluvat `logrotate`-asetukseen tai
  systemd-ajastimeen (luku *Paketit, palvelut ja lokit*), ei käsin
  ajettaviksi.

## Itsearviointi

- Osaat etsiä tiedostoja nimen, tyypin, koon ja iän perusteella ja
  rajata hakemistoja pois `-prune`-ehdolla.
- Osaat kirjoittaa turvallisen siivouskomennon, joka pakkaa tai
  poistaa vanhat tiedostot, ja tarkistaa sen ennen ajoa.
- Osaat välittää tiedostonimiä `find -print0 | xargs -0`-putkella ja
  ajaa komentoja rinnakkain.
- Osaat tehdä toistettavan `tar`-arkiston, palauttaa sen ja tarkistaa
  eheyden tarkistussummilla.
