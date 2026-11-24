# Symmetrinen salaus

Symmetrisessä salauksessa sama avain salaa ja purkaa. Se on nopeaa:
nykyinen suoritin salaa AES-GCM:llä useita gigatavuja sekunnissa
laitteistokäskyjen (AES-NI, ARMv8 Crypto) avulla. Kaikki suuret
tietomäärät salataan symmetrisesti; julkisen avaimen menetelmillä
sovitaan vain symmetrinen avain.

## Lohkosalain ja virtasalain

**AES** (*Advanced Encryption Standard*, 2001) on *lohkosalain*: se
muuntaa 16 tavun lohkon toiseksi 16 tavun lohkoksi avaimen
(128, 192 tai 256 bittiä) ohjaamana. Yksi lohko ei riitä viesteille,
joten lohkosalainta käytetään jossakin *toimintatilassa*.

**ChaCha20** on *virtasalain*: se tuottaa avaimesta ja noncesta
näennäissatunnaisen *avainvirran*, joka XORataan selvätekstiin.
ChaCha20 on nopea myös ilman AES-laitteistokäskyjä, ja siksi sitä
käytetään esimerkiksi mobiililaitteissa ja WireGuardissa.

## Toimintatilat

| Tila | Toiminta | Huomio |
|------|----------|--------|
| ECB | jokainen lohko salataan erikseen | paljastaa rakenteen, älä käytä |
| CBC | lohko XORataan edelliseen salattuun ennen salausta | satunnainen IV, täyte, ei eheyttä |
| CTR | AES salaa laskurin, tulos on avainvirta | nonce ei saa toistua, ei eheyttä |
| GCM | CTR + tunniste (GHASH) | AEAD, luku 4 |

### ECB paljastaa rakenteen

ECB-tilassa sama selvätekstilohko tuottaa aina saman salatun lohkon.
Esimerkissä viisirivinen "kuva" salataan kolmessa tilassa, ja jokainen
salattu lohko korvataan kirjaimella sen mukaan, onko sama lohko nähty
aiemmin:

```{.python tiedosto="esimerkit/03-ecb.py" osa="tilat"}
```

```{.tuloste tiedosto="esimerkit/03-ecb.odotettu"}
```

ECB:n tulos `A B C B A` toistaa kuvan rakenteen: rivit 1 ja 5 sekä 2 ja
4 ovat samat. Tunnettu esimerkki on ECB-tilassa salattu bittikarttakuva,
jossa kuvan ääriviivat erottuvat salatustakin. Sama ongelma koskee
tietokantakenttiä: ECB-salattu sukupuoli tai postinumero paljastaa
ryhmät. CBC ja CTR satunnaistavat tuloksen.

### Salaus ei suojaa eheyttä

CTR-tilassa salattu teksti on selväteksti XOR avainvirta. Hyökkääjä,
joka tuntee viestin muodon, voi muuttaa haluamaansa kohtaa tuntematta
avainta:

```{.python tiedosto="esimerkit/03-ctr-muokkaus.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/03-ctr-muokkaus.odotettu"}
```

Tätä kutsutaan *muokattavuudeksi* (*malleability*). CBC-tila on
samassa asemassa: salatun lohkon bitin kääntäminen kääntää saman bitin
seuraavassa selvätekstilohkossa. Ratkaisu on autentikoitu salaus
(luku 4).

### Noncen uudelleenkäyttö

Jos sama avain ja nonce salaavat kaksi viestiä, avainvirta on sama, ja
se kumoutuu, kun salatut viestit XORataan keskenään:

```{.python tiedosto="esimerkit/03-nonce-uudelleen.py" osa="virhe"}
```

```{.python tiedosto="esimerkit/03-nonce-uudelleen.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/03-nonce-uudelleen.odotettu"}
```

Tämä on yksi yleisimmistä todellisista virheistä: kovakoodattu nonce,
nollasta alkava laskuri jokaisessa prosessissa tai virtuaalikoneen
tilannevedoksesta palautettu laskuri. GCM-tilassa noncen toisto
paljastaa myös tunnisteavaimen, jolloin hyökkääjä voi väärentää
viestejä.

## Salaus komentorivillä

OpenSSL:n `enc`-komento salaa tiedoston salasanalla. Salasanasta
johdetaan avain PBKDF2:lla, ja satunnainen suola tallennetaan tiedoston
alkuun:

```{.bash tiedosto="esimerkit/03-openssl-enc.sh" osa="enc"}
```

```{.tuloste tiedosto="esimerkit/03-openssl-enc.odotettu"}
```

`openssl enc` ei tue AEAD-tiloja eikä siksi huomaa muutoksia.
Tiedostojen salaamiseen kannattaa käyttää työkaluja, jotka on tehty
siihen: **age** (moderni, yksinkertainen), **GnuPG** tai
salausavaimet hallitseva tallennusratkaisu.

## Käytännössä

- **Ei koskaan ECB:tä.** Monen kirjaston oletustila on historiallisista
  syistä ECB (esim. Javan `Cipher.getInstance("AES")`). Tila valitaan
  aina itse.
- **Ei pelkkää salausta.** CBC ja CTR ilman MAC:ia ovat muokattavissa,
  ja CBC on lisäksi altis täyteoraakkelihyökkäykselle (luku 11).
  Käytetään AEAD:ta.
- **Avaimen pituus:** AES-128 riittää nykyisiä hyökkäyksiä vastaan;
  AES-256 on yleinen oletus, koska se säilyttää marginaalin myös
  kvanttitietokoneita vastaan (luku 12) ja maksaa vain noin 40 %
  enemmän laskentaa.
- **Avain ei ole salasana.** Avain on 16–32 satunnaista tavua. Jos
  lähtökohta on salasana, avain johdetaan siitä hitaalla funktiolla
  (luku 6).
- **Hinta:** laitteistotuetulla AES:llä salaus maksaa alle tavun kohti
  yhden kellojakson; salauksen poistaminen suorituskykysyistä on lähes
  aina väärä säästökohde.

## Itsearviointi

- Osaat selittää, miksi ECB paljastaa rakenteen ja miksi CBC ja CTR
  eivät.
- Osaat näyttää, miten CTR-salattua viestiä muokataan ilman avainta,
  ja perustella, miksi salaus tarvitsee eheyssuojan.
- Osaat kertoa, mitä noncen uudelleenkäytöstä seuraa virtasalaimessa.
- Osaat salata ja purkaa tiedoston OpenSSL:llä ja tiedät, miksi se ei
  riitä eheyden suojaamiseen.
