# mTLS Spring Boot -palvelussa

Edellisten lukujen mekanismit ovat JDK:n varassa, jotta ne näkyvät.
Tässä luvussa sama kootaan Spring Boot -palveluksi: laskutus vaatii
mTLS:n, tunnistaa kutsujan SPIFFE-tunnisteesta, antaa oikeudet
palvelukohtaisesti ja kirjaa auditointitapahtumat.

## SSL-nippu

Spring Boot kuvaa avaimet ja luotetut varmenteet *SSL-nippuina*
(*SSL bundle*). PEM-tiedostoja käyttävä nippu on lähinnä sitä, mitä
SPIRE-agentti tai cert-manager kirjoittaa kontin levylle:

```{.yaml tiedosto="esimerkit/palvelu/src/main/resources/application.yaml" osa="ssl"}
```

`client-auth: need` vaatii asiakasvarmenteen kuten luvussa 4.
`reload-on-update` seuraa tiedostoja ja ottaa uuden varmenteen
käyttöön ilman uudelleenkäynnistystä, kun automaatio kirjoittaa sen
(luku 5).

Testi luo varmentajan ja kirjoittaa PEM-tiedostot tilapäishakemistoon
ennen kuin sovellus käynnistyy:

```{.java tiedosto="esimerkit/palvelu/src/test/java/fi/tutoriaalit/palveluturva/palvelu/LaskupalveluTest.java" osa="pem"}
```

## Kutsuja Spring Securityssä

Spring Securityn X.509-todennus lukee oletuksena varmenteen aiheen
CN-kentän. Työkuormien varmenteissa identiteetti on SAN-kentässä,
joten poiminta vaihdetaan:

```{.java tiedosto="esimerkit/palvelu/src/main/java/fi/tutoriaalit/palveluturva/palvelu/Turvallisuus.java" osa="ketju"}
```

Oikeudet tulevat asetuksista. Luettelo on lyhyt ja luettava, ja sen
muutokset näkyvät katselmoinnissa:

```{.yaml tiedosto="esimerkit/palvelu/src/main/resources/application.yaml" osa="luvat"}
```

Rajapinta vaatii oikeuden menetelmäkohtaisesti ja kirjaa jokaisen
pyynnön auditointilokiin korrelaatiotunnisteineen (luku 12):

```{.java tiedosto="esimerkit/palvelu/src/main/java/fi/tutoriaalit/palveluturva/palvelu/LaskuRajapinta.java" osa="rajapinta"}
```

## Testi oikealla TLS:llä

Testi käynnistää palvelun satunnaiseen porttiin ja kutsuu sitä eri
palvelujen varmenteilla:

```{.java tiedosto="esimerkit/palvelu/src/test/java/fi/tutoriaalit/palveluturva/palvelu/LaskupalveluTest.java" osa="testi"}
```

Suositukset todennetaan, koska sen varmenteen on myöntänyt luotettu
varmentaja, mutta sillä ei ole yhtään oikeutta. Tuntemattoman
varmentajan varmenteella yhteys ei synny lainkaan.

## Palveluverkossa

Jos mTLS hoidetaan sivuvaunussa (Istio, Linkerd), sovellus kuuntelee
tavallista HTTP:tä paikallisessa osoitteessa ja saa kutsujan
identiteetin otsakkeesta (Istiossa `X-Forwarded-Client-Cert`). Silloin
`x509()` korvataan esitodennuksella (*pre-authentication*), joka lukee
otsakkeen. Edellytykset ovat samat kuin luvussa 10: sovellukseen ei
pääse ohi sivuvaunun, ja sivuvaunu poistaa saapuvista pyynnöistä
otsakkeen. Istion `AuthorizationPolicy` voi tehdä palvelukohtaisen
valtuutuksen jo sivuvaunussa, mutta resurssitason päätökset (kenen
lasku) jäävät sovellukselle.

## Käytännössä

- **SAN, ei CN.** SPIFFE-tunniste ja muut identiteetit ovat SAN-
  kentässä. CN on vanhentunut ja usein tyhjä.
- **Tunnistamaton varmenne ei saa oikeuksia.** Luotetun varmentajan
  myöntämä tuntematon palvelu todennetaan, mutta sen oikeuksien
  joukko on tyhjä.
- **Oikeudet asetuksiin tai käytäntömoottoriin**, ei koodiin
  hajalleen. Luettelo palvelu → oikeudet on helppo katselmoida.
- **Testaa oikealla TLS:llä.** MockMvc ohittaa TLS:n kokonaan; vain
  oikea kättely testaa, että varmenteet, luottamusnippu ja `need`
  ovat kunnossa.

## Itsearviointi

- Osaat konfiguroida Spring Bootin SSL-nipun ja vaatia
  asiakasvarmenteen.
- Osaat poimia kutsujan identiteetin SAN-kentästä Spring Securityssä
  ja antaa oikeudet sen mukaan.
- Osaat testata mTLS-palvelun oikealla kättelyllä eri
  identiteeteillä.
- Osaat kertoa, mikä muuttuu, kun mTLS hoidetaan palveluverkossa.
