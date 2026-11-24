# Sivukanavat ja yleiset virheet

Matemaattisesti vahva algoritmi voi vuotaa salaisuuksia toteutuksen
kautta: ajoituksesta, virheilmoituksista, muistin käytöstä tai
virrankulutuksesta. Tällaisia vuotoja kutsutaan *sivukanaviksi*. Tämä
luku kokoaa yleisimmät sivukanavat ja virheet, joita kirjastojen
käyttäjät tekevät.

## Ajoitusvuoto

Tavallinen merkkijonovertailu palaa heti ensimmäisestä erosta. Jos
palvelin vertaa käyttäjän antamaa tunnistetta oikeaan, vastausaika
kertoo, montako alkumerkkiä meni oikein:

```{.python tiedosto="esimerkit/11-vertailu.py" osa="naiivi"}
```

```{.python tiedosto="esimerkit/11-vertailu.py" osa="hyokkays"}
```

Hyökkääjä arvaa merkin kerrallaan: 16 vaihtoehtoa kerran merkkiä kohti
16^10^ vaihtoehdon sijaan. Verkon yli eroja mitataan tilastollisesti
tuhansien pyyntöjen keskiarvoina, ja hyökkäys on osoitettu toimivaksi
myös internetin yli. Korjaus on vakioaikainen vertailu:

```{.python tiedosto="esimerkit/11-vertailu.py" osa="oikein"}
```

```{.tuloste tiedosto="esimerkit/11-vertailu.odotettu"}
```

Sama periaate koskee kaikkea salaisuudesta riippuvaa: ehtolauseita,
taulukkoindeksejä ja silmukoiden pituuksia. Kirjastojen kryptografiset
toteutukset on kirjoitettu *vakioaikaisiksi*; oma koodi ei yleensä ole.

## Virheviesti oraakkelina

CBC-tilassa purkaja poistaa täytteen. Jos palvelin vastaa eri tavalla
virheelliseen täytteeseen kuin muihin virheisiin, se toimii
*täyteoraakkelina* (*padding oracle*):

```{.python tiedosto="esimerkit/11-padding-oraakkeli.py" osa="oraakkeli"}
```

Hyökkääjä muuttaa edellistä lohkoa tavu kerrallaan ja kysyy
oraakkelilta, onko täyte kelvollinen. Kelvollinen täyte paljastaa yhden
tavun AES-purun välituloksesta, ja XOR edellisen lohkon kanssa
paljastaa selvätekstin:

```{.python tiedosto="esimerkit/11-padding-oraakkeli.py" osa="hyokkays"}
```

```{.tuloste tiedosto="esimerkit/11-padding-oraakkeli.odotettu"}
```

Koko viesti purkautuu enintään 4 096 kyselyllä lohkoa kohti. Hyökkäys
(Vaudenay 2002) on murtanut muun muassa ASP.NET:n, Javan
palvelinkirjastoja ja SSL 3.0:n (POODLE). Se on myös esimerkki
yleisemmästä säännöstä: purun on joko onnistuttava tai epäonnistuttava
yhdellä tavalla, ja eheys on tarkistettava *ennen* purkua. AEAD tekee
tämän rakenteellisesti.

## Muut sivukanavat

- **Välimuistiajoitus:** taulukkopohjainen AES-ohjelmistototeutus
  vuotaa avainta välimuistin kautta saman koneen toiselle prosessille.
  Laitteistototeutus (AES-NI) ja vakioaikaiset kirjastot poistavat
  ongelman.
- **Spekulatiivinen suoritus** (Spectre, Meltdown) vuotaa muistia
  suorittimen ennakoivan suorituksen kautta. Suojaus on
  käyttöjärjestelmän, kääntäjän ja selaimen tehtävä.
- **Virrankulutus ja sähkömagneettinen säteily** paljastavat avaimia
  sulautetuista laitteista ja älykorteista. Niitä käsitellään taidossa
  *Sulautettujen järjestelmien tietoturva*.
