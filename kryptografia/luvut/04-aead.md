# Autentikoitu salaus (AEAD)

*AEAD* (*authenticated encryption with associated data*) yhdistää
salauksen ja eheyssuojan yhdeksi operaatioksi. Salaus palauttaa
salatun tekstin ja tunnisteen (*tag*, yleensä 16 tavua). Purku joko
palauttaa alkuperäisen selvätekstin tai hylkää viestin: osittain
oikeaa tulosta ei ole. Nykyisessä ohjelmistossa symmetrinen salaus
tarkoittaa käytännössä aina AEAD:ta.

| Algoritmi | Käyttökohde | Nonce |
|-----------|-------------|-------|
| AES-256-GCM | oletus, laitteistotuki lähes kaikkialla | 12 tavua |
| ChaCha20-Poly1305 | laitteet ilman AES-käskyjä, WireGuard | 12 tavua |
| XChaCha20-Poly1305 | satunnainen nonce turvallisesti (libsodium) | 24 tavua |
| AES-GCM-SIV | kestää noncen toiston (vain tasa-arvo vuotaa) | 12 tavua |

## Liitetty data

AEAD:n kolmas syöte on *liitetty data* (*associated data*, AD): tietoa,
jota ei salata mutta joka sidotaan salattuun viestiin. Jos liitetty
data muuttuu, purku epäonnistuu. Tyypillisesti liitettyä dataa ovat
otsakkeet, versio, tietueen tunniste ja omistaja.

Esimerkissä tietokannan salattu kenttä sidotaan käyttäjään:

```{.python tiedosto="esimerkit/04-aead.py" osa="tietue"}
```

Jos hyökkääjä pääsee kirjoittamaan tietokantaan, hän ei voi lukea
salattuja kenttiä, mutta voisi kopioida Ainon salatun kentän omaan
riviinsä ja pyytää sovellusta näyttämään sen. Liitetty data estää
tämän:

```{.python tiedosto="esimerkit/04-aead.py" osa="vaihto"}
```

ChaCha20-Poly1305:llä on sama rajapinta:

```{.python tiedosto="esimerkit/04-aead.py" osa="chacha"}
```

```{.tuloste tiedosto="esimerkit/04-aead.odotettu"}
```

Väärällä avaimella tai muutetulla viestillä purku nostaa poikkeuksen.
Sitä ei pidä niellä hiljaa: hylätty viesti on hyökkäyksen tai vian
merkki ja kirjataan lokiin.

```{.python tiedosto="esimerkit/04-peukaloitu.kaatuu.py"}
```

```{.tuloste tiedosto="esimerkit/04-peukaloitu.virhe"}
```

## Testivektorit

Kryptografisten toteutusten oikeellisuus tarkistetaan standardien
*testivektoreilla*: kiinteillä syötteillä, joiden tulos on julkaistu.
Satunnaiset syötteet eivät paljasta virhettä, joka tuottaa
johdonmukaisesti väärän mutta purkautuvan tuloksen. RFC 8439 julkaisee
ChaCha20-Poly1305:n testivektorin:

```{.python tiedosto="esimerkit/04-testivektori.py"}
```

```{.tuloste tiedosto="esimerkit/04-testivektori.odotettu"}
```

## Noncen hallinta

AES-GCM:n ja ChaCha20-Poly1305:n nonce on 96 bittiä, ja sen on oltava
yksilöllinen jokaiselle samalla avaimella salatulle viestille. Kaksi
tapaa:

- **Satunnainen nonce** (`os.urandom(12)`) on yksinkertainen, mutta
  syntymäpäiväongelman vuoksi samalla avaimella saa salata enintään
  noin 2^32^ viestiä, ennen kuin törmäyksen todennäköisyys kasvaa
  liian suureksi. Raja on tarpeeksi suuri useimmille sovelluksille,
  mutta ei esimerkiksi verkkoliikenteen jokaiselle paketille.
- **Laskuri** on yksilöllinen niin kauan kuin sen tila säilyy. Sitä
  käytetään protokollissa (TLS, WireGuard), joissa kumpikin osapuoli
  pitää kirjaa lähetetyistä viesteistä.

Jos noncen yksilöllisyyttä ei voi taata, valitaan noncen toistoa
kestävä AES-GCM-SIV tai 192-bittisen noncen XChaCha20-Poly1305.

## Kirjekuorisalaus

Suurten tietomäärien avaimia ei kannata käyttää suoraan pääavaimella.
*Kirjekuorisalauksessa* (*envelope encryption*) jokainen tiedosto tai
tietue salataan omalla *datan avaimellaan* (DEK), ja datan avain
salataan *avainten avaimella* (KEK), joka on avaintenhallintapalvelussa
(KMS) tai laitteistoturvamoduulissa (HSM):

```{.python tiedosto="esimerkit/04-kirjekuori.py" osa="kirjekuori"}
```

```{.tuloste tiedosto="esimerkit/04-kirjekuori.odotettu"}
```

Avainten avaimen kierto salaa uudelleen vain 32 tavun datan avaimet,
ei gigatavujen dataa. Pilvipalveluiden tallennussalaus (AWS KMS, Google
Cloud KMS, Azure Key Vault) toimii näin.

## Käytännössä

- **Valmis rakenne ennen primitiiviä.** Jos kirjastossa on resepti,
  kuten `cryptography`:n `Fernet` tai libsodiumin `secretbox`, se on
  hyvä oletus. Sen formaatti sisältää version, noncen ja tunnisteen
  valmiiksi.
- **Formaattiin versio.** Salatun tiedon alkuun tallennetaan versio
  ja avaimen tunniste. Niiden avulla algoritmi ja avain voidaan
  vaihtaa myöhemmin (*crypto agility*).
- **Liitettyyn dataan konteksti.** Tietueen tunniste, omistaja,
  sarakkeen nimi ja formaatin versio estävät salattujen arvojen
  siirtämisen paikasta toiseen.
- **Ei omia yhdistelmiä.** "Salaa sitten MAC" on oikein vain, jos
  avaimet ovat erilliset, MAC kattaa noncen ja kaikki parametrit ja
  vertailu on vakioaikainen. AEAD hoitaa tämän valmiiksi.
- **Hinta:** AEAD lisää jokaiseen viestiin noncen ja tunnisteen
  (28 tavua). Pienissä viesteissä, kuten IoT-anturien lukemissa, se on
  merkittävä mutta perusteltu hinta.

## Itsearviointi

- Osaat salata ja purkaa tiedon AES-GCM:llä ja ChaCha20-Poly1305:llä ja
  käsitellä hylätyn viestin oikein.
- Osaat käyttää liitettyä dataa estämään salattujen arvojen siirtämisen
  toiseen kontekstiin.
- Osaat valita noncen luontitavan ja tunnet satunnaisen noncen rajan.
- Osaat selittää kirjekuorisalauksen ja avainten kierron.
