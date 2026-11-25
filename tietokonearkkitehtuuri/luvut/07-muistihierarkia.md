# Kirjoitus ja muistihierarkia

Edellinen luku käsitteli lukemista. Kirjoitus on monimutkaisempi, koska
välimuistissa ja muistissa on nyt saman datan kaksi kopiota, ja niiden on
pysyttävä yhtäpitävinä. Tämä luku käy läpi kirjoituspolitiikat,
monitasoisen hierarkian keskimääräisen viiveen ja sen, miten ohjelman
rakenne ratkaisee, kuinka hyvin hierarkia toimii.

## Kirjoituspolitiikat

Kirjoitusosumassa on kaksi vaihtoehtoa:

- **Läpikirjoitus** (*write-through*, WT): kirjoitus menee sekä
  välimuistiin että seuraavalle tasolle. Muisti on aina ajan tasalla,
  mutta jokainen talletus kuluttaa väylää. Talletukset kerätään
  **kirjoituspuskuriin**, jotta ydin ei odota muistia.
- **Takaisinkirjoitus** (*write-back*, WB): kirjoitus menee vain
  välimuistiin, ja rivi merkitään **likaiseksi** (*dirty*). Likainen rivi
  kirjoitetaan muistiin vasta, kun se poistetaan. Monta kirjoitusta
  samaan riviin maksaa yhden takaisinkirjoituksen.

Kirjoitushudissa on samoin kaksi vaihtoehtoa:

- **Kirjoitusvaraus** (*write-allocate*, WA): lohko tuodaan välimuistiin
  ja kirjoitetaan siellä. Luonteva pari takaisinkirjoitukselle.
- **Ei varausta** (*no-write-allocate*): kirjoitus menee suoraan
  seuraavalle tasolle, välimuisti ei muutu. Luonteva pari
  läpikirjoitukselle.

Esimerkki laskee muistiliikenteen tavuina kolmella yhdistelmällä:

```{.cpp tiedosto="esimerkit/07-kirjoitus.cpp" osa="politiikat"}
```

```{.tuloste tiedosto="esimerkit/07-kirjoitus.odotettu" rivit="1-4"}
```

Mikään politiikka ei voita aina:

- **`kupla`** kirjoittaa 1 022 kertaa saman 192 tavun taulukon sisällä.
  Takaisinkirjoitus siirtää vain 208 tavua (taulukon lohkot kerran
  sisään), läpikirjoitus yli 4 000 tavua. Tämä on takaisinkirjoituksen
  vahvin tapaus: toistuvat kirjoitukset samaan paikkaan.
- **`summa`** kirjoittaa taulukon kerran alusta loppuun ja lukee sen
  sitten. Ilman kirjoitusvarausta talletukset eivät tuo lohkoja turhaan,
  ja liikenne on pienin.
- **`matriisi`** on yllättävä: takaisinkirjoitus on *huonompi* kuin
  läpikirjoitus. Tulosmatriisin C rivi kirjoitetaan sana kerrallaan,
  mutta jokaisen sanan välissä pistetulo lukee A:ta ja B:tä ja syrjäyttää
  C:n lohkon pienestä välimuistista. Lohko tuodaan uudelleen,
  likaantuu, poistetaan ja kirjoitetaan takaisin, jopa neljästi samalle
  lohkolle.

Lähes kaikki nykyiset välimuistit ovat takaisinkirjoittavia ja
kirjoitusvaraavia, koska tyypillisissä ohjelmissa kirjoitukset osuvat
samoihin riveihin (pino, muuttujat, puskurit). Läpikirjoitusta käytetään
pienissä L1-välimuisteissa, joiden takana on takaisinkirjoittava L2
(esimerkiksi monet ARM Cortex-M- ja vanhat Intel-suunnitelmat), koska
se yksinkertaistaa koherenssia ja virheenkorjausta: L1:ssä ei ole koskaan
ainoaa kopiota.

Suurten kirjoitusten erikoistapaus on **suoratallennus** (*non-temporal
store*, `movnt` x86:ssa): kun ohjelma kirjoittaa megatavuja dataa, jota se
ei lue pian, kirjoitusvaraus vain syrjäyttäisi hyödyllistä dataa.
`memset` ja `memcpy` käyttävät suuria kokoja varten tällaisia käskyjä.

## Keskimääräinen muistiviive

Hierarkian suorituskyky tiivistyy yhteen lukuun, keskimääräiseen
muistiviiveeseen (AMAT, *average memory access time*):

