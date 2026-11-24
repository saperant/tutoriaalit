# Syvyys, sapluuna ja sekoitus

Rasteroinnin jälkeen jokaiselle fragmentille tehdään kiinteät testit
ja kirjoitus: sapluunatesti, syvyystesti ja lopuksi sekoitus
kehyspuskurin vanhan arvon kanssa. Nämä vaiheet ratkaisevat, mikä
näkyy: ilman niitä viimeisenä piirretty peittää aina aiemmat.

## Syvyyspuskuri

Syvyyspuskuri tallentaa jokaiselle pikselille lähimmän tähän asti
piirretyn pinnan syvyyden. Uusi fragmentti kirjoitetaan vain, jos se
läpäisee vertailun (`glDepthFunc`, tavallisesti `GL_LESS`: lähempi
voittaa), ja silloin myös syvyys päivitetään.

Esimerkki piirtää yhden suorakulmion ohjelmalla, jonka uniformit ovat
alue, syvyys ja väri:

```{.cpp tiedosto="esimerkit/06-syvyys.cpp" osa="glsl"}
```

```{.cpp tiedosto="esimerkit/06-syvyys.cpp" osa="suorakulmio"}
```

Molemmissa puoliskoissa piirretään ensin lähempi vihreä ja sitten
kauempi punainen suorakulmio:

```{.cpp tiedosto="esimerkit/06-syvyys.cpp" osa="syvyys"}
```

![Vasemmalla ilman syvyystestiä, oikealla testin kanssa. Alhaalla läpinäkyvät neliöt eri järjestyksissä.](kuvat/06-syvyys.png){width=40%}

Ilman syvyystestiä myöhemmin piirretty punainen peittää vihreän,
vaikka se on kauempana. Testin kanssa järjestyksellä ei ole väliä.
Tämä on syvyyspuskurin arvo: läpinäkymättömät pinnat voi piirtää
missä järjestyksessä tahansa.

### Syvyyden tarkkuus

Perspektiiviprojektion jälkeen syvyys ei ole lineaarinen: valtaosa
24-bittisen puskurin tarkkuudesta käytetään lähitason läheisyyteen.
Jos lähitaso on liian lähellä (esim. 0,001), kaukaiset pinnat
välkkyvät päällekkäin (*z-fighting*). Korjauksia on kaksi: lähitaso
niin kauas kuin mahdollista, tai *käänteinen syvyys* (reversed-Z),
jossa lähitaso kuvautuu ykköseksi ja kaukotaso nollaksi ja puskurina
käytetään 32-bittistä liukulukua. Käänteinen syvyys tasaa tarkkuuden
koko näkymään, ja se on nykyisten pelimoottorien oletus.

## Sapluuna

Sapluunapuskuri (stencil) on pikselikohtainen 8-bittinen laskuri.
Fragmentti voi verrata sitä viitearvoon ja kasvattaa, vähentää tai
korvata sen. Sapluunalla rajataan piirtoa (peili- ja porttinäkymät,
käyttöliittymän leikkaukset), merkitään alueita (ääriviivat valituille
kohteille) ja mitataan. Luku 12 käyttää sitä ylipiirron
laskemiseen.

## Sekoitus

Läpinäkyvät pinnat yhdistetään kehyspuskurin vanhaan arvoon
sekoitusyhtälöllä. Tavallinen "yli"-sekoitus on

tulos = α · lähde + (1 − α) · kohde.

```{.cpp tiedosto="esimerkit/06-syvyys.cpp" osa="sekoitus"}
```

```{.tuloste tiedosto="esimerkit/06-syvyys.odotettu"}
```

Sama kaksi neliötä eri järjestyksessä antaa eri värin: viimeisenä
piirretyn osuus on 50 %, ensimmäisen 25 %. Sekoitus ei ole
vaihdannainen, joten läpinäkyvät pinnat on piirrettävä kaukaisimmasta
lähimpään. Siksi pelimoottorit piirtävät ensin kaikki
läpinäkymättömät pinnat (syvyystesti ja -kirjoitus päällä, järjestys
vapaa) ja sitten läpinäkyvät takaa eteen lajiteltuina (syvyystesti
päällä, syvyyskirjoitus pois). Lajittelu kohteittain ei ratkaise
leikkaavia tai sisäkkäisiä pintoja; niille on järjestyksestä
riippumattomia menetelmiä (order-independent transparency), jotka ovat
kalliita.

**Esikerrottu alfa** (premultiplied alpha) tallentaa värin valmiiksi
alfalla kerrottuna ja sekoittaa yhtälöllä `GL_ONE`,
`GL_ONE_MINUS_SRC_ALPHA`. Se toimii oikein myös suodatuksessa ja
mip-tasoissa, joissa tavallinen alfa tuottaa tummia reunoja.

## Käytännössä

- **Läpinäkymättömät ensin, läpinäkyvät lajiteltuina perään.**
  Läpinäkymättömien järjestyksellä on väliä vain suorituskyvylle:
  edestä taakse piirto hyödyntää aikaista syvyystestiä (luku 12).
- **Lähitaso kauas tai käänteinen syvyys.** Älä pienennä
  lähitasoa vain siksi, että kamera leikkaa seinän läpi; ratkaise se
  törmäyksillä.
- **Esikerrottu alfa oletuksena.** Se välttää reunaongelmat ja tekee
  additiivisen ja tavallisen sekoituksen yhdistämisestä helppoa.
- **Sekoitus kuluttaa kaistaa**, koska kehyspuskurin vanha arvo on
  luettava. Isot läpinäkyvät pinnat (savu, käyttöliittymä koko ruudun
  päällä) ovat kalliita erityisesti mobiililaitteilla.

## Itsearviointi

- Osaat käyttää syvyystestiä ja selittää, miksi läpinäkymättömät
  pinnat voi piirtää missä järjestyksessä tahansa.
- Osaat selittää syvyyden epälineaarisuuden, z-fightingin ja
  käänteisen syvyyden idean.
- Osaat määrittää sekoitusyhtälön ja selittää, miksi läpinäkyvät
  pinnat on lajiteltava.
- Osaat kertoa, mihin sapluunapuskuria käytetään.
