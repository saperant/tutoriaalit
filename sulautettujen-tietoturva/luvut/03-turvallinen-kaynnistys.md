# Turvallinen käynnistys

Turvallinen käynnistys (*secure boot*) varmistaa, että laite ajaa vain
ohjelmistoa, jonka valmistaja on allekirjoittanut. Jokainen vaihe
tarkistaa seuraavan ennen kuin siirtää sille suorituksen. Näin syntyy
**luottamusketju** (*chain of trust*), jonka ensimmäinen lenkki on
**luottamuksen juuri** (*root of trust*): koodi ja avain, joita ei voi
muuttaa.

## Luottamusketju

Tyypillisessä mikrokontrollerissa ketju on lyhyt:

1. **ROM-käynnistin** on piirin valmistajan koodia
   vain luku -muistissa. Sitä ei voi päivittää eikä muuttaa.
2. Juuren **julkinen avain** tai sen tiiviste on poltettu
   OTP-muistiin (*one-time programmable*, eFuse) tehtaalla.
3. ROM tarkistaa **ensimmäisen vaiheen käynnistimen** allekirjoituksen
   tällä avaimella.
4. Käynnistin tarkistaa **sovelluksen** (tai käyttöjärjestelmän
   ytimen), joka voi tarkistaa omat moduulinsa.

Ketju on yhtä vahva kuin heikoin lenkkinsä. Jos jokin vaihe lataa
koodia tarkistamatta (esim. käynnistin hyväksyy sarjaportista tulevan
kuvan "huoltotilassa"), kaikki sitä edeltävät tarkistukset ovat
turhia.

Tämän tutoriaalin käynnistin on ROM:n roolissa: se on muistin
alussa, ja julkinen avain on käännetty sen sisään. Oikeassa piirissä
avaimen tiiviste olisi OTP:ssa, jolloin avaimen voi valita vasta
tehtaalla.

## Kuvan muoto

Laiteohjelmistokuva on otsake ja sovellus peräkkäin:

```{.c tiedosto="esimerkit/laite/lahde/otsake.h"}
```

Allekirjoitus kattaa otsakkeen alkuosan, ja siinä on sovelluksen
SHA-512-tiiviste. Näin allekirjoitettava viesti on lyhyt ja yhtenäinen,
ja sovellus voidaan tiivistää paloittain suoraan flashista. Sama
rakenne on MCUbootissa (otsake ja TLV-kentät) ja U-Bootin FIT-kuvissa.

## Allekirjoitus valmistajalla

Valmistajan rakennusjärjestelmä tiivistää sovelluksen, kokoaa
otsakkeen ja allekirjoittaa sen:

```{.python tiedosto="esimerkit/03-kuvatyokalu.py" osa="kuva"}
```

Sama tarkistus isäntäkoneella on hyödyllinen julkaisuputkessa: kuva
tarkistetaan ennen kuin se lähetetään laitteille.

```{.python tiedosto="esimerkit/03-kuvatyokalu.py" osa="tarkista"}
```

```{.tuloste tiedosto="esimerkit/03-kuvatyokalu.odotettu"}
```

Allekirjoitusavain on tuotteen arvokkain salaisuus: sillä voi
allekirjoittaa haittaohjelman, jonka jokainen laite hyväksyy. Se
säilytetään HSM:ssä, allekirjoitus tehdään erillisessä julkaisuputkessa
kahden henkilön hyväksynnällä, ja kehityskäyttöön on oma avain, jota
tuotantolaitteet eivät hyväksy.

## Tarkistus laitteessa

Laitteessa ei ole Pythonia eikä OpenSSL:ää, joten tarkistus tehdään
pienellä C-kirjastolla. Esimerkissä käytetään Monocypheria, jonka
oma allekirjoitusfunktio käyttää BLAKE2b-tiivistettä. Standardin
Ed25519 (RFC 8032) tiiviste on SHA-512, joten tiiviste lasketaan
itse ja Monocypher tarkistaa käyräyhtälön:

```{.c tiedosto="esimerkit/laite/lahde/ed25519.c"}
```

Käynnistin tarkistaa kuvan kolmessa vaiheessa:

```{.c tiedosto="esimerkit/laite/lahde/kaynnistin.c" osa="tarkista"}
```

Järjestyksellä on merkitystä:

- **Koko tarkistetaan ennen kuin sitä käytetään.** Otsakkeen kentät
  ovat hyökkääjän hallussa siihen asti, kunnes allekirjoitus on
  tarkistettu. Ilman rajaa tiivistys lukisi muistia mielivaltaisen
  pitkälle.
- **Allekirjoitus ensin, sitten tiiviste.** Allekirjoitus kertoo, että
  otsakkeen tiiviste on aito, ja tiiviste, että sovellus vastaa sitä.
- **Hyväksyntä on erityinen vakio**, ei `1` tai `true`. Syy selviää
  luvussa 10.

Kun kuva kelpaa, käynnistin siirtää suorituksen sovellukselle:
asettaa keskeytysvektorit, pinon ja hyppää sovelluksen alkuun.

```{.c tiedosto="esimerkit/laite/lahde/kaynnistin.c" osa="hyppy"}
```

## Skenaariot QEMU:ssa

Aito kuva käynnistyy:

```{.tuloste tiedosto="esimerkit/laite/testit/perus.odotettu"}
```

Jos hyökkääjä muuttaa sovellusta flashissa, tiiviste ei täsmää. Toisen
paikan aito kuva käynnistyy (paikat A ja B käsitellään luvussa 7):

```{.tuloste tiedosto="esimerkit/laite/testit/peukaloitu.odotettu"}
```

Hyökkääjän omalla avaimella allekirjoitettu kuva hylätään:

```{.tuloste tiedosto="esimerkit/laite/testit/vieras-avain.odotettu"}
```

## Tarkista ja käytä samaa dataa

Klassinen virhe on tarkistaa kuva yhdestä paikasta ja ajaa se
toisesta, tai lukea se kahdesti. Jos sovellus on ulkoisessa
SPI-flashissa, hyökkääjä voi vaihtaa piirin tai syöttää väylälle eri
dataa tarkistuksen ja suorituksen välissä (*time-of-check to
time-of-use*, TOCTOU). Ratkaisu: kopioi kuva sisäiseen muistiin,
tarkista kopio ja aja kopio. Esimerkin flash on piirin sisäistä, joten
kuva ajetaan paikallaan.

## Avainten kumoaminen

Jos allekirjoitusavain vuotaa, laitteiden pitää lakata luottamasta
siihen. Siksi piirit tallentavat OTP:hen useamman avaimen tiivisteen
ja kumoamisbitit: uusi laiteohjelmisto allekirjoitetaan seuraavalla
avaimella, ja käynnistin polttaa vanhan avaimen kumoamisbitin. Tämä
pitää suunnitella ennen kuin ensimmäinen laite lähtee tehtaalta, sillä
OTP:tä ei voi lisätä jälkikäteen.

## Käytännössä

- **Käytä valmista käynnistintä**, kuten MCUboot (Zephyr, NuttX,
  bare metal), Trusted Firmware-M tai U-Boot ja sen *verified boot*.
  Ne ovat valmiiksi auditoituja ja hoitavat kuvaformaatin, A/B-paikat
  ja versionhallinnan.
- **Ota piirin oma ROM-tarkistus käyttöön.** Ilman sitä
  ensimmäisen vaiheen käynnistintä voi muuttaa, ja ketju alkaa
  muokattavasta koodista.
- **Erota kehitys- ja tuotantoavaimet.** Tuotantolaite ei hyväksy
  kehitysavaimella allekirjoitettua kuvaa, eikä tuotantoavain ole
  koskaan kehittäjän koneella.
- **Varaa avaimille kumoamismahdollisuus** ja harjoittele avaimen
  vaihtoa ennen kuin sitä tarvitaan.
- **Tarkistus ei saa olla ohitettavissa.** Huoltotila, joka lataa
  koodia tarkistamatta, on takaovi.

## Itsearviointi

- Osaat kuvata luottamusketjun ROM:sta sovellukseen ja kertoa, mikä on
  luottamuksen juuri.
- Osaat selittää, miksi allekirjoitus kattaa tiivisteen eikä koko
  kuvaa, ja miksi otsakkeen kentät rajataan ennen käyttöä.
- Osaat tunnistaa tarkistuksen ja käytön välisen kilpatilanteen ja
  tavan välttää se.
- Osaat perustella, miksi allekirjoitusavain kuuluu HSM:ään ja miksi
  avainten kumoaminen suunnitellaan etukäteen.