$$
\text{AMAT} = t_1 + h_1 \cdot (t_2 + h_2 \cdot t_m)
$$

missä $t_1$ ja $t_2$ ovat L1:n ja L2:n osumaviiveet, $t_m$ keskusmuistin
viive ja $h_1$, $h_2$ hutisuhteet. $h_2$ on **paikallinen** hutisuhde:
niistä viitteistä, jotka pääsevät L2:lle asti, kuinka moni hutii.
**Globaali** hutisuhde $h_1 h_2$ kertoo, kuinka moni kaikista
viitteistä menee keskusmuistiin.

```{.cpp tiedosto="esimerkit/07-kirjoitus.cpp" osa="amat"}
```

```{.tuloste tiedosto="esimerkit/07-kirjoitus.odotettu" rivit="6-9"}
```

Tulosten tulkinta:

- `summa`: L1 hutii joka neljännellä viitteellä (16 tavun lohko, 4 tavun
  sanat), ja L2:n paikallinen hutisuhde on sama 25 %, koska data
  käydään läpi vain kahdesti. AMAT on lähes 10 jaksoa.
- `kupla`: L1-hutisuhde on 0,4 %, joten L2:n paikallinen hutisuhde
  (54 %) ei merkitse mitään. AMAT on 1,25.
- `matriisi`: L1 hutii joka kolmannella viitteellä, mutta L2 (2 KiB)
  pitää koko työjoukon, ja AMAT on 5,6 jaksoa.

Paikallinen L2-hutisuhde näyttää usein huolestuttavan suurelta, koska
L1 on jo suodattanut helpot viitteet. Vertaa siksi aina globaaleja
hutisuhteita tai suoraan AMATia.

Monitasoisuudessa on lisäksi kaksi suunnitteluvalintaa:

- **Sisältävä** (*inclusive*) hierarkia: kaikki L1:n lohkot ovat myös
  L2:ssa. Koherenssi on helpompi, koska riittää tarkistaa L2. Intelin
  L3 oli pitkään sisältävä.
- **Poissulkeva** (*exclusive*): lohko on vain yhdellä tasolla, joten
  kokonaiskapasiteetti on tasojen summa. AMD:n L3 on L2:lle
  uhrivälimuisti (*victim cache*).

## Silmukoiden järjestys

Sama algoritmi voi käyttää välimuistia hyvin tai surkeasti. C ja C++
tallentavat kaksiulotteisen taulukon riveittäin (*row-major*):
`m[i][j]` ja `m[i][j+1]` ovat vierekkäin, `m[i][j]` ja `m[i+1][j]` rivin
pituuden päässä. Esimerkki summaa 32 × 32 -matriisin (4 KiB)
molemmissa järjestyksissä:

```{.cpp tiedosto="esimerkit/07-silmukat.cpp" osa="ohjelma"}
```

```{.cpp tiedosto="esimerkit/07-silmukat.cpp" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/07-silmukat.odotettu"}
```

Käskyjä on täsmälleen yhtä paljon, mutta sarakkeittain luettuna
1 KiB:n välimuisti ei osu kertaakaan. Rivin pituus 128 tavua on
välimuistin joukkojen määrän monikerta, joten sarakkeen 32 alkiota
kuvautuvat vain neljään joukkoon (kahdeksaan riviin). Kun seuraavan
sarakkeen vuoro tulee, sen lohkot on jo syrjäytetty. 64 tavun lohkot
eivät auta. Vasta 8 KiB:n välimuisti, johon koko matriisi mahtuu,
tasoittaa eron: silloin jäljellä ovat vain pakolliset hudit (75 %
osumia 16 tavun lohkolla).

Oikeissa ohjelmissa matriisi on yleensä paljon välimuistia suurempi,
eikä suurempaa välimuistia voi ostaa. Ratkaisuja:

- **Silmukoiden vaihto** (*loop interchange*): sisin silmukka kulkee
  muistissa peräkkäin. Kääntäjä tekee tämän, jos se voi todistaa sen
  turvalliseksi.
- **Lohkominen** (*tiling*, *blocking*): matriisitulo lasketaan
  pienissä osamatriiseissa, jotka mahtuvat välimuistiin. Jokainen
  ladattu lohko käytetään monta kertaa ennen syrjäytystä. Kaikki
  tehokkaat BLAS-kirjastot toimivat näin, ja sama ajatus on GPU:iden
  jaetun muistin käytössä (taito *GPU-laskenta*).
