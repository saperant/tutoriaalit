# Tekstuurit

Pintojen yksityiskohtia ei mallinneta kolmioina vaan kuvina, jotka
liimataan pinnalle. **Tekstuuri** on kuva, jonka pikseleitä kutsutaan
**tekseleiksi** erotukseksi ruudun pikseleistä. Jokaisella kärjellä
on tekstuurikoordinaatti $(u, v)$, joka kertoo, mihin kohtaan kuvaa
kärki osuu. Rasteroija interpoloi koordinaatit (perspektiivikorjatusti)
ja fragmenttivarjostin hakee niiden kohdalta värin. Haun nimi on
**näytteenotto** (sampling), ja sen laatu ratkaisee, näyttääkö
tekstuuri terävältä, sumealta vai välkkyvältä.

## Tekstuurikoordinaatit

Koordinaatit ovat normalisoituja: $(0, 0)$ on kuvan yksi kulma ja
$(1, 1)$ vastakkainen, kuvan koosta riippumatta. Tässä tutoriaalissa
$v$ kasvaa alaspäin kuten kuvatiedostoissa; OpenGL:ssä $v = 0$ on
kuvan alareuna, mikä on yleinen syy ylösalaisin oleviin tekstuureihin.
Tekselin $i$ keskipiste on kohdassa $(i + 0{,}5)/\text{leveys}$, kuten
pikselinkin.

Koordinaatit voivat olla myös välin $0 \ldots 1$ ulkopuolella.
**Toisto** (repeat) ottaa koordinaatista vain murto-osan, jolloin
tekstuuri laatoittuu; lattia tai seinä voi toistaa samaa kuvaa
kymmeniä kertoja. Muita tapoja ovat **reunaan rajoitus** (clamp) ja
**peilattu toisto** (mirrored repeat). Tämän tutoriaalin tekstuurit
toistuvat:

```{.cpp tiedosto="esimerkit/yhteinen/tekstuuri.hpp" osa="tekstuuri"}
```

## Lähin ja bilineaarinen

**Lähin tekseli** (nearest) valitsee sen tekselin, jonka alueelle
koordinaatti osuu. Se on nopea ja tarkka pikseligrafiikalle, mutta
suurennettu tekstuuri näyttää kulmikkaalta.

**Bilineaarinen** suodatus (bilinear) ottaa neljä lähintä tekseliä ja
painottaa niitä etäisyyden mukaan: ensin vaakasuunnassa kaksi
lineaarista interpolointia, sitten pystysuunnassa yksi. Suurennettu
tekstuuri muuttuu sileäksi. Interpolointi tehdään lineaarisilla
väreillä, joten sRGB-tekstuurit puretaan ennen suodatusta
(näytönohjain tekee sen automaattisesti sRGB-muodoille).

```{.cpp tiedosto="esimerkit/10-suodatus.cpp" osa="naytteet"}
```

```{.tuloste tiedosto="esimerkit/10-suodatus.odotettu"}
```

Sarake *tekseli* on jatkuva tekselikoordinaatti $u \cdot 4 - 0{,}5$:
kokonaisluvussa näyte osuu tekselin keskelle, ja silloin molemmat
tavat antavat saman tuloksen. Puolivälissä lähin tekseli hyppää ja
bilineaarinen antaa keskiarvon. Kohdissa $u = 0$ ja $u = 1$ näkyy
toisto: bilineaarinen suodatus sekoittaa rivin ensimmäisen ja
viimeisen tekselin, koska niiden välissä on toistuvan tekstuurin
sauma. Jos tekstuuria ei ole tarkoitettu toistuvaksi (esimerkiksi
käyttöliittymän kuvat), tämä näkyy reunalla vääränvärisenä
juovana, ja oikea asetus on reunaan rajoitus.

## Pienennys ja aliasointi

Suurennuksessa (magnification) yksi tekseli peittää monta pikseliä,
ja bilineaarinen suodatus riittää. Pienennyksessä (minification)
yhden pikselin alalle osuu monta tekseliä, mutta näytteenotto lukee
niistä vain yhden tai neljä. Tulos riippuu sattumasta: pieni liike
vaihtaa luettua tekseliä, ja kaukainen shakkilauta välkkyy ja
muodostaa aaltomaisia kuvioita (moiré). Tämä on **aliasointia**:
signaalissa on korkeampia taajuuksia kuin näytteenotto pystyy
esittämään (Nyquistin raja on puolet näytteenottotaajuudesta).

Ratkaisu on suodattaa tekstuuri **ennen** näytteenottoa niin, että
yksi näyte edustaa koko pikselin alaa. Koska pikselin ala tekstuurissa
vaihtelee, suodatettuja versioita tarvitaan monta.

## Mipmapit

**Mipmap** (Williams 1983, *multum in parvo*) on ketju tekstuurin
pienennettyjä kopioita: jokainen taso on puolet edellisestä
kumpaankin suuntaan, ja jokainen tekseli on edellisen tason neljän
tekselin keskiarvo. Ketju vie vain kolmanneksen lisää muistia
($1/4 + 1/16 + \ldots = 1/3$).

