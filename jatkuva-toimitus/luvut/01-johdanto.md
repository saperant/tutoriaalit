# Johdanto {.runko-johdanto}

Ohjelmisto on hyödyllinen vasta, kun se on käyttäjällä. Matka
kehittäjän koneelta tuotantoon on siksi osa ohjelmistotyötä eikä sen
jälkeinen vaihe. Tämä tutoriaali käsittelee sitä matkaa: miten
muutokset yhdistetään toisiinsa, miten niiden toimivuus varmistetaan
automaattisesti, miten sama tarkistettu paketti viedään ympäristöstä
toiseen ja miten uusi versio annetaan käyttäjille niin, että virheen
vaikutus jää pieneksi.

Aiheen ydin on vanha ja yksinkertainen havainto: **kipeä asia kannattaa
tehdä useammin**. Jos muutosten yhdistäminen kerran kuussa on
tuskallista, se tehdään päivittäin, jolloin jokainen yhdistys on pieni.
Jos julkaisu kerran vuodessa on riski, julkaistaan viikoittain tai
päivittäin, jolloin jokainen julkaisu sisältää vähän muutoksia ja vian
syy löytyy nopeasti. Tiheä toistaminen pakottaa automatisoimaan, ja
automatisoitu askel on toistettava, tarkistettava ja halpa.

Tutoriaali on yleisteos. Periaatteet esitetään ensin ja työkalut
esimerkkeinä, koska työkalut vaihtuvat muutamassa vuodessa ja
periaatteet ovat pysyneet samoina 2000-luvun alusta. Jokaisesta
käytännöstä kerrotaan, mihin ongelmaan se vastaa, mitä se edellyttää ja
missä sen rajat ovat.

## Kolme käsitettä

Alan sanasto on vakiintunut, mutta sitä käytetään huolimattomasti.
Kolme käsitettä kannattaa pitää erillään.

| Käsite | Mitä tarkoittaa | Mihin päättyy |
|--------------------|--------------------------------------|----------------|
| jatkuva integraatio (CI) | jokainen kehittäjä yhdistää työnsä yhteiseen runkoon vähintään päivittäin, ja jokainen yhdistys tarkistetaan automaattisesti | tarkistettu runko |
| jatkuva toimitus (CD) | runko pidetään koko ajan julkaisukelpoisena; julkaisu on rutiinia ja liiketoiminnan päätös | julkaisukelpoinen paketti |
| jatkuva käyttöönotto | jokainen putken läpäissyt muutos viedään tuotantoon ilman erillistä päätöstä | tuotanto |

Englanniksi käsitteet ovat *continuous integration*, *continuous
delivery* ja *continuous deployment*. Lyhenne CD tarkoittaa
kirjallisuudessa yleensä jatkuvaa toimitusta, mutta arkipuheessa sillä
viitataan usein mihin tahansa automaattiseen käyttöönottoon.

Käsitteet rakentuvat toistensa päälle. Jatkuva toimitus ei onnistu
ilman jatkuvaa integraatiota, koska runko ei voi olla julkaisukelpoinen,
jos keskeneräinen työ odottaa viikkoja haaroissa. Jatkuva käyttöönotto
taas on jatkuvaa toimitusta, josta viimeinenkin käsin tehtävä päätös on
poistettu. Se ei ole kaikkien tavoite: moni organisaatio pysähtyy
perustellusti jatkuvaan toimitukseen (luku 8).

Huomaa, mitä määritelmissä ei sanota. Jatkuva integraatio ei tarkoita
CI-palvelinta. Palvelin, joka ajaa testit jokaiselle haaralle, on
hyödyllinen, mutta jos haarat elävät viikkoja, integraatio ei ole
jatkuvaa. Käytäntö on ihmisten tapa työskennellä, ja työkalu tukee
sitä.

## Palautesilmukka

Kaikki tutoriaalin käytännöt lyhentävät samaa silmukkaa: muutoksen
tekemisestä siihen hetkeen, kun tiedetään, toimiko se.

```{.dot otsikko="Palautesilmukat ja niiden tyypillinen kesto: mitä kauempana vika havaitaan, sitä kalliimpi se on korjata"}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.3;
  m [label="muutos"]; p [label="paikalliset\ntestit\n(sekunteja)"];
  r [label="yhdistys\nrunkoon"]; c [label="toimitus-\nputki\n(minuutteja)"];
  t [label="tuotanto"]; k [label="käyttäjä\n(tunteja\ntai päiviä)"];
  m -> p -> r -> c -> t -> k;
  p -> m [constraint=false, style=dashed];
  c -> m [constraint=false, style=dashed];
  k -> m [constraint=false, style=dashed];
}
```

Lyhyt silmukka on arvokas kolmesta syystä.

- **Vian syy on lähellä.** Kun testi hajoaa viisi minuuttia muutoksen
  jälkeen, syy on se muutos. Kun vika löytyy kolmen kuukauden
  julkaisusta, ehdokkaita on satoja.
- **Tekijä muistaa asian.** Tunnin vanhan muutoksen korjaa minuuteissa.
  Kuukauden vanhaan on ensin perehdyttävä uudelleen.
- **Väärä suunta huomataan ajoissa.** Käyttäjän palaute pienestä
  julkaisusta ohjaa seuraavaa. Suuri julkaisu on suuri veto.

