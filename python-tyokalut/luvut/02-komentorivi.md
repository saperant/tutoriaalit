# Komentorivityökalut

Komentorivi on työkalun rajapinta, ja kuten muutkin rajapinnat, se
suunnitellaan. Pythonin vakiokirjaston `argparse` jäsentää argumentit,
tarkistaa ne, tuottaa ohjeen (`--help`) ja virheilmoitukset ja palauttaa
virheellisestä komentorivistä paluuarvon 2. Kolmannen osapuolen
kirjastot (Click, Typer) tekevät saman tiiviimmin, mutta `argparse` on
aina saatavilla ja riittää lähes kaikkeen.

## Alikomennot

Kun työkalu tekee useaa toisiinsa liittyvää asiaa, alikomennot (kuten
`git commit` ja `git log`) pitävät rajapinnan selkeänä. Esimerkin
työkalussa on kaksi alikomentoa: `yhteenveto` laskee viestit
tasoittain, ja `virheet` suodattaa viestit tason ja komponentin
mukaan:

```{.python tiedosto="esimerkit/02-lokityokalu.py" osa="jasennin"}
```

- `set_defaults(toiminto=...)` liittää alikomentoon funktion. `main`
  kutsuu `args.toiminto(args)` eikä vertaile komennon nimeä.
- `choices` rajaa arvot. Väärä arvo pysäyttää jäsennyksen ennen kuin
  mitään on tehty.
- `nargs="*"` sallii nollan tai useamman tiedoston. Tyhjä lista
  tarkoittaa syötettä.
- `%(default)s` ohjetekstissä näyttää oletusarvon, joten ohje ei
  vanhene, kun oletus muuttuu.

Alikomentojen funktiot saavat valmiiksi jäsennetyt argumentit ja
palauttavat paluuarvon:

```{.python tiedosto="esimerkit/02-lokityokalu.py" osa="komennot"}
```

`yhteenveto --tiukka` palauttaa 1, jos lokissa on virheitä. Näin
CI-putki tai `make` voi pysähtyä virheeseen ilman lokin lukemista:
`lokityokalu yhteenveto --tiukka sim.log && make raportti`.

Esimerkki ajetaan argumenteilla `virheet --taso WARNING -`, ja loki
tulee syötteestä:

```{.tuloste tiedosto="esimerkit/02-lokityokalu.odotettu"}
```

## Tulosteet, lokitus ja putket

`main` kytkee jäsennyksen, lokituksen ja virheenkäsittelyn yhteen:

```{.python tiedosto="esimerkit/02-lokityokalu.py" osa="main"}
```

- **Tulokset `print`illä tulosteeseen, diagnostiikka `logging`illa
  virhetulosteeseen.** `-v` lisää diagnostiikkaa muuttamatta
  tulostetta.
- **Odotetut virheet paluuarvoksi, ei pinojäljeksi.** Puuttuva tiedosto
  on käyttäjän virhe: siitä kerrotaan yksi rivi ja palautetaan 2.
  Ohjelmointivirhe saa näkyä pinojälkenä, koska sen korjaaminen
  vaatii pinojäljen.
- **Suljettu putki.** Kun tuloste ohjataan `head`-komennolle, `head`
  sulkee putken luettuaan tarvitsemansa, ja seuraava kirjoitus
  aiheuttaa `BrokenPipeError`in. Työkalu lopettaa hiljaa, kuten
  Unixin työkalut. `BrokenPipeError` on `OSError`in aliluokka, joten
  sen käsittely tulee ensin.
- **`main(argv=None)`.** Testi voi kutsua `main(["virheet", "x.log"])`
  ilman aliprosessia, ja `None` tarkoittaa `sys.argv`-listaa.

Komentorivin ohje syntyy määrittelyistä:

```text
$ python3 02-lokityokalu.py virheet --help
usage: lokityokalu virheet [-h] [--taso {WARNING,ERROR,FATAL}]
                           [--komponentti NIMI]
                           [TIEDOSTO ...]
```

Ohjeen tarkka muotoilu vaihtelee Python-versioittain ja päätteen
leveyden mukaan, joten sitä ei kannata verrata testeissä.

## Argumenttien tarkistus

`type`-parametri voi olla mikä tahansa funktio, joka muuntaa
merkkijonon arvoksi. Kun funktio nostaa `ArgumentTypeError`in, argparse
näyttää sen viestin käyttäjälle. Yksiköt kannattaa jäsentää tässä
vaiheessa, jotta muu ohjelma käsittelee vain hertsejä eikä merkkijonoja:

```{.python tiedosto="esimerkit/02-validointi.kaatuu.py" osa="tyypit"}
```

Esimerkki jäsentää ensin oikean komentorivin ja sitten virheellisen
`--kello 100XHz uart`. argparse tulostaa käyttöohjeen ja virheen
virhetulosteeseen ja lopettaa paluuarvolla 2:

```text
uart: kello 125000000 Hz, siemen 7
usage: aja-sim [-h] --kello KELLO [--siemen SIEMEN] testi
aja-sim: error: argument --kello: virheellinen taajuus '100XHz', esim. 100MHz
```

## Käytännössä

- **Paluuarvot ovat osa rajapintaa.** Dokumentoi ne ohjeessa (0
  onnistui, 1 tulos ei kelpaa, 2 käyttövirhe) ja pidä ne vakaina.
  Skriptit ja CI nojaavat niihin.
- **Ei interaktiivisia kysymyksiä.** Työkalu, joka kysyy
  vahvistusta, jumittaa CI-putken. Vaarallinen toiminto saa lipun
  (`--pakota`), ja kuivaharjoitus (`--kuiva`) näyttää, mitä tehtäisiin.
- **Pitkät valitsimet skripteihin, lyhyet käsin kirjoittamiseen.**
  `--taso` on luettavampi skriptissä kuin `-t`.
- **Konfiguraation järjestys:** oletusarvo < asetustiedosto <
  ympäristömuuttuja < komentorivi. Komentorivi voittaa aina, koska se
  on käyttäjän tuorein tahto.
- **Logging-kirjasto oikein.** Kirjastomoduuli luo oman lokittajansa
  (`logging.getLogger(__name__)`) eikä koskaan kutsu `basicConfig`ia.
  Vain `main` päättää, mihin ja millä tasolla lokitetaan.
- **Sudenkuoppa:** `print` virhetulosteen sijaan tulosteeseen. Kun
  käyttäjä ohjaa tuloksen tiedostoon, virheilmoitus päätyy tiedostoon
  ja näyttää datalta.

## Itsearviointi

- Osaat rakentaa argparse-jäsentimen alikomennoilla ja liittää
  alikomentoon funktion `set_defaults`illa.
- Osaat kirjoittaa `type`-funktion, joka tarkistaa ja muuntaa arvon ja
  antaa selvän virheilmoituksen.
- Osaat erottaa tulokset ja diagnostiikan tulosteen ja
  virhetulosteen välillä ja asettaa lokituksen tason valitsimella.
- Osaat suunnitella paluuarvot ja käsitellä suljetun putken.