- **Pakkaus ennen salausta** paljastaa sisällön pituuden kautta
  (CRIME, BREACH), jos hyökkääjä voi lisätä omaa tekstiään samaan
  viestiin salaisuuden kanssa.

## Yleisimmät virheet

| Virhe | Seuraus | Oikein |
|-------|---------|--------|
| `random` avaimille ja tunnisteille | tunnisteet ennustettavissa | `secrets` (luku 2) |
| ECB tai salaus ilman eheyttä | rakenne vuotaa, muokattavuus | AEAD (luvut 3–4) |
| kovakoodattu tai toistuva nonce | avainvirta ja GCM:n tunnisteavain vuotavat | satunnainen tai laskuri (luku 4) |
| `sha256(avain + viesti)` | pituuslaajennus | HMAC (luku 5) |
| nopea tiiviste salasanoille | vuoto murtuu | Argon2id (luku 6) |
| oppikirja-RSA tai PKCS#1 v1.5 -salaus | salaus purkautuu | OAEP, mieluummin ECC (luvut 7–8) |
| varmennetarkistuksen ohitus | välimieshyökkäys | testivarmentaja (luku 9) |
| `==` salaisuuksien vertailuun | ajoitusvuoto | `hmac.compare_digest` |
| avain koodissa tai versionhallinnassa | kaikki salaus purettavissa | salaisuusvarasto, KMS |

## Avaintenhallinta

Salaus siirtää ongelman datan suojaamisesta avaimen suojaamiseen.
Käytännön järjestelmissä avaimet ovat useimmiten heikoin lenkki:

- **Avaimet pois koodista.** Avaimet ja salaisuudet luetaan
  ympäristöstä, salaisuusvarastosta (Vault, pilven Secret Manager) tai
  KMS:stä. Versionhallintaan joutunut avain on vaihdettava, vaikka
  commit poistettaisiin (taito *Tietoturva kehitystyössä*).
- **Vähimmät oikeudet.** Palvelu, joka vain salaa, ei tarvitse
  purkuoikeutta; KMS:ssä oikeudet annetaan operaatiokohtaisesti.
- **Kierto ja versiot.** Jokaisella avaimella on tunniste, joka
  tallennetaan salatun datan mukana (luku 4). Kierto on harjoiteltu
  rutiini, ei hätätoimenpide.
- **Laitteistosuojaus.** Arvokkaimmat avaimet (CA:n juuri, maksuliikenne)
  ovat HSM:ssä, josta niitä ei voi kopioida.

## Käytännössä

- **Korkean tason rajapinnat ensin.** Mitä vähemmän valintoja
  kehittäjä tekee, sitä vähemmän virheitä: TLS-kirjaston oletuskonteksti,
  `Fernet`, libsodium, `age`, HPKE.
- **Tarkistuslistat katselmointiin.** Satunnaisuuden lähde, nonce,
  eheys, vertailu, avainten säilytys ja versiointi käydään läpi
  jokaisessa kryptografiaa koskevassa muutoksessa.
- **Testivektorit ja negatiiviset testit.** Testataan, että väärä
  avain, muutettu viesti ja vanhentunut varmenne *hylätään*. Pelkkä
  onnistuneen polun testi ei paljasta, onko suoja päällä.
- **Asiantuntija-arvio.** Uusi protokolla tai kryptografinen
  arkkitehtuuri katselmoidaan alan asiantuntijalla ennen tuotantoa.

## Itsearviointi

- Osaat selittää ajoitusvuodon ja korjata sen vakioaikaisella
  vertailulla.
- Osaat kuvata täyteoraakkelihyökkäyksen periaatteen ja miksi AEAD
  estää sen.
- Osaat tunnistaa koodikatselmoinnissa taulukon yleiset virheet.
- Osaat suunnitella avainten säilytyksen, kierron ja oikeudet.
