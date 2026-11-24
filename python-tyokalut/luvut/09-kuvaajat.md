# Kuvaajat tiedostoon

Raporttiin, katselmointiin ja CI:n tuloksiin tarvitaan kuvaajia:
mittaussignaali, ajoitusmarginaalien jakauma, regressioajojen trendi.
Työkalu tuottaa ne tiedostoon ilman näyttöä. Matplotlib on Pythonin
vakiintunut kuvaajakirjasto. Sen olio-rajapinta sopii työkaluihin
paremmin kuin tutoriaaleista tuttu `pyplot`.

## Olio-rajapinta ilman pyplotia

`pyplot` pitää yllä globaalia "nykyistä kuvaa" ja valitsee
taustaosan ympäristön mukaan. Interaktiivisessa käytössä se on kätevä,
mutta työkalussa haitallinen: kuvat jäävät muistiin, jos niitä ei
suljeta, rinnakkaiset kuvat sekoittuvat, ja palvelimella ilman näyttöä
taustaosan valinta voi epäonnistua. `matplotlib.figure.Figure`
luodaan suoraan, se piirtää Agg-taustaosalla tiedostoon ja vapautuu
kuten mikä tahansa olio:

```{.python tiedosto="esimerkit/09-kuvaaja.py" osa="kuvaaja"}
```

- `figsize` ja `dpi` määräävät kuvan koon pikseleinä (8 × 100 = 800).
- `layout="constrained"` sovittaa akselien nimet ja selitteen kuvaan
  leikkaamatta.
- `savefig` päättelee muodon päätteestä. PDF ja SVG ovat
  vektorimuotoja, ja ne skaalautuvat raporttiin terävinä.
- `ax.set(...)` asettaa useita ominaisuuksia kerralla.

Esimerkin kuva:

![Syöttöjännitteen mittaus, kynnys ja ylitykset.](kuvat/mittaus.png){width=100%}

## Kuvan testaaminen

Kuvaa ei kannata verrata tavu tavulta: kirjasto- ja fonttiversiot
muuttavat pikseleitä, vaikka kuva on oikea. Testataan sen sijaan, että
kuva syntyy, se on oikeaa muotoa ja kokoa ja sen data on oikea. Koko
luetaan PNG-tiedoston otsakkeesta luvun 5 tekniikalla:

```{.python tiedosto="esimerkit/09-kuvaaja.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/09-kuvaaja.odotettu"}
```

Piirtokoodi ja datan laskenta pidetään erillään. Tunnusluvut ja
ylitykset testataan suoraan funktioista, ja kuvaajan testi varmistaa
vain, että piirto onnistuu. Jos kuvan ulkoasu on itsessään
vaatimus, pikselivertailuun toleransseineen on valmiita työkaluja
(`matplotlib.testing`, pytest-mpl).

## Käytännössä

- **`Figure`-olio työkaluissa, `pyplot` interaktiivisessa käytössä.**
  Jos `pyplot`ia käytetään, jokainen kuva suljetaan (`plt.close(fig)`),
  muuten muisti kasvaa jokaisella kuvalla.
- **Vektorimuoto raportteihin** (PDF, SVG), PNG verkkosivuille ja
  hyvin tiheälle datalle, jonka vektoriesitys olisi raskas.
- **Akselit yksiköineen ja otsikko**, joka kertoo mitä mitattiin.
  Kuva irtoaa raportista sähköpostiin ja diaesitykseen.
- **Ei taustaosan valintaa koodissa.** `Figure` ja `savefig` toimivat
  ilman `matplotlib.use("Agg")`-kutsua. Jos `pyplot`ia käytetään
  palvelimella, taustaosan voi asettaa ympäristömuuttujalla
  `MPLBACKEND=Agg`.
- **Sudenkuoppa:** tuhansien pisteiden hajontakuva PDF:nä. Jokainen
  piste on oma vektorielementtinsä. `rasterized=True` piirtosarjalle
  tai PNG pitää tiedoston pienenä.

## Itsearviointi

- Osaat piirtää kuvaajan tiedostoon matplotlibin olio-rajapinnalla
  ilman näyttöä.
- Osaat perustella, miksi `pyplot`in globaali tila on työkaluissa
  haitallinen.
- Osaat testata kuvaajaa tuottavan työkalun ilman pikselivertailua.
