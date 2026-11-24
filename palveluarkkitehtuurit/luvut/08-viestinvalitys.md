# Viestinvälitys

Asynkronisessa viestinnässä lähettäjä jättää viestin
*viestinvälittäjälle* (*message broker*) eikä odota vastaanottajaa.
Välittäjä säilyttää viestin, kunnes vastaanottaja ehtii käsitellä sen.
Lähettäjä ja vastaanottaja irtoavat toisistaan ajassa: myynti voi ottaa
tilauksia vastaan, vaikka varasto olisi huoltokatkolla, ja varasto
käsittelee jonon, kun se palaa.

## Välittäjä esimerkeissä

Esimerkin `viestit`-moduli upottaa ActiveMQ Artemis -välittäjän
sovellukseen. Riippuvuuksina on Spring Bootin Artemis-starter ja
välittäjän palvelinosa:

```{.xml tiedosto="esimerkit/viestit/pom.xml" osa="artemis"}
```

```{.yaml tiedosto="esimerkit/viestit/src/main/resources/application.yaml" osa="asetukset"}
```

Tuotannossa välittäjä on erillinen, replikoitu palvelu, ja
`spring.artemis.mode` on `native` ja osoite osoittaa siihen. Koodi ei
muutu.

## Jono ja aihe

Välittäjät tarjoavat kaksi perusmallia:

- **Jono** (*point-to-point*): jokainen viesti menee yhdelle
  vastaanottajalle. Jos jonoa kuuntelee monta kopiota samasta
  palvelusta, ne jakavat työn (*kilpailevat kuluttajat*, *competing
  consumers*). Komennot ("varaa tuotteet") kulkevat jonoissa.
- **Aihe** (*publish–subscribe*): jokainen tilaaja saa oman kopionsa.
  Tapahtumat ("tilaus vahvistettu") julkaistaan aiheisiin, ja uusi
  kiinnostunut palvelu tilaa aiheen muuttamatta julkaisijaa.

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/Viestinvalitys.java" osa="kuuntelijat"}
```

Kuuntelijoiden tehdas on transaktionaalinen: viesti kuitataan vasta,
kun käsittely on onnistunut. Jos käsittely heittää poikkeuksen, viesti
palaa jonoon ja toimitetaan uudelleen.

Tiedostossa näkyy myös yleinen Spring-sudenkuoppa.
`@Configuration`-luokan `@Bean`-metodin kutsu toisesta
`@Bean`-metodista palauttaa *saman* olion, ei uutta. Jos aiheiden tehdas rakennettaisiin kutsumalla
`jonot()` ja muuttamalla tulos julkaise–tilaa-tilaan, myös jonojen
kuuntelijat muuttuisivat aiheiden tilaajiksi, eikä yksikään komento
menisi perille. Siksi molemmat tehtaat rakennetaan yhteisellä
yksityisellä apumetodilla.

## Komento, tapahtuma ja kysely

Viestit jaetaan merkityksen mukaan, ja jako ohjaa nimeämistä ja
reititystä:

| Laji | Nimi | Vastaanottajia | Esimerkki |
|------|------|----------------|-----------|
| Komento | käskymuoto | yksi | `VARAA`, `VELOITA` |
| Tapahtuma | menneessä aikamuodossa | 0..n | `TilausVahvistettu` |
| Kysely ja vastaus | kysymys | yksi, vastaus takaisin | `VARATTU`, `MAKSU_HYLATTY` |

Tapahtuma kertoo, mitä on jo tapahtunut, eikä julkaisija tiedä, kuka
siitä välittää. Komento pyytää tiettyä palvelua tekemään jotain, ja
lähettäjä odottaa lopulta vastausta. Tapahtumalla voi olla kaksi
muotoa:

- **Ilmoitus** (*event notification*): vain tunniste ("tilaus 17
  vahvistettu"). Vastaanottaja hakee tarvitsemansa tiedot julkaisijalta,
  mikä luo takaisin synkronisen riippuvuuden.
- **Tilan siirto** (*event-carried state transfer*): tapahtuma sisältää
  tiedot, joita vastaanottajat tarvitsevat. Vastaanottaja voi rakentaa
  oman näkymänsä kysymättä mitään, mutta tapahtuman muoto on laajempi
  sopimus.

## Vähintään kerran

Välittäjä lupaa toimittaa viestin *vähintään kerran*: jos vastaanottaja
kaatuu ennen kuittausta, viesti toimitetaan uudelleen. Sama viesti voi
siis tulla kahdesti. "Täsmälleen kerran" -toimitusta ei ole yli verkon,
mutta sen vaikutuksen saa aikaan: vastaanottaja tunnistaa toiston ja
käsittelee viestin vain kerran. Tätä kutsutaan *idempotentiksi
vastaanottajaksi* (*idempotent consumer*), ja käsitellyt viestit
kirjataan *saapuneiden tauluun* (*inbox*):

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/yhteinen/Saapuneet.java" osa="saapuneet"}
```

Varaston käsittelijä tekee muutoksen, kirjaa viestin ja lähettää
vastauksen. Kirjaus ja muutos ovat samassa tietokantatransaktiossa, ja
vastaus lähtee samassa välittäjän transaktiossa, jossa komento
kuitataan:

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/varasto/VarastoKasittelija.java" osa="kasittele"}
```

Tietokanta vahvistetaan ennen välittäjää. Jos prosessi kaatuu
välissä, komento tulee uudelleen, `Saapuneet` löytää sen ja palauttaa
tallennetun vastauksen, ja vastaus lähetetään nyt. Testi lähettää
saman komennon kahdesti:

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/ViestitTest.java" osa="toisto"}
```

