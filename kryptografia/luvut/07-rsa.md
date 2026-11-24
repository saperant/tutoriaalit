# Julkisen avaimen salaus: RSA

Symmetrisessä salauksessa osapuolten on jaettava avain etukäteen.
*Julkisen avaimen* menetelmissä avainpari on kaksiosainen: julkinen
avain voidaan antaa kenelle tahansa, ja vain salaisen avaimen haltija
voi purkaa julkisella avaimella salatun viestin tai tehdä
allekirjoituksen, jonka julkinen avain varmentaa.

RSA (Rivest, Shamir, Adleman, 1977) perustuu siihen, että suurten
lukujen kertominen on helppoa mutta tulon jakaminen tekijöihin vaikeaa.

## RSA pienillä luvuilla

Avaimen luonti valitsee kaksi alkulukua *p* ja *q* ja laskee modulin
*n = pq*. Salainen eksponentti *d* on julkisen eksponentin *e*
käänteisluku modulo φ(n):

```{.python tiedosto="esimerkit/07-rsa-opetus.py" osa="avaimet"}
```

Salaus on potenssiin korotus modulo *n*, ja purku toinen potenssiin
korotus. Se toimii, koska Eulerin lauseen nojalla
$m^{ed} \equiv m \pmod{n}$:

```{.python tiedosto="esimerkit/07-rsa-opetus.py" osa="salaus"}
```

Allekirjoitus on sama operaatio toisin päin: salainen avain korottaa,
julkinen tarkistaa.

```{.python tiedosto="esimerkit/07-rsa-opetus.py" osa="allekirjoitus"}
```

## Oppikirja-RSA on rikki

Edellä kuvattu "oppikirja-RSA" on turvaton kolmesta syystä:

```{.python tiedosto="esimerkit/07-rsa-opetus.py" osa="heikkoudet"}
```

```{.tuloste tiedosto="esimerkit/07-rsa-opetus.odotettu"}
```

1. **Deterministisyys:** hyökkääjä voi salata arvauksensa julkisella
   avaimella ja verrata. Lyhyet viestit, kuten "kyllä" ja "ei",
   paljastuvat.
2. **Muokattavuus:** salatun viestin voi muuttaa toisen viestin
   salaukseksi tietämättä kumpaakaan.
3. **Avaimen koko:** turvallisuus edellyttää, ettei *n*:ää voi jakaa
   tekijöihin. Nykysuositus on vähintään 2048 bittiä, mieluiten 3072.

Siksi RSA:ta käytetään aina *täytteen* (*padding*) kanssa, joka
satunnaistaa ja jäsentää viestin ennen korotusta:

| Käyttö | Täyte | Huomio |
|--------|-------|--------|
| salaus | OAEP | PKCS#1 v1.5 -salaus on altis Bleichenbacherin hyökkäykselle |
| allekirjoitus | PSS | PKCS#1 v1.5 -allekirjoitus on yhä yleinen ja hyväksyttävä |

## RSA oikein

Kirjasto luo avaimen oikean kokoisista alkuluvuista ja hoitaa täytteet:

```{.python tiedosto="esimerkit/07-rsa-oikein.py" osa="avain"}
```

```{.python tiedosto="esimerkit/07-rsa-oikein.py" osa="oaep"}
```

```{.python tiedosto="esimerkit/07-rsa-oikein.py" osa="pss"}
```

```{.tuloste tiedosto="esimerkit/07-rsa-oikein.odotettu"}
```

RSA-OAEP salaa enintään noin 300 tavua 3072-bittisellä avaimella. Sillä
ei salata dataa vaan symmetrinen avain, jolla data salataan
(*hybridisalaus*). Nykyprotokollissa RSA-salausta ei juuri käytetä:
avain sovitaan Diffie–Hellmanilla (luku 8), ja RSA:ta käytetään
allekirjoituksiin.

## Käytännössä

- **Uusiin järjestelmiin elliptiset käyrät.** Ed25519 ja X25519 ovat
  nopeampia, avaimet ja allekirjoitukset ovat pienempiä, ja niissä on
  vähemmän tapoja tehdä virheitä. RSA on perusteltu, kun
  yhteensopivuus vaatii (vanhat järjestelmät, osa HSM-laitteista).
- **Avaimen koko:** RSA-2048 vastaa noin 112-bittistä ja RSA-3072
  128-bittistä turvallisuutta. RSA-4096 on hidas ja hyödyllinen lähinnä
  pitkäikäisille juuriavaimille.
- **e = 65537.** Pieni julkinen eksponentti (e = 3) on aiheuttanut
  hyökkäyksiä huonon täytteen kanssa.
- **Hinta:** RSA-allekirjoitus on salaisella avaimella hidas
  (millisekunteja), tarkistus nopea. Avaimen luonti vie 3072 bitillä
  satoja millisekunteja, joten avaimia ei luoda pyyntökohtaisesti.
- **Avaintiedostot:** salaiset avaimet tallennetaan PKCS#8-muodossa
  salasanalla suojattuna tai, mieluummin, avaintenhallintapalveluun tai
  HSM:ään, josta ne eivät koskaan poistu.

## Itsearviointi

- Osaat laskea RSA:n avaimet, salauksen ja allekirjoituksen pienillä
  luvuilla ja selittää, miksi se toimii.
- Osaat nimetä oppikirja-RSA:n kolme heikkoutta ja täytteet, jotka
  korjaavat ne.
- Osaat salata OAEP:lla ja allekirjoittaa PSS:llä kirjastoa käyttäen.
- Osaat perustella, milloin RSA on oikea valinta ja milloin ei.
