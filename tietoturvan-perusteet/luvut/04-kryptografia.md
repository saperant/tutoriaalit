# Kryptografia käyttäjän näkökulmasta

Kehittäjän ei tarvitse osata toteuttaa salausalgoritmeja, mutta hänen
on tiedettävä, mitä kukin kryptografinen työkalu takaa ja mitä ei.
Suurin osa kryptografiaan liittyvistä haavoittuvuuksista ei johdu
rikkoutuneista algoritmeista vaan väärästä työkalusta: tiivisteellä
yritetään salata, salauksella yritetään taata eheys tai salasanat
tallennetaan nopealla tiivisteellä. Algoritmien sisältö ja oikea
käyttö syvemmin ovat taidossa *Kryptografia*.

| Työkalu | Takaa | Ei takaa | Avain |
|---------|-------|----------|-------|
| tiiviste (SHA-256) | muutoksen havaitsemisen, kun oikea tiiviste saadaan luotettavasti | salassapitoa, aitoutta | ei avainta |
| MAC (HMAC) | eheyden ja aitouden avaimen haltijoiden kesken | salassapitoa, kiistämättömyyttä | jaettu salainen |
| symmetrinen salaus | luottamuksellisuuden | eheyttä (ellei AEAD) | jaettu salainen |
| todennettu salaus (AEAD, esim. AES-GCM) | luottamuksellisuuden ja eheyden | sitä, kuka avaimen haltijoista lähetti | jaettu salainen |
| julkisen avaimen salaus | luottamuksellisuuden vastaanottajalle | lähettäjän aitoutta | vastaanottajan avainpari |
| digitaalinen allekirjoitus | eheyden, aitouden ja kiistämättömyyden | salassapitoa | allekirjoittajan avainpari |
| salasanan tiiviste (scrypt, Argon2) | sen, että vuotanut tiiviste on hidas murtaa | mitään, jos salasana on heikko | suola, ei avainta |

## Tiivisteet: eheys, ei salassapito

Tiivistefunktio (*hash function*) laskee mielivaltaisesta datasta
kiinteän mittaisen tunnisteen. Hyvässä tiivistefunktiossa pienikin
muutos datassa muuttaa tiivisteen täysin, eikä kahta eri syötettä,
joilla on sama tiiviste, löydetä käytännössä. Tyypillinen käyttö on
ladatun tiedoston eheyden tarkistus:

```{.python tiedosto="esimerkit/04-tiiviste.py" osa="tiiviste"}
```

```{.tuloste tiedosto="esimerkit/04-tiiviste.odotettu"}
```

Tarkistus suojaa vain, jos oikea tiiviste saadaan eri kanavaa
pitkin kuin tiedosto. Jos hyökkääjä voi vaihtaa tiedoston, hän voi
vaihtaa samalla sivulla olevan tiivisteenkin. Siksi ohjelmistopaketit
allekirjoitetaan.

Tiiviste ei salaa. Jos salaisuuden mahdollisia arvoja on vähän,
hyökkääjä laskee niiden kaikkien tiivisteet ja vertaa:

```{.python tiedosto="esimerkit/04-pin.py" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/04-pin.odotettu"}
```

Sama koskee henkilötunnuksia, puhelinnumeroita ja sähköpostiosoitteita:
"anonymisointi" tiivistämällä ei anonymisoi, koska arvojoukko on
käytännössä lueteltavissa.

MD5 ja SHA-1 ovat rikki: niille osataan tuottaa törmäyksiä. Uusissa
järjestelmissä käytetään SHA-256:ta tai SHA-3:a. (Luvun *Todennus*
TOTP käyttää SHA-1:tä HMAC:n sisällä, mikä on yhä turvallista, mutta
uusiin protokolliin sitä ei valita.)

## MAC: aitous jaetulla avaimella

Kun maksupalvelu lähettää verkkokaupalle ilmoituksen maksusta
(*webhook*), kaupan on varmistettava, että viesti tuli todella
maksupalvelulta eikä sitä muutettu matkalla. Pelkkä tiiviste ei riitä,
koska hyökkääjä voi laskea väärennökselle uuden tiivisteen:

```{.python tiedosto="esimerkit/04-hmac.py" osa="hyokkays"}
```

**MAC** (*message authentication code*) on tiiviste, jonka laskemiseen
tarvitaan salainen avain. Ilman avainta oikeaa tunnistetta ei voi
laskea. Pythonissa se on `hmac`-moduli:

```{.python tiedosto="esimerkit/04-hmac.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/04-hmac.odotettu"}
```

Vertailu tehdään funktiolla `hmac.compare_digest`. Tavallinen `==`
lopettaa ensimmäiseen eroavaan merkkiin, jolloin vertailun kesto
paljastaa, kuinka monta merkkiä alusta oli oikein. Riittävällä
määrällä mittauksia hyökkääjä voi selvittää oikean tunnisteen merkki
kerrallaan (*timing attack*).

## Salaus ilman eheyttä

Salaus takaa luottamuksellisuuden: ilman avainta viestiä ei voi
lukea. Se ei takaa, ettei viestiä voi *muuttaa*. Seuraava esimerkki
käyttää havainnollistavaa jonosalainta. Hyökkääjä tietää viestin
muodon ja muuttaa siirrettävän summan koskematta avaimeen:

```{.python tiedosto="esimerkit/04-muokattavuus.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/04-muokattavuus.odotettu"}
```

