# Sivukanavat

Algoritmi voi olla matemaattisesti vahva, ja toteutus silti vuotaa
avaimen. **Sivukanava** on mikä tahansa fyysinen suure, joka riippuu
käsiteltävästä salaisuudesta: suoritusaika, virrankulutus,
sähkömagneettinen säteily, jopa ääni. Sulautetussa laitteessa
hyökkääjä pääsee mittaamaan niitä suoraan: oskilloskooppi
virransyötön vastukseen riittää.

## Ajoitus

Yleisin sivukanava on suoritusaika. Tunnisteen (MAC, PIN, salasana)
vertailu, joka palaa ensimmäisestä erosta, kertoo ajallaan, montako
tavua osui oikein:

```{.c tiedosto="esimerkit/09-vertailu.c" osa="vuotava"}
```

Hyökkääjä arvaa tunnisteen tavu kerrallaan ja valitsee arvon, jonka
tarkistus kesti pisimpään. Esimerkissä aika mallinnetaan
vertailukierroksilla, jotta tulos on toistettava; oikeassa
hyökkäyksessä mitataan kelloa ja keskiarvoistetaan kohina pois.

```{.c tiedosto="esimerkit/09-vertailu.c" osa="hyokkays"}
```

Vakioaikainen vertailu käy kaikki tavut läpi ja kerää erot yhteen.
Sama periaate ja sen syyt ovat taidossa *Kryptografia*; tässä se on
C:llä, koska laitteessa vertailun kirjoittaa usein itse tai valitsee
kirjastosta:

```{.c tiedosto="esimerkit/09-vertailu.c" osa="vakioaikainen"}
```

```{.tuloste tiedosto="esimerkit/09-vertailu.odotettu"}
```

Kahdeksan tavun tunniste löytyy noin kahdellatuhannella yrityksellä,
kun raaka haku vaatisi keskimäärin 2^63^ yritystä. Vakioaikaisuus
koskee kaikkea salaisuudesta riippuvaa: haarautumia, taulukkohakuja ja
silmukoiden pituuksia. Kääntäjä voi optimoida vakioaikaisen koodin
vuotavaksi, joten kirjastot (Monocypher, mbedTLS, libsodium)
tarjoavat valmiit vertailufunktiot (`crypto_verify16`,
`mbedtls_ct_memcmp`, `sodium_memcmp`).

## Virrankulutus

CMOS-logiikka kuluttaa virtaa, kun bitit vaihtavat tilaa, ja väylä
kuluttaa sitä enemmän, mitä useampi bitti on ykkönen. **Yksinkertainen
tehoanalyysi** (SPA) lukee käyrästä suoraan suorituksen kulun, esim.
RSA:n neliöinnit ja kertolaskut, joista eksponentin bitit näkyvät.
**Differentiaalinen tehoanalyysi** (DPA) ja sen yleisin muoto
**korrelaatiotehoanalyysi** (CPA) toimivat silloinkin, kun yksittäinen
käyrä ei paljasta mitään: hyökkääjä mittaa satoja tai tuhansia
salauksia tunnetuilla syötteillä ja etsii avainarvauksen, jonka
ennustama kulutus korreloi mittausten kanssa.

Esimerkki simuloi AES:n ensimmäisen kierroksen S-laatikkoa. S-laatikko
lasketaan määritelmästään:

```{.python tiedosto="esimerkit/09-tehoanalyysi.py" osa="sbox"}
```

Mittaus on tuloksen Hammingin paino ja kohina. Hyökkäys kokeilee kaikki
256 avaintavun arvoa:

```{.python tiedosto="esimerkit/09-tehoanalyysi.py" osa="mittaa"}
```

```{.tuloste tiedosto="esimerkit/09-tehoanalyysi.odotettu"}
```

![Korrelaatio jokaiselle 256 avainarvaukselle 2000 mittauksen jälkeen
samoilla mittauksilla kuin tulosteen viimeisessä sarakkeessa.
Maskaamattomassa toteutuksessa oikea avain erottuu selvästi muista.
Maskatussa se ei eroa kohinasta.](kuvat/tehoanalyysi.png){width=92%}

Satakin mittausta riittää maskaamattoman toteutuksen avaintavuun,
ja sama toistetaan jokaiselle 16 tavulle. **Maskaus** käsittelee
väliarvoja satunnaisella maskilla, joka vaihtuu joka suorituksella, joten
yksittäinen mittauspiste ei korreloi avaimen kanssa. Maskaus ei ole
täydellinen: toisen asteen hyökkäys yhdistää kaksi mittauspistettä
(maskattu arvo ja maski), mutta vaatii moninkertaisesti mittauksia ja
tarkemman laitteiston.

## Muut vastatoimet

- **Laitteistokiihdytin**, jossa on sivukanavasuojaus. Monissa
  mikrokontrollereissa on AES-lohko, mutta kaikkia ei ole suojattu;
  tarkista valmistajan dokumentaatio ja sertifioinnit.
- **Sekoitus** (*shuffling*): S-laatikoiden käsittelyjärjestys vaihtuu
  satunnaisesti, jolloin hyökkääjä ei tiedä, mitä mittauspiste esittää.
- **Kohina ja satunnaiset viiveet** lisäävät tarvittavien mittausten
  määrää.
- **Avainten rajattu käyttö.** Jos avainta käytetään vain vähän ja
  hyökkääjä ei voi valita syötteitä, tilastollisille hyökkäyksille ei
  ole tarpeeksi dataa.

## Käytännössä

- **Vakioaikainen vertailu** kaikille tunnisteille, MAC-arvoille ja
  salasanoille; älä kirjoita sitä itse, käytä kirjaston funktiota.
- **Valitse kryptografiakirjasto, joka on vakioaikainen.** Monocypher,
  libsodium ja nykyinen mbedTLS on suunniteltu sitä varten;
  itse kirjoitettu AES taulukkohauilla ei ole.
- **Arvioi tehoanalyysi uhkamallin mukaan.** Jos hyökkääjä voi mitata
  laitetta (maksukortti, älylukko, autoavain), käytä suojattua
  laitteistoa tai sertifioitua turvaelementtiä.
- **Harjoittele itse omalla kortilla.** Avoimet työkalut kuten
  ChipWhisperer harjoituskohteineen tekevät tehoanalyysistä
  kokeiltavan muutamalla sadalla eurolla.

## Itsearviointi

- Osaat tunnistaa ajoitusvuodon koodista ja korjata sen
  vakioaikaiseksi.
- Osaat selittää, miten korrelaatiotehoanalyysi löytää avaintavun
  mittauksista ja tunnetuista syötteistä.
- Osaat kuvata maskauksen ja sekoituksen periaatteen ja rajat.
