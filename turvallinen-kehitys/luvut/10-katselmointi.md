# Katselmointi ja julkaisu

Koneelliset tarkistukset löytävät tunnetut virheluokat. Katselmointi
löytää loput: väärän valtuutuslogiikan, puuttuvan tarkistuksen,
epäilyttävän muutoksen. Lisäksi se on kontrolli, joka estää yhtä
henkilöä, tai yhden henkilön kaapattua tiliä, viemästä muutosta
tuotantoon yksin. Tämä luku käsittelee katselmoinnin ja julkaisun
järjestämistä niin, että kontrollit ovat voimassa koneellisesti.

## Haarasuojaus

Päähaaran suojaus (GitHubissa *branch protection* tai *rulesets*,
GitLabissa *protected branches*) tekee käytännöistä pakollisia:

| Asetus | Mitä se estää |
|--------|---------------|
| muutokset vain pull requestin kautta | suora push päähaaraan ohi katselmoinnin |
| vähintään yksi hyväksyntä, ei tekijältä itseltään | yhden henkilön muutos tuotantoon |
| hyväksyntä vanhenee uusista commiteista | hyväksynnän jälkeen lisätty haitallinen muutos |
| pakolliset tarkistukset (CI) | yhdistäminen ennen kuin testit ja skannaukset ovat läpi |
| koodinomistajien hyväksyntä | kriittisen koodin muutos ilman asiantuntijaa |
| allekirjoitetut commitit | toisen nimissä tehdyt muutokset |
| ei ohitusta ylläpitäjille | "vain tämän kerran" -poikkeukset |

Viimeinen rivi on tärkeä. Jos ylläpitäjä voi ohittaa suojauksen,
ylläpitäjän tilin kaappaus ohittaa sen myös. Hätätilanteita varten
on erillinen, kirjattu menettely, eikä hiljainen ohitus.

## Koodinomistajat ja kahden henkilön sääntö

`CODEOWNERS`-tiedosto määrää, kenen hyväksyntä tarvitaan mihinkin
polkuun. Tietoturvan kannalta tärkeitä polkuja ovat todennus,
maksut, CI-työnkulut ja riippuvuustiedostot: niiden muutos voi
avata takaoven, vaikka muutos näyttäisi pieneltä.

```{.text tiedosto="esimerkit/10-CODEOWNERS"}
```

Viimeinen osuva rivi voittaa, ja kun rivillä on useita omistajia,
hyväksyntä keneltä tahansa heistä riittää. Tarkistus pull requestille:

```{.python tiedosto="esimerkit/10-katselmointi.py" osa="omistajat"}
```

```{.python tiedosto="esimerkit/10-katselmointi.py" osa="saanto"}
```

```{.tuloste tiedosto="esimerkit/10-katselmointi.odotettu"}
```

Neljäs tapaus näyttää, miksi tekijän oma hyväksyntä ei kelpaa: Liisa on
tietoturvatiimin ainoa jäsen, eikä hän voi hyväksyä omaa muutostaan
todennukseen. Tiimissä, jossa jonkin alueen osaaja on yksin, kahden
henkilön sääntö paljastaa riippuvuuden yhdestä ihmisestä. Se on myös
organisaation riski, ei vain tietoturvariski.

`CODEOWNERS`-tiedosto suojataan itsekin: sen omistaja on
alustatiimi, muuten kuka tahansa voisi poistaa itseltään vaatimuksen
muuttamalla tiedostoa.

## Mitä katselmoija katsoo

Katselmoijan aika on rajallinen, joten se kohdistetaan siihen, mitä
koneet eivät näe:

- **Luottamusrajat.** Mistä uusi syöte tulee, missä se tarkistetaan, ja
  päätyykö se tietokantaan, komentoon tai toiselle käyttäjälle.
- **Valtuutus.** Tarkistetaanko jokaisessa rajapinnassa, että
  *tällä käyttäjällä* on oikeus *tähän kohteeseen*?
- **Virhepolut.** Mitä tapahtuu, kun ulkoinen palvelu ei vastaa tai
  syöte on virheellinen: kaatuuko käsittely turvalliseen tilaan?
- **Riippuvuudet ja työnkulut.** Uusi riippuvuus, muuttunut
  CI-työnkulku tai lisätty oikeus ansaitsee erillisen katseen.
- **Mikä puuttuu.** Testit hyökkäystapauksille, lokimerkintä
  tietoturvatapahtumasta, dokumentaatio.

Pienet pull requestit katselmoidaan paremmin kuin suuret. Tuhannen
rivin muutoksessa takaovi on helppo piilottaa, kymmenen rivin muutoksessa
ei.

## Turvallinen julkaisuprosessi

Julkaisu kokoaa edellisten lukujen kontrollit yhteen:

1. **Julkaisu tagista tai suojatusta haarasta**, CI:ssä, ei kehittäjän
   koneelta. Kenelläkään ei ole julkaisuavainta omalla koneellaan.
2. **Build isännöidyssä ympäristössä** ja alkuperätieto (SLSA,
   luku 7). Lukitustiedoston mukaiset riippuvuudet.
3. **SBOM ja allekirjoitus** julkaisun mukana.
4. **Ympäristön hyväksyntä.** Tuotantoon vienti vaatii hyväksynnän
   henkilöltä, joka ei tehnyt muutosta (ympäristön suojaussäännöt).
5. **Vaiheittainen käyttöönotto** ja paluu edelliseen versioon
   valmiina: vahinko rajataan ja korjataan nopeasti.

Pakettirekistereihin julkaistaessa käytetään luotettua julkaisua
(*trusted publishing*): PyPI, npm ja crates.io hyväksyvät julkaisun
CI:n OIDC-identiteetillä ilman tallennettua API-tunnusta. Vuotava tunnus
ei voi julkaista haitallista versiota, koska tunnusta ei ole.

## Käytännössä

- **Haarasuojaus ilman ohituksia.** Pull request, hyväksyntä joltakulta
  muulta, pakolliset tarkistukset ja allekirjoitukset.
- **Koodinomistajat kriittisille poluille**, myös CI-työnkuluille,
  riippuvuustiedostoille ja `CODEOWNERS`-tiedostolle itselleen.
- **Pienet muutokset.** Katselmoitavuus on tietoturvaominaisuus.
- **Julkaisu vain CI:stä** ja luotettu julkaisu rekistereihin.
- **Erota tehtävät.** Muutoksen tekijä, hyväksyjä ja tuotantoon viejä
  eivät ole sama henkilö kriittisissä järjestelmissä.

## Itsearviointi

- Osaat määrittää haarasuojauksen, joka tekee katselmoinnista ja
  tarkistuksista pakollisia.
- Osaat kirjoittaa `CODEOWNERS`-tiedoston ja selittää, miten
  omistajuus ja kahden henkilön sääntö toteutuvat.
- Osaat kohdistaa katselmoinnin asioihin, joita koneellinen analyysi
  ei löydä.
- Osaat kuvata turvallisen julkaisuprosessin ja luotetun julkaisun.
