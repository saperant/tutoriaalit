# Pääsynhallinta pilvessä

Pilvessä lähes kaikki on rajapinnan takana: tallennustilit,
tietokannat, jonot, avainpalvelut ja itse infrastruktuuri. Jokainen
kutsu arvioidaan IAM-käytäntöjä vasten. Käytännöt ovat siksi
pilviympäristön tärkein suojaus, ja liian laaja käytäntö yleisin
pilvimurron syy.

## Käytännön rakenne

Esimerkin käytäntömuoto noudattaa pilvien IAM:ää. Lauseke kertoo
vaikutuksen, toiminnot, resurssit ja ehdot:

```{.java tiedosto="esimerkit/kaytannot/src/main/java/fi/tutoriaalit/palveluturva/kaytannot/Kaytanto.java" osa="lauseke"}
```

Päätöspiste saa pyynnön ja palauttaa päätöksen perusteineen:

```{.java tiedosto="esimerkit/kaytannot/src/main/java/fi/tutoriaalit/palveluturva/kaytannot/Moottori.java" osa="pyynto"}
```

## Arviointisäännöt

Säännöt ovat samat kuin AWS:n IAM:ssä ja pääpiirteissään muissakin
pilvissä:

```{.java tiedosto="esimerkit/kaytannot/src/main/java/fi/tutoriaalit/palveluturva/kaytannot/Moottori.java" osa="arvioi"}
```

1. **Oletuksena estetty.** Pyyntö, jota mikään ei salli, estetään.
2. **Nimenomainen esto voittaa.** Organisaatiotason esto (AWS:n SCP,
   Azuren Deny-määritys) ohittaa kaikki sallivat lausekkeet. Se on
   suojakaide, jota tilin ylläpitäjäkään ei voi kiertää.
3. **Ehdot rajaavat.** Lauseke osuu vain, jos kaikki sen ehdot
   täyttyvät.

## Liian laaja käytäntö

Kiireessä kirjoitettu käytäntö näyttää usein tältä:

```{.json tiedosto="esimerkit/kaytannot/src/test/resources/kaytannot/laskutus-laaja.json"}
```

Laskutus toimii, mutta sen murtanut hyökkääjä voi tehdä mitä
tahansa:

```{.java tiedosto="esimerkit/kaytannot/src/test/java/fi/tutoriaalit/palveluturva/kaytannot/KaytannotTest.java" osa="laaja"}
```

## Vähimmät oikeudet

Rajattu käytäntö luettelee toiminnot ja resurssit ja rajaa
kirjoituksen ehdolla:

```{.json tiedosto="esimerkit/kaytannot/src/test/resources/kaytannot/laskutus.json"}
```

Organisaation suojakaide estää poistot tuotannossa kaikilta:

```{.json tiedosto="esimerkit/kaytannot/src/test/resources/kaytannot/organisaatio.json"}
```

```{.java tiedosto="esimerkit/kaytannot/src/test/java/fi/tutoriaalit/palveluturva/kaytannot/KaytannotTest.java" osa="rajattu"}
```

Samat kolme pyyntöä kolmella käytäntöyhdistelmällä. Jokaisen
päätöksen perään moottori kirjaa perusteen: mikä lauseke salli, mikä
esti vai jäikö pyyntö oletuseston varaan. Viimeisessä ryhmässä
organisaation suojakaide pysäyttää poiston, vaikka palvelun oma
käytäntö sallisi kaiken:

```{.tuloste tiedosto="esimerkit/naytos/09-paatokset.odotettu"}
```

## Oikeudet käytön perusteella

Vähimpiä oikeuksia on vaikea kirjoittaa etukäteen. Käytännöllisempää
on lähteä liikkeelle kohtuullisesta käytännöstä ja kaventaa sitä
sen perusteella, mitä palvelu oikeasti tekee. Pilvien
pääsyanalyysityökalut (AWS IAM Access Analyzer, GCP:n IAM
Recommender) toimivat näin auditointilokin perusteella:

```{.java tiedosto="esimerkit/kaytannot/src/main/java/fi/tutoriaalit/palveluturva/kaytannot/Analyysi.java" osa="analyysi"}
```

