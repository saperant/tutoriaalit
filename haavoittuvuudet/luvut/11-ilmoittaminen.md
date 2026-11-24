# Vastuullinen ilmoittaminen

Haavoittuvuus voi löytyä omasta koodista, käytetystä kirjastosta tai
toisen valmistajan tuotteesta. Kaikissa tapauksissa tavoite on sama:
korjaus käyttäjille ennen kuin tieto virheestä on laajasti saatavilla.
*Koordinoitu haavoittuvuuksien julkistaminen* (*coordinated
vulnerability disclosure*, CVD) on vakiintunut tapa päästä siihen:
löytäjä ilmoittaa valmistajalle, valmistaja korjaa, ja tieto
julkistetaan yhdessä sovittuna ajankohtana.

## Vakavuuden kuvaaminen: CVSS ja CWE

*CWE* (*Common Weakness Enumeration*) luokittelee virheen tyypin:
esimerkiksi CWE-787 (kirjoitus puskurin ulkopuolelle), CWE-125 (luku
puskurin ulkopuolelta), CWE-416 (käyttö vapautuksen jälkeen), CWE-190
(kokonaisluvun ylivuoto) ja CWE-134 (hallitsematon
muotoilumerkkijono). Luokka kertoo kehittäjille, mitä korjataan ja mistä
variaatioita etsitään.

*CVSS* (*Common Vulnerability Scoring System*) kuvaa vakavuuden
vektorina ja pisteinä 0–10. Peruspisteet riippuvat siitä, miten
virheeseen päästään (hyökkäysreitti, monimutkaisuus, tarvittavat
oikeudet, käyttäjän toiminta), ulottuuko vaikutus toiseen
turvallisuusrajaan (*scope*) ja mitä luottamuksellisuudelle,
eheydelle ja saatavuudelle tapahtuu. Laskukaava on julkinen; paketin
`cvss.py` toteuttaa CVSS 3.1:n peruspisteet:

```{.python tiedosto="esimerkit/10-ilmoittaminen/cvss.py" osa="painot"}
```

```{.python tiedosto="esimerkit/10-ilmoittaminen/cvss.py" osa="pisteet"}
```

```{.text tiedosto="esimerkit/10-ilmoittaminen/vektorit.txt"}
```

```{.tuloste tiedosto="esimerkit/10-ilmoittaminen/odotettu" osa="t1"}
```

Vektorit kuvaavat tämän paketin virheitä. TLV-palvelun kaatuminen on
pelkkä saatavuuden menetys, mutta jos sama virhe voisi muuttaa
ohjausvuota, kaikki kolme vaikutusta ovat korkeita ja pisteet nousevat,
vaikka hyödyntäminen arvioitaisiin vaikeaksi (`AC:H`). Paikallinen
kuvatiedosto vaatii käyttäjän toiminnan (`UI:R`). Hiekkalaatikosta
murtautuminen muuttaa vaikutusalueen (`S:C`), mikä nostaa pisteitä.

CVSS kuvaa vakavuutta, ei riskiä. Riski riippuu siitä, onko ohjelma
käytössä, onko virhe tunnetusti hyödynnetty (esim. CISA:n *Known
Exploited Vulnerabilities* -luettelo) ja todennäköisyydestä (EPSS).
CVSS 4.0 julkaistiin vuonna 2023, ja se erottelee nämä tekijät
selvemmin; monet tietokannat käyttävät vielä 3.1:tä.

## CVE-tunnisteet

*CVE* (*Common Vulnerabilities and Exposures*) antaa haavoittuvuudelle
yksilöllisen tunnisteen, kuten CVE-2014-0160. Tunnisteen myöntää
*CNA* (*CVE Numbering Authority*): suuret valmistajat ja avoimen
lähdekoodin säätiöt ovat itse CNA:ita, ja muuten tunnisteen voi pyytää
CVE-ohjelmalta tai kansalliselta CERTiltä. Tunniste varataan usein
ennen julkistusta, jotta kaikki osapuolet puhuvat samasta virheestä.

## Ilmoittaminen valmistajalle

Hyvä ilmoitus on lyhyt ja toistettava:

1. **Mikä ohjelma ja versio**, ja miten se oli konfiguroitu.
2. **Mikä virhe**: luokka (CWE), kohta koodissa ja juurisyy, jos se on
   tiedossa.
3. **Miten toistetaan**: minimoitu syöte tai testitapaus ja
   sanitoijan raportti. Ei toimivaa hyökkäyskoodia.
4. **Arvio vaikutuksesta**: primitiivi ja CVSS-vektori perusteluineen.
5. **Ehdotus korjaukseksi**, jos sellainen on.
6. **Aikataulu**: milloin aiot julkistaa tai kertoa tiedosta muille.

Yhteystieto löytyy valmistajan `security.txt`-tiedostosta (RFC 9116),
tietoturvasivulta tai bug bounty -ohjelmasta. Jos valmistaja ei
vastaa, kansallinen CERT voi koordinoida: Suomessa Traficomin
Kyberturvallisuuskeskus ottaa vastaan haavoittuvuusilmoituksia ja
välittää niitä valmistajille. Kansainvälisesti vastaavaa työtä tekee
esimerkiksi CERT/CC.

