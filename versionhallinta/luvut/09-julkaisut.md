# Tagit, julkaisut ja alimodulit

Haara liikkuu, tagi ei. Julkaisu sidotaan tagiin, jotta "versio 1.2.0"
tarkoittaa aina täsmälleen samaa koodia. Tässä luvussa käsitellään myös
alimodulit, jotka sitovat toisen repositorion tiettyyn versioon.

## Kevyet ja annotoidut tagit

*Kevyt* tagi on pelkkä viite committiin, kuten haara, joka ei liiku.
*Annotoitu* tagi on oma olionsa: siinä on tekijä, aika ja viesti, ja sen
voi allekirjoittaa. Julkaisuihin käytetään annotoituja tageja:

```{.bash tiedosto="esimerkit/09-tagit.sh" osa="tagit"}
```

Tagit eivät siirry pushissa automaattisesti. `git push origin v1.0.0`
lähettää yhden ja `git push --follow-tags` annotoidut tagit, jotka
osoittavat pushattuihin committeihin. Julkaistua tagia ei siirretä:
jokainen, joka on jo hakenut sen, pitäisi vanhaa.

## Versionumerot ja describe

Semanttisessa versioinnissa (SemVer) numero on muotoa
`PÄÄ.SIVU.KORJAUS`: rajapintaa rikkova muutos kasvattaa pääversiota,
uusi yhteensopiva ominaisuus sivuversiota ja korjaus korjausversiota.
`git describe` kertoo nykyisen version suhteessa lähimpään annotoituun
tagiin. `v1.0.0-1-g544c816` tarkoittaa yhtä committia tagin jälkeen
commitissa `544c816`, ja `-dirty` valmistelemattomia muutoksia. Tunnisteen
voi upottaa käännökseen versiotiedoksi:

```{.bash tiedosto="esimerkit/09-tagit.sh" osa="describe"}
```

```{.tuloste tiedosto="esimerkit/09-tagit.odotettu"}
```

Aakkosjärjestyksessä `v1.10.0` tulisi ennen versiota `v1.2.0`.
`--sort=v:refname` järjestää versionumerot oikein.

## Alimodulit

Alimoduli on toisen repositorion tietty commit oman repositorion
alihakemistona. Pääprojekti tallentaa vain osoittimen: puussa on
*gitlink*-merkintä (tila `160000`), joka osoittaa alimodulin committiin.
Tiedosto `.gitmodules` kertoo, mistä alimoduli haetaan:

```{.bash tiedosto="esimerkit/09-alimodulit.sh" osa="lisays"}
```

Alimoduli ei seuraa lähteensä uusimpia muutoksia itsestään. Päivitys on
oma, tietoinen commitinsa pääprojektissa:

```{.bash tiedosto="esimerkit/09-alimodulit.sh" osa="paivitys"}
```

Kloonattaessa alimodulit eivät tule mukaan ilman valitsinta
`--recurse-submodules` (tai jälkikäteen `git submodule update --init
--recursive`):

```{.bash tiedosto="esimerkit/09-alimodulit.sh" osa="kloonaus"}
```

```{.tuloste tiedosto="esimerkit/09-alimodulit.odotettu"}
```

Alimodulit ovat tarkkoja mutta kömpelöitä. Unohtunut `update` jättää
vanhan version, alimodulin sisällä tehty commit voi jäädä irralliseen
HEADiin, ja jokainen kehittäjä tarvitsee lisäkomentoja. Kirjastoille
paketinhallinta (pip, npm, Cargo, Maven) versioineen on lähes aina parempi.
Alimoduli sopii, kun paketinhallintaa ei ole, kuten laiteohjelmistoissa,
HDL-projekteissa ja jaetuissa asetusrepositorioissa. Toinen vaihtoehto on
`git subtree`, joka kopioi toisen repositorion historian osaksi omaa.

## Käytännössä

- **Julkaisu = annotoitu tagi + CI.** Tagin push käynnistää julkaisuputken,
  joka rakentaa artefaktit juuri siitä commitista. Silloin julkaisu on
  toistettavissa.
- **Versio Gitistä, ei käsin.** `git describe --tags --dirty` tai
  setuptools-scm:n kaltainen työkalu tuottaa versiotunnisteen, jota ei
  unohdeta päivittää.
- **Muutosloki commit-viesteistä.** Rakenteiset viestit (esim.
  Conventional Commits) mahdollistavat muutoslokin ja versionumeron
  generoinnin.
- **Alimoduleille asetus `submodule.recurse true`**, jolloin `pull`,
  `switch` ja `checkout` päivittävät myös alimodulit.

## Itsearviointi

- Osaat tehdä annotoidun tagin, lähettää sen palvelimelle ja selittää,
  miksi julkaistua tagia ei siirretä.
- Osaat tulkita `git describe`n tulosteen ja järjestää versiot oikein.
- Osaat lisätä, päivittää ja kloonata alimodulin ja selittää, mitä
  pääprojekti siitä tallentaa.
- Osaat perustella, milloin alimoduli on parempi kuin paketinhallinta ja
  milloin huonompi.