Oikeat jonosalaimet ja lohkosalaimen CTR- ja CBC-tilat ovat samalla
tavalla muokattavissa. Siksi nykyaikainen valinta on aina
**todennettu salaus** (AEAD, *authenticated encryption with associated
data*), kuten AES-GCM tai ChaCha20-Poly1305. Se hylkää muutetun
viestin purkuvaiheessa. Kehittäjän ei tarvitse yhdistää salausta ja
MAC:ia itse: valmis AEAD-toteutus tekee sen oikein.

## Julkisen avaimen menetelmät ja allekirjoitukset

Symmetrisessä salauksessa molemmilla osapuolilla on sama avain, ja sen
jakaminen on ongelma. Julkisen avaimen menetelmissä avaimia on kaksi:
julkinen, jonka saa jakaa kaikille, ja yksityinen, joka pysyy
omistajalla.

- **Salaus julkisella avaimella**: kuka tahansa voi salata, vain
  yksityisen avaimen haltija voi purkaa. Käytännössä julkisella
  avaimella sovitaan symmetrinen avain, ja varsinainen data salataan
  symmetrisesti (hybridisalaus, esimerkiksi TLS).
- **Allekirjoitus yksityisellä avaimella**: vain haltija voi
  allekirjoittaa, kuka tahansa voi tarkistaa. Allekirjoitus takaa myös
  kiistämättömyyden, toisin kuin MAC, jonka voi laskea kumpi tahansa
  osapuoli.

Julkisen avaimen menetelmien heikko kohta on avaimen alkuperä: mistä
tiedän, että julkinen avain kuuluu pankilleni eikä hyökkääjälle?
**Varmenne** (*certificate*) on varmentajan allekirjoitus, joka sitoo
julkisen avaimen nimeen. Selaimet luottavat joukkoon juurivarmentajia,
ja **TLS** tarkistaa palvelimen varmenteen ennen yhteyden
muodostamista. Kun ohjelmassa näkyy `verify=False` tai vastaava,
juuri tämä tarkistus kytketään pois, ja yhteys on altis
välimieshyökkäykselle (*man in the middle*).

## Salasanojen tallennus

Salasanoja ei tallenneta selväkielisinä eikä salattuina (avain vuotaisi
samassa murrossa), vaan tiivisteinä. Tavallinen tiivistefunktio on
kuitenkin väärä valinta, koska se on suunniteltu nopeaksi:
näytönohjaimella voi kokeilla miljardeja salasanoja sekunnissa. Oikea
valinta on tarkoituksella hidas **salasanan tiivistefunktio**: Argon2,
scrypt tai bcrypt. Pythonin standardikirjastossa on scrypt:

```{.python tiedosto="esimerkit/04-salasanat.py" osa="tallennus"}
```

```{.tuloste tiedosto="esimerkit/04-salasanat.odotettu"}
```

Satunnainen **suola** (*salt*) tekee jokaisesta tiivisteestä erilaisen,
vaikka salasana olisi sama. Ilman suolaa hyökkääjä voisi murtaa kaikki
samat salasanat kerralla ja käyttää valmiiksi laskettuja taulukoita.
Parametrit tallennetaan tiivisteen yhteyteen, jotta niitä voi
myöhemmin kasvattaa: uuden käyttäjän tiiviste lasketaan uusilla
parametreilla, ja vanha päivitetään kirjautumisen yhteydessä.

## Satunnaisuus

Kryptografiset avaimet, istuntotunnisteet, kertakäyttökoodit ja suolat
on luotava kryptografisesti turvallisella satunnaislukugeneraattorilla.
Pythonissa se on `secrets`-moduli. `random`-moduli on tarkoitettu
simulaatioihin: sen sisäinen tila (Mersenne Twister) voidaan päätellä
624 peräkkäisestä 32-bittisestä tulosteesta, minkä jälkeen kaikki
seuraavat arvot ovat ennustettavissa.

## Käytännössä

- **Älä toteuta kryptografiaa itse.** Käytä valmiita, korkean tason
  kirjastoja ja niiden suositeltuja oletuksia. Tässä luvussa itse
  toteutettu "salain" on vain havainnollistus.
- **Valitse työkalu takuun mukaan.** Tarvitsetko salassapitoa,
  eheyttä, aitoutta vai kiistämättömyyttä? Taulukko luvun alussa
  kertoo, mikä työkalu antaa minkäkin.
- **Salaa aina todennetusti.** Valitse AEAD (AES-GCM,
  ChaCha20-Poly1305), älä pelkkää salausta.
- **Salasanoille hidas, suolattu tiiviste.** Argon2id, scrypt tai
  bcrypt; ei SHA-256:ta, ei MD5:tä.
- **Vertaile salaisuuksia vakioajassa.** `hmac.compare_digest`, ei
  `==`.
- **Satunnaisuus `secrets`-modulista.** Ei koskaan `random`-modulista
  tietoturvatarkoituksiin.
- **Älä kytke varmenteiden tarkistusta pois.** Jos testiympäristössä
  tarvitaan oma varmentaja, lisää se luotettuihin varmentajiin.
- **Avaimet ovat salaisuuksia.** Niiden hallinta (luku *Salaisuudet ja
  tunnistetietojen vuodot*) on usein vaikeampaa kuin algoritmin valinta.

## Itsearviointi

- Osaat kertoa, mitä tiiviste, MAC, salaus, todennettu salaus ja
  allekirjoitus kukin takaavat ja mitä eivät.
- Osaat tarkistaa viestin aitouden HMAC:lla ja vertailla tunnisteet
  vakioajassa.
- Osaat tallentaa salasanat suolattuna, hitaana tiivisteenä ja
  perustella valinnan.
- Osaat selittää, miksi tiivistetty henkilötunnus tai PIN-koodi ei ole
  suojattu.
