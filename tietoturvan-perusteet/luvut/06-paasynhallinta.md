# Pääsynhallinta

Pääsynhallinta päättää, saako todennettu toimija tehdä pyytämänsä
toimenpiteen kohteelle. Sen osat ovat **subjekti** (käyttäjä, palvelu
tai prosessi), **objekti** (tiedosto, tietue, toiminto) ja
**toimenpide** (luku, kirjoitus, poisto). Pääsynhallinnan puutteet
ovat OWASPin listalla web-sovellusten yleisin vakava haavoittuvuusluokka
(*broken access control*).

## Mallit

| Malli | Kuka päättää | Missä käytetään |
|-------|--------------|-----------------|
| DAC, harkinnanvarainen | objektin omistaja | Unixin tiedosto-oikeudet, jaetut asiakirjat |
| MAC, pakollinen | järjestelmän politiikka, ei omistaja | turvaluokitellut järjestelmät, SELinux |
| RBAC, roolipohjainen | ylläpitäjä antaa rooleja, roolit oikeuksia | useimmat liiketoimintasovellukset |
| ABAC, attribuuttipohjainen | sääntö subjektin, objektin ja ympäristön ominaisuuksista | hienojakoiset politiikat, pilvi-IAM |

Mallit eivät sulje toisiaan pois. Tyypillinen sovellus käyttää RBAC:ia
karkeaan jakoon ja lisää omistajuuden tarkistuksen (luvun lopun IDOR).

## Unixin tiedosto-oikeudet (DAC)

Unixissa tiedoston omistaja päättää oikeuksista kolmelle joukolle:
omistaja, ryhmä ja muut. Tavallisimmat virheet ovat salaisuudet, jotka
ovat muiden luettavissa, ja tiedostot, joihin kuka tahansa voi
kirjoittaa:

```{.python tiedosto="esimerkit/06-oikeudet.py" osa="tarkastus"}
```

```{.python tiedosto="esimerkit/06-oikeudet.py" osa="korjaus"}
```

```{.tuloste tiedosto="esimerkit/06-oikeudet.odotettu"}
```

Oikeudet kannattaa asettaa luontihetkellä (`os.open(..., 0o600)`,
`umask`) eikä jälkikäteen, koska tiedosto on muuten hetken ajan väärillä
oikeuksilla (luku *Kilpailutilanteet ja asetukset*). Palvelu ajetaan
omalla käyttäjällään, jolla ei ole pääkäyttäjän oikeuksia.

## RBAC: roolit

Roolipohjaisessa mallissa oikeudet annetaan rooleille ja roolit
käyttäjille. Kun työntekijä vaihtaa tehtävää, vaihdetaan rooli eikä
käydä läpi kymmeniä yksittäisiä oikeuksia:

```{.python tiedosto="esimerkit/06-rbac.py" osa="rbac"}
```

```{.tuloste tiedosto="esimerkit/06-rbac.odotettu"}
```

Oikeudet nimetään toimenpiteinä (`lasku:hyvita`), ei rooleina. Koodi
kysyy "saako hyvittää laskun", ei "onko talousosastolla". Silloin
roolien muuttaminen ei vaadi koodimuutoksia, ja oikeuksien
tarkastuslistan voi tuottaa suoraan datasta.

RBAC:n tyypillinen ongelma on **roolien paisuminen**: jokainen
poikkeus synnyttää uuden roolin, ja lopulta kaikilla on kaikki. Roolit
ja niiden jäsenet käydään läpi säännöllisesti, ja tehtävien erottelu
(*separation of duties*) estää esimerkiksi saman henkilön sekä
luomasta että hyväksymästä maksua.

## ABAC: säännöt ominaisuuksista

Kun pääsy riippuu tilanteesta, roolit eivät riitä. Attribuuttipohjainen
sääntö käyttää subjektin (osasto, selvitystaso), objektin (luokitus,
omistaja) ja ympäristön (verkko, kellonaika) ominaisuuksia:

```{.python tiedosto="esimerkit/06-abac.py" osa="abac"}
```

```{.tuloste tiedosto="esimerkit/06-abac.odotettu"}
```

Säännön palauttama syy on tärkeä sekä käyttäjälle että lokeille.
ABAC-säännöt ovat ilmaisuvoimaisia mutta vaikeita todeta oikeiksi,
joten ne testataan kattavasti ja pidetään yhdessä paikassa eikä
hajallaan koodissa. Laajemmissa järjestelmissä säännöt kirjoitetaan
erilliselle politiikkamoottorille (esimerkiksi Open Policy Agent).

## Objektitason tarkistus (IDOR)

Yleisin pääsynhallinnan virhe on tarkistaa vain, että käyttäjä on
kirjautunut, mutta ei sitä, että pyydetty objekti kuuluu hänelle.
Hyökkääjä vaihtaa osoitteessa olevan tunnisteen ja saa toisen
käyttäjän tiedot (*insecure direct object reference*, IDOR):

```{.python tiedosto="esimerkit/06-idor.py" osa="haavoittuva"}
```

```{.python tiedosto="esimerkit/06-idor.py" osa="korjattu"}
```

```{.tuloste tiedosto="esimerkit/06-idor.odotettu"}
```

Korjattu versio vastaa samoin sekä olemattomaan että toisen
käyttäjän laskuun. Jos se vastaisi "403 kielletty" olemassa olevaan ja
"404" olemattomaan, hyökkääjä voisi luetella olemassa olevat numerot.
Satunnaiset, arvaamattomat tunnisteet (UUID) vaikeuttavat luettelemista,
mutta eivät korvaa tarkistusta: tunniste voi vuotaa lokeista,
viittaustiedoista tai jaetusta linkistä.

## Käytännössä

- **Tarkista palvelimella, joka kerta.** Piilotettu painike tai
  käyttöliittymän tarkistus ei ole pääsynhallintaa. Täydellinen
  välitys: jokainen pyyntö tarkistetaan, myös rajapinnat, joita
  "kukaan ei käytä".
- **Kiellä oletuksena.** Uusi toiminto on suljettu, kunnes sille on
  määritelty oikeus. Kehysten oletus "kaikki kirjautuneet" on vaarallinen.
- **Tarkista omistajuus.** Jokaisessa tunnisteella haetussa objektissa
  kysytään, saako *tämä* käyttäjä *tämän* objektin. Yksinkertaisin tapa
  on rajata haku kyselyssä: `WHERE id = ? AND asiakas = ?`.
- **Vähimmät oikeudet myös palveluille.** Tietokantatunnus ilman
  `DROP`-oikeutta, pilvitunnus vain tarvittuihin resursseihin,
  kontti ilman pääkäyttäjää.
- **Keskitä päätökset.** Yksi pääsynhallintamoduuli, jota kaikki
  kutsuvat ja jota testataan taulukoilla (käyttäjä × toimenpide ×
  odotettu tulos).
- **Kirjaa kiellot.** Toistuvat kiellot samalta käyttäjältä ovat usein
  ensimmäinen merkki tunnustelusta.

## Itsearviointi

- Osaat valita tilanteeseen sopivan pääsynhallintamallin (DAC, MAC,
  RBAC, ABAC) ja perustella valinnan.
- Osaat toteuttaa roolipohjaisen pääsynhallinnan, jossa oikeudet ovat
  toimenpiteitä ja oletus on kielto.
- Osaat löytää ja korjata objektitason tarkistuksen puutteen (IDOR).
- Osaat tarkastaa tiedostojen oikeudet ja korjata liian sallivat
  asetukset.
