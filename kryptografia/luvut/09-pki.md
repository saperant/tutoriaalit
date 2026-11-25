# Varmenteet ja julkisen avaimen infrastruktuuri

Allekirjoitus todistaa, että viestin lähettäjällä on tietty salainen
avain. Se ei kerro, *kenen* avain se on. *Varmenne* (*certificate*)
sitoo julkisen avaimen nimeen: varmentaja (*certificate authority*, CA)
allekirjoittaa väitteen "avain X kuuluu palvelulle palvelu.example".
*Julkisen avaimen infrastruktuuri* (PKI) on varmentajien, sääntöjen ja
työkalujen kokonaisuus, joka tekee tästä luotettavaa.

## X.509-varmenne

Verkon varmenteet noudattavat X.509-standardia (RFC 5280). Tärkeimmät
kentät:

| Kenttä | Sisältö |
|--------|---------|
| Subject | kenelle varmenne on myönnetty |
| Issuer | kuka sen allekirjoitti |
| Validity | voimassaoloaika (*not before*, *not after*) |
| Subject Public Key | julkinen avain |
| Subject Alternative Name | nimet, joihin varmenne kelpaa (DNS, IP) |
| Basic Constraints | saako varmenteella allekirjoittaa muita varmenteita |
| Key Usage, Extended Key Usage | mihin avainta saa käyttää |
| Serial Number | varmentajan yksilöllinen numero (sulkulistoja varten) |

Nimen tarkistus tehdään *Subject Alternative Name* -kentästä; pelkän
*Common Name* -kentän tarkistusta selaimet eivät ole hyväksyneet
vuosiin.

## Luottamusketju

Selaimessa ja käyttöjärjestelmässä on noin 150 *juurivarmentajan*
varmennetta. Juuriavaimet säilytetään eristettyinä, ja ne allekirjoittavat
*välivarmentajia*, jotka myöntävät palvelinvarmenteet. Palvelin lähettää
oman varmenteensa ja välivarmenteet, ja asiakas rakentaa ketjun
luottamaansa juureen:

```{.dot otsikko="Luottamusketju. Palvelin lähettää palvelin- ja välivarmenteen; juurivarmenne on asiakkaalla valmiina."}
digraph {
  rankdir=LR; nodesep=0.4; ranksep=0.45;
  juuri [label="juurivarmenne\n(itse allekirjoitettu)"];
  vali [label="välivarmenne\nCA: kyllä"];
  palvelin [label="palvelinvarmenne\npalvelu.example\nCA: ei"];
  juuri -> vali [label="allekirjoittaa"];
  vali -> palvelin [label="allekirjoittaa"];
  sailo [label="asiakkaan\nluottamussäilö", shape=cylinder];
  { rank=same; sailo -> juuri [style=dashed, label="sisältää"]; }
}
```

Asiakas tarkistaa ketjusta neljä asiaa:

1. jokaisen varmenteen allekirjoitus tarkistetaan myöntäjän avaimella,
2. jokainen varmenne on voimassa, ja myöntäjät ovat CA-varmenteita,
3. palvelinvarmenteen nimi vastaa osoitetta, johon yhdistettiin,
4. varmenne ei ole sulkulistalla.

## Oma varmentaja OpenSSL:llä

Sisäverkon palveluille ja testaukseen tehdään usein oma varmentaja:

```{.bash tiedosto="esimerkit/09-ca.sh" osa="ca"}
```

Palvelin luo oman avaimensa ja *varmennepyynnön* (CSR). Salainen avain
ei koskaan lähde palvelimelta; CA näkee vain julkisen avaimen:

```{.bash tiedosto="esimerkit/09-ca.sh" osa="palvelin"}
```

```{.bash tiedosto="esimerkit/09-ca.sh" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/09-ca.odotettu"}
```

## Sama Pythonilla

`cryptography`-kirjaston rakentajalla varmenteita luodaan esimerkiksi
testeissä ja laitteiden tuotannossa. Kirjasto osaa myös tarkistaa
ketjun samoin säännöin kuin selain:

```{.python tiedosto="esimerkit/09-varmenne.py" osa="ca"}
```

```{.python tiedosto="esimerkit/09-varmenne.py" osa="palvelin"}
```

```{.python tiedosto="esimerkit/09-varmenne.py" osa="tarkistus"}
```

```{.tuloste tiedosto="esimerkit/09-varmenne.odotettu"}
```

## Sulkeminen ja voimassaolo

Jos salainen avain vuotaa, varmenne on *suljettava* (*revoke*) ennen
voimassaolon päättymistä. Sulkulistat (CRL) ja OCSP-kyselyt ovat
osoittautuneet hankaliksi: ne ovat hitaita, ja epäonnistunut tarkistus
ohitetaan usein. Siksi suunta on lyhyissä voimassaoloajoissa:
CA/Browser Forumin päätöksellä julkisten TLS-varmenteiden
enimmäiskesto lyhenee vaiheittain 47 päivään vuoteen 2029 mennessä,
ja Let's Encrypt tarjoaa jo muutaman päivän varmenteita. Lyhyt
voimassaolo edellyttää automaatiota: ACME-protokolla (RFC 8555) hakee
ja uusii varmenteet itse.

*Certificate Transparency* (CT) -lokeihin kirjataan jokainen julkisesti
myönnetty varmenne. Verkkotunnuksen omistaja voi seurata lokeja ja
huomata, jos joku on saanut varmenteen hänen nimelleen.

## Käytännössä

- **Julkiset palvelut: ACME.** Let's Encrypt tai muu ACME-palvelu ja
  automaattinen uusinta (certbot, Caddy, Kubernetesin cert-manager).
  Käsin uusittavat varmenteet vanhenevat aikanaan tuotannossa.
- **Sisäverkko: oma CA, ei itse allekirjoitettuja varmenteita.**
  Itse allekirjoitettu palvelinvarmenne opettaa käyttäjät ohittamaan
  varoitukset. Oman CA:n juurivarmenne jaetaan laitteille hallitusti
  (esim. step-ca, HashiCorp Vault PKI).
- **Ei varmennetarkistuksen ohitusta.** `verify=False`, `curl -k` ja
  `InsecureSkipVerify` poistavat TLS:n hyödyn. Testeissä luodaan
  testivarmentaja, kuten esimerkissä.
- **Laajennukset oikein:** CA-varmenteessa `basicConstraints=CA:TRUE`
  ja `keyCertSign`, palvelinvarmenteessa SAN-nimet ja
  `serverAuth`. Puuttuvat laajennukset rikkovat tiukat tarkistajat,
  kuten Python 3.13:n oletusasetukset.
- **Salaiset avaimet suojaan.** CA:n avain HSM:ään tai ainakin
  verkosta irrotetulle koneelle; palvelimen avain luetaan vain
  palveluprosessin oikeuksilla.

## Itsearviointi

- Osaat kuvata X.509-varmenteen tärkeimmät kentät ja luottamusketjun
  tarkistuksen vaiheet.
- Osaat luoda oman varmentajan ja palvelinvarmenteen OpenSSL:llä ja
  tarkistaa ketjun ja nimen.
- Osaat luoda ja tarkistaa varmenteita ohjelmallisesti testejä varten.
- Osaat selittää, miksi voimassaoloajat lyhenevät ja miten ACME ja CT
  liittyvät siihen.