```{.cpp tiedosto="esimerkit/yhteinen/tekstuuri.hpp" osa="mipmap"}
```

Taso valitaan sen mukaan, montako tekseliä yhden pikselin askel
ruudulla kattaa. Askeleen pituus saadaan tekstuurikoordinaattien
**derivaatoista** ruudun suhteen: kuinka paljon $u$ ja $v$ muuttuvat,
kun siirrytään yksi pikseli oikealle tai alas. Jos askel on $\rho$
tekseliä, taso $\log_2 \rho$ on se, jolla yksi tekseli vastaa yhtä
pikseliä. Putki laskee derivaatat interpoloimalla arvot myös
naapuripikselien kohdalla. Näytönohjaimet tekevät saman
varjostamalla pikselit $2 \times 2$ -ryhminä ja vertaamalla
naapureiden arvoja; siksi derivaatat (`dFdx`, `dFdy` GLSL:ssä) ovat
saatavilla fragmenttivarjostimessa.

**Trilineaarinen** suodatus ottaa bilineaarisen näytteen kahdelta
lähimmältä tasolta ja interpoloi niiden välillä, jotta tason
vaihtuminen ei näy terävänä rajana.

Pienen shakkiruudun mipmap-ketju näyttää, mitä keskiarvoistus tekee:
ylin taso on mustaa ja valkoista, kaikki pienemmät tasot tasaisen
harmaata, koska ruutujen yksityiskohtia ei voi esittää pienemmällä
resoluutiolla.

```{.cpp tiedosto="esimerkit/10-suodatus.cpp" osa="ketju"}
```

## Kolme suodatinta lattialla

Esimerkki piirtää kaukaisuuteen jatkuvan lattian kolmella
suodattimella ja vertaa niitä kuvaan, joka on laskettu 16 näytteellä
pikseliä kohden (4 × 4 -ylinäytteistys, luku *Reunanpehmennys*):

```{.cpp tiedosto="esimerkit/yhteinen/tekstuuri.hpp" osa="shakki"}
```

```{.cpp tiedosto="esimerkit/10-mipmap.cpp" osa="piirto"}
```

```{.cpp tiedosto="esimerkit/10-mipmap.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/10-mipmap.odotettu"}
```

![Ylhäältä alas: lähin tekseli, bilineaarinen, trilineaarinen
mipmapeilla ja vertailukuva 16 näytteellä pikseliä kohden.](kuvat/10-mipmap.png){width=45%}

Lähin tekseli on lähellä kulmikas ja kaukana kohinaa. Bilineaarinen
pehmentää lähialueen, mutta kaukana välkyntä säilyy, koska suodatin
kattaa edelleen vain neljä tekseliä. Trilineaarinen on lähimpänä
vertailukuvaa kummassakin osassa. Sen heikkous näkyy horisontissa:
alue muuttuu tasaisen harmaaksi liian aikaisin. Viistossa
katsotun pinnan pikseli kattaa tekstuurissa pitkän ja kapean alueen,
ja taso valitaan pidemmän sivun mukaan, joten kapea suunta sumenee
turhaan.

Tämän korjaa **anisotrooppinen suodatus**, joka ottaa pidemmän sivun
suunnassa useita näytteitä tarkemmalta tasolta. Se on näytönohjaimissa
asetus (2×–16×), ja se kannattaa lähes aina pitää päällä
lattioille ja teille.

## Muut tekstuurit

Tekstuuri on yleisesti taulukko, josta haetaan arvoja suodattaen.
Värin lisäksi tekstuureihin tallennetaan normaaleja (normaalikartat,
joilla tasainen pinta saa pienet kohoumat), kiiltoa ja karheutta,
ympäristön valoa (ympäristökartat ja kuutiokartat), varjojen
syvyyksiä ja laskennan välituloksia. Vain värikuvat ovat sRGB:tä;
muut tallennetaan lineaarisina.

## Käytännössä

- **Mipmapit kaikille pienentyville tekstuureille.** Ilman niitä
  kaukaiset pinnat välkkyvät, ja muistihakujen hajanaisuus hidastaa
  näytönohjainta.
- **Trilineaarinen ja anisotrooppinen** suodatus oletuksena 3D-pinnoille;
  lähin tekseli pikseligrafiikalle ja datalle, jota ei saa sekoittaa.
- **Valitse reunakäsittely tarkoituksella.** Toisto laatoille, reunaan
  rajoitus kuville, jotka eivät jatku.
- **Pura sRGB ennen suodatusta** ja luo mipmapit lineaarisilla
  arvoilla, tai pienemmät tasot tummuvat.
- **Tarkista $v$-akselin suunta** kuvatiedoston ja rajapinnan välillä.

## Itsearviointi

- Osaat kuvata tekstuurikoordinaatit, toiston ja reunaan
  rajoituksen.
- Osaat laskea bilineaarisen näytteen neljästä tekselistä.
- Osaat selittää, miksi pienennetty tekstuuri aliasoituu ja miten
  mipmapit sen estävät.
- Osaat kertoa, miten mipmap-taso valitaan derivaatoista ja miksi
  anisotrooppinen suodatus tarvitaan viistoille pinnoille.