Aikataulu sovitaan valmistajan kanssa. Yleinen lähtökohta on 90 päivää
ilmoituksesta julkistukseen (esim. Google Project Zero), ja sitä
lyhennetään, jos virhettä jo hyödynnetään, tai pidennetään, jos korjaus
on monimutkainen ja valmistaja toimii aktiivisesti.

## Oma vastaanottoprosessi

Valmistajan on helpointa ottaa ilmoituksia vastaan, kun ohjeet ovat
valmiina. `security.txt` kertoo, minne ilmoitus lähetetään ja millä
ehdoilla:

```{.text tiedosto="esimerkit/10-ilmoittaminen/security.txt"}
```

Tiedosto julkaistaan polussa `/.well-known/security.txt`. Pakollisia
kenttiä ovat `Contact` (URI) ja `Expires`, joka on annettava kerran;
standardi suosittelee alle vuoden voimassaoloa, jotta vanhentuneet
yhteystiedot eivät jää voimaan. Paketin tarkistin testaa nämä:

```{.python tiedosto="esimerkit/10-ilmoittaminen/tarkista_security.py" osa="tarkista"}
```

```{.bash tiedosto="esimerkit/10-ilmoittaminen/aja.sh" osa="security"}
```

```{.tuloste tiedosto="esimerkit/10-ilmoittaminen/odotettu" osa="t2"}
```

Tiedoston lisäksi tarvitaan prosessi: kuka lukee ilmoitukset, kuinka
nopeasti vastataan, miten korjaus tehdään ja julkaistaan ja miten
löytäjä mainitaan. Standardit ISO/IEC 29147 (haavoittuvuuksien
julkistaminen) ja ISO/IEC 30111 (haavoittuvuuksien käsittely) kuvaavat
prosessin osat. Julkaistu *julkistuskäytäntö* (*disclosure policy*)
kertoo tutkijoille, mitä testaaminen saa sisältää ja että hyvässä
uskossa toimivaa tutkijaa ei ryhdytä oikeustoimiin.

## Bug bounty -ohjelmat

*Bug bounty* -ohjelmassa valmistaja maksaa palkkion löydöksistä. Ohjelman
säännöt määrittelevät:

- **kohteet**: mitkä järjestelmät, sovellukset ja versiot kuuluvat
  ohjelmaan; kaikki muu on rajattu pois
- **sallitut menetelmät**: esim. ei palvelunestoa, ei toisten
  käyttäjien datan lukemista, ei sosiaalista manipulointia
- **ilmoittamisen ja julkistamisen ehdot** ja palkkioiden perusteet.

Säännöt ovat lupa: niiden ulkopuolella testaaminen on luvatonta, vaikka
kohde kuuluisi samalle yritykselle. Palvelut kuten HackerOne, Bugcrowd
ja Intigriti välittävät ohjelmia, ja monet avoimen lähdekoodin projektit
ovat mukana esimerkiksi Internet Bug Bounty -ohjelmassa.

## Valmistajan velvollisuudet

EU:n kyberkestävyyssäädös (*Cyber Resilience Act*, CRA) velvoittaa
digitaalisia tuotteita markkinoille saattavat valmistajat käsittelemään
haavoittuvuuksia koko tuen ajan, julkaisemaan korjaukset ja
ilmoittamaan aktiivisesti hyödynnetyistä haavoittuvuuksista
viranomaisille tiukoissa määräajoissa. *Tietoturvan perusteet* käsittelee
säädöksen tarkemmin. Käytännössä sama prosessi, jota tämä luku kuvaa,
on CRA:n vaatimusten ydin.

## Käytännössä

- **Ilmoita valmistajalle ennen julkistusta**, ja liitä mukaan
  minimoitu toistotapaus, sanitoijan raportti ja perusteltu arvio.
- **Kuvaa vakavuus CVSS-vektorina ja virhe CWE-luokkana**; perustele
  arvio, äläkä liioittele tai vähättele.
- **Julkaise oma `security.txt` ja julkistuskäytäntö**, ja pidä
  `Expires` ajan tasalla.
- **Noudata bug bounty -ohjelman sääntöjä kirjaimellisesti**: ne ovat
  lupasi rajat.

## Itsearviointi

- Osaat laskea CVSS 3.1 -peruspisteet vektorista ja perustella
  vektorin osat omalle löydökselle.
- Osaat nimetä tavallisimmat muistiturvallisuusvirheiden CWE-luokat.
- Osaat kirjoittaa haavoittuvuusilmoituksen valmistajalle ja kertoa,
  mihin otetaan yhteyttä, jos valmistaja ei vastaa.
- Osaat laatia `security.txt`-tiedoston ja kuvata valmistajan
  haavoittuvuuksien käsittelyprosessin osat.