```{.java tiedosto="esimerkit/kaytannot/src/test/java/fi/tutoriaalit/palveluturva/kaytannot/KaytannotTest.java" osa="analyysiTesti"}
```

Analyysi löysi lausekkeen `LueAsiakkaat`, jota ei ole käytetty. Se
poistetaan, ja jos sitä tarvitaankin, puuttuva oikeus näkyy heti
selvänä virheenä eikä hiljaisena riskinä.

## Politiikat koodina

Käytännöt ovat koodia: ne tallennetaan versionhallintaan,
katselmoidaan ja testataan CI:ssä ennen käyttöönottoa. Staattinen
tarkastus hylkää tyypilliset virheet:

```{.java tiedosto="esimerkit/kaytannot/src/main/java/fi/tutoriaalit/palveluturva/kaytannot/Tarkastus.java" osa="tarkastus"}
```

```{.java tiedosto="esimerkit/kaytannot/src/test/java/fi/tutoriaalit/palveluturva/kaytannot/KaytannotTest.java" osa="tarkastusTesti"}
```

Laajemmissa ympäristöissä käytetään yleiskäyttöistä käytäntömoottoria.
Open Policy Agent (OPA) ja sen kieli Rego, AWS Cedar sekä Kubernetesin
pääsynvalvojat (Kyverno, Gatekeeper) erottavat päätöksen sovelluksesta:
sovellus kysyy "saako tämä kutsuja tehdä tämän tälle resurssille" ja
käytäntö vastaa. Käytännöille kirjoitetaan yksikkötestejä kuten
koodille, ja tarkastus kuuluu samaan CI-putkeen kuin
infrastruktuurikoodi.

## Monta asiakasta samassa palvelussa

Kun sama palvelu ja tietokanta palvelevat useaa asiakasorganisaatiota
(*multi-tenancy*), vuokralaisen tunniste on osa jokaista
valtuutuspäätöstä. Luvun 2 käytäntö teki tämän yhdelle käyttäjälle
muuttujalla `${asiakas}`; sama rakenne rajaa kokonaisen organisaation
resurssit (`krn:kauppa:tiedostot/${vuokralainen}/*`). Kolme sääntöä:

- **Tunniste tulee todennetusta identiteetistä**, tokenin väitteestä,
  ei pyynnön osoitteesta tai rungosta.
- **Rajaus tehdään mahdollisimman alhaalla:** tietokannassa
  rivitason käytännöllä tai vuokralaiskohtaisella skeemalla ja
  avaimella (luku 7), jolloin sovelluskoodin unohtunut ehto ei vuoda
  toisen dataa.
- **Eristys testataan** samoin kuin muu valtuutus: testi kirjautuu
  vuokralaisena A ja yrittää lukea vuokralaisen B resurssin.

## Käytännössä

- **Ei jokerimerkkiä toimintoihin eikä resursseihin.** `*:*` on
  ylläpitäjän oikeus, ei palvelun.
- **Organisaatiotason estot suojakaiteiksi.** Lokien poisto,
  auditoinnin pysäytys, avainten poisto ja julkinen jako estetään
  kaikilta paitsi erilliseltä hätätililtä.
- **Ehdot oikeuksiin.** Lähdeidentiteetti, verkko, MFA ja tagit
  rajaavat, missä tilanteessa oikeutta saa käyttää.
- **Kavenna käytön perusteella** ja toista säännöllisesti. Oikeudet
  kertyvät ajan mittaan, ellei niitä karsita.
- **Ihmisille väliaikaiset oikeudet.** Pysyvien ylläpito-oikeuksien
  sijaan oikeus pyydetään tehtävää varten ja se vanhenee (*just in
  time access*).

## Itsearviointi

- Osaat kirjoittaa IAM-tyyppisen käytännön ja kertoa arviointisäännöt
  (oletusesto, nimenomainen esto, ehdot).
- Osaat tunnistaa liian laajan käytännön ja kaventaa sen vähimpiin
  oikeuksiin.
- Osaat kertoa, mistä vuokralaisen tunniste saadaan ja missä kerroksessa
  usean asiakkaan palvelun rajaus tehdään.
- Osaat käyttää auditointilokia käyttämättömien oikeuksien
  löytämiseen.
- Osaat tarkastaa käytännöt automaattisesti CI:ssä.