- **Täyte** (*padding*): rivin pituus, joka ei ole kahden potenssi,
  hajauttaa sarakkeen alkiot eri joukkoihin.

## DRAM ja kaistanleveys

Keskusmuisti ei ole vain hidas vaan myös rakenteeltaan epätasainen.
DRAM-piiri on jaettu pankkeihin, ja jokaisessa pankissa on
**rivipuskuri** (*row buffer*), johon kerrallaan avattu rivi
(tyypillisesti 1–8 KiB) luetaan. Saman avoimen rivin lukeminen on noin
kaksi kertaa nopeampaa kuin uuden rivin avaaminen. Peräkkäiset viitteet
ovat siis nopeampia myös DRAMissa.

Viive ja kaistanleveys ovat eri asioita. DDR5-kanava siirtää noin
40–50 GB/s, mutta yksittäinen huti kestää silti 80 ns. Littlen laki
kertoo, kuinka monta hutia on oltava yhtä aikaa käynnissä, jotta kaista
täyttyy: 50 GB/s × 80 ns = 4 000 tavua = 62 lohkoa. Siksi välimuistit
ovat **estämättömiä** (*non-blocking*): ne jatkavat palvelemista hudin
aikana ja pitävät kirjaa keskeneräisistä huteista MSHR-rekistereissä
(*miss status holding register*), ja epäjärjestyksessä suorittava ydin
(luku 11) tuottaa riippumattomia huteja rinnakkain. Tätä kutsutaan
**muistitason rinnakkaisuudeksi** (MLP). Osoitinjahti tuhoaa sen,
koska seuraava osoite selviää vasta edellisen hudin jälkeen.

DRAM-solu on pieni kondensaattori, ja sen varaus voi kääntyä
kosmisen säteilyn tai viereisten rivien toistuvan lukemisen
(*rowhammer*) vuoksi. Palvelimien muisti on siksi **ECC-muistia**:
jokaisen 64 bitin sanan rinnalle tallennetaan 8 tarkistusbittiä, joilla
muistiohjain korjaa yhden bitin virheen ja havaitsee kahden bitin
virheen (SEC-DED, Hamming-koodin laajennus). Korjaus tapahtuu lukiessa
ilman, että ohjelma huomaa mitään, ja käyttöjärjestelmä saa virheestä
ilmoituksen. Koodin periaate käydään läpi taidossa
*Tietoliikennetekniikka*.

## Käytännössä

- **Kulje muistissa peräkkäin.** Sisin silmukka viimeisen indeksin yli,
  data tiiviinä taulukkona eikä hajallaan olevina olioina. `std::vector`
  on lähes aina nopeampi kuin `std::list`, vaikka algoritminen
  vaativuus olisi sama.
- **Pidä työjoukko pienenä.** Käsittele data paloina, jotka mahtuvat
  L1:een tai L2:een, ja tee palalle kaikki vaiheet ennen seuraavaa
  (*kernel fusion*, *cache blocking*).
- **Mittaa kaista ja viive erikseen.** STREAM-mittari kertoo kaistan,
  osoitinjahtiin perustuva mittari (`lmbench lat_mem_rd`) viiveen.
  Työkalu `perf mem` ja Intelin VTune erottelevat hudit tasoittain.
- **Kirjoituspolitiikka on piilossa, mutta ei vaikutuksiltaan.**
  Takaisinkirjoitus tarkoittaa, että virrankatkossa tai
  DMA-siirrossa välimuistissa voi olla ainoa ajantasainen kopio. Siksi
  pysyvän muistin (NVDIMM, CXL) ohjelmointi vaatii erillisiä
  `clwb`/`cbo.flush`-käskyjä ja DMA vaatii koherenssia tai välimuistin
  tyhjennystä (luku 9).

## Itsearviointi

- Osaat verrata läpi- ja takaisinkirjoitusta sekä kirjoitusvarausta ja
  sen puuttumista muistiliikenteen kannalta ja nimetä tilanteen, jossa
  kukin voittaa.
- Osaat laskea kaksitasoisen hierarkian AMATin ja erottaa paikallisen ja
  globaalin hutisuhteen.
- Osaat selittää, miksi sarakkeittainen läpikäynti voi pudottaa
  osumasuhteen nollaan, ja korjata sen silmukoiden vaihdolla,
  lohkomisella tai täytteellä.
- Osaat kertoa, mitä ECC-muisti korjaa ja mitä se vain havaitsee.
