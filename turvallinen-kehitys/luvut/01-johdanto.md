# Johdanto {.runko-johdanto}

Useimmat tietoturvaongelmat eivät synny siksi, että kehittäjä ei
tietäisi SQL-injektiosta. Ne syntyvät, koska salasana jäi
asetustiedostoon, riippuvuuden uusi versio sisälsi takaoven, CI-ajo
sai tuotannon avaimet tai kiireessä yhdistetty muutos ohitti
katselmoinnin. Tämä tutoriaali käsittelee tietoturvaa **kehitystyön
käytäntönä**: miten tiimi järjestää työnsä niin, että turvallinen
tapa on helpoin tapa ja virheet jäävät kiinni koneellisesti ennen
tuotantoa.

Aihepiiri tunnetaan myös nimellä *DevSecOps*. Nimi korostaa, että
tietoturva ei ole erillinen vaihe kehityksen lopussa, vaan osa samaa
putkea kuin testaus ja julkaisu.

## Mitä tutoriaali kattaa

| Luku | Aihe | Kysymys, johon luku vastaa |
|------|------|----------------------------|
| 2 | Kehitysprosessi | Miten tietoturva kuuluu jokaiseen muutokseen? |
| 3 | Salaisuudet | Missä avaimet ovat ja mitä tehdään, kun ne vuotavat? |
| 4 | Kehitysympäristöt | Mitä kehittäjän koneella ja kontissa saa olla? |
| 5 | Riippuvuudet | Mistä tiedän, että asennettu paketti on oikea? |
| 6 | SBOM ja haavoittuvuudet | Mitä ohjelmistossa on ja onko se haavoittuva? |
| 7 | Allekirjoitukset | Kuka teki muutoksen ja vastaako julkaisu koodia? |
| 8 | Analyysi CI:ssä | Mitä koneet tarkistavat ja miten löydöksiä hallitaan? |
| 9 | CI:n turvallisuus | Miten itse putki pysyy turvallisena? |
| 10 | Katselmointi ja julkaisu | Kuka saa yhdistää ja julkaista mitä? |

Rajaus muihin taitoihin:

- **Tietoturvan perusteet** (esitieto) opettaa käsitteet,
  uhkamallinnuksen ja haavoittuvuusluokat. Tässä niitä *sovelletaan
  prosessiin*, eikä niitä selitetä uudelleen.
- **Versionhallinta** (esitieto): commitit, haarat ja koukut oletetaan
  tutuiksi.
- **Web-sovellusten tietoturva** ja **Palveluarkkitehtuurin
  tietoturva** jatkavat sovelluksen ja tuotantoympäristön suojaamiseen.
  Salaisuuksien hallinta tuotannossa (Vault, KMS, työkuormien
  identiteetit) syvenee jälkimmäisessä.

## Miten esimerkit on rakennettu

Esimerkit ovat Pythonia ja Bashia, ja ne toteuttavat pienessä
mittakaavassa samat tarkistukset, joita oikeat työkalut tekevät:
salaisuusskanneri, commit-koukku, lukitustiedoston tarkistus,
SBOM-generaattori, työnkulkujen tarkistin. Oma pieni toteutus näyttää,
miten työkalu toimii ja missä sen rajat kulkevat. Tuotannossa käytetään
valmiita työkaluja, ja jokainen luku nimeää ne.

Kaikki esimerkit toimivat ilman verkkoyhteyttä ja tuottavat aina saman
tulosteen. Git-esimerkit luovat tilapäisen repositorion ja ohittavat
käyttäjän omat git-asetukset (`GIT_CONFIG_GLOBAL=/dev/null`), jotta
esimerkiksi oma allekirjoitusasetus ei muuta tulosta. Python-esimerkit
tarkistetaan ruffilla tietoturvasääntöineen (`S`, flake8-bandit) ja
mypyllä tiukassa tilassa, Bash-esimerkit ShellCheckillä: samat
tarkistukset, joita luku *Analyysi CI:ssä* suosittelee.

```text
make testaa      # rakenne, tarkistukset ja kaikkien esimerkkien ajo
make pdf         # tämä dokumentti ja pikaopas
```

Kehityskontti (`.devcontainer/turvallinen-kehitys`) sisältää Pythonin,
ruffin, mypyn, ShellCheckin, gitin ja OpenSSH:n.

## Kolme periaatetta

Koko tutoriaalin läpi kulkee kolme periaatetta:

1. **Automatisoi muistettava.** Sääntö, jonka noudattaminen riippuu
   siitä, että joku muistaa, rikkoutuu ennen pitkää. Koukku, CI-tarkistus
   tai haarasuojaus ei unohda.
2. **Oleta, että jokin vuotaa.** Salaisuus päätyy lokiin, riippuvuus
   kaapataan, kehittäjän kone murretaan. Suunnittele niin, että
   vahinko on rajattu ja huomataan: lyhytikäiset tunnukset, vähimmät
   oikeudet, allekirjoitukset.
3. **Tee turvallisesta tavasta helppo.** Jos salaisuusvarastoon
   tallentaminen vaatii lipun ja viikon odotuksen, avain päätyy
   asetustiedostoon. Työkalujen ja käytäntöjen sujuvuus on
   tietoturvaominaisuus.
