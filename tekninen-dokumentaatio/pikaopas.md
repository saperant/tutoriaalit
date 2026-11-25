---
title: Tekninen dokumentaatio
subtitle: Pikaopas · lukijat · teksti · docs as code · viite koodista · arkkitehtuuri · tarkistukset
---

# Lukija ja tyyppi

| Tyyppi | Lukija haluaa | Muoto |
|--------|---------------|-------|
| opas | oppia | yksi polku, toimii varmasti |
| ohje | ratkaista ongelman | askeleet tavoitteeseen |
| viite | tarkistaa faktan | kattava, generoitu koodista |
| selitys | ymmärtää | perustelu ja vaihtoehdot |

- Yksi sivu, yksi tyyppi. Taustaa oppaaseen? Linkki selitykseen.
- README: mikä ja kenelle, kokeile, lisätiedot, lisenssi.
- Muutosloki: uusin ylimpänä, *Julkaisematon* kertyy matkan varrella,
  ryhmät Lisätty, Muutettu, Vanhentunut, Poistettu, Korjattu,
  Tietoturva.
- Toimintaohje: hälytys, tarkista, korjaa, varmista, kenelle soitetaan.

# Teksti

- Tärkein ensin: sivun, kappaleen ja luettelon alkuun.
- Tekijä näkyviin: ”Aja komento”, ei ”komento ajetaan”.
- Täsmällinen: luku ja yksikkö, ei ”nopea”.
- Yksi asia, yksi termi. Sanasto versionhallintaan.
- Ei ”helposti”, ”yksinkertaisesti”, ”tietenkin”.
- Esimerkki ennen sääntöä; kokonainen, todellinen ja ajettu.
- Koodin nimiä ei taivuteta: ”funktio `jasenna_rivi` palauttaa”.

# Kuvaus koodissa

```{.python tiedosto="esimerkit/saa/tilasto.py" osa="keskiarvo"}
```

- Sopimus: parametrit, paluuarvo, virheet, yksiköt, esimerkki.
- Miksi, ei mitä. Tyyppi allekirjoituksessa, ei kuvauksessa.
- C: kuvaukset otsakkeeseen, suunnat `[in]`, `[out]`, `[in,out]`.

```{.c tiedosto="esimerkit/c/puskuri.h" osa="lisaa"}
```

# Rakennus: varoitukset virheinä

| Työkalu | Komento | Löytää |
|---------|---------|--------|
| Sphinx | `sphinx-build -W --keep-going` ja `nitpicky = True` | viittaus olemattomaan |
| Sphinx | `sphinx-build -b doctest` | esimerkki ei toimi |
| MkDocs | `mkdocs build --strict` (ei `-q`) | rikkinäinen linkki tai ankkuri |
| Doxygen | `WARN_AS_ERROR = FAIL_ON_WARNINGS`, `EXTRACT_ALL = NO` | puuttuva tai väärä kuvaus |
| pytest | `--doctest-modules` | docstringin esimerkki |
| ruff | säännöstö `D` | julkinen nimi ilman docstringiä |

Jokaisella tarkistuksella on viallinen näyte, jonka on jäätävä kiinni.

# Sphinxin roolit

| Rooli | Kohde |
|-------|-------|
| `` :doc:`ohjeet` `` | sivu |
| `` :func:`saa.tilasto.yhteenveto` `` | funktio |
| `` :class:`~saa.lukema.Lukema` `` | luokka, lyhyt nimi |
| `` :mod:`saa.tilasto` `` | moduuli |

# OpenAPI

```{.yaml tiedosto="esimerkit/openapi/saa.yaml" osa="lukema"}
```

- Esimerkki jokaiselle toiminnolle; esimerkit ajetaan toteutusta vasten.
- Jokainen tilakoodi ja virherungon muoto kuvataan.
- Rikkova muutos: `deprecated: true`, muutosloki, uusi pääversio.

# Arkkitehtuuri

| C4-taso | Näyttää |
|---------|---------|
| 1 konteksti | järjestelmä, käyttäjät, naapurit |
| 2 kontit | ajettavat osat ja niiden yhteydet |
| 3 komponentit | kontin sisäiset osat (generoi koodista) |

- Laatikossa nimi, tekniikka ja vastuu; nuolella suunta ja teksti.
- Laatuvaatimus skenaariona: heräte, vaste, mittari.

Päätös (ADR): `NNNN-otsikko.md`, osiot Tausta, Päätös, Seuraukset.
Tilat: ehdotettu, hyväksytty, hylätty, korvattu. Päätöstä ei muokata:
uusi päätös korvaa vanhan.

```{.tuloste tiedosto="esimerkit/adr/hakemisto.odotettu"}
```

# Kaaviot

- Kaavio tekstinä versionhallintaan; kuvan piirtää rakennus.
- Koodista johdettava kaavio generoidaan ja verrataan testissä.
- Yksi kaavio, yksi kysymys; enintään kymmenkunta laatikkoa.

# Ylläpito

- Dokumentaatio samaan muutokseen kuin koodi ja valmiin määritelmään.
- Jokaisella sivulla omistaja; vanhentunut sivu poistetaan.
- Sisäiset linkit joka rakennuksessa, ulkoiset ajastetusti.
- Kysymys, joka esitetään kolmesti, kuuluu ohjeisiin.