Saapuneiden taulun pääavain suojaa myös samanaikaisilta kopioilta:
jos kaksi kopiota käsitellään yhtä aikaa, jälkimmäisen lisäys kaatuu
avainrikkomukseen, sen transaktio perutaan, ja uudelleentoimituksessa
se löytää ensimmäisen tuloksen.

## Kuolleiden kirjeiden jono

Viesti, jonka käsittely epäonnistuu joka kerta (*myrkkyviesti*,
*poison message*), toimitettaisiin loputtomiin ja tukkisi jonon. Siksi
välittäjä yrittää rajallisen määrän kertoja ja siirtää viestin sitten
*kuolleiden kirjeiden jonoon* (*dead letter queue*, DLQ):

```{.java tiedosto="esimerkit/viestit/src/main/java/fi/tutoriaalit/palvelut/viestit/Viestinvalitys.java" osa="dlq"}
```

```{.java tiedosto="esimerkit/viestit/src/test/java/fi/tutoriaalit/palvelut/viestit/ViestitTest.java" osa="myrkky"}
```

Kuolleiden kirjeiden jonoa valvotaan ja sen viestit tutkitaan:
useimmiten syy on ohjelmointivirhe tai odottamaton muoto. Korjauksen
jälkeen viestit siirretään takaisin alkuperäiseen jonoon.

## Järjestys ja viestien muoto

Jono säilyttää järjestyksen, kun sillä on yksi kuluttaja. Kilpailevat
kuluttajat ja uudelleentoimitukset rikkovat järjestyksen, joten
vastaanottajan on kestettävä myöhästyneet ja epäjärjestyksessä tulevat
viestit. Esimerkin saga tekee tämän tilakoneella: vastaus, joka ei sovi
nykyiseen tilaan, ohitetaan (luku 10). Jos järjestys on välttämätön,
viestit ryhmitellään avaimella (Artemisin viestiryhmät, Kafkan osiot),
jolloin saman tilauksen viestit käsittelee aina sama kuluttaja.

Viestin muoto on sopimus samoin kuin rajapinta. Samat säännöt
pätevät: lisää, älä muuta, ja lue suvaitsevaisesti. Laajoissa
järjestelmissä muodot kirjataan skeemarekisteriin (Avro, Protobuf tai
JSON Schema), joka hylkää yhteensopimattomat muutokset jo julkaisussa.

## Jonot vai loki: Kafka

Apache Kafka ei ole perinteinen jono vaan *pysyvä loki*. Viestit
kirjoitetaan aiheen osioihin, ne säilyvät määräajan riippumatta siitä,
onko joku lukenut ne, ja jokainen kuluttajaryhmä pitää kirjaa omasta
kohdastaan (*offset*).

| | Perinteinen välittäjä (Artemis, RabbitMQ) | Loki (Kafka) |
|---|---|---|
| Luettu viesti | poistetaan | säilyy määräajan |
| Uusi kuluttaja | saa vain uudet viestit | voi lukea historian alusta |
| Järjestys | jonossa, yhdellä kuluttajalla | osion sisällä |
| Rinnakkaisuus | kuluttajia lisäämällä | osioita lisäämällä |
| Uudelleentoisto | ei | kohdan siirto taaksepäin |
| Vahvuus | komennot, työjonot, reititys | tapahtumavirrat, analytiikka, suuri volyymi |

Lokin uudelleentoisto on voimakas työkalu: uuden palvelun näkymän voi
rakentaa lukemalla kaikki tapahtumat alusta. Kafkan hinta on
monimutkaisempi operointi ja osiointiin sidottu rinnakkaisuus.

## Käytännössä

- **Komennot jonoihin, tapahtumat aiheisiin.** Nimeä tapahtumat
  menneessä aikamuodossa; niiden julkaisija ei tunne vastaanottajia.
- **Jokainen kuluttaja on idempotentti.** Toimitus on vähintään kerran,
  joten toisto on normaali tilanne eikä virhe.
- **Kuolleiden kirjeiden jono ja sen valvonta** jokaiselle jonolle.
  Myrkkyviesti ei saa pysäyttää jonoa.
- **Älä luota järjestykseen**, ellei sitä ole erikseen taattu
  avaimella; tilakone ohittaa myöhästyneet viestit.
- **Hinnat:** välittäjä on uusi kriittinen palvelu, joka on
  replikoitava ja valvottava; viive kasvaa; virheiden jäljitys vaatii
  korrelaatiotunnukset ja hajautetun jäljityksen.

## Itsearviointi

- Osaat selittää jonon ja aiheen eron ja valita, kumpaan viesti
  kuuluu.
- Osaat erottaa komennon, tapahtuman ja kyselyn sekä ilmoituksen ja
  tilan siirron.
- Osaat toteuttaa idempotentin vastaanottajan saapuneiden taululla ja
  selittää, miksi täsmälleen kerran -toimitusta ei ole.
- Osaat konfiguroida kuolleiden kirjeiden jonon ja kertoa, mitä sen
  viesteille tehdään.
- Osaat verrata perinteistä välittäjää ja Kafkan kaltaista lokia.
