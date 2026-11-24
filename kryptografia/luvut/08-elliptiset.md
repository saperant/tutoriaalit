# Diffie–Hellman, elliptiset käyrät ja allekirjoitukset

## Diffie–Hellman

Diffie–Hellman (1976) ratkaisee ongelman, jota symmetrinen kryptografia
ei ratkaise: miten kaksi osapuolta sopivat yhteisestä salaisuudesta
julkisen kanavan yli. Kumpikin valitsee salaisen luvun ja lähettää
julkisen arvon; molemmat päätyvät samaan tulokseen, mutta salakuuntelija
ei voi laskea sitä:

```{.python tiedosto="esimerkit/08-dh-opetus.py" osa="dh"}
```

Turvallisuus perustuu *diskreetin logaritmin ongelmaan*: arvosta
*g^a^ mod p* ei saa tehokkaasti selville eksponenttia *a*, kun *p* on
suuri.

Diffie–Hellman yksinään ei kerro, *kenen* kanssa avain sovittiin.
Välissä oleva hyökkääjä voi sopia oman avaimen kummankin kanssa:

```{.python tiedosto="esimerkit/08-dh-opetus.py" osa="mitm"}
```

```{.tuloste tiedosto="esimerkit/08-dh-opetus.odotettu"}
```

Siksi avaintenvaihto *todennetaan*: vähintään toinen osapuoli
allekirjoittaa kättelyn, ja allekirjoituksen julkinen avain on
varmennettu (luvut 9 ja 10).

## Elliptiset käyrät

Elliptisen käyrän kryptografiassa (ECC) lukujen tilalla ovat käyrän
pisteet äärellisessä kunnassa. Pisteitä voi "laskea yhteen"
geometrisella säännöllä, ja *skalaarikertolasku* *kG* (piste *G* lisättynä
itseensä *k* kertaa) on helppo laskea mutta vaikea kumota. Sama
turvallisuus saavutetaan paljon pienemmillä avaimilla kuin RSA:lla:
256-bittinen käyrä vastaa 3072-bittistä RSA:ta.

Opetusesimerkin käyrässä on vain 19 pistettä:

```{.python tiedosto="esimerkit/08-kayra-opetus.py" osa="ryhmalaki"}
```

```{.python tiedosto="esimerkit/08-kayra-opetus.py" osa="ecdh"}
```

```{.tuloste tiedosto="esimerkit/08-kayra-opetus.odotettu"}
```

*19G* on äärettömyyspiste, eli *G*:n kertaluku on 19. Oikeissa käyrissä
kertaluku on noin 2^255^. Käyrän valinta on itsessään kryptografiaa:
standardikäyrät (Curve25519, P-256) on valittu niin, että
toteutuksessa on vähän ansoja.

| Käyrä | Avaintenvaihto | Allekirjoitus | Huomio |
|-------|----------------|---------------|--------|
| Curve25519 | X25519 | Ed25519 | moderni oletus, vaikea käyttää väärin |
| P-256 (secp256r1) | ECDH | ECDSA | FIPS-hyväksytty, laaja tuki |
| secp256k1 | ECDH | ECDSA, Schnorr | lohkoketjut |

## X25519 käytännössä

X25519-avaintenvaihdon tulos ei ole sellaisenaan avain, vaan siitä
johdetaan avaimet HKDF:llä:

```{.python tiedosto="esimerkit/08-x25519.py" osa="istunto"}
```

```{.python tiedosto="esimerkit/08-x25519.py" osa="vaihto"}
```

```{.tuloste tiedosto="esimerkit/08-x25519.odotettu"}
```

Ensimmäinen rivi tarkistaa toteutuksen RFC 7748:n testivektoria vastaan.
Kun molemmat osapuolet luovat jokaiselle yhteydelle uuden avainparin
(*efemeerinen* avaintenvaihto), vanhat viestit pysyvät salassa, vaikka
pitkäaikainen avain myöhemmin vuotaisi. Tätä kutsutaan
*eteenpäin salaisuudeksi* (*forward secrecy*).

## Digitaaliset allekirjoitukset

Allekirjoitus todistaa, että viesti on salaisen avaimen haltijalta eikä
sitä ole muutettu. Toisin kuin MAC, allekirjoituksen voi tarkistaa
kuka tahansa julkisella avaimella, joten se tarjoaa myös
kiistämättömyyden.

```{.python tiedosto="esimerkit/08-ed25519.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-ed25519.odotettu"}
```

Ed25519 on *deterministinen*: sama viesti tuottaa saman
allekirjoituksen. ECDSA sen sijaan tarvitsee jokaiselle allekirjoitukselle
satunnaisluvun, ja jos sama luku toistuu tai on ennustettava, salainen
avain paljastuu. Näin murrettiin PlayStation 3:n
laiteohjelmistoavain 2010. Nykyiset ECDSA-toteutukset johtavat luvun
deterministisesti (RFC 6979).

Komentorivillä allekirjoitus tehdään `openssl pkeyutl`-komennolla:

```{.bash tiedosto="esimerkit/08-openssl-allekirjoitus.sh" osa="allekirjoitus"}
```

```{.tuloste tiedosto="esimerkit/08-openssl-allekirjoitus.odotettu"}
```

Ohjelmistojakelussa allekirjoituksia tehdään työkaluilla, jotka
hoitavat myös avainten jakelun: **minisign**, **signify**,
**Sigstore**/**cosign** (konttikuvat ja paketit) ja **GPG**.

## Käytännössä

- **Oletuksena X25519 ja Ed25519.** P-256 ja ECDSA, kun vaaditaan
  FIPS-hyväksyntää tai yhteensopivuutta.
- **Avaintenvaihto todennetaan aina.** Pelkkä Diffie–Hellman on altis
  välimieshyökkäykselle. Käytä valmista protokollaa: TLS, Noise
  (WireGuard, Signal) tai HPKE (RFC 9180).
- **Julkiset avaimet tarkistetaan.** Vieraan julkisen avaimen on oltava
  käyrän piste. X25519 hoitaa tämän rakenteellisesti; muilla käyrillä
  kirjaston on tarkistettava se, tai *invalid curve* -hyökkäys
  paljastaa salaisen avaimen.
- **Allekirjoitettu sisältö yksiselitteiseksi.** Allekirjoitetaan
  kanoninen tavujono, johon kuuluu konteksti (mitä allekirjoitus
  koskee). Muuten samaa allekirjoitusta voidaan käyttää toiseen
  tarkoitukseen.
- **Hinta:** X25519 ja Ed25519 ovat noin kymmenen kertaa nopeampia kuin
  RSA-3072:n salaiset operaatiot, ja avaimet ovat 32 tavua.

## Itsearviointi

- Osaat selittää Diffie–Hellmanin ja miksi se tarvitsee todennuksen.
- Osaat kuvata elliptisen käyrän ryhmälain ja skalaarikertolaskun
  periaatteen ja niiden suhteen avainten kokoon.
- Osaat sopia istuntoavaimen X25519:llä ja HKDF:llä ja selittää
  eteenpäin salaisuuden.
- Osaat allekirjoittaa ja tarkistaa Ed25519:llä sekä Pythonilla että
  OpenSSL:llä.
