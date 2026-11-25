# Tiedostot ja hakemistot

Työkalut käyvät läpi tuloshakemistoja, etsivät tiedostoja ja
kirjoittavat raportteja, joita muut ohjelmat lukevat. `pathlib`
esittää polut olioina, joilla on metodit. Polkuja ei rakenneta
merkkijonoja yhdistelemällä, joten erotinmerkit ja suhteelliset polut
käsitellään oikein kaikilla alustoilla.

## Hakemistopuun läpikäynti

Regressioajo tuottaa hakemiston jokaiselle testille ja siemenelle.
Esimerkki luo rakenteen ensin tilapäishakemistoon:

```{.python tiedosto="esimerkit/06-tulokset.py" osa="rakenne"}
```

`/`-operaattori yhdistää polun osat, ja `mkdir(parents=True,
exist_ok=True)` luo puuttuvat välihakemistot. Läpikäynti hakee
ajohakemistot `glob`illa ja luokittelee ne lokin perusteella:

```{.python tiedosto="esimerkit/06-tulokset.py" osa="lapikaynti"}
```

`glob` ja `iterdir` palauttavat tiedostot siinä järjestyksessä kuin
tiedostojärjestelmä ne antaa. Järjestys vaihtelee koneittain, joten
tulokset lajitellaan aina ennen tulostusta. `relative_to` tekee
raporttiin lyhyet, koneesta riippumattomat polut, ja `as_posix` antaa
kauttaviivat myös Windowsissa.

`rglob` hakee rekursiivisesti, ja polun osat saadaan ominaisuuksina:

```{.python tiedosto="esimerkit/06-tulokset.py" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/06-tulokset.odotettu"}
```

## Atominen kirjoitus

Kun työkalu kirjoittaa tiedostoa, jota toinen prosessi lukee (CI:n
seuraava vaihe, raporttipalvelin, rinnakkainen ajo), lukija voi osua
puolikkaaseen tiedostoon. Kaatuva kirjoittaja voi lisäksi jättää
jälkeensä rikkinäisen tiedoston, joka korvaa vanhan ehjän.

Ratkaisu on taidosta *Python* tuttu: kirjoitetaan ensin
tilapäistiedostoon ja vaihdetaan se kohteen tilalle `os.replace`lla.
Nimen vaihto saman tiedostojärjestelmän sisällä on atominen, joten
lukija näkee joko vanhan tai uuden tiedoston. Työkalussa toteutus
viimeistellään kolmella asialla: tilapäistiedosto luodaan kohteen
viereen, data pakotetaan levylle ja keskeytys siivoaa jälkensä.

```{.python tiedosto="esimerkit/06-atominen.py" osa="atominen"}
```

- `mkstemp(dir=kohde.parent)` luo tilapäistiedoston samaan hakemistoon.
  Tilapäistiedosto `/tmp`-hakemistossa voi olla eri
  tiedostojärjestelmässä, jolloin `os.replace` ei ole atominen tai
  epäonnistuu.
- `fsync` pakottaa datan levylle ennen nimen vaihtoa. Ilman sitä
  sähkökatko voi jättää uuden nimen ja tyhjän sisällön.
- `except BaseException` siivoaa tilapäistiedoston myös Ctrl+C:n
  (`KeyboardInterrupt`) jälkeen ja nostaa poikkeuksen uudelleen.

```{.python tiedosto="esimerkit/06-atominen.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-atominen.odotettu"}
```

Keskeytetty kirjoitus ei muuttanut tiedostoa, eikä tilapäistiedostoa
jäänyt hakemistoon.

## Tilapäistiedostot

`tempfile.TemporaryDirectory()` luo hakemiston, joka poistetaan
sisältöineen `with`-lohkon lopussa, myös poikkeuksen jälkeen. Se on
oikea paikka välituotteille ja testien aineistolle. Kiinteä nimi
`/tmp/tyo` törmää toisen käyttäjän tai rinnakkaisen ajon kanssa, ja
ennustettava nimi jaetussa hakemistossa on tietoturvariski.

## Kopiointi, siirto ja arkistointi

Tiedostojen sisältöön koskemattomat operaatiot ovat modulissa `shutil`:

| Funktio | Tehtävä |
|---------|---------|
| `shutil.copy2(lahde, kohde)` | kopioi tiedoston ja sen aikaleimat |
| `shutil.copytree(lahde, kohde)` | kopioi hakemistopuun |
| `shutil.move(lahde, kohde)` | siirtää, myös tiedostojärjestelmästä toiseen |
| `shutil.make_archive(nimi, "gztar", juuri)` | pakkaa hakemiston arkistoksi |
| `shutil.disk_usage(polku)` | levytila ennen suurta ajoa |
| `shutil.rmtree(polku)` | poistaa puun; ks. sudenkuoppa alla |

## Käytännössä

- **`pathlib` aina, merkkijonopolut vain reunalla.** Ulkoiselle
  työkalulle polku annetaan `str(polku)`.
- **Lajittele.** Tiedostojärjestelmän järjestykseen nojaava tuloste
  muuttuu koneelta toiselle, ja raporttien vertailu hajoaa.
- **Atominen kirjoitus kaikelle, mitä joku muu lukee.** Erityisesti
  tulostiedostoille, joiden perusteella CI päättää jatkamisesta.
- **Suhteelliset polut skriptin sijainnista**, ei työhakemistosta:
  `Path(__file__).parent / "malli.toml"`. Työkalua ajetaan mistä
  tahansa hakemistosta.
- **Sudenkuoppa:** `shutil.rmtree` käyttäjän antamalle polulle ilman
  tarkistusta. Tyhjä merkkijono tai `.` poistaa väärän puun. Tarkista,
  että poistettava on työkalun oma hakemisto.
- **Sudenkuoppa:** `os.listdir` ja merkkijonojen yhdistely `+ "/" +`.
  Polku, jossa on välilyöntejä, ääkkösiä tai Windowsin erottimia,
  rikkoo sen.

## Itsearviointi

- Osaat käydä hakemistopuun läpi `glob`illa ja `rglob`illa ja tuottaa
  deterministisen tuloksen.
- Osaat kirjoittaa tiedoston atomisesti ja perustella, miksi
  tilapäistiedosto on kohteen vieressä.
- Osaat käyttää tilapäishakemistoja välituotteille ja testeille.
- Osaat kopioida, siirtää ja arkistoida tiedostoja `shutil`-modulilla.
