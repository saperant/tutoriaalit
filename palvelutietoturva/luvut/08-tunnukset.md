# Dynaamiset tunnukset ja jaetut avaimet

Staattinen tietokannan salasana on tyypillisesti yhteinen kaikille
palvelun instansseille, voimassa vuosia ja usein muillekin
tiedossa. Dynaamiset tunnukset kääntävät asetelman: jokainen
instanssi saa omat tunnuksensa, jotka on luotu sille ja jotka
vanhenevat itsestään.

## Vuokrattu tunnus

Salaisuusvarasto luo tietokantaan uuden käyttäjän pyynnöstä ja antaa
sen palvelulle vuokrana (*lease*). Kun vuokra päättyy, varasto
poistaa käyttäjän tietokannasta:

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/Salaisuusvarasto.java" osa="dynaaminen"}
```

Esimerkissä tietokanta kysyy varastolta, kelpaako tunnus. Oikeassa
Vaultissa varasto luo käyttäjän tietokantaan SQL-lauseella ja poistaa
sen vuokran päättyessä, joten tietokanta tarkistaa tunnukset itse.

```{.java tiedosto="esimerkit/salaisuudet/src/test/java/fi/tutoriaalit/palveluturva/salaisuudet/SalaisuudetTest.java" osa="dynaaminenTesti"}
```

Dynaamisista tunnuksista on kolme hyötyä:

- **Vuoto vanhenee.** Lokiin tai muistivedokseen päätynyt tunnus
  kelpaa vain vuokran ajan.
- **Jäljitettävyys.** Tietokannan lokissa näkyvä käyttäjä `v-1f3a…`
  kertoo, mikä instanssi teki mitä. Yhteisellä salasanalla kaikki
  näyttävät samalta.
- **Kumoaminen on kohdennettu.** Murretun palvelun tunnukset voidaan
  kumota kaikki kerralla vaikuttamatta muihin palveluihin.

Hinta on riippuvuus: jos varasto ei vastaa, uusia tunnuksia ei saa.
Vuokrat uusitaan hyvissä ajoin ennen päättymistä, ja varasto on
korkean saatavuuden palvelu.

## Jaetun avaimen kierto ilman katkoa

Kaikkea ei voi tehdä dynaamiseksi. Kolmannen osapuolen API-avain tai
webhook-viestien allekirjoitusavain on jaettu kahden osapuolen
kesken. Sen kierto ilman katkoa vaatii siirtymäajan, jona kumpikin
avain kelpaa:

```{.java tiedosto="esimerkit/salaisuudet/src/main/java/fi/tutoriaalit/palveluturva/salaisuudet/KierrettavaAvain.java" osa="kierra"}
```

```{.java tiedosto="esimerkit/salaisuudet/src/test/java/fi/tutoriaalit/palveluturva/salaisuudet/SalaisuudetTest.java" osa="kaksoisavain"}
```

Järjestys on sama kuin varmentajan kierrossa (luku 5): ensin
vastaanottaja hyväksyy molemmat, sitten lähettäjä vaihtaa uuteen ja
lopuksi vanha poistetaan. Vertailu tehdään vakioaikaisesti
(`MessageDigest.isEqual`), jottei vastausaika paljasta avainta.

## Käytännössä

- **Dynaamiset tunnukset tietokantoihin.** Vault, pilvien
  IAM-todennus tietokantoihin (RDS IAM, Cloud SQL IAM) ja
  Kubernetes-operaattorit tarjoavat ne valmiina.
- **Vuokra lyhyeksi, uusiminen automaattiseksi.** Tunnin vuokra, jota
  uusitaan puolivälissä, on tyypillinen.
- **Yhteysallas ja vuokrat yhteen.** Yhteysaltaan yhteydet pitää
  avata uudelleen uusilla tunnuksilla ennen kuin vanhat vanhenevat;
  muuten allas täyttyy hylätyistä yhteyksistä.
- **Kierrä jaetut avaimet aikataululla**, ei vain vuodon jälkeen.
  Kierto, joka on harjoiteltu, onnistuu myös hätätilanteessa.

## Itsearviointi

- Osaat kuvata dynaamisten tunnusten hyödyt ja niiden hinnan.
- Osaat kumota yhden palvelun kaikki tunnukset vaikuttamatta muihin.
- Osaat kiertää kahden osapuolen jakaman avaimen ilman katkoa.
- Osaat sovittaa vuokrat ja yhteysaltaan yhteen.
