# Tiivisteet, MAC ja avainten johtaminen

## Tiivistefunktiot

*Tiivistefunktio* (*hash function*) laskee mielivaltaisen pituisesta
datasta kiinteän mittaisen sormenjäljen. Kryptografiselta
tiivistefunktiolta vaaditaan kolme ominaisuutta:

1. **Alkukuvan löytämisen vaikeus:** tiivisteestä ei saa selville
   syötettä.
2. **Toisen alkukuvan löytämisen vaikeus:** annetulle syötteelle ei
   löydy toista, jolla on sama tiiviste.
3. **Törmäyskestävyys:** ei löydy mitään kahta syötettä, joilla on sama
   tiiviste. Syntymäpäiväongelman vuoksi n-bittisen tiivisteen
   törmäyksen löytäminen vaatii noin 2^n/2^ yritystä.

```{.python tiedosto="esimerkit/05-tiivisteet.py" osa="tiivisteet"}
```

Pieni muutos syötteessä muuttaa noin puolet tiivisteen biteistä
(*lumivyöryilmiö*), ja suurenkin tiedoston tiivisteen laskee
`hashlib.file_digest`:

```{.python tiedosto="esimerkit/05-tiivisteet.py" osa="lumivyory"}
```

```{.python tiedosto="esimerkit/05-tiivisteet.py" osa="tiedosto"}
```

```{.tuloste tiedosto="esimerkit/05-tiivisteet.odotettu"}
```

| Funktio | Tila | Käyttö |
|---------|------|--------|
| MD5, SHA-1 | rikki: törmäyksiä löydetään | vain yhteensopivuus, ei turvallisuutta |
| SHA-256, SHA-512 (SHA-2) | turvallinen | oletus |
| SHA3-256, SHAKE (SHA-3) | turvallinen, eri rakenne | varavaihtoehto, joustava pituus |
| BLAKE2, BLAKE3 | turvallinen, nopea | tiedostot, tarkistussummat |

Komentorivillä tiivisteet lasketaan `openssl dgst`- tai
`sha256sum`-komennolla. Julkaisujen eheys tarkistetaan vertaamalla
julkaistuun tiivistelistaan:

```{.bash tiedosto="esimerkit/05-openssl-dgst.sh" osa="dgst"}
```

```{.bash tiedosto="esimerkit/05-openssl-dgst.sh" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/05-openssl-dgst.odotettu"}
```

Tiiviste suojaa vain, jos tiivistelista saadaan luotettavaa reittiä.
Jos hyökkääjä voi vaihtaa tiedoston, hän voi yleensä vaihtaa myös
samalla sivulla olevan tiivisteen. Siksi tiivistelista allekirjoitetaan
(luku 8).

## Tiiviste ei ole MAC

*MAC* (*message authentication code*) on tiiviste, jonka laskemiseen
tarvitaan salainen avain. Luonteva mutta väärä toteutus on
`sha256(avain + viesti)`:

```{.python tiedosto="esimerkit/05-pituuslaajennus.py" osa="palvelin"}
```

SHA-256 käsittelee viestin 64 tavun lohkoina, ja tiiviste on sen
sisäinen tila viimeisen lohkon jälkeen. Hyökkääjä voi jatkaa
tiivistämistä siitä tilasta ja lisätä viestiin oman loppunsa
tuntematta avainta (*length extension*):

```{.python tiedosto="esimerkit/05-pituuslaajennus.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/05-pituuslaajennus.odotettu"}
```

Väärennetyssä viestissä on alkuperäisen ja lisäyksen välissä täytetavuja,
mutta moni jäsennin ohittaa ne, ja `rooli=admin` jää voimaan. Hyökkäys
koskee SHA-2:ta, MD5:tä ja SHA-1:tä. SHA-3 ja BLAKE2 eivät ole
alttiita, mutta oikea työkalu on silti HMAC.

## HMAC

HMAC (RFC 2104) tiivistää kahdesti eri avainjohdannaisilla, mikä estää
pituuslaajennuksen. Tyypillinen käyttö on webhook-kutsujen ja
API-pyyntöjen allekirjoitus jaetulla avaimella. Tilanne on tuttu
taidosta *Tietoturvan perusteet*; tässä toteutus tarkistetaan lisäksi
standardin testivektoria vastaan:

```{.python tiedosto="esimerkit/05-hmac.py" osa="webhook"}
```

```{.tuloste tiedosto="esimerkit/05-hmac.odotettu"}
```

Vertailu tehdään `hmac.compare_digest`-funktiolla, joka vie yhtä kauan
riippumatta siitä, missä kohtaa merkkijonot eroavat (luku 11).
Ensimmäinen tulosrivi tarkistaa toteutuksen RFC 4231:n testivektoria
vastaan. HMAC ei estä aidon kutsun lähettämistä uudelleen; toiston
torjunta on kuvattu luvussa 4.

## Avainten johtaminen: HKDF

Yhtä salaisuutta ei käytetä moneen tarkoitukseen. *HKDF* (RFC 5869)
johtaa yhdestä salaisuudesta (esim. avaintenvaihdon tuloksesta) eri
avaimet eri käyttötarkoituksiin. Vaiheita on kaksi: *extract* tiivistää
epätasaisen salaisuuden ja suolan tasaiseksi avaimeksi, ja *expand*
johtaa siitä halutun pituisen avaimen, joka riippuu `info`-kentästä:

```{.python tiedosto="esimerkit/05-hkdf.py" osa="tarkoitus"}
```

```{.tuloste tiedosto="esimerkit/05-hkdf.odotettu"}
```

`info`-kenttään kirjoitetaan sovellus, versio ja tarkoitus. Kaksi
eri ohjelmaa, jotka johtavat avaimia samasta salaisuudesta, eivät
silloin päädy samaan avaimeen. HKDF ei sovi salasanoille, koska se on
nopea; salasanat käsitellään luvussa 6.

## Käytännössä

- **SHA-256 on oletus.** MD5:tä ja SHA-1:tä käytetään vain
  yhteensopivuuteen, kun turvallisuus ei ole kyseessä (esim. Gitin
  vanhat objektitunnisteet, välimuistiavaimet). Uusia tiivisteitä
  tallennettaessa tallennetaan myös algoritmin nimi.
- **MAC on HMAC.** Älä yhdistä avainta ja viestiä itse. Myös
  API-allekirjoituksissa (esim. AWS Signature v4) on HMAC.
- **Allekirjoitettu sisältö yksiselitteiseksi.** Jos MAC lasketaan
  usean kentän yhdistelmästä, kentät erotetaan pituuksilla tai
  kanonisella esitysmuodolla: `"ab" + "c"` ja `"a" + "bc"` eivät saa
  tuottaa samaa syötettä (*canonicalization*).
- **Avaimet eri tarkoituksiin HKDF:llä.** Salausavain ja MAC-avain,
  palvelinsuunnan ja asiakassuunnan avain johdetaan erikseen.
- **Hinta:** SHA-256 laskee laitteistotuella yli gigatavun sekunnissa.
  Juuri nopeus tekee siitä sopimattoman salasanoille.

## Itsearviointi

- Osaat kuvata tiivistefunktion kolme turvallisuusominaisuutta ja
  valita sopivan tiivistefunktion.
- Osaat selittää pituuslaajennushyökkäyksen ja miksi HMAC estää sen.
- Osaat toteuttaa ja tarkistaa HMAC-allekirjoituksen vakioaikaisella
  vertailulla.
- Osaat johtaa käyttötarkoituskohtaiset avaimet HKDF:llä.
