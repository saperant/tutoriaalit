# Tietoturvapoikkeamien käsittely

Taidossa *Tietoturvan perusteet* kuvattiin poikkeaman vaiheet:
valmistautuminen, havaitseminen, rajaaminen, poistaminen,
palautuminen ja jälkianalyysi. Tässä luvussa katsotaan, mitä ne
tarkoittavat palvelukokonaisuudessa, jossa yksi palvelu on murrettu.

## Havaitseminen

Ihmisten käyttäytyminen vaihtelee, palvelujen ei. Laskutus kutsuu
samoja rajapintoja samassa järjestyksessä päivästä toiseen. Siksi
yksinkertainen sääntö on palveluille tehokas: hälytä, kun palvelu
tekee jotain, mitä se ei ole tehnyt perustasojaksolla.

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Poikkeama.java" osa="havaitse"}
```

Muita hyviä signaaleja ovat estettyjen valtuutusten äkillinen kasvu,
hylätyt TLS-kättelyt sisäverkossa (joku kokeilee), salaisuuksien
lukeminen poikkeavasta palvelusta ja lähtevä liikenne uuteen
kohteeseen.

## Aikajana

Kun hälytys tulee, kootaan aikajana: mitä murrettu identiteetti teki
ja missä järjestyksessä. Korrelaatiotunniste yhdistää palvelujen
lokit:

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Poikkeama.java" osa="aikajana"}
```

```{.java tiedosto="esimerkit/havainnointi/src/test/java/fi/tutoriaalit/palveluturva/havainnointi/HavainnointiTest.java" osa="poikkeamaTesti"}
```

Suosituspalvelu luki ensin tilauksen kuten tavallisesti, sitten
tietokannan salaisuuden ja yritti viedä asiakasrekisterin. Kaksi
jälkimmäistä ovat poikkeavia.

## Rajaaminen

Rajaamisen tavoite on pysäyttää hyökkääjä nopeasti, vaikka syy ei
olisi vielä selvä. Palvelukokonaisuudessa keinoja on useita, ja ne
tehdään järjestyksessä nopeimmasta pysyvimpään:

1. **Valtuutus pois:** murrettu identiteetti kumoamislistalle, jota
   jokainen palvelu tarkistaa, tai nimenomainen esto käytäntöön
   (luku 9). Vaikuttaa sekunneissa.
2. **Salaisuudet pois:** palvelun dynaamiset tunnukset kumotaan
   (luku 8), ja sen lukemat staattiset salaisuudet kierretään.
3. **Identiteetti pois:** uusia varmenteita ei myönnetä (luku 5),
   jolloin vanhat vanhenevat.
4. **Verkko kiinni:** verkkokäytäntö eristää palvelun (luku 10).
5. **Työkuorma talteen ja uudelleen:** kontin levy ja muisti
   tallennetaan tutkintaa varten, ja palvelu käynnistetään
   puhtaasta kuvasta.

```{.java tiedosto="esimerkit/havainnointi/src/main/java/fi/tutoriaalit/palveluturva/havainnointi/Poikkeama.java" osa="eristys"}
```

```{.java tiedosto="esimerkit/havainnointi/src/test/java/fi/tutoriaalit/palveluturva/havainnointi/HavainnointiTest.java" osa="eristysTesti"}
```

Työkuorman identiteettien, lyhytikäisten varmenteiden ja dynaamisten
tunnusten ansiosta rajaaminen on kohdennettua: suosituspalvelu
eristetään ilman, että muita palveluja tarvitsee pysäyttää tai
yhteisiä salasanoja vaihtaa.

## Jälkianalyysi

Jälkianalyysi (*post-mortem*) kirjoitetaan syyllistämättä. Se
vastaa kysymyksiin:

- **Miten hyökkääjä pääsi sisään?** Esimerkissä haavoittuva
  riippuvuus suosituspalvelussa.
- **Miksi se pääsi niin pitkälle?** Mikä kontrolli puuttui tai ei
  toiminut: oliko suosituspalvelulla oikeus salaisuuksiin, jota se ei
  tarvinnut?
- **Miksi havaitseminen kesti niin kauan kuin kesti?**
- **Mitkä muutokset estävät saman ketjun?** Kirjataan tehtävinä
  omistajineen ja seurataan.

Aikajana, auditointilokit ja käytäntöjen historia versionhallinnassa
ovat jälkianalyysin aineisto. Jos jokin niistä puuttui, sen
puuttuminen on itsessään löydös.

## Käytännössä

- **Harjoittele.** Rajaamisen keinot, joita ei ole koskaan käytetty,
  eivät toimi hätätilanteessa. Pöytäharjoitus "suosituspalvelu on
  murrettu" paljastaa puuttuvat oikeudet, ohjeet ja yhteystiedot.
- **Kumoamisen pitää olla nopeaa ja kohdennettua.** Jos ainoa keino
  on vaihtaa kaikkien palvelujen yhteinen salasana, poikkeama
  muuttuu katkoksi.
- **Säilytä todisteet ennen siivousta.** Kontin uudelleenkäynnistys
  hävittää muistin ja levyn.
- **Ilmoitusvelvollisuudet.** GDPR:n ja NIS2:n määräajat (72 h ja 24
  h ennakkovaroitus) alkavat havaitsemisesta. Yhteystiedot ja
  päätösvalta sovitaan etukäteen.

## Itsearviointi

- Osaat suunnitella palveluille havaitsemissäännön, joka perustuu
  poikkeamaan tavallisesta käytöksestä.
- Osaat koota poikkeaman aikajanan korrelaatiotunnisteen avulla.
- Osaat luetella murretun palvelun rajaamisen keinot nopeimmasta
  pysyvimpään.
- Osaat kirjoittaa syyllistämättömän jälkianalyysin rungon.
