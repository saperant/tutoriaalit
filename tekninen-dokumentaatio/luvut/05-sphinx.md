# Sphinx

Sphinx on Python-maailman dokumentaatiotyökalu, jolla on rakennettu
muun muassa Pythonin oma ja Linux-ytimen dokumentaatio. Sen vahvuus on
ristiviittaukset: dokumentti viittaa funktioon nimellä, ja Sphinx
tietää, onko kohde olemassa.

## Projekti

Sphinx-projekti on hakemisto, jossa on asetustiedosto `conf.py` ja
lähdetiedostot. Etusivun `toctree`-direktiivi kokoaa sivut puuksi
(luku 2). Asetuksista olennaisimmat ovat laajennukset ja tarkistusten
tiukkuus:

```{.python tiedosto="esimerkit/sphinx/conf.py" osa="laajennukset"}
```

Asetus `nitpicky` on oletuksena pois päältä, jolloin viittaus
olemattomaan funktioon jää hiljaa pelkäksi tekstiksi. Se kannattaa
kytkeä päälle heti projektin alussa: sadan varoituksen korjaaminen
jälkikäteen on työläämpää kuin yhden kerrallaan.

## Viite koodista

Laajennus `autodoc` tuo moduulin, lukee sen docstringit ja tuottaa
niistä viitesivun. Viitesivun lähde on siksi lyhyt:

```{.rst tiedosto="esimerkit/sphinx/viite.rst"}
```

Itse sisältö on koodissa (luku 7), joten viite ei voi kuvata
funktiota, jota ei ole. Laajennus `napoleon` muuntaa Googlen ja NumPyn
tyylin docstringit Sphinxin omaan merkintään, ja asetus
`autodoc_typehints` näyttää tyyppivihjeet parametrien kuvauksissa,
joten tyyppiä ei kirjoiteta kahteen paikkaan.

Koska `autodoc` tuo moduulin, moduulin tuonnilla ei saa olla
sivuvaikutuksia. Skripti, joka avaa tietokantayhteyden tuotaessa,
avaa sen myös dokumentaatiota rakennettaessa.

## Ristiviittaukset

Rooli liittää tekstin kohteeseen. Yleisimmät:

| Rooli | Kohde | Esimerkki |
|-----------|-------------------------|-----------------------------------|
| `:doc:` | toinen sivu | `` :doc:`ohjeet` `` |
| `:ref:` | nimetty kohta sivulla | `` :ref:`asennus` `` |
| `:func:` | funktio | `` :func:`saa.tilasto.yhteenveto` `` |
| `:class:` | luokka | `` :class:`~saa.lukema.Lukema` `` |
| `:mod:` | moduuli | `` :mod:`saa.tilasto` `` |
| `:exc:` | poikkeus | `` :exc:`saa.lukema.LukemaVirhe` `` |

Aaltoviiva nimen edessä näyttää tekstissä vain viimeisen osan
(`Lukema` eikä `saa.lukema.Lukema`). Kun funktio nimetään uudelleen,
jokainen siihen viittaava sivu tuottaa varoituksen, joten vanhentunut
viittaus ei jää huomaamatta.

Toisen projektin kohteisiin viitataan laajennuksella `intersphinx`,
joka lataa kohdeprojektin julkaiseman luettelon `objects.inv`.
Esimerkkiprojekti ei käytä sitä, koska rakennus ei saa riippua
verkosta; standardikirjaston tyypit on siksi merkitty asetuksissa
tunnetuiksi poikkeuksiksi.

## Esimerkit testeinä

Laajennus `doctest` ajaa dokumenttisivujen esimerkit. Direktiivi
`doctest` sisältää tulkin istunnon (luvun 4 opas), ja pari `testcode`
ja `testoutput` kokonaisen ohjelman ja sen tulosteen:

```{.rst tiedosto="esimerkit/sphinx/ohjeet.rst"}
```

Jos kirjaston virheilmoitus muuttuu, ohjeen esimerkki epäonnistuu
rakennuksessa. Opas on juuri se dokumentti, jonka jokaisen askeleen
pitää toimia, ja tällä tavalla se myös pysyy toimivana.

## Varoitukset virheinä

Rakennuskomento on `sphinx-build`. Kolme valitsinta tekee siitä
tarkistuksen:

```{.makefile tiedosto="esimerkit/Makefile" osa="sphinx"}
```

Kohde rakentaa HTML:n, ajaa esimerkit ja vertaa dokumentoitujen
kohteiden luetteloa tallennettuun. Lopuksi se tekee lähteistä kopion,
lisää siihen viittauksen funktioon, joka on poistettu, ja varmistaa,
että rakennus epäonnistuu juuri siihen:

```{.tuloste tiedosto="esimerkit/sphinx/rikki.odotettu"}
```

Kohdeluettelo luetaan tiedostosta `objects.inv`, jonka Sphinx
kirjoittaa jokaisen rakennuksen yhteydessä:

```{.python tiedosto="esimerkit/tyokalut/kohteet.py" osa="sphinx"}
```

```{.tuloste tiedosto="esimerkit/sphinx/kohteet.odotettu"}
```

Luettelo on rajapinnan dokumentoitu pinta. Kun joku lisää julkisen
funktion ilman viitettä tai poistaa dokumentoidun, luettelo muuttuu,
ja muutos näkyy katselmoinnissa. HTML:n vertaaminen tavu tavulta ei
toimisi: se muuttuu jokaisessa Sphinxin versiossa.

## Käytännössä

- **`-W` ja `nitpicky` alusta asti.** Varoitus, joka ei pysäytä
  rakennusta, jää korjaamatta.
- **Viite generoidaan, opas kirjoitetaan.** `autodoc` ei tee
  dokumentaatiota valmiiksi: se tekee yhden neljästä tyypistä.
- **Viittaa rooleilla, älä kirjoita nimiä koodina.** `` `yhteenveto` ``
  on pelkkää tekstiä; `` :func:`saa.tilasto.yhteenveto` `` on
  tarkistettu linkki.
- **Älä tuo sivuvaikutuksia.** Moduulin pitää olla tuotavissa ilman
  verkkoa, tietokantaa ja komentoriviargumentteja.
- **Teema viimeisenä.** Sisältö ja rakenne ratkaisevat. Teeman voi
  vaihtaa yhdellä rivillä, sekavaa rakennetta ei.
- **Muut kielet.** Sphinx ei ole vain Pythonille: C- ja C++-koodin
  Doxygen-kuvaukset saa samaan dokumentaatioon Breathe-laajennuksella,
  ja Markdownia voi kirjoittaa MyST-laajennuksella.

## Itsearviointi

- Osaat pystyttää Sphinx-projektin ja tuottaa viitesivun
  docstringeistä.
- Osaat viitata funktioon, luokkaan ja toiseen sivuun roolilla ja
  kertoa, mitä rakennus tekee, kun kohde puuttuu.
- Osaat kirjoittaa dokumenttisivulle esimerkin, joka ajetaan testinä.
- Osaat selittää, miksi generoidusta dokumentaatiosta verrataan
  kohdeluetteloa eikä HTML:ää.
