# Aliprosessit ja ulkoiset työkalut

Insinöörin työkalu ohjaa usein toisia työkaluja: simulaattoria,
synteesityökalua, kääntäjää tai versionhallintaa. Python on niiden
liimakieli. `subprocess.run` käynnistää ohjelman, odottaa sen
päättymistä ja palauttaa paluuarvon sekä tulosteet.

## Komento listana

Komento annetaan listana: ensimmäinen alkio on ohjelma, loput sen
argumentteja. Komentotulkkia ei käynnistetä, joten argumentit
välittyvät sellaisinaan, eikä välilyönti, puolipiste tai lainausmerkki
tiedostonimessä muuta komentoa:

```{.python tiedosto="esimerkit/07-lainaus.py" osa="lainaus"}
```

```{.tuloste tiedosto="esimerkit/07-lainaus.odotettu"}
```

`shell=True` merkkijonon kanssa antoi käyttäjän syötteen
komentotulkille, ja `echo HYÖKKÄYS` suoritettiin. Sama aukko kaataa
työkalun tavallisella tiedostonimellä, jossa on välilyönti. Jos
komentotulkkia tarvitaan (putket, uudelleenohjaukset), jokainen arvo
lainataan `shlex.quote`lla. `shlex.join` muotoilee komennon lokiin
niin, että sen voi kopioida ja ajaa sellaisenaan.

## Yksi ajo: paluuarvo, tulosteet ja aikaraja

Esimerkissä ulkoisena työkaluna on pieni simulaattorin korvike, joka
käyttäytyy kuin oikea komentorivisimulaattori: loki tulosteeseen,
paluuarvo 0 tai 1. Yksi testi jumittuu ja yksi kaatuu
työkaluvirheeseen:

```{.python tiedosto="esimerkit/07-ajot/simulaattori.py"}
```

Ajofunktio luokittelee lopputuloksen. Paluuarvo ei yksin riitä:
simulaattori voi palauttaa nollan, vaikka testipenkki raportoi
virheitä, tai epäonnistua syystä, joka ei liity testattavaan piiriin:

```{.python tiedosto="esimerkit/07-ajot/main.py" osa="aja"}
```

- **`capture_output=True, text=True`** kerää tulosteet merkkijonoiksi.
  Suurilla tulosteilla kannattaa ohjata tuloste tiedostoon
  (`stdout=f`), jottei kaikki ole muistissa.
- **`timeout`** on pakollinen kaikelle, mikä voi jumittua. `run`
  tappaa lapsiprosessin aikarajan ylittyessä ja nostaa
  `TimeoutExpired`in.
- **`check=False` ja oma tulkinta.** Tulos luokitellaan itse.

`check=True` nostaa `CalledProcessError`in nollasta poikkeavalla
paluuarvolla. Se sopii, kun epäonnistuminen on aina virhe:

```{.python tiedosto="esimerkit/07-ajot/main.py" osa="check"}
```

## Monta ajoa rinnakkain

Regressioajossa on kymmeniä tai satoja simulaatioita. Ne ajetaan
rinnakkain säiepoolilla. Säikeet riittävät, koska varsinainen työ
tehdään lapsiprosesseissa, ja Python vain odottaa. Globaali
tulkkilukko (GIL) ei rajoita odottamista:

```{.python tiedosto="esimerkit/07-ajot/main.py" osa="rinnakkain"}
```

```{.tuloste tiedosto="esimerkit/07-ajot.odotettu"}
```

Jumittunut testi ei pysäyttänyt muita, ja työkaluvirhe erottuu
testin epäonnistumisesta. Ensimmäistä tarvitaan, kun lisenssipalvelin
on alhaalla, jälkimmäistä, kun piirissä on vika. `pool.map` palauttaa
tulokset syötteen järjestyksessä, vaikka ajot valmistuisivat eri
järjestyksessä. Raportti pysyy siksi deterministisenä.

Rinnakkaisuuden aste valitaan resurssien mukaan: simulaattorilisenssit,
muisti ja ytimet. `os.process_cpu_count()` (Python 3.13+) tai
`len(os.sched_getaffinity(0))` kertoo käytettävissä olevat ytimet.
Raskas laskenta Pythonissa itsessään vaatisi prosessipoolin
(`ProcessPoolExecutor`), koska tulkkilukko estää säikeitä laskemasta
Python-koodia rinnakkain.

## Käytännössä

- **Lista, ei merkkijono; `shell=True` vain lainattuna.** Tämä on
  komentoinjektion ja välilyöntivirheiden yleisin lähde.
- **Aikaraja kaikelle.** Jumittunut simulaatio pysäyttää koko yön
  regressioajon ja varaa lisenssin.
- **Erota työkalun ja testin epäonnistuminen.** Eri vika vaatii eri
  toimenpiteen ja eri ihmisen.
- **`sys.executable` Python-alityökaluille**, ei `"python3"`. Se on
  sama tulkki ja sama virtuaaliympäristö kuin kutsujalla.
- **Tallenna komento lokiin `shlex.join`illa.** Epäonnistuneen ajon
  voi toistaa käsin kopioimalla.
- **Sudenkuoppa:** `Popen` ilman `communicate`a ja täyttyvä putki.
  Kun lapsi kirjoittaa enemmän kuin putken puskuri vetää, molemmat
  odottavat toisiaan ikuisesti. `run` ja `communicate` hoitavat tämän.
- **Sudenkuoppa:** ympäristömuuttujat. Lapsi perii ympäristön.
  Lisenssipalvelin, lokaali ja polut annetaan tarvittaessa
  `env=`-parametrilla kopioimalla `os.environ` ja muuttamalla
  kopiota.

## Itsearviointi

- Osaat käynnistää ulkoisen ohjelman listana ja perustella, miksi
  `shell=True` merkkijonon kanssa on vaarallinen.
- Osaat käsitellä paluuarvon, tulosteet ja aikarajan ja luokitella
  lopputuloksen.
- Osaat ajaa ulkoisia ohjelmia rinnakkain säiepoolilla ja tuottaa
  deterministisen raportin.
