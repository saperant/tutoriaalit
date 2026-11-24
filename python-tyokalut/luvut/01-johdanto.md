# Johdanto {.runko-johdanto}

Insinöörityössä iso osa ohjelmoinnista on työkaluja: skripti, joka
jäsentää simulaattorin lokin, muuntaa rekisterikartan C-otsakkeeksi,
purkaa mittalaitteen binääritiedoston tai ajaa sata regressiotestiä
rinnakkain ja kokoaa tuloksista raportin. Työkalu kirjoitetaan usein
nopeasti, mutta sitä käytetään vuosia, ja siihen nojataan, kun
päätetään, onko piiri valmis valmistukseen.

Tämä tutoriaali opettaa kirjoittamaan tällaiset työkalut Pythonilla
niin, että ne ovat luotettavia, testattuja ja muiden käytettävissä.
Kielen idiomit ovat esitietona taidossa *Python*, ja komentorivin käyttö
taidossa *Komentorivi ja Linux*. Tästä jatketaan taitoon
*EDA-skriptaus*, jossa samoilla välineillä hallitaan
laitteistosuunnittelun työkaluketjuja.

## Mitä hyvä työkalu tekee

Hyvä komentorivityökalu käyttäytyy kuten Unixin perustyökalut, joten
sitä voi yhdistellä toisiin ja ajaa automaattisesti:

- **Tulokset tulosteeseen, diagnostiikka virhetulosteeseen.** Kun
  tuloste ohjataan tiedostoon tai seuraavalle ohjelmalle, varoitukset
  eivät sotke sitä.
- **Paluuarvo kertoo onnistumisen.** 0 on onnistuminen, muut arvot
  epäonnistumisia. CI-putki ja `make` päättävät jatkamisesta pelkän
  paluuarvon perusteella.
- **Syöte tiedostosta tai putkesta.** Ilman tiedostonimeä luetaan
  syötettä, jolloin työkalun voi panna putken keskelle.
- **Virheellinen syöte pysäyttää selvällä viestillä** heti reunalla,
  ennen kuin mitään on tehty.
- **Deterministinen tuloste.** Sama syöte tuottaa saman tuloksen.
  Tiedostojärjestelmän järjestys, sanakirjan täyttöjärjestys ja
  kellonaika eivät saa vuotaa tulokseen huomaamatta, muuten tuloksia
  ei voi verrata.

## Ensimmäinen työkalu

Simulaattori kirjoittaa lokiin rivejä, joissa on aika, taso ja
komponentti:

```{.text tiedosto="esimerkit/01-yhteenveto.syote"}
```

Työkalu laskee viestit tasoittain ja komponenteittain. Jäsentäminen on
oma funktionsa, joka palauttaa `None` rivillä, joka ei ole viesti:

```{.python tiedosto="esimerkit/01-yhteenveto.py" osa="jasenna"}
```

Laskenta ja tulostus erotetaan toisistaan. `main` saa argumentit
parametrina ja palauttaa paluuarvon, jonka `sys.exit` välittää
käyttöjärjestelmälle:

```{.python tiedosto="esimerkit/01-yhteenveto.py" osa="yhteenveto"}
```

```{.tuloste tiedosto="esimerkit/01-yhteenveto.odotettu"}
```

Tämä rakenne toistuu koko tutoriaalissa: puhtaat funktiot tekevät
työn, ja `main` kytkee ne syötteeseen, tulosteeseen ja paluuarvoon.
Puhtaita funktioita voi testata ilman aliprosesseja ja tiedostoja
(luku 10).

## Esimerkit ja työkalut

Esimerkit on testattu Python 3.12:lla. Ne tarkistetaan
`ruff`-tarkistimella ja `mypy --strict` -tyyppitarkistimella, ja niiden
tuloste verrataan odotettuun. NumPy ja matplotlib ovat ainoat
ulkoiset kirjastot. Kehityskontissa (`.devcontainer/python-tyokalut`)
on kaikki valmiina. Ilman konttia riittää virtuaaliympäristö:

```text
python3 -m venv .venv && . .venv/bin/activate
pip install numpy matplotlib ruff mypy pytest
```

## Tutoriaalin rakenne

Luku 2 rakentaa komentorivikäyttöliittymän ja luku 3 paketoi työkalun
asennettavaksi. Luvut 4–6 käsittelevät syötteitä: tekstimuodot,
binäärimuodot ja tiedostojärjestelmän. Luku 7 ohjaa ulkoisia
työkaluja, luvut 8–9 käsittelevät numeerista dataa ja kuvaajia, ja
luku 10 testaa kaiken. Jokainen luku päättyy osioihin *Käytännössä* ja
*Itsearviointi*. Jos osaat itsearvioinnin asiat, voit siirtyä
seuraavaan lukuun.