Sama asia on käsitelty tutoriaalissa *Ohjelmistoprojektin hallinta*
erän koon ja virtauksen käsittein. Tässä tutoriaalissa näkökulma on
tekninen: millä rakenteilla pieni erä tehdään mahdolliseksi ja
turvalliseksi.

## Esimerkit ja mallit

Toimitusputkea, haarautumismallia tai kanarialintujulkaisua on vaikea
näyttää kirjan sivulla oikeassa mittakaavassa. Tutoriaali käyttää siksi
kahdenlaisia esimerkkejä.

**Oikeat työkalut pienessä mittakaavassa.** Yhdistämisristiriidat
tehdään oikealla Gitillä väliaikaisiin repositorioihin, putken vaiheet
ajavat oikeat tarkistimet (ruff, mypy, pytest), artefakti on oikea
tar-paketti ja tietokantamuutokset ajetaan SQLiteen. Kohteena on pieni
sovellus `viite`, joka laskee viitenumeron tarkisteen.

**Mallit.** Haaran iän vaikutus ristiriitoihin, epävakaiden testien
kertautuminen, julkaisustrategioiden erot ja GitOps-täsmäytys
esitetään muutaman kymmenen rivin Python-malleina hakemistossa
`esimerkit/toimitus`. Malli ei ole työkalu. Sen tehtävä on näyttää
mekanismi niin pienenä, että sen voi lukea kokonaan ja muuttaa
parametreja itse. Mallien luvut ovat havainnollistuksia, eikä niitä
pidä siirtää sellaisinaan omaan projektiin.

Kaikki esimerkit ajetaan tämän tutoriaalin testeissä, ja niiden
tulosteet on tarkistettu. Satunnaisuutta käyttävät mallit alustetaan
kiinteällä siemenluvulla ja väliaikaiset Git-repositoriot kiinteillä
päivämäärillä, joten tulosteet ovat samat joka ajossa. Yksi esimerkki
on poikkeus: luvun 6 GitHub Actions -työnkulku tarkistetaan skeemaa
vasten, mutta sitä ei ajeta. Luvussa 6 on lisäksi tapaustutkimus, joka
kuvaa näiden tutoriaalien oman toimitusputken sellaisena kuin se on.

## Esitiedot ja rajaus

Esitietoina ovat *Testivetoinen kehitys ja testisuunnittelu* sekä
*Kontit ja pilvi-infrastruktuuri*. Ensimmäinen siksi, että koko
aihe nojaa automaattisiin testeihin: putki on niin luotettava kuin sen
testit. Jälkimmäinen siksi, että konttikuva on nykyisin tavallisin
artefakti ja Kubernetes tavallinen käyttöönottokohde. Esimerkkien
lukemiseen riittää Python ja Gitin peruskäyttö.

Usea naapuritutoriaali käsittelee samaa aihetta omasta suunnastaan.
Niiden sisältöä ei toisteta, vaan niihin viitataan.

| Aihe | Tutoriaali |
|------------------------------------|-----------------------------------|
| haarat, yhdistäminen, tagit, semanttinen versiointi | *Versionhallinta (Git)* |
| CI-putki C- ja C++-projektille, toistettava käännös | *Käännösjärjestelmät, testaus ja CI* |
| konttikuvan putki, Helm, Terraform, Kubernetes-käyttöönotot | *Kontit ja pilvi-infrastruktuuri* |
| salaisuudet, toimitusketjun turvallisuus, SBOM, allekirjoitukset | *Tietoturva kehitystyössä* |
| palvelinten konfiguraationhallinta (Ansible) | *Palvelinympäristöt* |
| integraatiotestit putkessa, migraatioiden testaus | *Integraatiotestaus ja Testcontainers* |
| SLO, virhebudjetti, valvonta ja havaittavuus | *Skaalautuvien järjestelmien suunnittelu* |
| erän koko, virtaus, läpimenoaika | *Ohjelmistoprojektin hallinta* |
| DevOps ja SRE organisaation rakenteena | *Tiimit ja organisaatiomallit* |

Tietoturva rajataan tässä tutoriaalissa pois lähes kokonaan. Putki on
tuotantoon johtava reitti ja siksi hyökkääjälle arvokas kohde, mutta
sen suojaaminen on oma aiheensa, jonka *Tietoturva kehitystyössä*
käsittelee.

## Tutoriaalin rakenne

Luvut etenevät muutoksen matkan mukaisessa järjestyksessä.

- **Luvut 2–3** käsittelevät integraatiota: miksi työ yhdistetään
  päivittäin ja miten se onnistuu, kun työ on kesken.
- **Luvut 4–6** käsittelevät toimitusputkea: vaiheet ja nopea palaute,
  artefaktit ja ympäristöt sekä putken kuvaaminen koodina.
- **Luvut 7–9** käsittelevät julkaisemista: ominaisuusliput,
  julkaisustrategiat ja tietokantamuutokset.
- **Luku 10** käsittelee infrastruktuuria koodina ja GitOpsia.
- **Luku 11** käsittelee toimituskyvyn mittaamista ja mittareiden
  väärinkäyttöä.

Jokainen luku päättyy osioihin *Käytännössä* ja *Itsearviointi*.
