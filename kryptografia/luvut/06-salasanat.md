# Salasanojen tallennus

Palvelu ei tallenna salasanoja, vaan niistä lasketun tarkisteen.
Kirjautuessa tarkiste lasketaan uudelleen ja verrataan. Tavoitteena on,
että vuotanut käyttäjätietokanta ei paljasta salasanoja, tai ainakin
niiden murtaminen on kallista. Ihmisten salasanat ovat ennustettavia ja
toistuvat palvelusta toiseen, joten vuoto yhdestä palvelusta uhkaa
käyttäjien tilejä muuallakin.

## Miksi tavallinen tiiviste ei riitä

Kokeillaan tilannetta, jossa tietokanta on vuotanut ja hyökkääjällä on
lista yleisistä salasanoista:

```{.python tiedosto="esimerkit/06-sanakirja.py" osa="suolaton"}
```

Ilman suolaa hyökkääjä laskee listan tiivisteet kerran ja vertaa niitä
kaikkiin käyttäjiin. Samat salasanat näkyvät samoina tiivisteinä.
*Suola* on käyttäjäkohtainen satunnainen arvo, joka tallennetaan
tiivisteen viereen:

```{.python tiedosto="esimerkit/06-sanakirja.py" osa="suolattu"}
```

```{.tuloste tiedosto="esimerkit/06-sanakirja.odotettu"}
```

Suola estää valmiit taulukot ja paljastaa vain, kuinka monta kertaa
kutakin käyttäjää vastaan joudutaan arvaamaan. Heikot salasanat murtuvat
silti, koska SHA-256:ta lasketaan näytönohjaimella kymmeniä miljardeja
kertoja sekunnissa. Salasanatiivisteen on siksi oltava *tarkoituksella
hidas* ja *muistia vaativa*, jotta näytönohjaimet ja erikoispiirit eivät
saa suurta etua.

## Argon2id

**Argon2id** voitti salasanatiivisteiden kilpailun (Password Hashing
Competition) 2015 ja on nykyinen suositus (RFC 9106). Sen asetukset:

- *muisti* (`memory_cost`, KiB): kuinka paljon muistia yksi laskenta
  vaatii,
- *kierrokset* (`iterations`): montako kertaa muisti käydään läpi,
- *kaistat* (`lanes`): rinnakkaisuus.

OWASP:n vähimmäissuositus on 19 MiB muistia, 2 kierrosta ja 1 kaista.
Arvot valitaan niin, että yksi tarkistus vie palvelimella noin
50–500 ms.

```{.python tiedosto="esimerkit/06-argon2.py" osa="asetukset"}
```

```{.python tiedosto="esimerkit/06-argon2.py" osa="tallennus"}
```

```{.tuloste tiedosto="esimerkit/06-argon2.odotettu"}
```

Tulos tallennetaan *PHC-merkkijonona*, jossa ovat algoritmi, versio,
asetukset, suola ja tiiviste. Tarkistus lukee asetukset merkkijonosta,
joten asetuksia voidaan kiristää vanhoja tiivisteitä rikkomatta. Kun
käyttäjä kirjautuu onnistuneesti vanhoilla asetuksilla tallennetulla
tiivisteellä, salasana tiivistetään uusilla asetuksilla.

## scrypt ja bcrypt

**scrypt** (RFC 7914) on myös muistia vaativa, ja se on Pythonin
vakiokirjastossa:

```{.python tiedosto="esimerkit/06-scrypt.py" osa="scrypt"}
```

```{.tuloste tiedosto="esimerkit/06-scrypt.odotettu"}
```

**bcrypt** (1999) on yhä laajasti käytössä ja hyväksyttävä, kun
työkerroin on vähintään 10. Se katkaisee salasanan 72 tavuun eikä vaadi
muistia, joten se on näytönohjaimilla nopeampi murtaa kuin Argon2id.
**PBKDF2** on FIPS-hyväksytty, ja sitä käytetään, kun sääntely vaatii;
sille tarvitaan suuri kierrosmäärä (OWASP: 600 000 kierrosta
SHA-256:lla).

## Pippuri ja muut täydennykset

*Pippuri* (*pepper*) on kaikille käyttäjille yhteinen salainen avain,
jota ei tallenneta tietokantaan vaan esimerkiksi salaisuusvarastoon.
Se voidaan antaa Argon2:lle `secret`-parametrina tai tiivisteet voidaan
salata AEAD:lla. Jos vain tietokanta vuotaa, tiivisteitä ei voi murtaa
lainkaan. Pippurin kierto on kuitenkin hankalaa, joten se on lisäsuoja
eikä korvaa hyvää salasanatiivistettä.

## Käytännössä

- **Ei omaa toteutusta.** Kirjastot: Pythonissa `argon2-cffi` tai
  `cryptography`, Javassa Spring Securityn `Argon2PasswordEncoder`,
  Nodessa `argon2`, PHP:ssä `password_hash`. Useimmat kehykset tekevät
  myös uudelleentiivistyksen puolestasi.
- **Pituusrajat:** vähintään 8 merkkiä (NIST SP 800-63B: 15 ilman
  monivaiheista tunnistusta), enimmäispituus vähintään 64 merkkiä.
  Pakolliset erikoismerkit ja säännöllinen vaihto eivät auta: ne
  johtavat ennustettaviin malleihin, kuten `Kevät2026!`.
- **Vuotaneet salasanat torjutaan.** Rekisteröinnissä tarkistetaan,
  ettei salasana ole tunnetussa vuotolistassa (esim. Have I Been Pwned
  -palvelun k-anonymiteettirajapinta).
- **Yritysten rajoitus.** Hidas tiiviste suojaa vuotanutta tietokantaa;
  verkon yli tehtyjä arvauksia rajoitetaan erikseen (taidot
  *Tietoturvan perusteet* ja *Web-sovellusten tietoturva*).
- **Palvelunesto:** hidas tiiviste on myös hyökkääjän työkalu.
  Kirjautumisyritysten määrää rajoitetaan ennen tiivisteen laskentaa.
- **Mieluiten ei salasanoja lainkaan.** Pääsyavaimet (WebAuthn) ja
  kertakirjautuminen poistavat salasanojen tallennuksen kokonaan.

## Itsearviointi

- Osaat selittää, miksi nopea tiiviste ei sovi salasanoille ja mitä
  suola estää ja mitä ei.
- Osaat tallentaa ja tarkistaa salasanan Argon2id:llä PHC-muodossa ja
  päivittää asetukset kirjautumisen yhteydessä.
- Osaat valita Argon2id-asetukset ja perustella ne vasteajalla.
- Osaat kertoa, milloin bcrypt, scrypt tai PBKDF2 on hyväksyttävä
  valinta.
