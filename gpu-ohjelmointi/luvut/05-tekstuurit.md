# Tekstuurit ja kehyspuskurit

Tekstuuri on GPU:n muistissa oleva kuva, jota varjostin lukee
*näytteistimen* (sampler) kautta. Näytteistin tekee laitteistossa
kolme asiaa: muuntaa koordinaatit 0–1 tekseleiksi, käsittelee reunat
(toisto, peilaus, venytys) ja *suodattaa* eli laskee arvon
lähimmistä tekseleistä. Kaikki tämä tapahtuu tekstuuriyksikössä,
eikä se maksa varjostimen käskyjä.

## Tekstuurin luonti

```{.cpp tiedosto="esimerkit/05-tekstuurit.cpp" osa="tekstuuri"}
```

`glTextureStorage2D` varaa kaikki mip-tasot kerralla
muuttumattomana. Tasoja on log₂(koko) + 1: 256×256-tekstuurilla
yhdeksän, kooltaan 256, 128, …, 1. `glGenerateTextureMipmap` laskee
pienemmät tasot keskiarvoina. Oikeissa sovelluksissa mip-tasot
lasketaan etukäteen työkalussa ja tekstuurit tallennetaan GPU:n
pakattuihin muotoihin (BC, ASTC, ETC), jotka vievät neljäsosan tai
vähemmän muistia ja kaistaa.

## Suodatus suurennettaessa

Varjostimet piirtävät koko ruudun kattavan kolmion, jonka UV-
koordinaatit kulkevat nollasta yhteen kuvan yli:

```{.cpp tiedosto="esimerkit/05-tekstuurit.cpp" osa="glsl"}
```

2×2-ruutukuvio venytetään 64×64 pikseliin:

```{.cpp tiedosto="esimerkit/05-tekstuurit.cpp" osa="suurennus"}
```

```{.tuloste tiedosto="esimerkit/05-tekstuurit.odotettu"}
```

Lähin teksel (`GL_NEAREST`) antaa terävät reunat, joten jokainen
teksel näkyy 32×32-ruutuna. Lineaarinen suodatus (`GL_LINEAR`)
interpoloi neljän lähimmän tekselin välillä, jolloin syntyy liukuma.
Pikselitaiteessa ja tietotaulukoissa (hakutaulut) halutaan lähin
teksel, valokuvamaisissa pinnoissa lineaarinen.

## Suodatus pienennettäessä ja mip-tasot

Kun 256 pystyraitaa piirretään 32 pikseliin, yhteen pikseliin osuu
kahdeksan tekseliä. Ilman mip-tasoja näytteistin lukee yhden tekselin
ja ohittaa muut, jolloin tulos riippuu siitä, mihin näyte osuu. Tässä
jokainen näyte osui mustaan raitaan, ja koko rivi on musta, vaikka
oikea keskiarvo on harmaa. Tämä on **laskostumista** (aliasing), ja
liikkuvassa kuvassa se näkyy välkkeenä ja moiré-kuvioina.

```{.cpp tiedosto="esimerkit/05-tekstuurit.cpp" osa="pienennys"}
```

Mip-tasoilla näytteistin valitsee tason, jonka tekselit ovat suunnilleen
pikselin kokoisia, ja lukee siltä. `GL_LINEAR_MIPMAP_LINEAR`
(trilineaarinen suodatus) interpoloi lisäksi kahden lähimmän tason
välillä. Taso valitaan UV-koordinaattien derivaatoista naapuripikselien
välillä, minkä vuoksi fragmentit ajetaan 2×2-ryhminä (luku 2).

Vinoon katsotuilla pinnoilla, kuten lattialla tai tiellä, pikselin
peittämä alue tekstuurissa on venynyt. **Anisotrooppinen suodatus**
(`GL_TEXTURE_MAX_ANISOTROPY`) ottaa useita näytteitä venymän
suunnassa ja pitää kuvan terävänä.

## Kehyspuskurit ja piirto tekstuuriin

Kehyspuskuri (framebuffer object, FBO) kokoaa liitännät, joihin piirto
menee: yksi tai useampi värikuva, syvyys ja sapluuna. Liitännät ovat
tekstuureja tai *renderöintipuskureita* (renderbuffer), joita ei voi
lukea varjostimessa mutta jotka ajuri voi tallentaa tehokkaammin.
Tämän tutoriaalin `Kehys`-luokka (luku 3) käyttää värille
tekstuuria ja syvyydelle renderöintipuskuria.

Kun väriliitäntä on tekstuuri, sitä voi seuraavassa vaiheessa lukea
toisessa varjostimessa. Tämä *piirto tekstuuriin* (render to texture)
on lähes kaikkien nykyisten tekniikoiden perusta: varjokartat,
viivästetty varjostus (luku 11), heijastukset, jälkikäsittely (bloom,
sumennus, sävykartoitus) ja käyttöliittymän koostaminen.

Yhtä tekstuuria ei saa lukea ja kirjoittaa samassa piirrossa, ellei
käytä erityisiä laajennuksia; tulos olisi määrittelemätön. Siksi
monivaiheiset tekniikat vuorottelevat kahden tekstuurin välillä
(ping-pong).

## Värit ja sRGB

Kuvatiedostojen värit ovat yleensä sRGB-koodattuja (gamma ≈ 2,2), mutta
valaistuslaskenta on tehtävä lineaarisessa tilassa. Tekstuurimuoto
`GL_SRGB8_ALPHA8` muuntaa luettaessa sRGB:stä lineaariseksi, ja
kehyspuskurin sRGB-muoto muuntaa kirjoitettaessa takaisin. Jos
muunnokset unohtuvat, valaistus näyttää liian tummalta ja liukumat
epätasaisilta. Esimerkeissä käytetään lineaarista RGBA8:aa, jotta
luvut ovat helppoja tarkistaa.

## Käytännössä

- **Mip-tasot aina, kun tekstuuria voidaan pienentää.** Ne poistavat
  laskostumisen ja *nopeuttavat* piirtoa, koska pienen tason tekselit
  mahtuvat välimuistiin. Muistia ne vievät kolmanneksen lisää.
- **Pakatut tekstuurimuodot** (BC7, ASTC) säästävät muistia ja kaistaa
  4–8-kertaisesti. Pakkaus tehdään työkalulla etukäteen, ei
  ajonaikaisesti.
- **Erottele näytteistimen tila ja tekstuuri.** OpenGL 3.3:n
  näytteistinoliot (`glCreateSamplers`) ja Vulkanin erilliset
  näytteistimet tekevät suodatuksesta ja reunakäsittelystä
  uudelleenkäytettäviä.
- **Väritila on päätettävä tekstuurikohtaisesti:** värikuvat sRGB,
  normaalikartat, karheuskartat ja muu data lineaarisina.
- **`texelFetch` lukee tekselin kokonaislukuindeksillä ilman
  suodatusta**; se on oikea valinta, kun tekstuuri on dataa eikä
  kuva (luku 11).

## Itsearviointi

- Osaat luoda tekstuurin mip-tasoineen ja valita suodatuksen
  suurennukselle ja pienennykselle.
- Osaat selittää laskostumisen ja sen, miksi mip-tasot ja
  trilineaarinen suodatus poistavat sen.
- Osaat rakentaa kehyspuskurin liitäntöineen, piirtää tekstuuriin ja
  lukea tuloksen seuraavassa vaiheessa.
- Osaat kertoa, milloin tekstuuri on sRGB- ja milloin lineaarinen, ja
  mitä virheellinen valinta aiheuttaa.
